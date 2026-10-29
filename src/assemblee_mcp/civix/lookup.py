"""Recherches composées au-dessus du client : députés par nom, groupes, membres d'un groupe."""

import asyncio
import math
import re

from assemblee_mcp.civix.budget import CivixBudgetError, can_afford
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixNotFoundError
from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.limits import (
    CIVIX_PAGE_SIZE,
    MAX_DIRECTORY_PAGES,
    MAX_NAME_SEARCHES,
    SEARCH_CATEGORY_CAP,
)
from assemblee_mcp.textutils import fold, strip_accents, tokens

DEPUTE_UID_PATTERN = re.compile(r"^PA\d+$", re.IGNORECASE)
CURRENT_LEGISLATURE = 17
ASCII_LIMIT = 127
MIN_STEM_LENGTH = 3
MAX_WORD_SEARCHES = 2


async def list_groupes(client: CivixClient) -> list[Groupe]:
    """Groupes parlementaires (appel mis en cache)."""
    return list((await client.list_groupes()).attributes.groups)


async def find_groupe(client: CivixClient, abbr: str) -> Groupe | None:
    """Retrouve un groupe par son sigle, sans tenir compte de la casse."""
    wanted = fold(abbr)
    for groupe in await list_groupes(client):
        if fold(groupe.abbr) == wanted:
            return groupe
    return None


async def groupe_abbreviations(client: CivixClient) -> dict[str, str]:
    """Correspondance identifiant de groupe vers sigle."""
    return {groupe.uid: groupe.abbr for groupe in await list_groupes(client)}


async def all_deputes(
    client: CivixClient, *, groupe: str | None = None, legislature: int | None = None
) -> list[Depute]:
    """Parcourt toutes les pages de `/deputes` (50 par page, pages suivantes en parallèle)."""
    first = await client.list_deputes(
        groupe=groupe, legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE
    )
    deputes = list(first.attributes.results)
    total = first.pagination.total if first.pagination else None
    if first.pagination is None or first.pagination.next_page is None:
        return deputes
    page_count = (
        min(math.ceil(total / CIVIX_PAGE_SIZE), MAX_DIRECTORY_PAGES)
        if total
        else MAX_DIRECTORY_PAGES
    )
    if not can_afford(page_count - 1):
        raise CivixBudgetError
    pages = await asyncio.gather(
        *(
            client.list_deputes(
                groupe=groupe, legislature=legislature, page=page, page_size=CIVIX_PAGE_SIZE
            )
            for page in range(2, page_count + 1)
        )
    )
    for page in pages:
        deputes.extend(page.attributes.results)
    return deputes


async def groupe_member_uids(client: CivixClient, abbr: str) -> set[str]:
    """Identifiants des députés actuellement membres d'un groupe."""
    return {depute.uid for depute in await all_deputes(client, groupe=abbr)}


def name_score(depute: Depute, query_tokens: list[str]) -> int | None:
    """Score de correspondance nom/requête (plus petit = meilleur), `None` si aucune."""
    words = tokens(depute.full_name)
    haystack = " ".join(words)
    if not all(token in haystack for token in query_tokens):
        return None
    exact = sum(1 for token in query_tokens if token in words)
    return len(query_tokens) - exact


def rank_by_name(deputes: list[Depute], query: str) -> list[Depute]:
    """Garde les députés dont le nom contient tous les mots de la requête, meilleurs d'abord."""
    query_tokens = tokens(query)
    if not query_tokens:
        return []
    scored = [(name_score(depute, query_tokens), depute) for depute in deputes]
    matches = [(score, depute) for score, depute in scored if score is not None]
    matches.sort(key=lambda item: (item[0], fold(item[1].full_name)))
    return [depute for _, depute in matches]


def is_exact_name(depute: Depute, query: str) -> bool:
    """Vrai si la requête est exactement le nom complet (dans un sens ou dans l'autre)."""
    query_tokens = sorted(tokens(query))
    return sorted(tokens(depute.full_name)) == query_tokens


async def resolve_groupe(client: CivixClient, groupe: str) -> str:
    """Sigle officiel d'un groupe ; lève `CivixNotFoundError` s'il est inconnu."""
    found = await find_groupe(client, groupe)
    if found is not None:
        return found.abbr
    known = ", ".join(groupe.abbr for groupe in await list_groupes(client))
    raise CivixNotFoundError(f"Groupe « {groupe} » inconnu. Groupes disponibles : {known}.")


def stem_before_accent(word: str) -> str:
    """Début d'un mot jusqu'à sa première lettre accentuée (la recherche CIVIX l'accepte)."""
    for index, char in enumerate(word):
        if ord(char) > ASCII_LIMIT:
            return word[:index]
    return word


def name_search_variants(name: str) -> list[str]:
    """Formulations du nom à essayer dans `/search`, de la plus fidèle à la plus tolérante.

    CIVIX est sensible aux accents et ne retrouve pas certains noms accentués : on essaie le nom
    tel que saisi, sans accents, les mots les plus longs un à un, puis leur début avant l'accent.
    """
    typed = " ".join(name.split())
    words = sorted(typed.split(), key=len, reverse=True)
    stems = [
        stem
        for word in words
        if (stem := stem_before_accent(word)) != word and len(stem) >= MIN_STEM_LENGTH
    ]
    candidates = [typed, strip_accents(typed), *stems]
    if len(words) > 1:
        candidates += words[:MAX_WORD_SEARCHES]
    return list(dict.fromkeys(candidates))[:MAX_NAME_SEARCHES]


async def search_deputes(client: CivixClient, nom: str) -> tuple[list[Depute], bool]:
    """Députés trouvés par `/search`, filtrés localement ; indique si la liste est tronquée.

    S'arrête à la première formulation qui donne un député correspondant au nom.
    """
    for variant in name_search_variants(nom):
        hits = (await client.search(variant)).attributes.results.deputes
        matches = rank_by_name([hit.to_depute() for hit in hits], nom)
        if matches:
            return matches, len(hits) >= SEARCH_CATEGORY_CAP
    return [], False


async def find_deputes(
    client: CivixClient,
    nom: str,
    *,
    groupe: str | None = None,
    legislature: int | None = None,
) -> list[Depute]:
    """Cherche des députés par nom (législature en cours uniquement) : le résolveur unique.

    Un identifiant (PA…) est exact. Sinon, si l'annuaire est déjà en mémoire il fait foi ;
    sinon on essaie `/search` (plusieurs formulations), puis l'annuaire complet quand la
    recherche ne trouve rien ou que sa liste est tronquée. La comparaison ignore accents et casse.
    """
    if legislature not in {None, CURRENT_LEGISLATURE}:
        raise CivixNotFoundError("Seule la 17e législature est couverte pour les députés.")
    abbr = await resolve_groupe(client, groupe) if groupe is not None else None
    if DEPUTE_UID_PATTERN.match(nom.strip()):
        return [(await client.get_depute(nom.strip().upper())).attributes.deputy]
    matches = await _match_by_name(client, nom)
    return _only_groupe(matches, abbr) if abbr is not None else matches


async def _match_by_name(client: CivixClient, nom: str) -> list[Depute]:
    """Députés dont le nom correspond, via l'annuaire en mémoire, `/search` ou l'annuaire."""
    cached = client.directory.cached()
    if cached is not None:
        return rank_by_name(cached, nom)
    matches, truncated = await search_deputes(client, nom)
    if matches and not truncated:
        return matches
    return rank_by_name(await client.directory.load(), nom)


def _only_groupe(deputes: list[Depute], groupe: str) -> list[Depute]:
    wanted = fold(groupe)
    return [
        depute
        for depute in deputes
        if depute.groupe_abrev is not None and fold(depute.groupe_abrev) == wanted
    ]
