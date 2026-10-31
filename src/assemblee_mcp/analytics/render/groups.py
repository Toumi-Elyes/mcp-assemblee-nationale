"""Rendu des analyses de groupes : positions, accords, cohésion et résultats serrés."""

from collections.abc import Sequence

from assemblee_mcp.analytics.models import (
    CloseVote,
    GroupCohesion,
    GroupStances,
    Method,
    PairAgreement,
    Stance,
)
from assemblee_mcp.analytics.render.shared import finish_analysis, percent, table
from assemblee_mcp.formatting import (
    field_text,
    format_date,
    truncate,
)
from assemblee_mcp.links import scrutin_page_url

STANCE_SYMBOLS = {
    Stance.POUR: "P",
    Stance.CONTRE: "C",
    Stance.ABSTENTION: "A",
    Stance.PARTAGE: "~",
}


STANCE_LEGEND = (
    "P = pour, C = contre, A = abstention, ~ = position partagée, – = pas de vote exprimé"
)


def render_positions(rows: Sequence[GroupStances], groups: Sequence[str], method: Method) -> str:
    """Tableau des positions majoritaires des groupes, scrutin par scrutin."""
    header = ["Scrutin", *groups]
    body_rows = [
        [
            f"{format_date(row.scrutin.day)} n°{row.scrutin.numero} — "
            f"{truncate(row.scrutin.title, 70)} ({row.scrutin.result}) "
            f"{scrutin_page_url(row.scrutin.uid, numero=row.scrutin.numero)}",
            *[
                STANCE_SYMBOLS[stance] if (stance := row.stances.get(group)) else "–"
                for group in groups
            ],
        ]
        for row in rows
    ]
    body = "## Positions majoritaires des groupes\n\n" + table(header, body_rows)
    body += f"\n\nLégende : {STANCE_LEGEND}."
    return finish_analysis(body, method)


def render_agreements(pairs: Sequence[PairAgreement], groups: Sequence[str], method: Method) -> str:
    """Matrice d'accord entre groupes."""
    lookup = {(pair.group_a, pair.group_b): pair for pair in pairs} | {
        (pair.group_b, pair.group_a): pair for pair in pairs
    }
    rows = []
    for group in groups:
        cells = []
        for other in groups:
            pair = lookup.get((group, other))
            cells.append("" if group == other else percent(pair.rate) if pair else "–")
        rows.append([group, *cells])
    shared = [pair.shared for pair in pairs]
    span = f"{min(shared)} à {max(shared)}" if shared else "0"
    body = (
        "## Accords entre groupes (même position majoritaire)\n\n"
        + table(["", *groups], rows)
        + f"\n\nNombre de scrutins comparés par paire : {span}."
    )
    return finish_analysis(body, method)


def render_cohesion(rows: Sequence[GroupCohesion], method: Method) -> str:
    """Part des votes de chaque groupe alignés sur sa position majoritaire."""
    body = "## Votes alignés sur la position majoritaire du groupe\n\n" + table(
        ["Groupe", "Scrutins", "Votes exprimés", "Alignés", "Part alignée"],
        [
            [
                field_text(row.group),
                str(row.scrutins),
                str(row.expressed),
                str(row.aligned),
                percent(row.rate),
            ]
            for row in rows
        ],
    )
    return finish_analysis(body, method)


def no_close_vote_text(max_margin: int, scanned: int, closest: int | None) -> str:
    """Réponse sans résultat serré : ce qui a été parcouru et comment élargir."""
    closest_text = f" Le plus serré était de {closest} voix." if closest is not None else ""
    return (
        "## Résultats serrés\n\n"
        f"Aucun des {scanned} scrutin(s) parcourus n'a un écart de {max_margin} voix ou moins."
        f"{closest_text} Pour élargir : augmentez `ecart_max`, `periode_jours` (30 au plus) ou "
        "`max_scrutins`, ou choisissez `type_scrutin` « tous »."
    )


def render_close_votes(
    rows: Sequence[CloseVote], max_margin: int, method: Method, closest: int | None = None
) -> str:
    """Scrutins au résultat serré, ou ce qui a été parcouru s'il n'y en a aucun."""
    if not rows:
        body = no_close_vote_text(max_margin, method.analysed, closest)
        return finish_analysis(body, method)
    body = f"## Résultats serrés (écart de {max_margin} voix ou moins)\n\n" + table(
        ["Écart", "Pour", "Contre", "Abst.", "Date", "Scrutin", "Résultat"],
        [
            [
                str(row.margin),
                str(row.pour),
                str(row.contre),
                str(row.abstention),
                format_date(row.scrutin.day),
                f"n°{row.scrutin.numero} — {truncate(row.scrutin.title, 80)} (`{row.scrutin.uid}`) "
                f"{scrutin_page_url(row.scrutin.uid, numero=row.scrutin.numero)}",
                field_text(row.scrutin.result),
            ]
            for row in rows
        ],
    )
    return finish_analysis(body, method)
