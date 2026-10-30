"""Outils de consultation des scrutins publics."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.archive import ARCHIVED_LEGISLATURES
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Position, ScrutinVotesResponse
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.formatting import (
    VoteFilters,
    format_scrutin,
    format_scrutin_list,
    format_statements,
    format_votes,
    select_votes,
)
from assemblee_mcp.limits import DEFAULT_PAGE_SIZE
from assemblee_mcp.tools.common import (
    GroupeAbbreviation,
    LegislatureNumber,
    Page,
    PositionName,
    ScrutinUid,
    ToolFunction,
    ToolSet,
    civix_tool,
)


class ScrutinTools(ToolSet):
    """Recherche, détail, votes individuels et déclarations de groupes."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (
            self.rechercher_scrutins,
            self.obtenir_scrutin,
            self.votes_scrutin,
            self.declarations_groupes,
        )

    @civix_tool
    async def rechercher_scrutins(
        self,
        mots_cles: Annotated[
            str | None,
            Field(
                description=(
                    "Mots-clés du sujet (« retraites », « assurance chômage », « budget 2026 »). "
                    "Utiliser les accents français ; laisser vide pour lister les plus récents."
                ),
                max_length=200,
            ),
        ] = None,
        legislature: LegislatureNumber | None = None,
        page: Page = 1,
    ) -> str:
        """Cherche des scrutins (votes de l'Assemblée nationale) par sujet.

        À utiliser pour retrouver le vote d'un texte, d'un article ou d'un amendement. Renvoie
        pour chaque scrutin la date, le résultat officiel, le titre et son `uid`, à passer à
        obtenir_scrutin ou votes_scrutin. Un même texte donne souvent plusieurs scrutins
        (amendements, articles, vote sur l'ensemble).
        """
        found = await search_scrutins(
            self.client,
            mots_cles,
            legislature=legislature,
            page=page,
            page_size=DEFAULT_PAGE_SIZE,
        )
        return format_scrutin_list(found, mots_cles)

    @civix_tool
    async def obtenir_scrutin(self, uid: ScrutinUid) -> str:
        """Détail d'un scrutin : titre, date, type, résultat officiel et décomptes.

        Donne le nombre de pour, contre et abstentions, global puis par groupe parlementaire.
        Pour savoir comment un député ou un groupe a voté, utiliser ensuite votes_scrutin.
        """
        response, abbreviations = await asyncio.gather(
            self.client.get_scrutin(uid), self._abbreviations_or_empty()
        )
        return format_scrutin(response, abbreviations)

    @civix_tool
    async def votes_scrutin(
        self,
        uid: ScrutinUid,
        groupe: Annotated[
            GroupeAbbreviation | None,
            Field(
                description="Ne garder que les députés de ce groupe (sigle, cf. lister_groupes)."
            ),
        ] = None,
        position: Annotated[
            PositionName | None,
            Field(
                description="Ne garder que cette position : pour, contre, abstention, non_votant."
            ),
        ] = None,
        nom: Annotated[
            str | None,
            Field(
                description="Ne garder que les noms contenant ce texte (accents et casse ignorés).",
                max_length=100,
            ),
        ] = None,
    ) -> str:
        """Votes individuels des députés sur un scrutin, regroupés par position.

        Les totaux officiels sont toujours indiqués ; la liste de noms est limitée à 60 noms
        (utiliser `groupe`, `position` ou `nom` pour affiner). Pour savoir comment UN député a
        voté sur un sujet, préférer comment_a_vote.
        """
        response, group_abbr, member_uids = await self._votes_of_group(uid, groupe)
        wanted = Position(position) if position is not None else None
        selected = select_votes(
            response.attributes.votes, member_uids=member_uids, position=wanted, nom=nom
        )
        at_date = response.attributes.scrutin.legislature in ARCHIVED_LEGISLATURES
        filters = VoteFilters(group_abbr, wanted, nom, groupe_at_date=at_date)
        return format_votes(response, selected, filters)

    @civix_tool
    async def declarations_groupes(self, uid: ScrutinUid) -> str:
        """Déclarations publiques des groupes parlementaires sur un scrutin.

        Reprend telles quelles les explications de vote publiées par les groupes (souvent
        aucune). Ne contient aucune analyse : à citer comme déclarations des groupes.
        """
        response = await self.client.get_statements(uid)
        return format_statements(response, uid)

    async def _abbreviations_or_empty(self) -> dict[str, str]:
        """Sigles des groupes ; un échec n'empêche pas d'afficher le scrutin."""
        try:
            return await lookup.groupe_abbreviations(self.client)
        except CivixError:
            return {}

    async def _votes_of_group(
        self, uid: str, groupe: str | None
    ) -> tuple[ScrutinVotesResponse, str | None, set[str] | None]:
        """Votes d'un scrutin et, si `groupe` est donné, sigle officiel et membres du groupe.

        Pour une législature close, les membres sont ceux du groupe à la date du scrutin.
        """
        if groupe is None:
            return await self.client.get_votes(uid), None, None
        legislature = lookup.legislature_of_scrutin(uid)
        if legislature in ARCHIVED_LEGISLATURES:
            return await self._archived_votes_of_group(uid, groupe, legislature)
        abbr = await lookup.resolve_groupe(self.client, groupe)
        response, members = await asyncio.gather(
            self.client.get_votes(uid), lookup.groupe_member_uids(self.client, abbr)
        )
        return response, abbr, members

    async def _archived_votes_of_group(
        self, uid: str, groupe: str, legislature: int
    ) -> tuple[ScrutinVotesResponse, str, set[str]]:
        """Votes d'un scrutin d'une législature close et membres du groupe ce jour-là."""
        abbr = await lookup.resolve_groupe(self.client, groupe, legislature)
        response = await self.client.get_votes(uid)
        day = response.attributes.scrutin.date_scrutin
        if day is None:
            return response, abbr, set()
        return response, abbr, lookup.archived_member_uids(legislature, abbr, day.date())


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les scrutins."""
    ScrutinTools(client).register(mcp)
