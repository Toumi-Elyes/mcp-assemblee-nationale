"""Mise en forme des réponses en markdown français concis, sans interprétation politique.

Un module par thème (`scrutins`, `votes`, `declarations`, `deputes`, `groupes`, `recherche`) ;
`text` et `sources` portent le nettoyage de texte tiers, les liens sources et le pied de page.
Ce fichier expose l'API publique du package.
"""

from assemblee_mcp.formatting.declarations import MAX_STATEMENT_LENGTH, format_statements
from assemblee_mcp.formatting.deputes import (
    ScrutinPosition,
    format_comment_a_vote,
    format_depute,
    format_depute_candidates,
    format_deputes,
    format_no_scrutin,
    position_from_votes,
    position_unavailable,
)
from assemblee_mcp.formatting.groupes import format_groupe, format_groupes
from assemblee_mcp.formatting.recherche import format_search
from assemblee_mcp.formatting.scrutins import format_scrutin, format_scrutin_list, scrutin_line
from assemblee_mcp.formatting.sources import FOOTER, finish, pagination_hint, source_line
from assemblee_mcp.formatting.text import (
    MAX_FIELD_LENGTH,
    field_text,
    format_date,
    sanitize,
    truncate,
)
from assemblee_mcp.formatting.votes import VoteFilters, format_votes, select_votes

__all__ = [
    "FOOTER",
    "MAX_FIELD_LENGTH",
    "MAX_STATEMENT_LENGTH",
    "ScrutinPosition",
    "VoteFilters",
    "field_text",
    "finish",
    "format_comment_a_vote",
    "format_date",
    "format_depute",
    "format_depute_candidates",
    "format_deputes",
    "format_groupe",
    "format_groupes",
    "format_no_scrutin",
    "format_scrutin",
    "format_scrutin_list",
    "format_search",
    "format_statements",
    "format_votes",
    "pagination_hint",
    "position_from_votes",
    "position_unavailable",
    "sanitize",
    "scrutin_line",
    "select_votes",
    "source_line",
    "truncate",
]
