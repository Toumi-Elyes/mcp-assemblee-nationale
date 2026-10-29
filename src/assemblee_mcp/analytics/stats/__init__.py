"""Calculs purs sur les scrutins, sans accès réseau.

Un module par thème : `activity` (volumes, tendances, textes), `groups` (positions et accords des
groupes) et `deputes` (votes de députés nommés) ; `shared` regroupe les briques communes."""

from assemblee_mcp.analytics.stats.activity import (
    NO_DOSSIER_LABEL,
    busiest_days,
    dossier_timeline,
    in_period,
    make_rate,
    rank_texts,
    rate_table,
    trends,
    weekly_volumes,
)
from assemblee_mcp.analytics.stats.deputes import compare_deputes, depute_bilan
from assemblee_mcp.analytics.stats.groups import (
    agreements,
    close_votes,
    closest_margin,
    cohesion,
    group_stances,
    stance,
)
from assemblee_mcp.analytics.stats.shared import day_of, evenly_spaced, spread_order

__all__ = [
    "NO_DOSSIER_LABEL",
    "agreements",
    "busiest_days",
    "close_votes",
    "closest_margin",
    "cohesion",
    "compare_deputes",
    "day_of",
    "depute_bilan",
    "dossier_timeline",
    "evenly_spaced",
    "group_stances",
    "in_period",
    "make_rate",
    "rank_texts",
    "rate_table",
    "spread_order",
    "stance",
    "trends",
    "weekly_volumes",
]
