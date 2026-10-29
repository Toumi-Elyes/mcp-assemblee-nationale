"""Briques communes aux calculs : jours, libellés, échantillonnage régulier."""

from collections.abc import Sequence
from datetime import date

from assemblee_mcp.analytics.models import (
    ScrutinRef,
)
from assemblee_mcp.civix.models import (
    ScrutinDetail,
    ScrutinSummary,
)

UNKNOWN_LABEL = "non précisé"


def day_of(scrutin: ScrutinSummary | ScrutinDetail) -> date | None:
    """Jour du scrutin."""
    return scrutin.date_scrutin.date() if scrutin.date_scrutin else None


def ordinal(day: date | None) -> int:
    """Numéro de jour d'une date (0 si absente), pour trier."""
    return day.toordinal() if day else 0


def evenly_spaced[Item](items: Sequence[Item], count: int) -> list[Item]:
    """`count` éléments régulièrement répartis (ordre conservé) ; tous si `count` suffit."""
    if count >= len(items):
        return list(items)
    if count <= 0:
        return []
    step = len(items) / count
    return [items[int(index * step)] for index in range(count)]


def scrutin_ref(scrutin: ScrutinDetail) -> ScrutinRef:
    """Référence courte d'un scrutin détaillé."""
    return ScrutinRef(
        uid=scrutin.uid,
        numero=scrutin.numero,
        day=day_of(scrutin),
        title=scrutin.titre,
        result=(scrutin.result_label or UNKNOWN_LABEL),
    )


def result_text(scrutin: ScrutinSummary) -> str:
    """Résultat en un mot : adopté, rejeté ou non précisé."""
    adopted = scrutin.adopted
    if adopted is None:
        return UNKNOWN_LABEL
    return "adopté" if adopted else "rejeté"
