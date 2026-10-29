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

    def tendances_du_mois() -> str:
        return (
            "Fais un point factuel sur l'activité de l'Assemblée nationale ces 30 derniers jours : "
            "utilise tendances_scrutins puis textes_les_plus_votes, et résume le volume de "
            "scrutins, la part d'adoption par type de scrutin et les textes qui ont donné lieu "
            "au plus de votes. Reste neutre, sans interprétation politique, indique la méthode "
            "(période, échantillon) et cite les liens sources."
        )

    def bilan_groupe(
        groupe: Annotated[str, Field(description="Sigle du groupe, par exemple « SOC ».")],
    ) -> str:
        return (
            f"Dresse un bilan factuel du groupe parlementaire « {groupe} » sur les 30 derniers "
            "jours : effectif avec obtenir_groupe, homogénéité des votes avec cohesion_groupes "
            "et convergences avec les autres groupes avec accords_entre_groupes. Présente les "
            "chiffres tels quels, sans jugement ni interprétation politique, rappelle la "
            "méthode et la taille de l'échantillon, et cite les sources."
        )

    def comparer_deux_deputes(
        depute_a: Annotated[str, Field(description="Nom du premier député.")],
        depute_b: Annotated[str, Field(description="Nom du second député.")],
    ) -> str:
        return (
            f"Compare factuellement les votes de « {depute_a} » et « {depute_b} » avec "
            "comparer_deputes (sur un sujet que je choisis, ou sur les 30 derniers jours), puis "
            "présente le taux de positions identiques, le nombre de scrutins comparés et les "
            "limites de l'échantillon. Si un nom est ambigu, demande-moi de préciser. Aucun "
            "jugement : décris uniquement les données."
        )

    for function in (
        resumer_scrutin,
        mon_depute,
        comparer_groupes,
        tendances_du_mois,
        bilan_groupe,
        comparer_deux_deputes,
    ):
        mcp.prompt(function)
