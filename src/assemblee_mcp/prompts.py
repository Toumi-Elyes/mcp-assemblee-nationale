"""Prompts MCP : amorces de conversation pour les cas d'usage courants."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field


def register(mcp: FastMCP) -> None:
    """Enregistre les prompts."""

    def resumer_scrutin(
        sujet: Annotated[str, Field(description="Sujet du vote, par exemple « retraites ».")],
    ) -> str:
        return (
            f"Retrouve le scrutin de l'Assemblée nationale le plus pertinent sur « {sujet} » "
            "avec rechercher_scrutins (précise lequel si plusieurs textes correspondent), "
            "puis résume-le avec obtenir_scrutin : date, résultat officiel, décomptes pour, "
            "contre et abstentions, et répartition par groupe. Reste factuel et neutre, "
            "sans interprétation politique, et cite le lien source."
        )

    def mon_depute(
        nom: Annotated[str, Field(description="Nom du député, par exemple « Marine Le Pen ».")],
    ) -> str:
        return (
            f"Présente le député « {nom} » avec rechercher_deputes puis obtenir_depute : "
            "groupe, circonscription et liens officiels. Si le nom est ambigu, liste les "
            "candidats et demande-moi de choisir. Propose ensuite de regarder ses votes avec "
            "comment_a_vote sur un sujet de mon choix. Reste factuel et neutre."
        )

    def comparer_groupes(
        sujet: Annotated[str, Field(description="Sujet du vote, par exemple « budget 2026 ».")],
    ) -> str:
        return (
            f"Compare la position des groupes parlementaires sur « {sujet} » : trouve le "
            "scrutin pertinent avec rechercher_scrutins, puis utilise obtenir_scrutin pour le "
            "tableau pour/contre/abstention par groupe et declarations_groupes pour leurs "
            "explications publiques éventuelles. Présente un tableau factuel, sans jugement "
            "ni interprétation politique, et cite les liens sources."
        )

    for function in (resumer_scrutin, mon_depute, comparer_groupes):
        mcp.prompt(function)
