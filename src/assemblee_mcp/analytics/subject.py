"""Suivi d'un sujet d'une législature à l'autre, de la 14e (2012) à la 17e.

Pour chaque législature, les scrutins dont le titre correspond au sujet : recherche CIVIX pour
les 16e et 17e, archive de l'Assemblée embarquée pour les 14e et 15e (aucun appel réseau). On
compte les scrutins lus, leur résultat et leur nature, et on cite les derniers votes sur
l'ensemble d'un texte. Rien n'est classé : c'est un relevé, pas une mesure d'importance.
"""

import asyncio
from collections import Counter
from dataclasses import dataclass
from datetime import date

from assemblee_mcp.analytics.models import Method
from assemblee_mcp.analytics.render.shared import (
    SOURCE_CIVIX,
    method_block,
    table,
    type_label,
    warning_block,
)
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import ScrutinSummary
from assemblee_mcp.civix.models.kinds import KIND_ENSEMBLE
from assemblee_mcp.civix.scrutin_archive import ARCHIVE_SOURCE
from assemblee_mcp.civix.search import ScrutinPool, search_scrutin_pool
from assemblee_mcp.formatting import field_text, finish, format_date, source_line, truncate

FOLLOWED_LEGISLATURES = (17, 16, 15, 14)
"""Législatures suivies, de la plus récente à la plus ancienne."""
LEGISLATURE_YEARS = {14: "2012 à 2017", 15: "2017 à 2022", 16: "2022 à 2024", 17: "depuis 2024"}
MAX_HIGHLIGHTS = 3


@dataclass(frozen=True)
class LegislatureSubject:
    """Scrutins d'une législature correspondant au sujet."""

    legislature: int
    matching: int
    items: list[ScrutinSummary]
    truncated: bool
    note: str | None

    @property
    def adopted(self) -> int:
        """Scrutins lus adoptés."""
        return sum(1 for item in self.items if item.adopted is True)

    @property
    def rejected(self) -> int:
        """Scrutins lus rejetés."""
        return sum(1 for item in self.items if item.adopted is False)

    @property
    def kinds(self) -> Counter[str]:
        """Nombre de scrutins lus par nature (amendement, article, texte, autre)."""
        return Counter(item.kind for item in self.items)

    @property
    def days(self) -> list[date]:
        """Jours des scrutins lus."""
        return [item.date_scrutin.date() for item in self.items if item.date_scrutin]

    def highlights(self) -> list[ScrutinSummary]:
        """Derniers votes sur l'ensemble d'un texte, sinon derniers scrutins."""
        whole = [item for item in self.items if item.kind == KIND_ENSEMBLE]
        return (whole or self.items)[:MAX_HIGHLIGHTS]


async def follow_subject(client: CivixClient, subject: str) -> list[LegislatureSubject]:
    """Scrutins du sujet dans chaque législature suivie (16e et 17e lues en parallèle)."""
    pools = await asyncio.gather(
        *(
            search_scrutin_pool(client, subject, legislature=number)
            for number in FOLLOWED_LEGISLATURES
        )
    )
    return [
        legislature_subject(number, pool)
        for number, pool in zip(FOLLOWED_LEGISLATURES, pools, strict=True)
    ]


def legislature_subject(legislature: int, pool: ScrutinPool) -> LegislatureSubject:
    """Relevé d'une législature à partir des scrutins trouvés."""
    return LegislatureSubject(legislature, pool.matching, pool.items, pool.truncated, pool.note)


def period_cell(row: LegislatureSubject) -> str:
    """Premier et dernier jour des scrutins lus, ou un tiret."""
    days = row.days
    if not days:
        return "—"
    first, last = min(days), max(days)
    return format_date(first) if first == last else f"{format_date(first)} → {format_date(last)}"


def overview_table(rows: list[LegislatureSubject]) -> str:
    """Tableau d'ensemble, une ligne par législature."""
    header = [
        "Législature",
        "Scrutins trouvés",
        "Lus",
        "Votes sur l'ensemble",
        "Adoptés",
        "Rejetés",
        "Premier → dernier vote lu",
    ]
    body = [
        [
            f"{row.legislature}e ({LEGISLATURE_YEARS[row.legislature]})",
            str(row.matching),
            str(len(row.items)),
            str(row.kinds[KIND_ENSEMBLE]),
            str(row.adopted),
            str(row.rejected),
            period_cell(row),
        ]
        for row in rows
    ]
    return table(header, body)


def highlight_line(item: ScrutinSummary) -> str:
    """Ligne d'un scrutin cité : date, résultat, titre et identifiant."""
    result = "adopté" if item.adopted else "rejeté" if item.adopted is False else "résultat inconnu"
    when = format_date(item.date_scrutin.date() if item.date_scrutin else None)
    return f"- {when} · {result} · {truncate(item.titre, 200)} (`{item.uid}`)"


def legislature_section(row: LegislatureSubject) -> str:
    """Détail d'une législature : nature des scrutins et derniers votes cités."""
    title = f"### {row.legislature}e législature ({LEGISLATURE_YEARS[row.legislature]})"
    if not row.items:
        return f"{title}\n\nAucun scrutin trouvé."
    kinds = ", ".join(f"{count} {type_label(kind)}" for kind, count in row.kinds.most_common())
    whole = row.kinds[KIND_ENSEMBLE]
    cited = "Derniers votes sur l'ensemble d'un texte" if whole else "Derniers scrutins"
    lines = [title, "", f"Scrutins lus : {kinds}.", "", f"{cited} :"]
    lines += [highlight_line(item) for item in row.highlights()]
    if row.note:
        lines += ["", f"_{field_text(row.note)}_"]
    return "\n".join(lines)


def subject_method(rows: list[LegislatureSubject]) -> Method:
    """Méthode du suivi d'un sujet."""
    truncated = [f"{row.legislature}e" for row in rows if row.truncated]
    notes = [f"Lecture limitée aux scrutins les plus récents pour : {', '.join(truncated)}."]
    return Method(
        period="de la 14e législature (juillet 2012) à aujourd'hui",
        analysed=sum(len(row.items) for row in rows),
        matching=sum(row.matching for row in rows),
        truncated=bool(truncated),
        counted=(
            "scrutins dont le titre contient le sujet (expression exacte, sinon tous ses mots "
            "utiles) : recherche CIVIX pour les 16e et 17e législatures, archive des scrutins "
            "de l'Assemblée pour les 14e et 15e ; nature et résultat comptés sur les scrutins lus."
        ),
        limits=[
            "un texte peut traiter du sujet sans le nommer dans le titre de ses scrutins ;",
            "un texte donne souvent beaucoup de scrutins d'amendements : un nombre plus élevé "
            "d'une législature à l'autre ne mesure ni l'importance du sujet ni l'activité des "
            "députés ;",
            "les législatures n'ont pas la même durée (la 16e a duré deux ans).",
        ],
        notes=notes if truncated else [],
    )


def render_subject(subject: str, rows: list[LegislatureSubject]) -> str:
    """Réponse du suivi d'un sujet : tableau d'ensemble, détail par législature, méthode."""
    method = subject_method(rows)
    heading = f"## Suivi de « {field_text(subject)} » d'une législature à l'autre"
    if not any(row.items for row in rows):
        body = (
            f"{heading}\n\nAucun scrutin trouvé de 2012 à aujourd'hui. Essayez d'autres mots-clés, "
            "au singulier, avec les accents français."
        )
        return finish(body, source_line(SOURCE_CIVIX, ARCHIVE_SOURCE))
    sections = "\n\n".join(legislature_section(row) for row in rows)
    follow = "Pour le détail ou les votes d'un scrutin, utilisez son identifiant (`uid`)."
    body = f"{heading}\n\n{overview_table(rows)}\n\n{sections}\n\n{follow}"
    text = f"{warning_block(method)}{body}\n\n{method_block(method)}"
    return finish(text, source_line(SOURCE_CIVIX, ARCHIVE_SOURCE))
