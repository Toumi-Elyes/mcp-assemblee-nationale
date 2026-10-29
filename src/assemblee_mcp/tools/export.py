"""Exports machine-lisibles de scrutins et de votes (CSV ou JSON)."""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.analytics import exporting, gather
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import ScrutinSummary
from assemblee_mcp.civix.search import search_scrutin_pool
from assemblee_mcp.formatting import FOOTER, source_line
from assemblee_mcp.links import civix_scrutin_url
from assemblee_mcp.tools.analyses import DateText, parse_range
from assemblee_mcp.tools.common import (
    ANALYTICS_DEADLINE_SECONDS,
    LISTING_MAX_CALLS,
    READ_ONLY_ANNOTATIONS,
    ScrutinUid,
    limited,
)

ExportFormat = Annotated[
    Literal["csv", "json"], Field(description="Format de sortie : `csv` (avec en-tête) ou `json`.")
]
MAX_SUBJECT_ROWS = 100
SOURCE_ASSEMBLEE = "https://www.assemblee-nationale.fr/dyn/17/scrutins"
SOURCE_CIVIX = "https://www.civix.fr/api/v1/scrutins"
FENCES = {"csv": "csv", "json": "json"}


def wrap(fmt: str, data: str, count: int, notes: list[str], source: str) -> str:
    """Données dans un bloc de code, avec nombre de lignes, notes, source et pied de page."""
    header = f"Export {fmt.upper()} : {count} ligne(s)."
    extras = "".join(f"\n{note}" for note in notes)
    block = f"```{FENCES[fmt]}\n{data}\n```"
    return f"{header}{extras}\n\n{block}\n\n{source}\n{FOOTER}"


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'export."""

    @limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    async def exporter_scrutins(
        date_debut: Annotated[
            DateText | None,
            Field(description="Début de période AAAA-MM-JJ (avec `date_fin`, 90 jours au plus)."),
        ] = None,
        date_fin: Annotated[
            DateText | None, Field(description="Fin de période AAAA-MM-JJ.")
        ] = None,
        sujet: Annotated[
            str | None,
            Field(
                description="Mots-clés, à la place des dates (100 scrutins au plus).",
                max_length=200,
            ),
        ] = None,
        format: ExportFormat = "csv",
        max_lignes: Annotated[
            int, Field(description="Nombre maximal de lignes exportées.", ge=1, le=1000)
        ] = 500,
    ) -> str:
        """Exporte une liste de scrutins en CSV ou JSON, pour analyser les données soi-même.

        À utiliser quand on veut des données brutes (tableur, script) plutôt qu'un résumé. Indiquer
        soit `date_debut` et `date_fin` (90 jours au plus), soit `sujet`. Colonnes : uid, numero,
        date, legislature, type, contexte, resultat, titre, dossier_ref, dossier_libelle,
        url_civix. Les votes individuels s'exportent avec exporter_votes.
        """
        by_dates = date_debut is not None or date_fin is not None
        if by_dates == (sujet is not None):
            raise ToolError("Indiquez soit `date_debut` et `date_fin`, soit `sujet`.")
        notes: list[str] = []
        items: list[ScrutinSummary]
        if sujet is not None:
            pool = await search_scrutin_pool(client, sujet)
            items = pool.items
            if pool.truncated or pool.matching > MAX_SUBJECT_ROWS:
                notes.append(f"Export limité aux {MAX_SUBJECT_ROWS} scrutins les plus récents.")
            if pool.note:
                notes.append(pool.note)
        else:
            if date_debut is None or date_fin is None:
                raise ToolError("`date_debut` et `date_fin` vont ensemble.")
            start, end = parse_range(date_debut, date_fin)
            found = await gather.fetch_period(client, start, end)
            items = found.items
            if found.truncated:
                notes.append("Export tronqué : période trop dense pour être lue en entier.")
        if len(items) > max_lignes:
            notes.append(f"Export limité à {max_lignes} lignes (`max_lignes`).")
        rows = [exporting.scrutin_row(item) for item in items[:max_lignes]]
        data = exporting.serialise(format, exporting.SCRUTIN_COLUMNS, rows)
        source = source_line(SOURCE_CIVIX, SOURCE_ASSEMBLEE)
        return wrap(format, data, len(rows), notes, source)

    @limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    async def exporter_votes(scrutin_uid: ScrutinUid, format: ExportFormat = "csv") -> str:
        """Exporte les votes individuels d'un scrutin en CSV ou JSON.

        À utiliser pour obtenir la liste brute des votes d'un scrutin (un député par ligne) :
        scrutin_uid, depute_uid, prenom, nom, position (pour, contre, abstention, non_votant),
        par_delegation. Les députés absents ne figurent pas dans la liste.
        """
        response = await client.get_votes(scrutin_uid)
        votes = response.attributes.votes
        rows = [exporting.vote_row(scrutin_uid, vote) for vote in votes]
        data = exporting.serialise(format, exporting.VOTE_COLUMNS, rows)
        notes = ["Les députés sans vote enregistré sont absents de la liste."]
        civix = response.source.civix_page or civix_scrutin_url(scrutin_uid)
        source = source_line(civix, response.source.assemblee_url)
        return wrap(format, data, len(rows), notes, source)

    for function in (exporter_scrutins, exporter_votes):
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)
