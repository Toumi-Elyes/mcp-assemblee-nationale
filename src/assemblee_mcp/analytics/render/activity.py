"""Rendu des analyses d'activité : tendances, textes, chronologie, chiffres d'ensemble."""

from collections.abc import Sequence

from assemblee_mcp.analytics.models import (
    AssemblyStats,
    DossierTimeline,
    Method,
    Rate,
    TextActivity,
    TimelineEntry,
    Trends,
    WeekVolume,
)
from assemblee_mcp.analytics.render.shared import (
    NO_DATA,
    finish_analysis,
    percent,
    rate_rows,
    table,
    type_label,
)
from assemblee_mcp.formatting import (
    field_text,
    format_date,
    truncate,
)
from assemblee_mcp.links import assemblee_scrutin_url

TITLE_WIDTH = 90


def rates_table(label: str, rates: Sequence[Rate], *, label_as_type: bool = False) -> str:
    """Tableau des effectifs et parts d'adoption, avec `label` en première colonne."""
    header = [label, "Scrutins", "Adoptés", "Rejetés", "Part adoptée"]
    return table(header, rate_rows(rates, label_as_type=label_as_type))


def weeks_table(weeks: Sequence[WeekVolume]) -> str:
    """Tableau du volume de scrutins par semaine."""
    rows = [[format_date(week.week_start), str(week.scrutins), str(week.adopted)] for week in weeks]
    return table(["Semaine du", "Scrutins", "Adoptés"], rows)


def render_trends(result: Trends, method: Method) -> str:
    """Tendances générales des scrutins."""
    overall = result.overall
    days = [[format_date(day.day), str(day.scrutins)] for day in result.busiest_days]
    lines = [
        f"## Tendances des scrutins — du {format_date(result.start)} au {format_date(result.end)}",
        "",
        f"{result.total} scrutins, dont {overall.adopted} adoptés et {overall.rejected} rejetés "
        f"(part d'adoption : {percent(overall.rate)}).",
        "",
        "### Volume par semaine\n",
        weeks_table(result.weeks),
        "",
        "### Par type de scrutin\n",
        rates_table("Type", result.by_type, label_as_type=True),
        "",
        "### Par contexte législatif\n",
        rates_table("Contexte", result.by_context),
        "",
        "### Jours comptant le plus de scrutins\n",
        table(["Jour", "Scrutins"], days),
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
    body = "## Textes comptant le plus de scrutins\n\n" + table(
        header, [text_row(row) for row in rows]
    )
    body += "\n\nPour la chronologie d'un texte, utilisez `dossier_legislatif`."
    return finish_analysis(body, method)


def entry_line(entry: TimelineEntry) -> str:
    """Ligne de chronologie."""
    number = f"n°{entry.numero} · " if entry.numero is not None else ""
    link = assemblee_scrutin_url(entry.legislature, entry.numero)
    page = f" · {link}" if link else ""
    return (
        f"- {format_date(entry.day)} · {number}{type_label(entry.kind)} · {entry.result} — "
        f"{truncate(entry.title, 200)} (`{entry.uid}`){page}"
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
            f"- {truncate(row.libelle, 120)} (`{row.dossier_ref}`) : {row.scrutins} scrutins"
            for row in result.other_dossiers
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
                    field_text(groupe.abbr),
                    field_text(groupe.libelle),
                    NO_DATA if groupe.effectif is None else str(groupe.effectif),
                ]
                for groupe in result.groups
            ],
        ),
    ]
    return finish_analysis("\n".join(lines), method)
