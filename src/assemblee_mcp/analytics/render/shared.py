"""Briques communes du rendu : tableaux, pourcentages, bloc « Méthode », sources."""

from collections.abc import Sequence

from assemblee_mcp.analytics.models import (
    Method,
    Rate,
)
from assemblee_mcp.formatting import (
    field_text,
    finish,
    source_line,
)
from assemblee_mcp.limits import CURRENT_LEGISLATURE

SOURCE_CIVIX = "https://www.civix.fr/api/v1/scrutins"


SOURCE_ASSEMBLEE = "https://www.assemblee-nationale.fr/dyn/{legislature}/scrutins"


NO_DATA = "n/d"


TYPE_LABELS = {
    "amendement": "amendements",
    "article": "articles",
    "texte": "votes sur l'ensemble d'un texte",
    "autre": "autres scrutins (motions, résolutions, suspensions de séance…)",
}


def percent(rate: float | None) -> str:
    """Pourcentage à la française, ou `n/d`."""
    return NO_DATA if rate is None else f"{round(rate * 100)} %"


def table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Tableau markdown."""
    head = "| " + " | ".join(header) + " |\n|" + "---|" * len(header)
    body = "\n".join("| " + " | ".join(cell for cell in row) + " |" for row in rows)
    return f"{head}\n{body}" if rows else head


def type_label(kind: str) -> str:
    """Libellé français d'un type de scrutin."""
    return TYPE_LABELS.get(kind, field_text(kind.replace("_", " ")))


def rate_rows(rates: Sequence[Rate], *, label_as_type: bool = False) -> list[list[str]]:
    """Lignes de tableau des effectifs et parts d'adoption."""
    return [
        [
            type_label(rate.label) if label_as_type else field_text(rate.label),
            str(rate.total),
            str(rate.adopted),
            str(rate.rejected),
            percent(rate.rate),
        ]
        for rate in rates
    ]


def method_block(method: Method) -> str:
    """Bloc « Méthode » : période, taille d'échantillon, définitions et limites."""
    sample = f"{method.analysed} scrutin(s) analysé(s)"
    if method.matching is not None:
        sample += f" sur {method.matching} correspondant(s)"
    lines = ["### Méthode", ""]
    if method.period:
        lines.append(f"- Période : {method.period}")
    lines.append(f"- Échantillon : {sample}")
    if method.truncated:
        lines.append("- Échantillon tronqué : les résultats ne portent pas sur tous les scrutins.")
    lines.append(f"- Ce qui est compté : {method.counted}")
    lines += [f"- Limite : {limit}" for limit in method.limits]
    lines += [f"- {note}" for note in method.notes]
    return "\n".join(lines)


def warning_block(method: Method) -> str:
    """Avertissements (échantillon trop mince…) en tête de réponse, ou texte vide."""
    if not method.warnings:
        return ""
    return "\n".join(f"> **Attention** : {warning}" for warning in method.warnings) + "\n\n"


def finish_analysis(body: str, method: Method) -> str:
    """Avertissements, corps, méthode, ligne « Source : » et pied de page CIVIX."""
    assemblee = SOURCE_ASSEMBLEE.format(legislature=method.legislature or CURRENT_LEGISLATURE)
    source = source_line(SOURCE_CIVIX, assemblee)
    return finish(f"{warning_block(method)}{body}\n\n{method_block(method)}", source)


def explained_percent(rate: float | None, reason: str) -> str:
    """Pourcentage, ou la raison pour laquelle il ne peut pas être calculé."""
    return f"non calculable : {reason}" if rate is None else percent(rate)
