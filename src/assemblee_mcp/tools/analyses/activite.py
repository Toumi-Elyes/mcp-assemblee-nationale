"""Outils d'analyse de l'activité générale de l'Assemblée (tendances, textes, périodes)."""

import asyncio
from datetime import date
from typing import Annotated, Literal

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.models import AssemblyStats, GroupSeats, Method, TextActivity
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Groupe, ScrutinSummary
from assemblee_mcp.formatting import pagination_hint, scrutin_line
from assemblee_mcp.limits import (
    ANALYTICS_DEADLINE_SECONDS,
    CURRENT_LEGISLATURE,
    LEGISLATURE_SAMPLE_PAGES,
    LISTING_MAX_CALLS,
    LOCAL_PAGE_SIZE,
)
from assemblee_mcp.pagination import paginate
from assemblee_mcp.tools.analyses.parameters import (
    KIND_VALUES,
    KindParameter,
    PeriodDays,
)
from assemblee_mcp.tools.common import LegislatureNumber, ToolFunction, ToolSet, limited
from assemblee_mcp.tools.periods import DateText, describe_period, parse_range

listing_tool = limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)


def listing_method(found: gather.Listing, start: date, end: date, *, counted: str) -> Method:
    """Méthode d'une analyse qui porte sur tous les scrutins lus d'une période."""
    return Method(
        period=describe_period(start, end),
        analysed=len(found.items),
        matching=len(found.items),
        truncated=found.truncated,
        counted=counted,
    )


def trends_method(found: gather.Listing, start: date, end: date) -> Method:
    """Méthode de `tendances_scrutins`."""
    method = listing_method(
        found,
        start,
        end,
        counted=(
            "chaque scrutin public est compté une fois ; part d'adoption = adoptés / "
            "(adoptés + rejetés) ; types et contextes tels que publiés par CIVIX."
        ),
    )
    return method.model_copy(
        update={
            "limits": [
                "un amendement, un article et un vote sur l'ensemble comptent chacun pour un "
                "scrutin : les volumes reflètent surtout les amendements.",
            ]
        }
    )


def texts_method(
    found: gather.Listing, start: date, end: date, ranked: list[TextActivity], shown: int
) -> Method:
    """Méthode de `textes_les_plus_votes`."""
    method = listing_method(
        found,
        start,
        end,
        counted=(
            "scrutins regroupés par dossier législatif (référence CIVIX) ; les scrutins sans "
            "dossier sont réunis à part."
        ),
    )
    return method.model_copy(
        update={
            "limits": ["classement par nombre de scrutins, non par importance du texte."],
            "notes": [f"{len(ranked)} dossiers distincts, {min(shown, len(ranked))} affichés."],
        }
    )


def filter_by_result(
    items: list[ScrutinSummary], result: Literal["adopte", "rejete", "tous"]
) -> list[ScrutinSummary]:
    """Garde les scrutins adoptés ou rejetés (tous si `result` vaut `tous`)."""
    if result == "tous":
        return items
    wanted = result == "adopte"
    return [item for item in items if item.adopted is wanted]


def assembly_stats(
    items: list[ScrutinSummary],
    total: int | None,
    groups: list[Groupe],
    deputies: int | None,
) -> AssemblyStats:
    """Chiffres d'ensemble de la législature à partir de l'échantillon lu."""
    return AssemblyStats(
        legislature=CURRENT_LEGISLATURE,
        total_scrutins=total,
        sample_size=len(items),
        overall=stats.make_rate("Tous les scrutins", items),
        by_type=stats.rate_table(items, lambda item: item.kind),
        groups=[
            GroupSeats(abbr=groupe.abbr, libelle=groupe.libelle, effectif=groupe.effectif)
            for groupe in groups
        ],
        deputies=deputies,
    )


class ActiviteTools(ToolSet):
    """Chiffres d'ensemble sur l'activité de vote, à partir des listes de scrutins."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (
            self.tendances_scrutins,
            self.textes_les_plus_votes,
            self.scrutins_par_periode,
            self.statistiques_assemblee,
        )

    @listing_tool
    async def tendances_scrutins(
        self,
        periode_jours: PeriodDays = 30,
        legislature: LegislatureNumber | None = None,
    ) -> str:
        """Tendances générales des scrutins de l'Assemblée sur une période récente.

        Pour une législature close (`legislature`), la période se termine à son dernier scrutin.

        À utiliser pour les questions d'ensemble (« que s'est-il passé à l'Assemblée ce mois-ci ? »,
        « combien de votes, quelle part d'adoption ? ») plutôt que pour un vote précis. Donne le
        volume de scrutins par semaine, la part de scrutins adoptés au total, par type
        (amendements, articles, ensembles de textes) et par contexte (PLF, PLFSS, propositions
        de loi), et les jours les plus chargés.
        """
        end = await gather.period_end(self.client, legislature)
        start = gather.period_start(end, periode_jours)
        found = await gather.fetch_period(self.client, start, end, legislature=legislature)
        result = stats.trends(found.items, start, end)
        method = trends_method(found, start, end).model_copy(update={"legislature": legislature})
        return render.render_trends(result, method)

    @listing_tool
    async def textes_les_plus_votes(
        self,
        periode_jours: PeriodDays = 30,
        limite: Annotated[int, Field(description="Nombre de textes à afficher.", ge=1, le=30)] = 10,
    ) -> str:
        """Textes (dossiers législatifs) ayant donné lieu au plus de scrutins sur une période.

        À utiliser pour savoir quels textes ont occupé l'Assemblée récemment. Pour chaque dossier :
        nombre de scrutins (dont amendements, articles et votes sur l'ensemble), adoptés/rejetés,
        date du dernier vote. Un grand nombre de scrutins reflète surtout le nombre d'amendements.
        """
        start, end = gather.last_days(periode_jours)
        found = await gather.fetch_period(self.client, start, end)
        ranked = stats.rank_texts(found.items)
        method = texts_method(found, start, end, ranked, limite)
        return render.render_top_texts(ranked[:limite], method)

    @listing_tool
    async def scrutins_par_periode(
        self,
        date_debut: DateText,
        date_fin: DateText,
        type: KindParameter = "tous",
        resultat: Annotated[
            Literal["adopte", "rejete", "tous"],
            Field(description="Ne garder que les scrutins adoptés ou rejetés."),
        ] = "tous",
        page: Annotated[int, Field(description="Numéro de page, à partir de 1.", ge=1, le=100)] = 1,
    ) -> str:
        """Liste filtrée des scrutins entre deux dates (90 jours au plus).

        À utiliser pour parcourir les scrutins d'une période : filtrer par type (ensemble d'un
        texte, article, amendement) et par résultat (adopté ou rejeté). 20 scrutins par page,
        du plus récent au plus ancien. Pour des chiffres agrégés, préférer tendances_scrutins.
        """
        start, end = parse_range(date_debut, date_fin)
        found = await gather.fetch_period(self.client, start, end)
        kept = filter_by_result(gather.select_kind(found.items, KIND_VALUES[type]), resultat)
        shown, pagination = paginate(kept, page, LOCAL_PAGE_SIZE)
        method = listing_method(
            found,
            start,
            end,
            counted="scrutins publics dont la date est dans la période, après filtres.",
        ).model_copy(
            update={
                "matching": None,
                "notes": [f"{len(kept)} scrutin(s) correspondent aux filtres (type, résultat)."],
            }
        )
        lines = "\n".join(scrutin_line(item) for item in shown) or "Aucun scrutin."
        hint = pagination_hint(pagination, len(shown), "scrutin(s)")
        body = f"## Scrutins {describe_period(start, end)}\n\n{lines}\n\n{hint}"
        return render.finish_analysis(body, method)

    @listing_tool
    async def statistiques_assemblee(self) -> str:
        """Chiffres d'ensemble de la législature en cours : scrutins, groupes, députés.

        À utiliser pour une vue générale de l'Assemblée : nombre total de scrutins depuis le
        début de la législature, part de scrutins adoptés (estimée sur un échantillon réparti
        sur toute la législature), effectifs de chaque groupe parlementaire et nombre de
        députés.
        """
        (items, total), groups, deputies = await asyncio.gather(
            gather.sample_legislature_pages(
                self.client, CURRENT_LEGISLATURE, LEGISLATURE_SAMPLE_PAGES
            ),
            lookup.list_groupes(self.client),
            self.client.list_deputes(legislature=CURRENT_LEGISLATURE, page_size=1),
        )
        deputy_count = deputies.pagination.total if deputies.pagination else None
        result = assembly_stats(items, total, groups, deputy_count)
        method = Method(
            period=f"{CURRENT_LEGISLATURE}e législature",
            analysed=len(items),
            matching=total,
            truncated=True,
            counted=(
                "total de scrutins fourni par CIVIX ; parts d'adoption estimées sur des pages de "
                "scrutins réparties sur toute la législature."
            ),
            limits=[
                "estimation sur échantillon, non sur tous les scrutins ;",
                "le nombre de députés est celui que CIVIX recense, remplaçants compris.",
            ],
        )
        return render.render_assembly(result, method)


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'activité générale."""
    ActiviteTools(client).register(mcp)
