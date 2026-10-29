"""Réponses complètes par point d'accès : l'enveloppe paramétrée par ses attributs."""

from assemblee_mcp.civix.models.deputes import DeputeDetail, DeputeList
from assemblee_mcp.civix.models.envelope import CivixResponse
from assemblee_mcp.civix.models.groupes import GroupeDetail, GroupeList
from assemblee_mcp.civix.models.recherche import SearchResults
from assemblee_mcp.civix.models.scrutins import Scrutin, ScrutinList, ScrutinVotes, StatementList

SearchResponse = CivixResponse[SearchResults]


ScrutinListResponse = CivixResponse[ScrutinList]


ScrutinResponse = CivixResponse[Scrutin]


ScrutinVotesResponse = CivixResponse[ScrutinVotes]


StatementsResponse = CivixResponse[StatementList]


DeputeListResponse = CivixResponse[DeputeList]


DeputeDetailResponse = CivixResponse[DeputeDetail]


GroupeListResponse = CivixResponse[GroupeList]


GroupeDetailResponse = CivixResponse[GroupeDetail]
