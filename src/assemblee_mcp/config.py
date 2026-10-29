"""Configuration du serveur, lue depuis les variables d'environnement."""

import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://www.civix.fr/api/v1"
DEFAULT_TIMEOUT_SECONDS = 10.0
CONNECT_TIMEOUT_SECONDS = 5.0
POOL_TIMEOUT_SECONDS = 5.0
DEFAULT_CACHE_TTL_SECONDS = 600.0
DEFAULT_CACHE_MAX_ENTRIES = 500
DEFAULT_VOTES_CACHE_MAX_ENTRIES = 150
DEFAULT_DETAIL_CACHE_MAX_ENTRIES = 400
IMMUTABLE_TTL_SECONDS = 86400.0
IMMUTABLE_AFTER_DAYS = 2
MAX_CONCURRENT_REQUESTS = 4
MAX_CONNECTIONS = 8
MAX_KEEPALIVE_CONNECTIONS = 4
DEFAULT_RETRY_DELAY_SECONDS = 0.3
DEFAULT_USER_AGENT = (
    "mcp-assemblee-nationale (+https://github.com/Toumi-Elyes/mcp-assemblee-nationale)"
)


@dataclass(frozen=True)
class Settings:
    """Paramètres du client CIVIX et du serveur."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    cache_ttl: float = DEFAULT_CACHE_TTL_SECONDS
    cache_max_entries: int = DEFAULT_CACHE_MAX_ENTRIES
    votes_cache_max_entries: int = DEFAULT_VOTES_CACHE_MAX_ENTRIES
    detail_cache_max_entries: int = DEFAULT_DETAIL_CACHE_MAX_ENTRIES
    immutable_ttl: float = IMMUTABLE_TTL_SECONDS
    retry_delay: float = DEFAULT_RETRY_DELAY_SECONDS
    user_agent: str = DEFAULT_USER_AGENT

    @classmethod
    def from_env(cls) -> Settings:
        """Construit les paramètres à partir des variables `CIVIX_*`."""
        return cls(
            base_url=os.environ.get("CIVIX_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            timeout=float(os.environ.get("CIVIX_TIMEOUT", DEFAULT_TIMEOUT_SECONDS)),
            cache_ttl=float(os.environ.get("CIVIX_CACHE_TTL", DEFAULT_CACHE_TTL_SECONDS)),
            cache_max_entries=int(
                os.environ.get("CIVIX_CACHE_MAX_ENTRIES", DEFAULT_CACHE_MAX_ENTRIES)
            ),
            user_agent=os.environ.get("CIVIX_USER_AGENT", DEFAULT_USER_AGENT),
        )
