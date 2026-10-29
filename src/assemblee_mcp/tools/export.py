"""Exports machine-lisibles de scrutins et de votes (CSV ou JSON)."""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.analytics import exporting, gather
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import ScrutinSummary
from assemblee_mcp.civix.search import search_scrutin_pool
from assemblee_mcp.formatting import FOOTER, source_line
from assemblee_mcp.limits import ANALYTICS_DEADLINE_SECONDS, LISTING_MAX_CALLS
from assemblee_mcp.links import assemblee_scrutin_url, civix_scrutin_url
from assemblee_mcp.tools.common import ScrutinUid, ToolFunction, ToolSet, limited
from assemblee_mcp.tools.periods import DateText, parse_range

ExportFormat = Annotated[
    Literal["csv", "json"], Field(description="Format de sortie : `csv` (avec en-tête) ou `json`.")
]
StartDate = Annotated[
    DateText | None,
    Field(description="Début de période AAAA-MM-JJ (avec `date_fin`, 90 jours au plus)."),
]
EndDate = Annotated[DateText | None, Field(description="Fin de période AAAA-MM-JJ.")]
SubjectKeywords = Annotated[
    str | None,
    Field(description="Mots-clés, à la place des dates (100 scrutins au plus).", max_length=200),
]
MaxLines = Annotated[int, Field(description="Nombre maximal de lignes exportées.", ge=1, le=1000)]
# Un scrutin compte au plus 577 votes : 600 lignes exportent un vote complet.
DEFAULT_VOTE_LINES = 600
VoteLines = Annotated[int, Field(description="Nombre maximal de lignes exportées.", ge=1, le=1000)]
# Une recherche par mots-clés ne remonte que deux pages de CIVIX : au plus 100 scrutins.
MAX_SUBJECT_ROWS = 100
SOURCE_ASSEMBLEE = "https://www.assemblee-nationale.fr/dyn/17/scrutins"
SOURCE_CIVIX = "https://www.civix.fr/api/v1/scrutins"

type ExportedScrutins = tuple[list[ScrutinSummary], list[str]]


def wrap_export(format_name: str, data: str, count: int, notes: list[str], source: str) -> str:
    """Données dans un bloc de code, avec nombre de lignes, notes, source et pied de page."""
    header = f"Export {format_name.upper()} : {count} ligne(s)."
    extras = "".join(f"\n{note}" for note in notes)
    block = f"```{format_name}\n{data}\n```"
    return f"{header}{extras}\n\n{block}\n\n{source}\n{FOOTER}"


class ExportTools(ToolSet):
    """Exports de scrutins et de votes pour qui veut analyser les données soi-même."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.exporter_scrutins, self.exporter_votes)

    @limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    async def exporter_scrutins(
        self,
        date_debut: StartDate = None,
        date_fin: EndDate = None,
        sujet: SubjectKeywords = None,
        format: ExportFormat = "csv",
        max_lignes: MaxLines = 500,
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
        if sujet is not None:
            items, notes = await self._scrutins_of_subject(sujet)
        else:
            items, notes = await self._scrutins_of_period(date_debut, date_fin)
        if len(items) > max_lignes:
            notes.append(f"Export limité à {max_lignes} lignes (`max_lignes`).")
        rows = [exporting.scrutin_row(item) for item in items[:max_lignes]]
        data = exporting.serialise(format, exporting.SCRUTIN_COLUMNS, rows)
        source = source_line(SOURCE_CIVIX, SOURCE_ASSEMBLEE)
        return wrap_export(format, data, len(rows), notes, source)

    @limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    async def exporter_votes(
        self,
        scrutin_uid: ScrutinUid,
        format: ExportFormat = "csv",
        max_lignes: VoteLines = DEFAULT_VOTE_LINES,
    ) -> str:
        """Exporte les votes individuels d'un scrutin en CSV ou JSON.

        À utiliser pour obtenir la liste brute des votes d'un scrutin (un député par ligne) :
        scrutin_uid, depute_uid, prenom, nom, groupe, position (pour, contre, abstention,
        non_votant), par_delegation. `groupe` est le groupe actuel du député, ce qui permet de
        regrouper les votes par groupe. Les députés absents ne figurent pas dans la liste.
        """
        response = await self.client.get_votes(scrutin_uid)
        votes = response.attributes.votes
        groups, notes = await self._groups_by_deputy()
        rows = [
            exporting.vote_row(scrutin_uid, vote, groups.get(vote.deputy_uid))
            for vote in votes[:max_lignes]
        ]
        notes.append("Les députés sans vote enregistré sont absents de la liste.")
        if len(votes) > max_lignes:
            notes.append(
                f"Export limité à {max_lignes} lignes (`max_lignes`) sur {len(votes)} votes."
            )
        data = exporting.serialise(format, exporting.VOTE_COLUMNS, rows)
        civix = response.source.civix_page or civix_scrutin_url(scrutin_uid)
        scrutin = response.attributes.scrutin
        assemblee = assemblee_scrutin_url(scrutin.legislature, scrutin.numero)
        source = source_line(civix, assemblee)
        return wrap_export(format, data, len(rows), notes, source)

    async def _groups_by_deputy(self) -> tuple[dict[str, str], list[str]]:
        """Sigle du groupe actuel de chaque député (annuaire en cache), avec une note de méthode."""
        try:
            directory = await self.client.directory.load()
        except CivixError:
            return {}, ["Colonne `groupe` vide : annuaire des députés momentanément indisponible."]
        groups = {d.uid: d.groupe_abrev for d in directory if d.groupe_abrev is not None}
        return groups, [
            "`groupe` : groupe actuel du député (peut différer de celui du jour du vote)."
        ]

    async def _scrutins_of_subject(self, subject: str) -> ExportedScrutins:
        """Scrutins d'une recherche par mots-clés, avec les notes de limite éventuelles."""
        pool = await search_scrutin_pool(self.client, subject)
        notes: list[str] = []
        if pool.truncated or pool.matching > MAX_SUBJECT_ROWS:
            notes.append(f"Export limité aux {MAX_SUBJECT_ROWS} scrutins les plus récents.")
        if pool.note:
            notes.append(pool.note)
        return pool.items, notes

    async def _scrutins_of_period(
        self, start_text: str | None, end_text: str | None
    ) -> ExportedScrutins:
        """Scrutins d'une période, avec une note si la période est trop dense pour être lue."""
        if start_text is None or end_text is None:
            raise ToolError("`date_debut` et `date_fin` vont ensemble.")
        start, end = parse_range(start_text, end_text)
        found = await gather.fetch_period(self.client, start, end)
        notes = (
            ["Export tronqué : période trop dense pour être lue en entier."]
            if found.truncated
            else []
        )
        return found.items, notes


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'export."""
    ExportTools(client).register(mcp)
