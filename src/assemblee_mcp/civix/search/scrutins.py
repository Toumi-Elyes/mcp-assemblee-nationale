"""Recherche de scrutins par mots-clés : requête exacte, puis recherche élargie."""

import asyncio
import math
from dataclasses import dataclass, replace

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import (
    Pagination,
    ScrutinListResponse,
    ScrutinSummary,
)
from assemblee_mcp.civix.scrutin_archive import COMPLETED_LEGISLATURES, search_archive
from assemblee_mcp.civix.search.broaden import (
    BroadQuery,
    broad_note,
    broaden,
    contains_all,
    stem_note,
    stem_query,
    summary_text,
)
from assemblee_mcp.limits import (
    BROAD_POOL_PAGES,
    CIVIX_PAGE_SIZE,
    EXACT_POOL_PAGES,
)
from assemblee_mcp.textutils import fold


@dataclass(frozen=True)
class ScrutinSearch:
    """Résultat d'une recherche de scrutins, éventuellement élargie."""

    response: ScrutinListResponse | None
    """`None` quand la recherche a porté sur l'archive embarquée (14e et 15e législatures)."""
    results: list[ScrutinSummary]
    pagination: Pagination | None
    note: str | None = None


ARCHIVE_POOL_SIZE = CIVIX_PAGE_SIZE * EXACT_POOL_PAGES
"""Taille d'un lot tiré de l'archive : celle d'un lot de recherche exacte chez CIVIX."""


def archive_matches(legislature: int, query: str) -> tuple[list[ScrutinSummary], str | None]:
    """Scrutins archivés d'une recherche : expression exacte, sinon tous les mots utiles.

    Même logique que chez CIVIX, sur les titres de l'archive de l'Assemblée, sans appel réseau.
    """
    exact = search_archive(legislature, (fold(query.strip()),))
    if exact:
        return exact, None
    stemmed = stem_query(query.strip())
    if stemmed is not None:
        singular = search_archive(legislature, (fold(stemmed),))
        if singular:
            return singular, stem_note(query, stemmed)
    broad = broaden(query)
    if broad is None:
        return [], None
    matches = search_archive(legislature, broad.required)
    return matches, broad_note(query, broad, truncated=False) if matches else None


def scrutins_empty(response: ScrutinListResponse) -> bool:
    """Vrai si CIVIX n'a trouvé aucun scrutin."""
    pagination = response.pagination
    return not response.attributes.results and (pagination is None or not pagination.total)


async def search_scrutins(
    client: CivixClient,
    query: str | None,
    *,
    legislature: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> ScrutinSearch:
    """Cherche des scrutins (au plus 4 appels CIVIX ; aucun pour les 14e et 15e législatures).

    Expression exacte, puis la même au singulier, puis tous ses mots utiles (recherche élargie).
    """
    if query and legislature in COMPLETED_LEGISLATURES:
        items, note = archive_matches(legislature, query)
        start = (page - 1) * page_size
        pagination = Pagination(
            page=page,
            page_size=page_size,
            next_page=page + 1 if start + page_size < len(items) else None,
            count_total=len(items),
        )
        return ScrutinSearch(None, items[start : start + page_size], pagination, note)
    exact = await client.list_scrutins(
        query, legislature=legislature, page=page, page_size=page_size
    )
    if query is None or not scrutins_empty(exact):
        return ScrutinSearch(exact, list(exact.attributes.results), exact.pagination)
    stemmed = stem_query(query)
    if stemmed is not None:
        singular = await client.list_scrutins(
            stemmed, legislature=legislature, page=page, page_size=page_size
        )
        if not scrutins_empty(singular):
            results = list(singular.attributes.results)
            note = stem_note(query, stemmed)
            return ScrutinSearch(singular, results, singular.pagination, note)
    broad = broaden(query)
    if broad is None:
        return ScrutinSearch(exact, [], exact.pagination)
    pool, truncated = await broad_pool(client, broad, legislature)
    matches = [item for item in pool if contains_all(summary_text(item), broad.required)]
    start = (page - 1) * page_size
    shown = matches[start : start + page_size]
    pagination = Pagination(
        page=page,
        page_size=page_size,
        next_page=page + 1 if start + page_size < len(matches) else None,
        count_total=len(matches),
    )
    return ScrutinSearch(
        exact, shown, pagination, broad_note(query or "", broad, truncated=truncated)
    )


async def broad_pool(
    client: CivixClient, broad: BroadQuery, legislature: int | None
) -> tuple[list[ScrutinSummary], bool]:
    """Scrutins contenant le mot distinctif (les 300 plus récents), du plus récent au plus ancien.

    Lit la première page, puis seulement les pages que CIVIX annonce (6 au plus), en parallèle.
    Renvoie aussi si la liste est tronquée (des pages au-delà de la limite existaient).
    """
    first = await client.list_scrutins(
        broad.term, legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE
    )
    pool = list(first.attributes.results)
    total = first.pagination.total if first.pagination else None
    available = math.ceil(total / CIVIX_PAGE_SIZE) if total else 1
    last_page = min(available, BROAD_POOL_PAGES)
    pages = await asyncio.gather(
        *(
            client.list_scrutins(
                broad.term, legislature=legislature, page=number, page_size=CIVIX_PAGE_SIZE
            )
            for number in range(2, last_page + 1)
        )
    )
    for page in pages:
        pool.extend(page.attributes.results)
    return pool, available > BROAD_POOL_PAGES


def is_last(page: ScrutinListResponse) -> bool:
    """Vrai si CIVIX n'annonce pas de page suivante."""
    return page.pagination is None or page.pagination.next_page is None


@dataclass(frozen=True)
class ScrutinPool:
    """Scrutins correspondant à une recherche, jusqu'à 100, du plus récent au plus ancien."""

    items: list[ScrutinSummary]
    matching: int
    truncated: bool
    note: str | None = None


async def search_scrutin_pool(
    client: CivixClient, query: str, *, legislature: int | None = None
) -> ScrutinPool:
    """Rassemble les scrutins d'une recherche (au plus 9 appels CIVIX), sans pagination.

    Expression exacte, puis la même au singulier, puis tous ses mots utiles (recherche élargie).
    """
    if legislature in COMPLETED_LEGISLATURES:
        items, note = archive_matches(legislature, query)
        return ScrutinPool(
            items[:ARCHIVE_POOL_SIZE], len(items), len(items) > ARCHIVE_POOL_SIZE, note
        )
    first = await client.list_scrutins(
        query, legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE
    )
    if not scrutins_empty(first):
        return await exact_pool(client, query, legislature, first)
    stemmed = stem_query(query)
    if stemmed is not None:
        singular = await client.list_scrutins(
            stemmed, legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE
        )
        if not scrutins_empty(singular):
            found = await exact_pool(client, stemmed, legislature, singular)
            return replace(found, note=stem_note(query, stemmed))
    broad = broaden(query)
    if broad is None:
        return ScrutinPool([], 0, False)
    pool, truncated = await broad_pool(client, broad, legislature)
    matches = [item for item in pool if contains_all(summary_text(item), broad.required)]
    note = broad_note(query, broad, truncated=truncated)
    return ScrutinPool(matches, len(matches), truncated, note)


async def exact_pool(
    client: CivixClient, query: str, legislature: int | None, first: ScrutinListResponse
) -> ScrutinPool:
    """Scrutins d'une requête exacte : première page déjà lue, plus `EXACT_POOL_PAGES - 1` pages."""
    items = list(first.attributes.results)
    last = first
    for number in range(2, EXACT_POOL_PAGES + 1):
        if is_last(last):
            break
        last = await client.list_scrutins(
            query, legislature=legislature, page=number, page_size=CIVIX_PAGE_SIZE
        )
        items.extend(last.attributes.results)
    total = first.pagination.total if first.pagination else None
    return ScrutinPool(items, total if total is not None else len(items), not is_last(last))
