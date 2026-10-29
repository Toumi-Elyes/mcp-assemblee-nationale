"""Outils sur les groupes parlementaires."""

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.formatting import format_groupe, format_groupes
from assemblee_mcp.tools.common import GroupeAbbreviation, ToolFunction, ToolSet, civix_tool


class GroupeTools(ToolSet):
    """Liste et fiche des groupes parlementaires."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.lister_groupes, self.obtenir_groupe)

    @civix_tool
    async def lister_groupes(self) -> str:
        """Liste les groupes parlementaires de l'Assemblée nationale avec leur sigle et effectif.

        À utiliser pour connaître les sigles (RN, LFI-NFP, SOC…) avant de filtrer par groupe.
        """
        return format_groupes(await self.client.list_groupes())

    @civix_tool
    async def obtenir_groupe(self, abbr: GroupeAbbreviation) -> str:
        """Fiche d'un groupe parlementaire : nom complet, effectif, législature."""
        found = await lookup.find_groupe(self.client, abbr)
        if found is None:
            raise ToolError(
                f"Groupe « {abbr} » inconnu. Utilisez lister_groupes pour voir les sigles."
            )
        return format_groupe(await self.client.get_groupe(found.abbr))


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les groupes."""
    GroupeTools(client).register(mcp)
