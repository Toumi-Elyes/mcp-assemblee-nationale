"""Modèles Pydantic des réponses de l'API CIVIX.

Seul le bloc `data.attributes` de chaque réponse est modélisé : CIVIX en recopie le contenu
directement sous `data`, ce que `extra="ignore"` écarte. Un module par thème ; ce fichier expose
l'API publique du package.
"""

from assemblee_mcp.civix.models.base import CivixModel, Position
from assemblee_mcp.civix.models.deputes import Depute, DeputeDetail, DeputeList, DeputeUrls
from assemblee_mcp.civix.models.envelope import (
    ASSEMBLEE_HOMEPAGE,
    Citation,
    CivixResponse,
    Data,
    Meta,
    Pagination,
    Source,
)
from assemblee_mcp.civix.models.groupes import Groupe, GroupeDetail, GroupeList, GroupeUrls
from assemblee_mcp.civix.models.recherche import (
    DeputeSearchHit,
    DossierSearchHit,
    GroupeSearchHit,
    ScrutinSearchHit,
    SearchResults,
    SearchResultsByKind,
)
from assemblee_mcp.civix.models.responses import (
    DeputeDetailResponse,
    DeputeListResponse,
    GroupeDetailResponse,
    GroupeListResponse,
    ScrutinListResponse,
    ScrutinResponse,
    ScrutinVotesResponse,
    SearchResponse,
    StatementsResponse,
)
from assemblee_mcp.civix.models.scrutins import (
    Demandeur,
    DossierLegislatif,
    GroupeStatement,
    GroupVoteCounts,
    Objet,
    Scrutin,
    ScrutinDetail,
    ScrutinList,
    ScrutinSummary,
    ScrutinVotes,
    Sort,
    StatementList,
    TypeVote,
    Vote,
    VoteCounts,
)

__all__ = [
    "ASSEMBLEE_HOMEPAGE",
    "Citation",
    "CivixModel",
    "CivixResponse",
    "Data",
    "Demandeur",
    "Depute",
    "DeputeDetail",
    "DeputeDetailResponse",
    "DeputeList",
    "DeputeListResponse",
    "DeputeSearchHit",
    "DeputeUrls",
    "DossierLegislatif",
    "DossierSearchHit",
    "GroupVoteCounts",
    "Groupe",
    "GroupeDetail",
    "GroupeDetailResponse",
    "GroupeList",
    "GroupeListResponse",
    "GroupeSearchHit",
    "GroupeStatement",
    "GroupeUrls",
    "Meta",
    "Objet",
    "Pagination",
    "Position",
    "Scrutin",
    "ScrutinDetail",
    "ScrutinList",
    "ScrutinListResponse",
    "ScrutinResponse",
    "ScrutinSearchHit",
    "ScrutinSummary",
    "ScrutinVotes",
    "ScrutinVotesResponse",
    "SearchResponse",
    "SearchResults",
    "SearchResultsByKind",
    "Sort",
    "Source",
    "StatementList",
    "StatementsResponse",
    "TypeVote",
    "Vote",
    "VoteCounts",
]
