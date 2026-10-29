"""Rendu des analyses de députés nommés."""

from assemblee_mcp.analytics.models import (
    DeputeBilan,
    DeputeComparison,
    Method,
)
from assemblee_mcp.analytics.render.shared import finish_analysis, percent, table
from assemblee_mcp.formatting import (
    field_text,
)


def render_bilan(result: DeputeBilan, method: Method) -> str:
    """Positions d'un député sur un échantillon de scrutins."""
    group = f" ({result.group})" if result.group else ""
    lines = [
        f"## Votes de {field_text(result.name)}{group} sur l'échantillon",
        "",
        table(
            ["Pour", "Contre", "Abstention", "Non-votant", "Absent de la liste des votes"],
            [
                [
                    str(result.pour),
                    str(result.contre),
                    str(result.abstention),
                    str(result.non_votant),
                    str(result.absent),
                ]
            ],
        ),
        "",
        f"- Votes exprimés par délégation : {result.by_delegation}",
        f"- Alignement sur la position majoritaire du groupe : {result.aligned} sur "
        f"{result.comparable} votes comparables ({percent(result.alignment_rate)})",
    ]
    return finish_analysis("\n".join(lines), method)


def render_comparison(result: DeputeComparison, method: Method) -> str:
    """Accord entre deux députés."""
    lines = [
        f"## {field_text(result.name_a)} et {field_text(result.name_b)} : votes comparés",
        "",
        f"- Scrutins de l'échantillon : {result.scrutins}",
        f"- Scrutins où les deux ont exprimé un vote : {result.shared}",
        f"- Même position sur : {result.agreed} ({percent(result.rate)})",
        f"- Vote exprimé par {field_text(result.name_a)} seulement : {result.only_a}",
        f"- Vote exprimé par {field_text(result.name_b)} seulement : {result.only_b}",
    ]
    return finish_analysis("\n".join(lines), method)
