"""Outils sur les députés et le composite « Comment a voté… ? »."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError
from assemblee_mcp.civix.models import Depute, Pagination, ScrutinSummary
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.formatting import (
    ScrutinPosition,
    format_comment_a_vote,
    format_depute,
    format_depute_candidates,
    format_deputes,
    format_no_scrutin,
    pagination_hint,
    position_from_votes,
    position_unavailable,
)
from assemblee_mcp.tools.common import (
    DEFAULT_PAGE_SIZE,
    READ_ONLY_ANNOTATIONS,
    GroupeAbbreviation,
    LegislatureNumber,
    Page,
    ScrutinUid,
    civix_tool,
)

DeputeUid = Annotated[
    str,
    Field(
        description="Identifiant du député, par exemple « PA793214 » (voir rechercher_deputes).",
        min_length=3,
        max_length=32,
        pattern=r"^[A-Za-z0-9]+$",
    ),
]
MAX_SCRUTINS = 5
MAX_CANDIDATES = 10


def pick_depute(candidates: list[Depute], query: str) -> Depute | None:
    """Choisit le député visé : unique résultat, ou unique correspondance exacte du nom."""
    if len(candidates) == 1:
        return candidates[0]
    exact = [depute for depute in candidates if lookup.is_exact_name(depute, query)]
    return exact[0] if len(exact) == 1 else None


def page_of(deputes: list[Depute], page: int) -> tuple[list[Depute], Pagination]:
    """Découpe localement une liste de députés en pages."""
    start = (page - 1) * DEFAULT_PAGE_SIZE
    end = start + DEFAULT_PAGE_SIZE
    pagination = Pagination(
        page=page,
        page_size=DEFAULT_PAGE_SIZE,
        next_page=page + 1 if end < len(deputes) else None,
        count_total=len(deputes),
    )
    return deputes[start:end], pagination


async def position_for_summary(
    client: CivixClient, depute_uid: str, summary: ScrutinSummary
) -> ScrutinPosition:
    """Position du député sur un scrutin de la liste, tolérante aux échecs ponctuels."""
    try:
        return position_from_votes(await client.get_votes(summary.uid), depute_uid)
    except CivixError:
        return position_unavailable(summary)


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils sur les députés."""

    @civix_tool
    async def rechercher_deputes(
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
            response = await client.list_deputes(
                groupe=groupe, legislature=legislature, page=page, page_size=DEFAULT_PAGE_SIZE
            )
            deputes = list(response.attributes.results)
            hint = pagination_hint(response.pagination, len(deputes), "député(s)")
            return format_deputes(deputes, "Députés", hint)
        found = await lookup.find_deputes(client, nom, groupe=groupe, legislature=legislature)
        shown, pagination = page_of(found, page)
        hint = pagination_hint(pagination, len(shown), "député(s)")
        return format_deputes(shown, f"Députés correspondant à « {nom} »", hint)

    @civix_tool
    async def obtenir_depute(uid: DeputeUid) -> str:
        """Fiche d'un député : groupe, circonscription, législature, liens officiels."""
        return format_depute(await client.get_depute(uid.upper()))

    @civix_tool
    async def comment_a_vote(
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
            raise ToolError("Indiquez soit `sujet`, soit `scrutin_uid` (un seul des deux).")
        candidates = await lookup.find_deputes(client, depute)
        if not candidates:
            return format_deputes([], f"Député « {depute} »")
        chosen = pick_depute(candidates, depute)
        if chosen is None:
            return format_depute_candidates(depute, candidates, MAX_CANDIDATES)
        if scrutin_uid is not None:
            response = await client.get_votes(scrutin_uid)
            entries = [position_from_votes(response, chosen.uid)]
            pool = "Scrutin demandé."
        else:
            assert sujet is not None
            listing = await search_scrutins(client, sujet, page_size=MAX_SCRUTINS)
            summaries = listing.results[:MAX_SCRUTINS]
            if not summaries:
                return format_no_scrutin(sujet)
            entries = list(
                await asyncio.gather(
                    *(position_for_summary(client, chosen.uid, summary) for summary in summaries)
                )
            )
            total = listing.pagination.total if listing.pagination else None
            of_total = f" sur {total}" if total is not None else ""
            broadened = f"_{listing.note}_\n\n" if listing.note else ""
            pool = (
                f"{broadened}{len(entries)} premier(s) scrutin(s){of_total} "
                f"trouvé(s) pour « {sujet} » "
                "(un texte donne souvent plusieurs scrutins : amendements, articles, ensemble). "
                "Pour un scrutin précis, redemandez avec `scrutin_uid`."
            )
        return format_comment_a_vote(chosen, entries, pool)

    for function in (rechercher_deputes, obtenir_depute, comment_a_vote):
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)
