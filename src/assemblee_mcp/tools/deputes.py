"""Outils sur les députés, dont « Comment a voté… ? » (position d'un député sur un sujet)."""

import asyncio
import difflib
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.archive import ARCHIVED_LEGISLATURES
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError, CivixNotFoundError
from assemblee_mcp.civix.models import Depute, ScrutinSummary
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.formatting import (
    ScrutinPosition,
    format_comment_a_vote,
    format_depute,
    format_depute_card,
    format_deputes,
    format_no_scrutin,
    pagination_hint,
    position_from_votes,
    position_unavailable,
)
from assemblee_mcp.limits import COMMENT_MAX_CALLS, CURRENT_LEGISLATURE, DEFAULT_PAGE_SIZE
from assemblee_mcp.pagination import paginate
from assemblee_mcp.textutils import fold
from assemblee_mcp.tools.common import (
    DeputeLegislature,
    GroupeAbbreviation,
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
        departement: Annotated[
            str | None,
            Field(
                description=(
                    "Département de la circonscription, en toutes lettres, par exemple "
                    "« Gironde » ou « Côte-d'Or » (accents, tirets et casse ignorés). Pour une "
                    "ville, indiquez son département."
                ),
                min_length=2,
                max_length=60,
            ),
        ] = None,
        legislature: DeputeLegislature = None,
        page: Page = 1,
    ) -> str:
        """Cherche des députés par nom, groupe, département ou législature (17e par défaut).

        À utiliser pour retrouver l'identifiant (`uid`) d'un député avant d'appeler
        obtenir_depute. Les 14e, 15e et 16e législatures sont couvertes aussi. Sans `nom`,
        liste les députés (filtrables par groupe et par département). Pour « Qui est mon
        député ? », passez le département de la personne : la circonscription exacte dépend de
        l'adresse, ne la devinez pas. Pour une législature close, le groupe indiqué est le
        dernier du député dans cette législature.
        """
        if departement is not None:
            return await self._deputes_of_departement(departement, nom, groupe, legislature, page)
        if nom is None:
            return await self._list_deputes(groupe, legislature, page)
        found = await lookup.find_deputes(self.client, nom, groupe=groupe, legislature=legislature)
        shown, pagination = paginate(found, page, DEFAULT_PAGE_SIZE)
        hint = pagination_hint(pagination, len(shown), "député(s)")
        if not found and legislature is None:
            hint = lookup.archived_name_hint(nom)
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
        legislature: DeputeLegislature = None,
    ) -> str:
        """Fiche d'un député : groupe, circonscription, législature, liens officiels.

        Indiquer `uid` ou `nom` (si le nom est ambigu, les candidats sont listés). La
        législature vaut 17 par défaut ; un ancien député (14e à 16e législature) est retrouvé
        automatiquement par son `uid`, dans sa législature la plus récente.
        """
        if (uid is None) == (nom is None):
            raise ToolError("Indiquez soit `uid`, soit `nom` (un seul des deux).")
        if uid is not None:
            return await self._card_for_uid(uid.upper(), legislature)
        resolved = await resolve_depute(self.client, str(nom), legislature)
        if isinstance(resolved, str):
            return resolved
        return await self._card_for_uid(resolved.uid, resolved.legislature)

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
        legislature: DeputeLegislature = None,
    ) -> str:
        """Répond à « Comment a voté le député X sur le sujet Y ? ».

        Indiquer `depute` et soit `sujet`, soit `scrutin_uid`. Retrouve le député (si le nom est
        ambigu, liste les candidats pour que l'utilisateur choisisse), puis donne sa position
        (pour, contre, abstention, non-votant) sur les 5 premiers scrutins correspondant au
        sujet, avec les liens sources. Un sujet donne souvent plusieurs scrutins (amendements,
        articles, ensemble du texte) : citer le titre de chacun. Aucune interprétation. La
        législature vaut 17 par défaut ; elle se déduit de `scrutin_uid` s'il est donné
        (14e à 17e législature).
        """
        if (sujet is None) == (scrutin_uid is None):
            raise ToolError(SINGLE_TARGET_MESSAGE)
        number = legislature or lookup.legislature_of_scrutin(str(scrutin_uid))
        resolved = await resolve_depute(self.client, depute, number)
        if isinstance(resolved, str):
            return resolved
        if scrutin_uid is not None:
            return await self._answer_for_scrutin(resolved, scrutin_uid)
        return await self._answer_for_subject(resolved, str(sujet), number)

    async def _list_deputes(self, groupe: str | None, legislature: int | None, page: int) -> str:
        """Liste paginée des députés d'une législature, filtrée par groupe."""
        number = legislature or CURRENT_LEGISLATURE
        abbr = await lookup.resolve_groupe(self.client, groupe, number) if groupe else None
        if number != CURRENT_LEGISLATURE:
            return await self._list_archived_deputes(number, abbr, page)
        response = await self.client.list_deputes(
            groupe=abbr, legislature=number, page=page, page_size=DEFAULT_PAGE_SIZE
        )
        deputes = list(response.attributes.results)
        hint = pagination_hint(response.pagination, len(deputes), "député(s)")
        return format_deputes(deputes, "Députés", hint)

    async def _deputes_of_departement(
        self,
        departement: str,
        nom: str | None,
        groupe: str | None,
        legislature: int | None,
        page: int,
    ) -> str:
        """Députés élus dans un département, par numéro de circonscription."""
        number = legislature or CURRENT_LEGISLATURE
        everyone = await self.client.directory_for(number).load()
        names = {
            fold(d.circ_departement): d.circ_departement for d in everyone if d.circ_departement
        }
        wanted = names.get(fold(departement).strip())
        if wanted is None:
            close = difflib.get_close_matches(fold(departement), list(names), n=3, cutoff=0.6)
            suggestion = (
                " Vouliez-vous dire : " + ", ".join(f"« {names[key]} »" for key in close) + " ?"
                if close
                else " Indiquez le nom du département en toutes lettres, par exemple « Gironde »."
            )
            return f"Aucun département « {departement} » parmi les circonscriptions.{suggestion}"
        abbr = await lookup.resolve_groupe(self.client, groupe, number) if groupe else None
        found = [
            d
            for d in everyone
            if d.circ_departement == wanted
            and (abbr is None or d.groupe_abrev == abbr)
            and (nom is None or all(token in fold(d.full_name) for token in fold(nom).split()))
        ]
        found.sort(key=lambda d: (d.circ_num or 0, d.nom))
        shown, pagination = paginate(found, page, DEFAULT_PAGE_SIZE)
        hint = pagination_hint(pagination, len(shown), "député(s)")
        note = (
            "Une circonscription peut compter plusieurs noms si un député a été remplacé en "
            "cours de mandat. Pour savoir quelle circonscription correspond à une adresse, "
            "voir https://www.assemblee-nationale.fr/dyn/vos-deputes."
        )
        title = f"Députés du département « {wanted} » ({number}e législature)"
        return format_deputes(shown, title, f"{hint}\n{note}".strip())

    async def _list_archived_deputes(self, legislature: int, abbr: str | None, page: int) -> str:
        """Liste paginée des députés d'une législature close (index embarqué)."""
        everyone = await self.client.directory_for(legislature).load()
        wanted = [d for d in everyone if abbr is None or d.groupe_abrev == abbr]
        shown, pagination = paginate(wanted, page, DEFAULT_PAGE_SIZE)
        hint = pagination_hint(pagination, len(shown), "député(s)")
        return format_deputes(shown, f"Députés de la {legislature}e législature", hint)

    async def _card_for_uid(self, uid: str, legislature: int | None) -> str:
        """Fiche d'un député ; un identifiant inconnu de la 17e est cherché dans les archives."""
        number = legislature or CURRENT_LEGISLATURE
        if number != CURRENT_LEGISLATURE:
            return format_depute_card(await lookup.find_depute_by_uid(self.client, uid, number))
        try:
            return format_depute(await self.client.get_depute(uid))
        except CivixNotFoundError:
            if legislature is not None:
                raise
            return await self._card_from_archives(uid)

    async def _card_from_archives(self, uid: str) -> str:
        """Fiche d'un ancien député retrouvé dans l'index d'une législature close."""
        for number in ARCHIVED_LEGISLATURES:
            try:
                return format_depute_card(await lookup.find_depute_by_uid(self.client, uid, number))
            except CivixNotFoundError:
                continue
        raise CivixNotFoundError

    async def _answer_for_scrutin(self, depute: Depute, scrutin_uid: str) -> str:
        """Position du député sur un scrutin précis."""
        response = await self.client.get_votes(scrutin_uid)
        entry = position_from_votes(response, depute.uid)
        return format_comment_a_vote(depute, [entry], "Scrutin demandé.")

    async def _answer_for_subject(
        self, depute: Depute, subject: str, legislature: int | None
    ) -> str:
        """Position du député sur les premiers scrutins correspondant au sujet."""
        found = await search_scrutins(
            self.client, subject, legislature=legislature, page_size=MAX_SCRUTINS_PER_SUBJECT
        )
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
