"""Rendu markdown des analyses : chiffres, bloc « Méthode », sources et pied de page.

Même découpage que `stats` : `activity`, `groups`, `deputes` ; `shared` porte les tableaux, les
pourcentages et le bloc de méthode."""

from assemblee_mcp.analytics.render.activity import (
    render_assembly,
    render_timeline,
    render_top_texts,
    render_trends,
)
from assemblee_mcp.analytics.render.deputes import render_bilan, render_comparison
from assemblee_mcp.analytics.render.groups import (
    STANCE_SYMBOLS,
    render_agreements,
    render_close_votes,
    render_cohesion,
    render_positions,
)
from assemblee_mcp.analytics.render.shared import finish_analysis, method_block, percent

__all__ = [
    "STANCE_SYMBOLS",
    "finish_analysis",
    "method_block",
    "percent",
    "render_agreements",
    "render_assembly",
    "render_bilan",
    "render_close_votes",
    "render_cohesion",
    "render_comparison",
    "render_positions",
    "render_timeline",
    "render_top_texts",
    "render_trends",
]
