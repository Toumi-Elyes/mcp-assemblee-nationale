"""Outils sur les scrutins publics."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Position
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.formatting import (
    VoteFilters,
    format_scrutin,
    format_scrutin_list,
    format_statements,
    format_votes,
    select_votes,
)
from assemblee_mcp.tools.common import (
    DEFAULT_PAGE_SIZE,
    READ_ONLY_ANNOTATIONS,
    GroupeAbbreviation,
    LegislatureNumber,
    Page,
    PositionName,
    ScrutinUid,
    civix_tool,
)


async def abbreviations_or_empty(client: CivixClient) -> dict[str, str]:
    """Sigles des groupes ; un échec n'empêche pas d'afficher le scrutin."""
    try:
        return await lookup.groupe_abbreviations(client)
    except CivixError:
        return {}


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les scrutins."""

    @civix_tool
    async def rechercher_scrutins(
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
            client, mots_cles, legislature=legislature, page=page, page_size=DEFAULT_PAGE_SIZE
        )
        return format_scrutin_list(found, mots_cles)

    @civix_tool
    async def obtenir_scrutin(uid: ScrutinUid) -> str:
        """Détail d'un scrutin : titre, date, type, résultat officiel et décomptes.

        Donne le nombre de pour, contre et abstentions, global puis par groupe parlementaire.
        Pour savoir comment un député ou un groupe a voté, utiliser ensuite votes_scrutin.
        """
        response, abbreviations = await asyncio.gather(
            client.get_scrutin(uid), abbreviations_or_empty(client)
        )
        return format_scrutin(response, abbreviations)

    @civix_tool
    async def votes_scrutin(
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
        member_uids: set[str] | None = None
        groupe_sigle: str | None = None
        if groupe is None:
            response = await client.get_votes(uid)
        else:
            found = await lookup.find_groupe(client, groupe)
            if found is None:
                known = ", ".join(g.abbr for g in await lookup.list_groupes(client))
                raise ToolError(f"Groupe « {groupe} » inconnu. Groupes disponibles : {known}.")
            groupe_sigle = found.abbr
            response, member_uids = await asyncio.gather(
                client.get_votes(uid), lookup.groupe_member_uids(client, found.abbr)
            )
        wanted = Position(position) if position is not None else None
        selected = select_votes(
            response.attributes.votes, member_uids=member_uids, position=wanted, nom=nom
        )
        return format_votes(response, selected, VoteFilters(groupe_sigle, wanted, nom))

    @civix_tool
    async def declarations_groupes(uid: ScrutinUid) -> str:
        """Déclarations publiques des groupes parlementaires sur un scrutin.

        Reprend telles quelles les explications de vote publiées par les groupes (souvent
        aucune). Ne contient aucune analyse : à citer comme déclarations des groupes.
        """
        response = await client.get_statements(uid)
        return format_statements(response, uid)

    for function in (rechercher_scrutins, obtenir_scrutin, votes_scrutin, declarations_groupes):
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)
