"""Recherches composées au-dessus du client : députés par nom, groupes, membres d'un groupe."""

import asyncio
import math
import re

from assemblee_mcp.civix.budget import CivixBudgetError, can_afford
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixNotFoundError
from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.textutils import fold, tokens

DEPUTE_UID_PATTERN = re.compile(r"^PA\d+$", re.IGNORECASE)
DIRECTORY_PAGE_SIZE = 50
MAX_DIRECTORY_PAGES = 15
CURRENT_LEGISLATURE = 17
MAX_TOKEN_SEARCHES = 2
MIN_NAME_WORDS = 2


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
        groupe=groupe, legislature=legislature, page=1, page_size=DIRECTORY_PAGE_SIZE
    )
    deputes = list(first.attributes.results)
    total = first.pagination.total if first.pagination else None
    if first.pagination is None or first.pagination.next_page is None:
        return deputes
    page_count = (
        min(math.ceil(total / DIRECTORY_PAGE_SIZE), MAX_DIRECTORY_PAGES)
        if total
        else MAX_DIRECTORY_PAGES
    )
    if not can_afford(page_count - 1):
        raise CivixBudgetError
    pages = await asyncio.gather(
        *(
            client.list_deputes(
                groupe=groupe, legislature=legislature, page=page, page_size=DIRECTORY_PAGE_SIZE
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
    known = ", ".join(g.abbr for g in await list_groupes(client))
    raise CivixNotFoundError(f"Groupe « {groupe} » inconnu. Groupes disponibles : {known}.")


async def search_deputes(client: CivixClient, nom: str) -> list[Depute]:
    """Députés trouvés par `/search`, filtrés localement sans tenir compte des accents.

    Si l'expression complète ne donne rien, les mots les plus longs sont cherchés un à un :
    CIVIX est sensible aux accents, mais le nom de famille en comporte rarement.
    """
    hits = (await client.search(nom)).attributes.results.deputes
    matches = rank_by_name([hit.to_depute() for hit in hits], nom)
    words = sorted(tokens(nom), key=len, reverse=True)
    if matches or len(words) < MIN_NAME_WORDS:
        return matches
    for word in words[:MAX_TOKEN_SEARCHES]:
        found = (await client.search(word)).attributes.results.deputes
        matches = rank_by_name([hit.to_depute() for hit in found], nom)
        if matches:
            return matches
    return []


async def find_deputes(
    client: CivixClient,
    nom: str,
    *,
    groupe: str | None = None,
    legislature: int | None = None,
) -> list[Depute]:
    """Cherche des députés par nom (législature en cours uniquement).

    `/deputes` n'a pas de filtre par nom : on passe par `/search`, puis on filtre localement.
    Sans résultat, l'annuaire est parcouru si le budget d'appels le permet.
    """
    if legislature not in {None, CURRENT_LEGISLATURE}:
        raise CivixNotFoundError("Seule la 17e législature est couverte pour les députés.")
    abbr = await resolve_groupe(client, groupe) if groupe is not None else None
    if DEPUTE_UID_PATTERN.match(nom.strip()):
        return [(await client.get_depute(nom.strip().upper())).attributes.deputy]
    matches = await search_deputes(client, nom)
    if abbr is not None:
        matches = _only_groupe(matches, abbr)
    if matches or not can_afford(MAX_DIRECTORY_PAGES):
        return matches
    directory = await all_deputes(client, groupe=abbr, legislature=legislature)
    return rank_by_name(directory, nom)


def _only_groupe(deputes: list[Depute], groupe: str) -> list[Depute]:
    wanted = fold(groupe)
    return [d for d in deputes if d.groupe_abrev is not None and fold(d.groupe_abrev) == wanted]
