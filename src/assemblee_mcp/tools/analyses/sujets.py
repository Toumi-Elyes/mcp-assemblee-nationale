"""Outil de suivi d'un sujet sur plusieurs législatures."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics.subject import follow_subject, render_subject
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.limits import ANALYTICS_DEADLINE_SECONDS, LISTING_MAX_CALLS
from assemblee_mcp.tools.common import ToolFunction, ToolSet, limited

listing_tool = limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)


class SujetTools(ToolSet):
    """Suivi d'un sujet de la 14e législature (2012) à aujourd'hui."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.suivre_sujet,)

    @listing_tool
    async def suivre_sujet(
        self,
        sujet: Annotated[
            str,
            Field(
                description=(
                    "Mots-clés du sujet, au singulier et avec les accents français "
                    "(« retraite », « mariage », « assurance chômage »)."
                ),
                min_length=2,
                max_length=200,
            ),
        ],
    ) -> str:
        """Suit un sujet d'une législature à l'autre, de 2012 (14e) à aujourd'hui (17e).

        À utiliser pour « Depuis quand l'Assemblée vote-t-elle sur X ? », « Qu'a-t-on voté sur
        X sous chaque législature ? ». Donne, par législature, le nombre de scrutins dont le
        titre correspond, leur nature, adoptés et rejetés, et les derniers votes sur l'ensemble
        d'un texte avec leur `uid`. Relevé factuel : un nombre de scrutins ne mesure pas
        l'importance d'un sujet.
        """
        return render_subject(sujet, await follow_subject(self.client, sujet))


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre l'outil de suivi d'un sujet."""
    SujetTools(client).register(mcp)
