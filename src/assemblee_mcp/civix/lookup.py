"""Recherches composées au-dessus du client : députés par nom, groupes, membres d'un groupe."""

import asyncio
import math
import re
from datetime import date

from assemblee_mcp.civix.archive import ARCHIVED_LEGISLATURES, load_archive
from assemblee_mcp.civix.budget import CivixBudgetError, can_afford
from assemblee_mcp.civix.client import CivixClient, unsupported_legislature_message
from assemblee_mcp.civix.errors import CivixNotFoundError
from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.limits import (
    CIVIX_PAGE_SIZE,
    CURRENT_LEGISLATURE,
    MAX_DIRECTORY_PAGES,
    MAX_NAME_SEARCHES,
    SEARCH_CATEGORY_CAP,
)
from assemblee_mcp.textutils import fold, strip_accents, tokens

DEPUTE_UID_PATTERN = re.compile(r"^PA\d+$", re.IGNORECASE)
SCRUTIN_UID_PATTERN = re.compile(r"^VTANR5L(\d+)V\d+$")
ASCII_LIMIT = 127
MIN_STEM_LENGTH = 3
MAX_WORD_SEARCHES = 2
HINT_MAX_NAMES = 5


def legislature_of_scrutin(uid: str) -> int | None:
    """Législature lue dans l'identifiant d'un scrutin (`VTANR5L16V4105` : la 16e), sinon `None`."""
    found = SCRUTIN_UID_PATTERN.match(uid)
    return int(found.group(1)) if found else None


async def list_groupes(client: CivixClient, legislature: int | None = None) -> list[Groupe]:
    """Groupes parlementaires d'une législature (17e par défaut ; la 17e vient du cache CIVIX)."""
    number = legislature or CURRENT_LEGISLATURE
    if number == CURRENT_LEGISLATURE:
        return list((await client.list_groupes()).attributes.groups)
    archive = load_archive(number)
    if archive is None:
        raise CivixNotFoundError(unsupported_legislature_message(number))
    return list(archive.groupes.values())


async def find_groupe(
    client: CivixClient, abbr: str, legislature: int | None = None
) -> Groupe | None:
    """Retrouve un groupe par son sigle, sans tenir compte de la casse."""
    wanted = fold(abbr)
    for groupe in await list_groupes(client, legislature):
        if fold(groupe.abbr) == wanted:
            return groupe
    return None


async def groupe_abbreviations(
    client: CivixClient, legislature: int | None = None
) -> dict[str, str]:
    """Correspondance identifiant de groupe vers sigle.

    Sans législature, réunit tous les groupes connus (17e par l'API, législatures closes par
    l'index) : leurs identifiants sont distincts, ce qui suffit à afficher des scrutins anciens.
    """
    if legislature is not None:
        return {groupe.uid: groupe.abbr for groupe in await list_groupes(client, legislature)}
    mapping = {groupe.uid: groupe.abbr for groupe in await list_groupes(client)}
    for number in ARCHIVED_LEGISLATURES:
        archive = load_archive(number)
        if archive is not None:
            mapping.update({uid: groupe.abbr for uid, groupe in archive.groupes.items()})
    return mapping


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


def archived_member_uids(legislature: int, abbr: str, day: date) -> set[str]:
    """Membres d'un groupe d'une législature close au jour donné (sigle déjà résolu)."""
    archive = load_archive(legislature)
    if archive is None:
        raise CivixNotFoundError(unsupported_legislature_message(legislature))
    members: set[str] = set()
    for groupe in archive.groupes.values():
        if groupe.abbr == abbr:
            members |= archive.members_at(groupe.uid, day)
    return members


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


async def resolve_groupe(client: CivixClient, groupe: str, legislature: int | None = None) -> str:
    """Sigle officiel d'un groupe ; lève `CivixNotFoundError` s'il est inconnu."""
    found = await find_groupe(client, groupe, legislature)
    if found is not None:
        return found.abbr
    known = ", ".join(item.abbr for item in await list_groupes(client, legislature))
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


def archived_name_hint(nom: str) -> str:
    """Indique, si le nom existe dans une législature close, comment la demander ; sinon `""`."""
    lines: list[str] = []
    for number in ARCHIVED_LEGISLATURES:
        archive = load_archive(number)
        matches = rank_by_name(archive.deputes, nom)[:HINT_MAX_NAMES] if archive else []
        if matches:
            names = ", ".join(f"{depute.full_name} (`{depute.uid}`)" for depute in matches)
            lines.append(
                f"Correspondance dans la {number}e législature : {names}. "
                f"Relancez avec `legislature={number}`."
            )
    return "\n".join(lines)


async def find_deputes(
    client: CivixClient,
    nom: str,
    *,
    groupe: str | None = None,
    legislature: int | None = None,
) -> list[Depute]:
    """Cherche des députés par nom dans une législature (17e par défaut) : le résolveur unique.

    Un identifiant (PA…) est exact. Sinon, si l'annuaire de la législature est déjà en mémoire
    il fait foi ; sinon, pour la 17e, on essaie `/search` (plusieurs formulations) puis
    l'annuaire complet quand la recherche ne trouve rien ou que sa liste est tronquée. Les
    législatures closes se lisent dans l'index embarqué. La comparaison ignore accents et casse.
    """
    number = legislature or CURRENT_LEGISLATURE
    client.directory_for(number)
    abbr = await resolve_groupe(client, groupe, number) if groupe is not None else None
    if DEPUTE_UID_PATTERN.match(nom.strip()):
        return [await find_depute_by_uid(client, nom.strip().upper(), number)]
    matches = await _match_by_name(client, nom, number)
    return _only_groupe(matches, abbr) if abbr is not None else matches


async def find_depute_by_uid(client: CivixClient, uid: str, legislature: int) -> Depute:
    """Député d'identifiant `uid` dans la législature ; `CivixNotFoundError` s'il est inconnu."""
    if legislature == CURRENT_LEGISLATURE:
        return (await client.get_depute(uid)).attributes.deputy
    found = next((d for d in await client.directory_for(legislature).load() if d.uid == uid), None)
    if found is None:
        raise CivixNotFoundError(f"Aucun député {uid} dans la {legislature}e législature.")
    return found


async def _match_by_name(client: CivixClient, nom: str, legislature: int) -> list[Depute]:
    """Députés dont le nom correspond, via l'annuaire en mémoire, `/search` ou l'annuaire."""
    directory = client.directory_for(legislature)
    cached = directory.cached()
    if cached is not None:
        return rank_by_name(cached, nom)
    matches, truncated = await search_deputes(client, nom)
    if matches and not truncated:
        return matches
    return rank_by_name(await directory.load(), nom)


def _only_groupe(deputes: list[Depute], groupe: str) -> list[Depute]:
    wanted = fold(groupe)
    return [
        depute
        for depute in deputes
        if depute.groupe_abrev is not None and fold(depute.groupe_abrev) == wanted
    ]
