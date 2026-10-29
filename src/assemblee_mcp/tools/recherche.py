"""Recherche globale dans les données de l'Assemblée nationale."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.search import search_everything
from assemblee_mcp.formatting import format_search
from assemblee_mcp.tools.common import Page, ToolFunction, ToolSet, civix_tool


class RechercheTools(ToolSet):
    """Outil de recherche transversale (scrutins, députés, groupes, dossiers)."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.rechercher,)

    @civix_tool
    async def rechercher(
        self,
        requete: Annotated[
            str,
            Field(
                description=(
                    "Mots-clés : sujet d'un vote, nom de député ou de groupe, titre d'un texte. "
                    "Utiliser les accents français."
                ),
                min_length=2,
                max_length=200,
            ),
        ],
        page: Page = 1,
    ) -> str:
        """Recherche globale dans les données de l'Assemblée nationale (CIVIX).

        À utiliser quand on ne sait pas encore si l'on cherche un scrutin, un député, un groupe
        ou un dossier législatif. Renvoie jusqu'à 8 résultats par catégorie avec leurs
        identifiants, à réutiliser dans les autres outils. Pour un sujet de vote précis,
        préférer rechercher_scrutins ; pour une personne, rechercher_deputes.
        """
        found = await search_everything(self.client, requete, page=page)
        return format_search(found, requete)


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils de recherche."""
    RechercheTools(client).register(mcp)
