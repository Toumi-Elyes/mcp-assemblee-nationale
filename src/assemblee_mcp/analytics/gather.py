"""Collecte des données CIVIX nécessaires aux analyses, avec des volumes d'appels bornés.

La liste des scrutins est triée du plus récent au plus ancien et ne sait pas filtrer par date :
on lit donc les pages utiles, en repérant par dichotomie la page de départ d'une période passée.
"""

import asyncio
import math
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from assemblee_mcp.analytics.stats import day_of, evenly_spaced
from assemblee_mcp.civix.budget import CivixBudgetError
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Scrutin, ScrutinListResponse, ScrutinSummary, ScrutinVotes
from assemblee_mcp.civix.search import search_scrutin_pool
from assemblee_mcp.limits import (
    BATCH_PAGES,
    CIVIX_PAGE_SIZE,
    DOSSIER_MAX_PAGES,
    MAX_LIST_PAGES,
    SAMPLE_MAX_PAGES,
)


@dataclass(frozen=True)
class Listing:
    """Scrutins d'une période, du plus récent au plus ancien."""

    items: list[ScrutinSummary]
    total: int | None
    pages: int
    truncated: bool


@dataclass(frozen=True)
class Sample:
    """Échantillon de scrutins retenus pour une analyse détaillée."""

    chosen: list[ScrutinSummary]
    matching: int
    truncated: bool
    note: str | None = None


def current_day() -> date:
    """Jour courant (UTC)."""
    return datetime.now(UTC).date()


def page_days(page: ScrutinListResponse) -> list[date]:
    """Jours des scrutins d'une page."""
    return [day for item in page.attributes.results if (day := day_of(item)) is not None]


def is_last_page(page: ScrutinListResponse) -> bool:
    """Vrai si CIVIX n'annonce pas de page suivante."""
    return page.pagination is None or page.pagination.next_page is None


async def first_page_reaching(
    client: CivixClient, end: date, last_page: int, legislature: int | None
) -> int:
    """Première page dont le scrutin le plus ancien date au plus tard de `end` (dichotomie)."""
    low, high = 1, last_page
    while low < high:
        middle = (low + high) // 2
        page = await client.list_scrutins(
            legislature=legislature, page=middle, page_size=CIVIX_PAGE_SIZE
        )
        days = page_days(page)
        if days and min(days) <= end:
            high = middle
        else:
            low = middle + 1
    return low


async def read_pages_until(
    client: CivixClient,
    first_page: int,
    start: date,
    legislature: int | None,
    max_pages: int,
) -> tuple[list[ScrutinSummary], int, bool]:
    """Lit des pages par lots jusqu'à dépasser `start`.

    Renvoie les scrutins lus, le nombre de pages lues et si la fin de la période est atteinte.
    """
    collected: list[ScrutinSummary] = []
    fetched = 0
    reached_end = False
    while fetched < max_pages and not reached_end:
        count = min(BATCH_PAGES, max_pages - fetched)
        numbers = range(first_page + fetched, first_page + fetched + count)
        pages = await asyncio.gather(
            *(
                client.list_scrutins(
                    legislature=legislature, page=number, page_size=CIVIX_PAGE_SIZE
                )
                for number in numbers
            )
        )
        for page in pages:
            collected.extend(page.attributes.results)
            days = page_days(page)
            passed_start = bool(days) and min(days) < start
            reached_end = reached_end or passed_start or is_last_page(page) or not days
        fetched += count
    return collected, fetched, reached_end


async def fetch_period(
    client: CivixClient,
    start: date,
    end: date,
    *,
    legislature: int | None = None,
    max_pages: int = MAX_LIST_PAGES,
) -> Listing:
    """Scrutins entre `start` et `end`, lus page par page depuis la plus utile."""
    first = await client.list_scrutins(legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE)
    total = first.pagination.total if first.pagination else None
    first_days = page_days(first)
    first_page = 1
    if total and first_days and max(first_days) > end:
        last_page = math.ceil(total / CIVIX_PAGE_SIZE)
        first_page = await first_page_reaching(client, end, last_page, legislature)
    collected, fetched, reached_end = await read_pages_until(
        client, first_page, start, legislature, max_pages
    )
    kept = [item for item in collected if (day := day_of(item)) is not None and start <= day <= end]
    return Listing(kept, total, fetched, truncated=not reached_end)


def select_kind(items: list[ScrutinSummary], kind: str | None) -> list[ScrutinSummary]:
    """Garde un seul type de scrutin (`texte`, `amendement`, `article`, `scrutin`)."""
    return items if kind is None else [item for item in items if item.type == kind]


async def sample_from_period(
    client: CivixClient,
    days: int,
    count: int,
    *,
    today: date,
    kind: str | None = None,
) -> tuple[Sample, Listing]:
    """Échantillon régulier de `count` scrutins parmi ceux des `days` derniers jours."""
    start = today - timedelta(days=days)
    listing = await fetch_period(client, start, today, max_pages=SAMPLE_MAX_PAGES)
    pool = select_kind(listing.items, kind)
    return Sample(evenly_spaced(pool, count), len(pool), listing.truncated), listing


async def sample_from_query(
    client: CivixClient, query: str, count: int, *, kind: str | None = None
) -> Sample:
    """Les `count` scrutins les plus récents d'une recherche par mots-clés ou dossier."""
    pool = await search_scrutin_pool(client, query)
    items = select_kind(pool.items, kind)
    return Sample(items[:count], len(items), pool.truncated or len(items) > count, pool.note)


async def fetch_dossier_scrutins(
    client: CivixClient, reference: str | None, title: str, fallback: list[ScrutinSummary]
) -> tuple[list[ScrutinSummary], int]:
    """Scrutins d'un dossier (au plus `DOSSIER_MAX_PAGES` pages) et leur nombre total."""
    if reference is None:
        same = [
            item for item in fallback if item.dossier_libelle == title or item.dossier_ref is None
        ]
        return same, len(same)
    first = await client.list_scrutins(reference, page=1, page_size=CIVIX_PAGE_SIZE)
    total = first.pagination.total if first.pagination and first.pagination.total else 0
    items = list(first.attributes.results)
    last_page = min(math.ceil(total / CIVIX_PAGE_SIZE), DOSSIER_MAX_PAGES)
    for batch_start in range(2, last_page + 1, BATCH_PAGES):
        numbers = range(batch_start, min(batch_start + BATCH_PAGES, last_page + 1))
        pages = await asyncio.gather(
            *(
                client.list_scrutins(reference, page=number, page_size=CIVIX_PAGE_SIZE)
                for number in numbers
            )
        )
        for page in pages:
            items.extend(page.attributes.results)
    return [item for item in items if item.dossier_ref == reference], total


async def sample_legislature_pages(
    client: CivixClient, legislature: int, page_count: int
) -> tuple[list[ScrutinSummary], int | None]:
    """Scrutins de pages réparties sur la législature, et le nombre total de scrutins."""
    first = await client.list_scrutins(legislature=legislature, page=1, page_size=CIVIX_PAGE_SIZE)
    total = first.pagination.total if first.pagination else None
    last_page = math.ceil(total / CIVIX_PAGE_SIZE) if total else 1
    others = [
        number for number in evenly_spaced(list(range(1, last_page + 1)), page_count) if number != 1
    ]
    pages = await asyncio.gather(
        *(
            client.list_scrutins(legislature=legislature, page=number, page_size=CIVIX_PAGE_SIZE)
            for number in others
        )
    )
    items = list(first.attributes.results)
    for page in pages:
        items.extend(page.attributes.results)
    return items, total


async def fetch_details(client: CivixClient, scrutins: list[ScrutinSummary]) -> list[Scrutin]:
    """Détail (décomptes par groupe) de chaque scrutin ; ceux indisponibles sont omis."""

    async def one(uid: str) -> Scrutin | None:
        try:
            return (await client.get_scrutin(uid)).attributes
        except CivixBudgetError:
            raise
        except CivixError:
            return None

    results = await asyncio.gather(*(one(item.uid) for item in scrutins))
    return [result for result in results if result is not None]


async def fetch_votes(client: CivixClient, scrutins: list[ScrutinSummary]) -> list[ScrutinVotes]:
    """Votes individuels de chaque scrutin ; ceux indisponibles sont omis."""

    async def one(uid: str) -> ScrutinVotes | None:
        try:
            return (await client.get_votes(uid)).attributes
        except CivixBudgetError:
            raise
        except CivixError:
            return None

    results = await asyncio.gather(*(one(item.uid) for item in scrutins))
    return [result for result in results if result is not None]
