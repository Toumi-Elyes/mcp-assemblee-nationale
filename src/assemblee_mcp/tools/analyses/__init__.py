"""Outils d'analyse : tendances générales et agrégats sur plusieurs scrutins ou députés.

Cinq familles, une par module : `activite` (chiffres d'ensemble), `textes` (dossiers et
résultats serrés), `sujets` (un sujet d'une législature à l'autre), `groupes` (comparaisons
entre groupes) et `deputes` (députés nommés).
"""

from fastmcp import FastMCP

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.tools.analyses import activite, deputes, groupes, sujets, textes


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre tous les outils d'analyse."""
    for module in (activite, textes, sujets, groupes, deputes):
        module.register(mcp, client)
