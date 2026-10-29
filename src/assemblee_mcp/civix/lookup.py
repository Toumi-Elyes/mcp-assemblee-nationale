"""Recherches composées au-dessus du client : députés par nom, groupes, membres d'un groupe."""

import asyncio
import math
import re

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Depute, Groupe
from assemblee_mcp.textutils import fold, tokens

DEPUTE_UID_PATTERN = re.compile(r"^PA\d+$", re.IGNORECASE)
DIRECTORY_PAGE_SIZE = 50
MAX_DIRECTORY_PAGES = 20


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


async def find_deputes(
    client: CivixClient,
    nom: str,
    *,
    groupe: str | None = None,
    legislature: int | None = None,
) -> list[Depute]:
    """Cherche des députés par nom.

    `/deputes` n'a pas de filtre par nom : on passe par `/search` (sensible aux accents), puis
    on filtre localement sans tenir compte des accents. Sans résultat, on parcourt l'annuaire.
    """
    if DEPUTE_UID_PATTERN.match(nom.strip()):
        return [(await client.get_depute(nom.strip().upper())).attributes.deputy]
    matches: list[Depute] = []
    if legislature is None:
        hits = (await client.search(nom)).attributes.results.deputes
        matches = rank_by_name([hit.to_depute() for hit in hits], nom)
        if groupe is not None:
            matches = _only_groupe(matches, groupe)
    if matches:
        return matches
    directory = await all_deputes(client, groupe=groupe, legislature=legislature)
    return rank_by_name(directory, nom)


def _only_groupe(deputes: list[Depute], groupe: str) -> list[Depute]:
    wanted = fold(groupe)
    return [d for d in deputes if d.groupe_abrev is not None and fold(d.groupe_abrev) == wanted]
