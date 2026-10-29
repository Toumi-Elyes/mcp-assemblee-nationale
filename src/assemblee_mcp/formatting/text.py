"""Texte brut : dates en français, nettoyage et raccourcissement de contenus tiers."""

import re
from datetime import date

MAX_TITLE_LENGTH = 240
MAX_FIELD_LENGTH = 300

INVISIBLE_CHARS = re.compile(
    "[\x00-\x08\x0b-\x1f\x7f\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]"
)

MONTHS = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def format_date(value: date | None) -> str:
    """Date en français, par exemple « 4 juin 2026 »."""
    if value is None:
        return "date inconnue"
    day = "1er" if value.day == 1 else str(value.day)
    return f"{day} {MONTHS[value.month - 1]} {value.year}"


def sanitize(text: str) -> str:
    """Retire les caractères de contrôle, invisibles ou bidirectionnels et neutralise `![`."""
    return INVISIBLE_CHARS.sub("", text).replace("![", "! [")


def truncate(text: str, limit: int = MAX_TITLE_LENGTH) -> str:
    """Nettoie un texte tiers sur une ligne et le raccourcit s'il est trop long."""
    clean = " ".join(sanitize(text).split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def field_text(text: str) -> str:
    """Champ tiers d'une seule ligne, plafonné à 300 caractères."""
    return truncate(text, MAX_FIELD_LENGTH)
