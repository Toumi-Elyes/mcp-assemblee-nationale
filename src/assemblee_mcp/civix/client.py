"""Client asynchrone de l'API CIVIX : nouvelle tentative, cache mémoire, modèles Pydantic."""

import asyncio
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from assemblee_mcp.civix.budget import CivixBudgetError, charge_call
from assemblee_mcp.civix.cache import CacheKey, TtlCache
from assemblee_mcp.civix.errors import (
    UNEXPECTED_MESSAGE,
    CivixError,
    CivixNotFoundError,
    CivixUnavailableError,
)
from assemblee_mcp.civix.models import (
    CivixModel,
    CivixResponse,
    DeputeDetailResponse,
    DeputeListResponse,
    GroupeDetailResponse,
    GroupeListResponse,
    Scrutin,
    ScrutinListResponse,
    ScrutinResponse,
    ScrutinVotesResponse,
    SearchResponse,
    StatementsResponse,
)
from assemblee_mcp.config import (
    CONNECT_TIMEOUT_SECONDS,
    IMMUTABLE_AFTER_DAYS,
    MAX_CONCURRENT_REQUESTS,
    MAX_CONNECTIONS,
    MAX_KEEPALIVE_CONNECTIONS,
    POOL_TIMEOUT_SECONDS,
    Settings,
)

QueryParams = Mapping[str, str | int | bool | None]
MAX_ATTEMPTS = 2
FORBIDDEN_SEGMENTS = frozenset({"", ".", ".."})
RETRYABLE_STATUSES = frozenset({HTTPStatus.BAD_GATEWAY, HTTPStatus.GATEWAY_TIMEOUT})
VOTES_SUFFIX = "/votes"
DETAIL_PATH_SLASHES = 2


def segment(value: str) -> str:
    """Encode une valeur insérée dans un chemin d'URL ; refuse `""`, `.` et `..`."""
    if value in FORBIDDEN_SEGMENTS:
        raise CivixNotFoundError
    return quote(value, safe="")


def parse_response(response: httpx.Response) -> Any:
    """Corps JSON d'une réponse CIVIX, ou l'erreur française correspondant au statut HTTP.

    429 et 503 ne sont pas rejoués : insister aggraverait la charge d'un service déjà saturé.
    """
    status = response.status_code
    if status == HTTPStatus.NOT_FOUND:
        raise CivixNotFoundError
    if status >= HTTPStatus.INTERNAL_SERVER_ERROR or status == HTTPStatus.TOO_MANY_REQUESTS:
        raise CivixUnavailableError
    if status >= HTTPStatus.BAD_REQUEST:
        raise CivixError(UNEXPECTED_MESSAGE)
    try:
        return response.json()
    except ValueError as error:
        raise CivixError(UNEXPECTED_MESSAGE) from error


class CivixClient:
    """Interroge CIVIX avec cache TTL, une nouvelle tentative et erreurs en français."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Prépare le client ; `transport` et `clock` sont injectables pour les tests."""
        settings_ = settings or Settings.from_env()
        self.settings = settings_
        self._transport = transport
        self._clock = clock
        self._http: httpx.AsyncClient | None = None
        self._cache = TtlCache(settings_.cache_max_entries, settings_.cache_ttl, clock)
        self._votes_cache = TtlCache(settings_.votes_cache_max_entries, settings_.cache_ttl, clock)
        self._detail_cache = TtlCache(
            settings_.detail_cache_max_entries, settings_.cache_ttl, clock
        )
        self._inflight: dict[CacheKey, asyncio.Future[CivixResponse[Any]]] = {}
        self._slots = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def aclose(self) -> None:
        """Ferme la connexion HTTP sous-jacente."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                base_url=self.settings.base_url,
                timeout=httpx.Timeout(
                    self.settings.timeout,
                    connect=CONNECT_TIMEOUT_SECONDS,
                    pool=POOL_TIMEOUT_SECONDS,
                ),
                limits=httpx.Limits(
                    max_connections=MAX_CONNECTIONS,
                    max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS,
                ),
                headers={"User-Agent": self.settings.user_agent, "Accept": "application/json"},
                transport=self._transport,
            )
        return self._http

    async def search(self, query: str, *, page: int = 1, page_size: int = 10) -> SearchResponse:
        """Recherche globale (députés, scrutins, groupes, dossiers)."""
        params: QueryParams = {"search": query, "page": page, "page_size": page_size}
        return await self._get("/search", params, SearchResponse)

    async def list_scrutins(
        self,
        search: str | None = None,
        *,
        legislature: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> ScrutinListResponse:
        """Liste de scrutins, filtrée par mots-clés et législature."""
        params: QueryParams = {
            "search": search,
            "legislature": legislature,
            "page": page,
            "page_size": page_size,
        }
        return await self._get("/scrutins", params, ScrutinListResponse)

    async def get_scrutin(self, uid: str) -> ScrutinResponse:
        """Détail d'un scrutin avec décomptes."""
        return await self._get(f"/scrutins/{segment(uid)}", {}, ScrutinResponse)

    async def get_votes(self, uid: str) -> ScrutinVotesResponse:
        """Votes individuels d'un scrutin."""
        return await self._get(f"/scrutins/{segment(uid)}/votes", {}, ScrutinVotesResponse)

    async def get_statements(self, uid: str) -> StatementsResponse:
        """Déclarations publiques des groupes sur un scrutin."""
        return await self._get(f"/scrutins/{segment(uid)}/statements", {}, StatementsResponse)

    async def list_deputes(
        self,
        *,
        groupe: str | None = None,
        legislature: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> DeputeListResponse:
        """Liste de députés (CIVIX plafonne `page_size` à 50 ; aucun filtre par nom)."""
        params: QueryParams = {
            "groupe": groupe,
            "legislature": legislature,
            "page": page,
            "page_size": page_size,
        }
        return await self._get("/deputes", params, DeputeListResponse)

    async def get_depute(self, uid: str) -> DeputeDetailResponse:
        """Détail d'un député."""
        return await self._get(f"/deputes/{segment(uid)}", {}, DeputeDetailResponse)

    async def list_groupes(self) -> GroupeListResponse:
        """Liste des groupes parlementaires."""
        return await self._get("/groupes", {}, GroupeListResponse)

    async def get_groupe(self, abbr: str) -> GroupeDetailResponse:
        """Détail d'un groupe."""
        return await self._get(f"/groupes/{segment(abbr)}", {}, GroupeDetailResponse)

    async def _get[AttributesT: CivixModel](
        self,
        path: str,
        params: QueryParams,
        response_model: type[CivixResponse[AttributesT]],
    ) -> CivixResponse[AttributesT]:
        """Réponse du cache, d'une requête identique déjà en vol, ou d'un nouvel appel."""
        clean = {
            key: str(value).lower() if isinstance(value, bool) else str(value)
            for key, value in params.items()
            if value is not None
        }
        key: CacheKey = (path, tuple(sorted(clean.items())))
        cache = self._cache_for(path)
        cached = cache.get(key)
        if cached is not None and isinstance(cached, response_model):
            return cached
        pending = self._inflight.get(key)
        if pending is not None:
            shared = await pending
            if isinstance(shared, response_model):
                return shared
        parsed = await self._load_and_share(key, path, clean, response_model)
        cache.set(key, parsed, self._ttl_for(parsed))
        return parsed

    async def _load_and_share[AttributesT: CivixModel](
        self,
        key: CacheKey,
        path: str,
        params: dict[str, str],
        response_model: type[CivixResponse[AttributesT]],
    ) -> CivixResponse[AttributesT]:
        """Appelle CIVIX en laissant les requêtes identiques simultanées attendre ce résultat."""
        future: asyncio.Future[CivixResponse[Any]] = asyncio.get_running_loop().create_future()
        future.add_done_callback(lambda done: done.cancelled() or done.exception())
        self._inflight[key] = future
        try:
            parsed = await self._load(path, params, response_model)
        except BaseException as error:
            failure = error if isinstance(error, CivixError) else CivixUnavailableError()
            future.set_exception(failure)
            raise
        else:
            future.set_result(parsed)
            return parsed
        finally:
            del self._inflight[key]

    def _cache_for(self, path: str) -> TtlCache:
        """Cache adapté au chemin : votes et détails de scrutin ont chacun le leur."""
        if path.endswith(VOTES_SUFFIX):
            return self._votes_cache
        if path.startswith("/scrutins/") and path.count("/") == DETAIL_PATH_SLASHES:
            return self._detail_cache
        return self._cache

    def _ttl_for(self, response: CivixResponse[Any]) -> float | None:
        """Durée de cache longue pour un scrutin vieux de plus de 2 jours (données figées)."""
        attributes = response.attributes
        if not isinstance(attributes, Scrutin) or attributes.scrutin.date_scrutin is None:
            return None
        voted = attributes.scrutin.date_scrutin
        now = datetime.now(voted.tzinfo)
        if now - voted > timedelta(days=IMMUTABLE_AFTER_DAYS):
            return self.settings.immutable_ttl
        return None

    async def _load[AttributesT: CivixModel](
        self,
        path: str,
        params: dict[str, str],
        response_model: type[CivixResponse[AttributesT]],
    ) -> CivixResponse[AttributesT]:
        """Appelle CIVIX et valide la réponse avec le modèle du point d'accès."""
        payload = await self._fetch_json(path, params)
        try:
            return response_model.model_validate(payload)
        except ValidationError as error:
            raise CivixError(UNEXPECTED_MESSAGE) from error

    async def _fetch_json(self, path: str, params: dict[str, str]) -> Any:
        """GET JSON avec une seule nouvelle tentative, réservée aux pannes passagères."""
        for attempt in range(MAX_ATTEMPTS):
            if attempt > 0:
                await asyncio.sleep(self.settings.retry_delay)
            self._charge_attempt(attempt)
            try:
                async with self._slots:
                    response = await self._client().get(path, params=params)
            except httpx.TransportError:
                continue
            except httpx.HTTPError as error:
                raise CivixUnavailableError from error
            if response.status_code in RETRYABLE_STATUSES:
                continue
            return parse_response(response)
        raise CivixUnavailableError

    def _charge_attempt(self, attempt: int) -> None:
        """Compte l'appel ; une nouvelle tentative sans budget devient « indisponible »."""
        try:
            charge_call()
        except CivixBudgetError:
            if attempt == 0:
                raise
            raise CivixUnavailableError from None
