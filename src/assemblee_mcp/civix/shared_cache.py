"""Cache partagé entre instances Vercel, au-dessus du cache mémoire de chaque instance.

Une instance froide refait normalement tous les appels à CIVIX. Le Runtime Cache de Vercel
(persistant entre instances et déploiements) sert de second niveau : le cache mémoire reste le
premier niveau, ce cache n'est lu qu'en cas d'absence, et alimenté à chaque lecture de CIVIX.
Hors de Vercel (poste local, tests), il est inactif et ne coûte rien. Une panne ou une lenteur
du cache partagé ne fait jamais échouer une demande : on lit CIVIX comme s'il n'existait pas.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import Callable, Coroutine, Mapping, Sequence
from typing import Any, Protocol

from assemblee_mcp.limits import (
    SHARED_CACHE_COOLDOWN_SECONDS,
    SHARED_CACHE_MAX_BYTES,
    SHARED_CACHE_MAX_CONCURRENT,
    SHARED_CACHE_SCHEMA_VERSION,
    SHARED_CACHE_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

NAMESPACE = "civix"
ROOT_TAG = "civix"
ENDPOINT_VARIABLE = "RUNTIME_CACHE_ENDPOINT"
HEADERS_VARIABLE = "RUNTIME_CACHE_HEADERS"
DISABLE_VARIABLE = "CIVIX_SHARED_CACHE"
DISABLED_VALUES = frozenset({"0", "off", "false", "non"})
TELEMETRY_VARIABLE = "VERCEL_TELEMETRY_DISABLED"


class SharedBackend(Protocol):
    """Stockage clé-valeur partagé : c'est tout ce que le cache partagé demande au Runtime Cache."""

    async def get(self, key: str) -> object | None:
        """Valeur JSON enregistrée sous `key`, ou `None`."""
        ...

    async def set(self, key: str, value: object, ttl: int, tags: Sequence[str]) -> None:
        """Enregistre `value` (JSON) `ttl` secondes, sous les étiquettes `tags`."""
        ...


def hash_key(key: str) -> str:
    """Empreinte SHA-256 d'une clé (le hachage 32 bits par défaut du SDK produit des collisions)."""
    return hashlib.sha256(key.encode()).hexdigest()


class RuntimeCacheBackend:
    """Adaptateur du Runtime Cache de Vercel (SDK officiel `vercel-cache`)."""

    def __init__(self) -> None:
        """Ouvre le client du SDK ; sa télémétrie vers Vercel est coupée sauf demande contraire."""
        os.environ.setdefault(TELEMETRY_VARIABLE, "1")
        from vercel.cache import AsyncRuntimeCache  # noqa: PLC0415

        self._cache = AsyncRuntimeCache(key_hash_function=hash_key, namespace=NAMESPACE)

    async def get(self, key: str) -> object | None:
        """Valeur du Runtime Cache, `None` si absente ou périmée."""
        value: object | None = await self._cache.get(key)
        return value

    async def set(self, key: str, value: object, ttl: int, tags: Sequence[str]) -> None:
        """Écrit dans le Runtime Cache avec durée de vie et étiquettes."""
        await self._cache.set(key, value, {"ttl": ttl, "tags": list(tags)})


def running_on_vercel(environ: Mapping[str, str]) -> bool:
    """Vrai si le Runtime Cache est joignable : le SDK exige ces deux variables."""
    if environ.get(DISABLE_VARIABLE, "").lower() in DISABLED_VALUES:
        return False
    return bool(environ.get(ENDPOINT_VARIABLE)) and bool(environ.get(HEADERS_VARIABLE))


class SharedCache:
    """Second niveau de cache : sérialise, versionne, étiquette et tolère toutes les pannes."""

    def __init__(
        self,
        backend: SharedBackend | None = None,
        *,
        wall_clock: Callable[[], float] = time.time,
        clock: Callable[[], float] = time.monotonic,
        timeout: float = SHARED_CACHE_TIMEOUT_SECONDS,
        cooldown: float = SHARED_CACHE_COOLDOWN_SECONDS,
        max_bytes: int = SHARED_CACHE_MAX_BYTES,
    ) -> None:
        """Crée le cache ; sans `backend` il est inactif. Les horloges sont injectables."""
        self._backend = backend
        self._wall_clock = wall_clock
        self._clock = clock
        self._timeout = timeout
        self._cooldown = cooldown
        self._max_bytes = max_bytes
        self._paused_until = 0.0
        self._slots = asyncio.Semaphore(SHARED_CACHE_MAX_CONCURRENT)

    @classmethod
    def from_environment(cls) -> SharedCache:
        """Cache branché sur le Runtime Cache sur Vercel, inactif ailleurs."""
        if not running_on_vercel(os.environ):
            return cls()
        return cls(RuntimeCacheBackend())

    @property
    def enabled(self) -> bool:
        """Vrai si un stockage partagé est branché."""
        return self._backend is not None

    async def get(self, name: str) -> tuple[Any, float] | None:
        """Données JSON enregistrées sous `name` et leur durée de vie restante, ou `None`."""
        backend = self._backend
        if backend is None:
            return None
        key = self._key(name)
        envelope = await self._guarded(backend.get(key))
        if not isinstance(envelope, dict) or envelope.get("key") != key or "data" not in envelope:
            return None
        expires_at = envelope.get("expires_at")
        if not isinstance(expires_at, int | float):
            return None
        remaining = expires_at - self._wall_clock()
        if remaining <= 0:
            return None
        return envelope["data"], remaining

    async def put(self, name: str, kind: str, data: Any, ttl: float) -> None:
        """Enregistre `data` (JSON) `ttl` secondes sous l'étiquette `kind` ; ignoré si trop gros."""
        backend = self._backend
        if backend is None or ttl < 1:
            return
        key = self._key(name)
        envelope = {"key": key, "expires_at": self._wall_clock() + ttl, "data": data}
        size = len(json.dumps(envelope).encode())
        if size > self._max_bytes:
            logger.info("cache partagé : %s ignoré (%d octets, trop gros)", name, size)
            return
        tags = (ROOT_TAG, f"{ROOT_TAG}:{kind}")
        await self._guarded(backend.set(key, envelope, int(ttl), tags))

    def _key(self, name: str) -> str:
        return f"v{SHARED_CACHE_SCHEMA_VERSION}:{name}"

    async def _guarded(self, operation: Coroutine[Any, Any, Any]) -> Any:
        """Exécute l'accès avec délai, concurrence bornée et pause après échec ; `None` si KO."""
        if self._clock() < self._paused_until:
            operation.close()
            return None
        try:
            async with self._slots:
                return await asyncio.wait_for(operation, self._timeout)
        except Exception:
            logger.warning("cache partagé indisponible, lecture directe de CIVIX", exc_info=True)
            self._paused_until = self._clock() + self._cooldown
            return None
