"""Cache mémoire à durée de vie limitée, utilisé par le client CIVIX."""

from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from assemblee_mcp.civix.models import CivixResponse

# Une requête = chemin + paramètres triés : deux appels identiques partagent la même clé.
type CacheKey = tuple[str, tuple[tuple[str, str], ...]]


class TtlCache:
    """Cache LRU à durée de vie limitée et taille plafonnée.

    Il garde des réponses de types différents : `Any` est le paramètre de l'enveloppe générique.
    """

    def __init__(self, max_entries: int, ttl: float, clock: Callable[[], float]) -> None:
        """Crée un cache de `max_entries` valeurs gardées `ttl` secondes (`clock` en secondes)."""
        self._max_entries = max_entries
        self._ttl = ttl
        self._clock = clock
        self._entries: OrderedDict[CacheKey, tuple[float, CivixResponse[Any]]] = OrderedDict()

    def get(self, key: CacheKey) -> CivixResponse[Any] | None:
        """Valeur en cache non expirée, sinon `None`."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at <= self._clock():
            del self._entries[key]
            return None
        self._entries.move_to_end(key)
        return value

    def set(self, key: CacheKey, value: CivixResponse[Any], ttl: float | None = None) -> None:
        """Mémorise une valeur en évinçant les plus anciennes au-delà du plafond."""
        self._entries[key] = (self._clock() + (self._ttl if ttl is None else ttl), value)
        self._entries.move_to_end(key)
        while len(self._entries) > self._max_entries:
            self._entries.popitem(last=False)
