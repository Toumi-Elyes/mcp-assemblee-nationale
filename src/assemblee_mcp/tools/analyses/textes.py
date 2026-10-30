"""Outils d'analyse centrés sur les textes de loi et sur le résultat de leurs scrutins."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.dossier import analyse_dossier
from assemblee_mcp.analytics.models import Method
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.formatting import format_no_scrutin
from assemblee_mcp.limits import (
    ANALYTICS_DEADLINE_SECONDS,
    ANALYTICS_MAX_CALLS,
    DEFAULT_ANALYSED_SCRUTINS,
    LISTING_MAX_CALLS,
)
from assemblee_mcp.tools.analyses.parameters import KindParameter, MaxScrutins, SamplePeriodDays
from assemblee_mcp.tools.analyses.sampling import (
    sample_notes,
    sample_period,
    small_sample_warnings,
)
from assemblee_mcp.tools.common import ToolFunction, ToolSet, limited
from assemblee_mcp.tools.periods import describe_period

listing_tool = limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
analytics_tool = limited(ANALYTICS_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)


class TexteTools(ToolSet):
    """Chronologie d'un texte et votes au résultat serré."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.dossier_legislatif, self.votes_serres)

    @listing_tool
    async def dossier_legislatif(
        self,
        texte: Annotated[
            str,
            Field(
                description="Mots-clés du texte (« loi de finances 2027 ») ou référence (DLR…).",
                min_length=2,
                max_length=200,
            ),
        ],
    ) -> str:
        """Chronologie de tous les scrutins d'un texte de loi (dossier législatif).

        À utiliser pour suivre un texte de bout en bout : votes sur les articles, motions et vote
        sur l'ensemble, avec les résultats ; les amendements sont comptés mais non listés un à
        un. Accepte des mots-clés ou une référence de dossier (DLR…). Si plusieurs dossiers
        correspondent, le plus voté est détaillé et les autres sont proposés.
        """
        analysis = await analyse_dossier(self.client, texte)
        if analysis is None:
            return format_no_scrutin(texte)
        return render.render_timeline(analysis.timeline, analysis.method)

    @analytics_tool
    async def votes_serres(
        self,
        periode_jours: SamplePeriodDays = 30,
        max_scrutins: MaxScrutins = DEFAULT_ANALYSED_SCRUTINS,
        ecart_max: Annotated[
            int, Field(description="Écart maximal entre pour et contre, en voix.", ge=0, le=100)
        ] = 20,
        type_scrutin: KindParameter = "texte",
    ) -> str:
        """Scrutins au résultat serré (faible écart entre pour et contre) sur une période récente.

        À utiliser pour repérer les votes qui se sont joués à quelques voix. Par défaut, ne
        regarde que les votes sur l'ensemble d'un texte ; `type_scrutin` permet d'inclure les
        articles, amendements ou tous les scrutins.
        """
        sample, start, end = await sample_period(
            self.client, periode_jours, max_scrutins, type_scrutin
        )
        details = await gather.fetch_details(self.client, sample.chosen)
        method = Method(
            period=describe_period(start, end),
            analysed=len(details),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=f"écart = |pour − contre| ; scrutins d'écart au plus {ecart_max} voix.",
            limits=["les abstentions et non-votants ne sont pas dans l'écart."],
            notes=sample_notes(sample, max_scrutins, regular=True),
            warnings=small_sample_warnings(len(details), "scrutin(s) analysé(s)"),
        )
        close = stats.close_votes(details, ecart_max)
        return render.render_close_votes(close, ecart_max, method, stats.closest_margin(details))


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les textes."""
    TexteTools(client).register(mcp)
