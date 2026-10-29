"""Collecte des données CIVIX nécessaires aux analyses, avec des volumes d'appels bornés."""

import asyncio
import math
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from assemblee_mcp.analytics.stats import day_of, evenly_spaced
from assemblee_mcp.civix.budget import CivixBudgetError
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Scrutin, ScrutinSummary, ScrutinVotes
from assemblee_mcp.civix.search import search_scrutin_pool

LIST_PAGE_SIZE = 50
MAX_LIST_PAGES = 20
BATCH_PAGES = 3
SAMPLE_MAX_PAGES = 10


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


def page_dates(items: list[ScrutinSummary]) -> list[date]:
    """Jours des scrutins d'une page."""
    return [day for item in items if (day := day_of(item)) is not None]


async def first_page_reaching(
    client: CivixClient, end: date, last_page: int, legislature: int | None
) -> int:
    """Première page dont le scrutin le plus ancien date au plus tard de `end` (dichotomie)."""
    low, high = 1, last_page
    while low < high:
        middle = (low + high) // 2
        page = await client.list_scrutins(
            legislature=legislature, page=middle, page_size=LIST_PAGE_SIZE
        )
        days = page_dates(list(page.attributes.results))
        if days and min(days) <= end:
            high = middle
        else:
            low = middle + 1
    return low


async def fetch_period(
    client: CivixClient,
    start: date,
    end: date,
    *,
    legislature: int | None = None,
    max_pages: int = MAX_LIST_PAGES,
) -> Listing:
    """Scrutins entre `start` et `end` (la liste CIVIX est triée du plus récent au plus ancien)."""
    first = await client.list_scrutins(legislature=legislature, page=1, page_size=LIST_PAGE_SIZE)
    total = first.pagination.total if first.pagination else None
    first_days = page_dates(list(first.attributes.results))
    first_page = 1
    if total and first_days and max(first_days) > end:
        last_page = math.ceil(total / LIST_PAGE_SIZE)
        first_page = await first_page_reaching(client, end, last_page, legislature)
    collected: list[ScrutinSummary] = []
    page = first_page
    fetched = 0
    exhausted = False
    while fetched < max_pages and not exhausted:
        numbers = list(range(page, page + min(BATCH_PAGES, max_pages - fetched)))
        responses = await asyncio.gather(
            *(
                client.list_scrutins(legislature=legislature, page=n, page_size=LIST_PAGE_SIZE)
                for n in numbers
            )
        )
        for response in responses:
            collected.extend(response.attributes.results)
            days = page_dates(list(response.attributes.results))
            reached_start = bool(days) and min(days) < start
            last = response.pagination is None or response.pagination.next_page is None
            exhausted = exhausted or reached_start or last or not days
        fetched += len(numbers)
        page += len(numbers)
    kept = [i for i in collected if (d := day_of(i)) is not None and start <= d <= end]
    return Listing(kept, total, fetched, truncated=not exhausted)


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


def current_day() -> date:
    """Jour courant (UTC)."""
    return datetime.now(UTC).date()
