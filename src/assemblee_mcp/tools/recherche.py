"""Recherche globale."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.formatting import format_search
from assemblee_mcp.tools.common import READ_ONLY_ANNOTATIONS, Page, civix_tool


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre l'outil de recherche globale."""

    @civix_tool
    async def rechercher(
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
        response = await client.search(requete, page=page)
        return format_search(response, requete)

    mcp.tool(
        rechercher,
        name="rechercher",
        annotations=READ_ONLY_ANNOTATIONS,
        output_schema=None,
    )
