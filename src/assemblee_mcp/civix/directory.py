"""Annuaire complet des députés, gardé en mémoire pour retrouver un nom sans la recherche CIVIX.

La recherche de CIVIX ne trouve pas certains noms accentués (« Thiébaut », « Trouvé ») et tronque
ses résultats à 8. L'annuaire (une quinzaine de pages) est donc lu une fois, puis gardé 24 h :
chaque recherche locale est ensuite gratuite et insensible aux accents et à la casse.
"""

import asyncio
import math
from collections.abc import Awaitable, Callable

from pydantic import TypeAdapter, ValidationError

from assemblee_mcp.civix.budget import unbudgeted
from assemblee_mcp.civix.models import Depute, DeputeListResponse
from assemblee_mcp.civix.shared_cache import SharedCache
from assemblee_mcp.limits import CIVIX_PAGE_SIZE, MAX_DIRECTORY_PAGES

type PageFetcher = Callable[[int], Awaitable[DeputeListResponse]]

SHARED_NAME = "directory"
DEPUTES_ADAPTER = TypeAdapter(list[Depute])


class DeputyDirectory:
    """Liste de tous les députés, chargée à la demande et partagée entre les appels."""

    def __init__(
        self,
        fetch_page: PageFetcher,
        ttl: float,
        clock: Callable[[], float],
        shared: SharedCache | None = None,
    ) -> None:
        """Prépare l'annuaire ; `fetch_page(n)` lit la page `n` de `/deputes` (50 députés).

        `shared` est le cache partagé entre instances, essayé avant de relire les 15 pages.
        """
        self._fetch_page = fetch_page
        self._ttl = ttl
        self._clock = clock
        self._shared = shared if shared is not None else SharedCache()
        self._entry: tuple[float, list[Depute]] | None = None
        self._lock = asyncio.Lock()

    def cached(self) -> list[Depute] | None:
        """Annuaire déjà chargé et encore valable, sinon `None`."""
        if self._entry is None or self._entry[0] <= self._clock():
            return None
        return self._entry[1]

    async def load(self) -> list[Depute]:
        """Annuaire complet ; le charge (hors budget d'appels) s'il n'est pas en mémoire."""
        async with self._lock:
            cached = self.cached()
            if cached is not None:
                return cached
            deputes, ttl = await self._read_shared() or await self._read_remote()
            self._entry = (self._clock() + ttl, deputes)
            return deputes

    async def _read_shared(self) -> tuple[list[Depute], float] | None:
        """Annuaire du cache partagé et sa durée restante, ou `None` s'il est absent ou ancien."""
        found = await self._shared.get(SHARED_NAME)
        if found is None:
            return None
        data, remaining = found
        try:
            return DEPUTES_ADAPTER.validate_python(data), remaining
        except ValidationError:
            return None

    async def _read_remote(self) -> tuple[list[Depute], float]:
        """Lit CIVIX (hors budget d'appels), puis copie l'annuaire dans le cache partagé."""
        with unbudgeted():
            deputes = await self._read_all_pages()
        data = DEPUTES_ADAPTER.dump_python(deputes, mode="json", by_alias=True)
        await self._shared.put(SHARED_NAME, SHARED_NAME, data, self._ttl)
        return deputes, self._ttl

    async def _read_all_pages(self) -> list[Depute]:
        """Lit la première page, puis les suivantes en parallèle."""
        first = await self._fetch_page(1)
        deputes = list(first.attributes.results)
        total = first.pagination.total if first.pagination else None
        has_more = first.pagination is not None and first.pagination.next_page is not None
        if not has_more:
            return deputes
        last_page = math.ceil(total / CIVIX_PAGE_SIZE) if total else MAX_DIRECTORY_PAGES
        pages = await asyncio.gather(
            *(
                self._fetch_page(number)
                for number in range(2, min(last_page, MAX_DIRECTORY_PAGES) + 1)
            )
        )
        for page in pages:
            deputes.extend(page.attributes.results)
        return deputes
