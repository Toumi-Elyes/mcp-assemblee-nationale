"""Validation des liens renvoyés par l'API : seuls des sites attendus sont repris."""

from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset(
    {
        "www.civix.fr",
        "civix.fr",
        "www.assemblee-nationale.fr",
        "data.assemblee-nationale.fr",
    }
)


def is_safe_url(url: str) -> bool:
    """Vrai pour une URL https sans identifiants, sur un site attendu."""
    try:
        parts = urlsplit(url.strip())
        port = parts.port
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.hostname in ALLOWED_HOSTS
        and parts.username is None
        and port is None
        and url.strip().isprintable()
        and not any(char.isspace() for char in url.strip())
    )


def safe_url(url: str | None, fallback: str | None = None) -> str | None:
    """Renvoie `url` si elle est sûre, sinon `fallback` (ou `None`)."""
    if url is not None and is_safe_url(url):
        return url.strip()
    return fallback
