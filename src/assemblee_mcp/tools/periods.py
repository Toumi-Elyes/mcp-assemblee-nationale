"""Dates et périodes saisies par l'utilisateur : validation et description."""

import re
from datetime import date
from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.limits import MAX_RANGE_DAYS

ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DateText = Annotated[
    str,
    Field(description="Date au format AAAA-MM-JJ.", pattern=r"^\d{4}-\d{2}-\d{2}$"),
]


def parse_day(value: str, label: str) -> date:
    """Convertit `AAAA-MM-JJ` en date ; lève `ToolError` si invalide."""
    if not ISO_DAY.match(value):
        raise ToolError(f"{label} invalide : attendu AAAA-MM-JJ (par exemple 2026-10-01).")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ToolError(f"{label} invalide : « {value} » n'est pas une date.") from error


def parse_range(start_text: str, end_text: str) -> tuple[date, date]:
    """Valide une plage de dates (ordre et durée maximale)."""
    start = parse_day(start_text, "date_debut")
    end = parse_day(end_text, "date_fin")
    if end < start:
        raise ToolError("date_fin doit être postérieure ou égale à date_debut.")
    if (end - start).days > MAX_RANGE_DAYS:
        raise ToolError(f"La période ne peut pas dépasser {MAX_RANGE_DAYS} jours.")
    return start, end


def describe_period(start: date, end: date) -> str:
    """Période en texte, jours inclus."""
    return f"du {start.isoformat()} au {end.isoformat()} ({(end - start).days + 1} jours)"
