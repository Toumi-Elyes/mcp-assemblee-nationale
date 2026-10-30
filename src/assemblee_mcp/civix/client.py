"""Client asynchrone de l'API CIVIX : nouvelle tentative, cache mémoire, modèles Pydantic."""

import asyncio
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any
from urllib.parse import quote, urlencode

import httpx
from pydantic import ValidationError

from assemblee_mcp.civix.archive import covered_legislatures, load_archive
from assemblee_mcp.civix.budget import CivixBudgetError, charge_call
from assemblee_mcp.civix.cache import CacheKey, TtlCache
from assemblee_mcp.civix.directory import ArchivedDirectory, DeputyDirectory, Directory
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
from assemblee_mcp.civix.scrutin_archive import complete_list, complete_response
from assemblee_mcp.civix.shared_cache import SharedCache
from assemblee_mcp.config import (
    CONNECT_TIMEOUT_SECONDS,
    IMMUTABLE_AFTER_DAYS,
    MAX_CONCURRENT_REQUESTS,
    MAX_CONNECTIONS,
    MAX_KEEPALIVE_CONNECTIONS,
    POOL_TIMEOUT_SECONDS,
    Settings,
)
from assemblee_mcp.limits import CIVIX_PAGE_SIZE, CURRENT_LEGISLATURE

QueryParams = Mapping[str, str | int | bool | None]
MAX_ATTEMPTS = 2
FORBIDDEN_SEGMENTS = frozenset({"", ".", ".."})
RETRYABLE_STATUSES = frozenset({HTTPStatus.BAD_GATEWAY, HTTPStatus.GATEWAY_TIMEOUT})
VOTES_SUFFIX = "/votes"
DETAIL_PATH_SLASHES = 2


def unsupported_legislature_message(legislature: int) -> str:
    """Message français pour une législature dont les députés ne sont pas disponibles."""
    return (
        f"La {legislature}e législature n'est pas couverte pour les députés "
        f"(législatures disponibles : {covered_legislatures()})."
    )


def segment(value: str) -> str:
    """Encode une valeur insérée dans un chemin d'URL ; refuse `""`, `.` et `..`."""
    if value in FORBIDDEN_SEGMENTS:
        raise CivixNotFoundError
    return quote(value, safe="")


def shared_name(key: CacheKey) -> str:
    """Nom stable d'une requête dans le cache partagé : chemin et paramètres triés."""
    path, params = key
    return f"{path}?{urlencode(params)}"


def shared_kind(path: str) -> str:
    """Étiquette du cache partagé : détail ou votes de scrutin, sinon la ressource lue."""
    if path.endswith(VOTES_SUFFIX):
        return "scrutin-votes"
    parts = path.strip("/").split("/")
    if parts[0] == "scrutins" and len(parts) == 2:  # noqa: PLR2004
        return "scrutin-detail"
    return parts[0]


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
        shared_cache: SharedCache | None = None,
    ) -> None:
        """Prépare le client ; `transport`, `clock` et `shared_cache` sont injectables (tests).

        Sans `shared_cache`, le second niveau est le Runtime Cache sur Vercel, inactif ailleurs.
        """
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
        self._shared = shared_cache if shared_cache is not None else SharedCache.from_environment()
        self._inflight: dict[CacheKey, asyncio.Future[CivixResponse[Any]]] = {}
        self._slots = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.directory = DeputyDirectory(
            lambda page: self.list_deputes(page=page, page_size=CIVIX_PAGE_SIZE),
            settings_.immutable_ttl,
            clock,
            self._shared,
        )

    def directory_for(self, legislature: int) -> Directory:
        """Annuaire des députés d'une législature : API pour la 17e, index embarqué pour la 16e.

        Lève `CivixNotFoundError` pour une législature qu'aucune source ne couvre.
        """
        if legislature == CURRENT_LEGISLATURE:
            return self.directory
        archive = load_archive(legislature)
        if archive is None:
            raise CivixNotFoundError(unsupported_legislature_message(legislature))
        return ArchivedDirectory(archive.deputes)

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
        """Liste de scrutins, filtrée par mots-clés et législature.

        Les scrutins des 14e et 15e législatures sont complétés par l'archive de l'Assemblée.
        """
        params: QueryParams = {
            "search": search,
            "legislature": legislature,
            "page": page,
            "page_size": page_size,
        }
        return complete_list(await self._get("/scrutins", params, ScrutinListResponse))

    async def get_scrutin(self, uid: str) -> ScrutinResponse:
        """Détail d'un scrutin avec décomptes (complété par l'archive pour les 14e et 15e)."""
        return complete_response(await self._get(f"/scrutins/{segment(uid)}", {}, ScrutinResponse))

    async def get_votes(self, uid: str) -> ScrutinVotesResponse:
        """Votes individuels (décomptes complétés par l'archive pour les 14e et 15e)."""
        path = f"/scrutins/{segment(uid)}/votes"
        return complete_response(await self._get(path, {}, ScrutinVotesResponse))

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
        shared = await self._read_shared(key, response_model)
        if shared is not None:
            cache.set(key, *shared)
            return shared[0]
        pending = self._inflight.get(key)
        if pending is not None:
            awaited = await pending
            if isinstance(awaited, response_model):
                return awaited
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
            await self._write_shared(key, path, parsed)
            return parsed
        finally:
            del self._inflight[key]

    async def _read_shared[AttributesT: CivixModel](
        self, key: CacheKey, response_model: type[CivixResponse[AttributesT]]
    ) -> tuple[CivixResponse[AttributesT], float] | None:
        """Réponse du cache partagé et sa durée restante ; absente, périmée ou de forme ancienne
        (le modèle a changé sans changer la version du schéma) : `None`, on lit CIVIX.
        """
        found = await self._shared.get(shared_name(key))
        if found is None:
            return None
        data, remaining = found
        try:
            return response_model.model_validate(data), remaining
        except ValidationError:
            return None

    async def _write_shared(self, key: CacheKey, path: str, response: CivixResponse[Any]) -> None:
        """Copie une réponse fraîche dans le cache partagé, pour la même durée qu'en mémoire."""
        ttl = self._ttl_for(response) or self.settings.cache_ttl
        data = response.model_dump(mode="json", by_alias=True)
        await self._shared.put(shared_name(key), shared_kind(path), data, ttl)

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
