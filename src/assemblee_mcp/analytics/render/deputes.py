"""Rendu des analyses de députés nommés."""

from collections.abc import Mapping, Sequence

from assemblee_mcp.analytics.models import (
    DeputeBilan,
    DeputeComparison,
    Method,
)
from assemblee_mcp.analytics.render.shared import (
    explained_percent,
    finish_analysis,
    percent,
    table,
)
from assemblee_mcp.formatting import (
    field_text,
)

NO_COMPARABLE_VOTE = "aucun vote exprimé comparable à la position du groupe"
NO_COMMON_SCRUTIN = "aucun scrutin où les deux ont voté"


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
        f"{result.comparable} votes comparables "
        f"({explained_percent(result.alignment_rate, NO_COMPARABLE_VOTE)})",
    ]
    return finish_analysis("\n".join(lines), method)


def render_comparison(result: DeputeComparison, method: Method) -> str:
    """Accord entre deux députés."""
    lines = [
        f"## {field_text(result.name_a)} et {field_text(result.name_b)} : votes comparés",
        "",
        f"- Scrutins de l'échantillon : {result.scrutins}",
        f"- Scrutins où les deux ont exprimé un vote : {result.shared}",
        f"- Même position sur : {result.agreed} "
        f"({explained_percent(result.rate, NO_COMMON_SCRUTIN)})",
        f"- Vote exprimé par {field_text(result.name_a)} seulement : {result.only_a}",
        f"- Vote exprimé par {field_text(result.name_b)} seulement : {result.only_b}",
    ]
    return finish_analysis("\n".join(lines), method)


def render_deputes_matrix(
    names: Sequence[str],
    comparisons: Sequence[DeputeComparison],
    expressed: Mapping[str, int],
    method: Method,
) -> str:
    """Matrice d'accord entre plusieurs députés, deux à deux."""
    lookup = {(item.name_a, item.name_b): item for item in comparisons} | {
        (item.name_b, item.name_a): item for item in comparisons
    }
    labels = [field_text(name) for name in names]
    rows = []
    for name, label in zip(names, labels, strict=True):
        cells = []
        for other in names:
            pair = lookup.get((name, other))
            cells.append("" if pair is None else f"{percent(pair.rate)} ({pair.shared})")
        rows.append([label, *cells])
    votes = "\n".join(
        f"- {label} : {expressed[name]} vote(s) exprimé(s)"
        for name, label in zip(names, labels, strict=True)
    )
    body = (
        "## Accords entre députés (même position)\n\n"
        + table(["", *labels], rows)
        + "\n\nDans chaque case : part de scrutins votés de la même façon, et entre parenthèses "
        "le nombre de scrutins où les deux ont exprimé un vote.\n\n" + votes
    )
    return finish_analysis(body, method)
