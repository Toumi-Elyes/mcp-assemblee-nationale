"""Mise en forme markdown des analyses : chiffres, méthode, sources et pied de page."""

from collections.abc import Sequence

from assemblee_mcp.analytics.models import (
    AssemblyStats,
    CloseVote,
    DeputeBilan,
    DeputeComparison,
    DossierTimeline,
    GroupCohesion,
    GroupStances,
    Method,
    PairAgreement,
    Rate,
    Stance,
    TextActivity,
    TimelineEntry,
    Trends,
)
from assemblee_mcp.formatting import (
    field_text,
    finish,
    format_date,
    source_line,
    truncate,
)

SOURCE_CIVIX = "https://www.civix.fr/api/v1/scrutins"
SOURCE_ASSEMBLEE = "https://www.assemblee-nationale.fr/dyn/17/scrutins"
NO_DATA = "n/d"
TITLE_WIDTH = 90
TYPE_LABELS = {
    "amendement": "amendements",
    "article": "articles",
    "texte": "votes sur l'ensemble d'un texte",
    "scrutin": "autres scrutins (motions…)",
    "motion_censure": "motions de censure",
}
STANCE_SYMBOLS = {
    Stance.POUR: "P",
    Stance.CONTRE: "C",
    Stance.ABSTENTION: "A",
    Stance.PARTAGE: "~",
}
STANCE_LEGEND = (
    "P = pour, C = contre, A = abstention, ~ = position partagée, – = pas de vote exprimé"
)


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


def finish_analysis(body: str, method: Method) -> str:
    """Corps, méthode, ligne « Source : » et pied de page CIVIX."""
    source = source_line(SOURCE_CIVIX, SOURCE_ASSEMBLEE)
    return finish(f"{body}\n\n{method_block(method)}", source)


def render_trends(result: Trends, method: Method) -> str:
    """Tendances générales des scrutins."""
    overall = result.overall
    lines = [
        f"## Tendances des scrutins — du {format_date(result.start)} au {format_date(result.end)}",
        "",
        f"{result.total} scrutins, dont {overall.adopted} adoptés et {overall.rejected} rejetés "
        f"(part d'adoption : {percent(overall.rate)}).",
        "",
        "### Volume par semaine",
        "",
        table(
            ["Semaine du", "Scrutins", "Adoptés"],
            [[format_date(w.week_start), str(w.scrutins), str(w.adopted)] for w in result.weeks],
        ),
        "",
        "### Par type de scrutin",
        "",
        table(
            ["Type", "Scrutins", "Adoptés", "Rejetés", "Part adoptée"],
            rate_rows(result.by_type, label_as_type=True),
        ),
        "",
        "### Par contexte législatif",
        "",
        table(
            ["Contexte", "Scrutins", "Adoptés", "Rejetés", "Part adoptée"],
            rate_rows(result.by_context),
        ),
        "",
        "### Jours comptant le plus de scrutins",
        "",
        table(
            ["Jour", "Scrutins"],
            [[format_date(d.day), str(d.scrutins)] for d in result.busiest_days],
        ),
    ]
    return finish_analysis("\n".join(lines), method)


def text_row(row: TextActivity) -> list[str]:
    """Ligne de tableau d'un dossier législatif."""
    name = truncate(row.libelle, TITLE_WIDTH)
    reference = f" (`{row.dossier_ref}`)" if row.dossier_ref else ""
    return [
        name + reference,
        str(row.scrutins),
        f"{row.amendements} / {row.articles} / {row.ensemble}",
        str(row.adopted),
        str(row.rejected),
        format_date(row.last_date),
    ]


def render_top_texts(rows: Sequence[TextActivity], method: Method) -> str:
    """Dossiers législatifs classés par nombre de scrutins."""
    header = [
        "Dossier",
        "Scrutins",
        "Amend. / art. / ensemble",
        "Adoptés",
        "Rejetés",
        "Dernier vote",
    ]
    body = "## Textes comptant le plus de scrutins\n\n" + table(header, [text_row(r) for r in rows])
    body += "\n\nPour la chronologie d'un texte, utilisez `dossier_legislatif`."
    return finish_analysis(body, method)


def entry_line(entry: TimelineEntry) -> str:
    """Ligne de chronologie."""
    number = f"n°{entry.numero} · " if entry.numero is not None else ""
    return (
        f"- {format_date(entry.day)} · {number}{type_label(entry.kind)} · {entry.result} — "
        f"{truncate(entry.title, 200)} (`{entry.uid}`)"
    )


def render_timeline(result: DossierTimeline, method: Method) -> str:
    """Chronologie des scrutins d'un dossier."""
    amendments = result.amendements
    reference = f" (`{result.dossier_ref}`)" if result.dossier_ref else ""
    lines = [
        f"## Dossier : {truncate(result.libelle, 200)}{reference}",
        "",
        f"{result.total} scrutins, dont {amendments.total} sur des amendements "
        f"({amendments.adopted} adoptés, {amendments.rejected} rejetés).",
    ]
    if result.final_votes:
        lines += ["", "### Votes sur l'ensemble du texte", ""]
        lines += [entry_line(entry) for entry in result.final_votes]
    lines += ["", "### Chronologie (hors amendements)", ""]
    lines += [entry_line(entry) for entry in result.entries] or ["Aucun scrutin hors amendements."]
    if result.other_dossiers:
        lines += ["", "### Autres dossiers correspondant à la recherche", ""]
        lines += [
            f"- {truncate(r.libelle, 120)} (`{r.dossier_ref}`) : {r.scrutins} scrutins"
            for r in result.other_dossiers
        ]
    return finish_analysis("\n".join(lines), method)


def render_assembly(result: AssemblyStats, method: Method) -> str:
    """Chiffres d'ensemble de la législature."""
    legislature = f" — {result.legislature}e législature" if result.legislature else ""
    total = NO_DATA if result.total_scrutins is None else str(result.total_scrutins)
    lines = [
        f"## Statistiques de l'Assemblée nationale{legislature}",
        "",
        f"- Scrutins publics depuis le début de la législature : {total}",
        f"- Députés recensés : {NO_DATA if result.deputies is None else result.deputies}",
        f"- Part de scrutins adoptés (échantillon de {result.sample_size}) : "
        f"{percent(result.overall.rate)}",
        "",
        "### Par type de scrutin (échantillon)",
        "",
        table(
            ["Type", "Scrutins", "Adoptés", "Rejetés", "Part adoptée"],
            rate_rows(result.by_type, label_as_type=True),
        ),
        "",
        "### Groupes parlementaires",
        "",
        table(
            ["Sigle", "Groupe", "Députés"],
            [
                [
                    field_text(g.abbr),
                    field_text(g.libelle),
                    NO_DATA if g.effectif is None else str(g.effectif),
                ]
                for g in result.groups
            ],
        ),
    ]
    return finish_analysis("\n".join(lines), method)


def render_positions(rows: Sequence[GroupStances], groups: Sequence[str], method: Method) -> str:
    """Tableau des positions majoritaires des groupes, scrutin par scrutin."""
    header = ["Scrutin", *groups]
    body_rows = [
        [
            f"{format_date(row.scrutin.day)} n°{row.scrutin.numero} — "
            f"{truncate(row.scrutin.title, 70)} ({row.scrutin.result})",
            *[STANCE_SYMBOLS[s] if (s := row.stances.get(g)) else "–" for g in groups],
        ]
        for row in rows
    ]
    body = "## Positions majoritaires des groupes\n\n" + table(header, body_rows)
    body += f"\n\nLégende : {STANCE_LEGEND}."
    return finish_analysis(body, method)


def render_agreements(pairs: Sequence[PairAgreement], groups: Sequence[str], method: Method) -> str:
    """Matrice d'accord entre groupes."""
    lookup = {(p.group_a, p.group_b): p for p in pairs} | {(p.group_b, p.group_a): p for p in pairs}
    rows = []
    for group in groups:
        cells = []
        for other in groups:
            pair = lookup.get((group, other))
            cells.append("" if group == other else percent(pair.rate) if pair else "–")
        rows.append([group, *cells])
    shared = [p.shared for p in pairs]
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
                field_text(r.group),
                str(r.scrutins),
                str(r.expressed),
                str(r.aligned),
                percent(r.rate),
            ]
            for r in rows
        ],
    )
    return finish_analysis(body, method)


def render_close_votes(rows: Sequence[CloseVote], max_margin: int, method: Method) -> str:
    """Scrutins au résultat serré."""
    if not rows:
        body = (
            "## Résultats serrés\n\n"
            f"Aucun scrutin de l'échantillon n'a un écart de {max_margin} voix ou moins."
        )
        return finish_analysis(body, method)
    body = f"## Résultats serrés (écart de {max_margin} voix ou moins)\n\n" + table(
        ["Écart", "Pour", "Contre", "Abst.", "Date", "Scrutin", "Résultat"],
        [
            [
                str(r.margin),
                str(r.pour),
                str(r.contre),
                str(r.abstention),
                format_date(r.scrutin.day),
                f"n°{r.scrutin.numero} — {truncate(r.scrutin.title, 80)} (`{r.scrutin.uid}`)",
                field_text(r.scrutin.result),
            ]
            for r in rows
        ],
    )
    return finish_analysis(body, method)


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
