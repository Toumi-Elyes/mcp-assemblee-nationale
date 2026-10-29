"""Outils sur les groupes parlementaires."""

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.formatting import format_groupe, format_groupes
from assemblee_mcp.tools.common import READ_ONLY_ANNOTATIONS, GroupeAbbreviation, civix_tool


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les groupes."""

    @civix_tool
    async def lister_groupes() -> str:
        """Liste les groupes parlementaires de l'Assemblée nationale avec leur sigle et effectif.

        À utiliser pour connaître les sigles (RN, LFI-NFP, SOC…) avant de filtrer par groupe.
        """
        return format_groupes(await client.list_groupes())

    @civix_tool
    async def obtenir_groupe(abbr: GroupeAbbreviation) -> str:
        """Fiche d'un groupe parlementaire : nom complet, effectif, législature."""
        found = await lookup.find_groupe(client, abbr)
        if found is None:
            raise ToolError(
                f"Groupe « {abbr} » inconnu. Utilisez lister_groupes pour voir les sigles."
            )
        return format_groupe(await client.get_groupe(found.abbr))

    for function in (lister_groupes, obtenir_groupe):
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)
