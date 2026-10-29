"""Outils sur les députés, dont « Comment a voté… ? » (position d'un député sur un sujet)."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Depute, ScrutinSummary
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.formatting import (
    ScrutinPosition,
    format_comment_a_vote,
    format_depute,
    format_deputes,
    format_no_scrutin,
    pagination_hint,
    position_from_votes,
    position_unavailable,
)
from assemblee_mcp.limits import COMMENT_MAX_CALLS, DEFAULT_PAGE_SIZE
from assemblee_mcp.pagination import paginate
from assemblee_mcp.tools.common import (
    GroupeAbbreviation,
    LegislatureNumber,
    Page,
    ScrutinUid,
    ToolFunction,
    ToolSet,
    civix_tool,
    limited,
)
from assemblee_mcp.tools.resolution import resolve_depute

DeputeUid = Annotated[
    str,
    Field(
        description="Identifiant du député, par exemple « PA793214 » (voir rechercher_deputes).",
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9]+$",
    ),
]
# « Comment a voté… ? » examine les premiers scrutins du sujet : assez pour être parlant,
# peu pour tenir dans le budget d'appels.
MAX_SCRUTINS_PER_SUBJECT = 5
SINGLE_TARGET_MESSAGE = "Indiquez soit `sujet`, soit `scrutin_uid` (un seul des deux)."


class DeputeTools(ToolSet):
    """Recherche de députés, fiche et position d'un député sur un sujet."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.rechercher_deputes, self.obtenir_depute, self.comment_a_vote)

    @civix_tool
    async def rechercher_deputes(
        self,
        nom: Annotated[
            str | None,
            Field(
                description="Nom, prénom ou nom complet du député (accents et casse ignorés).",
                max_length=100,
            ),
        ] = None,
        groupe: Annotated[
            GroupeAbbreviation | None, Field(description="Sigle du groupe, par exemple « RN ».")
        ] = None,
        legislature: LegislatureNumber | None = None,
        page: Page = 1,
    ) -> str:
        """Cherche des députés par nom, groupe ou législature.

        À utiliser pour retrouver l'identifiant (`uid`) d'un député avant d'appeler
        obtenir_depute. Sans `nom`, liste les députés (filtrables par groupe).
        """
        if nom is None:
            return await self._list_deputes(groupe, legislature, page)
        found = await lookup.find_deputes(self.client, nom, groupe=groupe, legislature=legislature)
        shown, pagination = paginate(found, page, DEFAULT_PAGE_SIZE)
        hint = pagination_hint(pagination, len(shown), "député(s)")
        return format_deputes(shown, f"Députés correspondant à « {nom} »", hint)

    @civix_tool
    async def obtenir_depute(
        self,
        uid: Annotated[
            DeputeUid | None, Field(description="Identifiant du député (PA…), à la place de `nom`.")
        ] = None,
        nom: Annotated[
            str | None,
            Field(
                description="Nom du député, à la place de `uid` (accents et casse ignorés).",
                min_length=2,
                max_length=100,
            ),
        ] = None,
    ) -> str:
        """Fiche d'un député : groupe, circonscription, législature, liens officiels.

        Indiquer `uid` ou `nom` (si le nom est ambigu, les candidats sont listés).
        """
        if (uid is None) == (nom is None):
            raise ToolError("Indiquez soit `uid`, soit `nom` (un seul des deux).")
        if uid is not None:
            return format_depute(await self.client.get_depute(uid.upper()))
        resolved = await resolve_depute(self.client, str(nom))
        if isinstance(resolved, str):
            return resolved
        return format_depute(await self.client.get_depute(resolved.uid))

    @limited(COMMENT_MAX_CALLS)
    async def comment_a_vote(
        self,
        depute: Annotated[
            str,
            Field(
                description="Nom du député (« Marine Le Pen », « Panot ») ou son `uid`.",
                min_length=2,
                max_length=100,
            ),
        ],
        sujet: Annotated[
            str | None,
            Field(
                description="Sujet du vote en mots-clés (« retraites », « budget »), avec accents.",
                max_length=200,
            ),
        ] = None,
        scrutin_uid: Annotated[
            ScrutinUid | None,
            Field(description="Identifiant d'un scrutin précis, à la place de `sujet`."),
        ] = None,
    ) -> str:
        """Répond à « Comment a voté le député X sur le sujet Y ? ».

        Indiquer `depute` et soit `sujet`, soit `scrutin_uid`. Retrouve le député (si le nom est
        ambigu, liste les candidats pour que l'utilisateur choisisse), puis donne sa position
        (pour, contre, abstention, non-votant) sur les 5 premiers scrutins correspondant au
        sujet, avec les liens sources. Un sujet donne souvent plusieurs scrutins (amendements,
        articles, ensemble du texte) : citer le titre de chacun. Aucune interprétation.
        """
        if (sujet is None) == (scrutin_uid is None):
            raise ToolError(SINGLE_TARGET_MESSAGE)
        resolved = await resolve_depute(self.client, depute)
        if isinstance(resolved, str):
            return resolved
        if scrutin_uid is not None:
            return await self._answer_for_scrutin(resolved, scrutin_uid)
        return await self._answer_for_subject(resolved, str(sujet))

    async def _list_deputes(self, groupe: str | None, legislature: int | None, page: int) -> str:
        """Liste paginée des députés, filtrée par groupe et législature."""
        abbr = await lookup.resolve_groupe(self.client, groupe) if groupe is not None else None
        response = await self.client.list_deputes(
            groupe=abbr, legislature=legislature, page=page, page_size=DEFAULT_PAGE_SIZE
        )
        deputes = list(response.attributes.results)
        hint = pagination_hint(response.pagination, len(deputes), "député(s)")
        return format_deputes(deputes, "Députés", hint)

    async def _answer_for_scrutin(self, depute: Depute, scrutin_uid: str) -> str:
        """Position du député sur un scrutin précis."""
        response = await self.client.get_votes(scrutin_uid)
        entry = position_from_votes(response, depute.uid)
        return format_comment_a_vote(depute, [entry], "Scrutin demandé.")

    async def _answer_for_subject(self, depute: Depute, subject: str) -> str:
        """Position du député sur les premiers scrutins correspondant au sujet."""
        found = await search_scrutins(self.client, subject, page_size=MAX_SCRUTINS_PER_SUBJECT)
        summaries = found.results[:MAX_SCRUTINS_PER_SUBJECT]
        if not summaries:
            return format_no_scrutin(subject)
        entries = await asyncio.gather(
            *(self._position_on(depute.uid, summary) for summary in summaries)
        )
        total = found.pagination.total if found.pagination else None
        of_total = f" sur {total}" if total is not None else ""
        broadened = f"_{found.note}_\n\n" if found.note else ""
        pool = (
            f"{broadened}{len(entries)} premier(s) scrutin(s){of_total} "
            f"trouvé(s) pour « {subject} » "
            "(un texte donne souvent plusieurs scrutins : amendements, articles, ensemble). "
            "Pour un scrutin précis, redemandez avec `scrutin_uid`."
        )
        return format_comment_a_vote(depute, list(entries), pool)

    async def _position_on(self, depute_uid: str, summary: ScrutinSummary) -> ScrutinPosition:
        """Position du député sur un scrutin de la liste, tolérante aux échecs ponctuels."""
        try:
            return position_from_votes(await self.client.get_votes(summary.uid), depute_uid)
        except CivixError:
            return position_unavailable(summary)


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les députés."""
    DeputeTools(client).register(mcp)
