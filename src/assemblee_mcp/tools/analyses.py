"""Outils d'analyse : tendances générales et agrégats sur plusieurs scrutins ou députés."""

import asyncio
import math
import re
from datetime import date, timedelta
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.models import AssemblyStats, GroupSeats, GroupStances, Method
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Depute, Pagination, ScrutinSummary
from assemblee_mcp.civix.search import search_scrutin_pool
from assemblee_mcp.formatting import (
    format_depute_candidates,
    format_deputes,
    format_no_scrutin,
    pagination_hint,
    scrutin_line,
)
from assemblee_mcp.tools.common import (
    ANALYTICS_DEADLINE_SECONDS,
    ANALYTICS_MAX_CALLS,
    LISTING_MAX_CALLS,
    READ_ONLY_ANNOTATIONS,
    LegislatureNumber,
    limited,
)
from assemblee_mcp.tools.deputes import MAX_CANDIDATES, pick_depute

KindName = Literal["tous", "texte", "article", "amendement", "autre"]
KIND_VALUES: dict[str, str | None] = {
    "tous": None,
    "texte": "texte",
    "article": "article",
    "amendement": "amendement",
    "autre": "scrutin",
}
KIND_DESCRIPTION = (
    "Type de scrutin : `texte` (vote sur l'ensemble d'un texte), `article`, `amendement`, "
    "`autre` (motions…) ou `tous`."
)
DOSSIER_REF = re.compile(r"^DLR[A-Za-z0-9]{3,30}$")
ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_RANGE_DAYS = 90
LISTING_PAGE_SIZE = 20
SAMPLE_PAGES = 10
DOSSIER_MAX_PAGES = 6
DOSSIER_BATCH = 3
DOSSIER_PAGE_SIZE = 50
CURRENT_LEGISLATURE = 17

PeriodTrends = Annotated[
    int, Field(description="Nombre de jours à analyser, jusqu'à aujourd'hui.", ge=7, le=90)
]
PeriodSample = Annotated[
    int,
    Field(
        description="Nombre de jours à analyser, jusqu'à aujourd'hui (30 au plus).",
        ge=7,
        le=30,
    ),
]
MaxScrutins = Annotated[
    int,
    Field(
        description="Nombre maximal de scrutins analysés (échantillon borné).",
        ge=3,
        le=30,
    ),
]
Subject = Annotated[
    str,
    Field(
        description="Sujet en mots-clés (« retraites »), avec accents.",
        min_length=2,
        max_length=200,
    ),
]
DossierReference = Annotated[
    str,
    Field(
        description="Référence d'un dossier législatif, par exemple « DLR5L17N54898 ».",
        pattern=r"^DLR[A-Za-z0-9]{3,30}$",
    ),
]
DateText = Annotated[
    str,
    Field(description="Date au format AAAA-MM-JJ.", pattern=r"^\d{4}-\d{2}-\d{2}$"),
]


def parse_day(value: str, label: str) -> date:
    """Convertit `AAAA-MM-JJ` en date ; lève `ToolError` si invalide."""
    if not ISO_DAY.match(value):
        raise ToolError(f"{label} invalide : attendu AAAA-MM-JJ (par exemple 2026-10-01).")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ToolError(f"{label} invalide : « {value} » n'est pas une date.") from error


def parse_range(start_text: str, end_text: str) -> tuple[date, date]:
    """Valide une plage de dates (ordre et durée maximale de 90 jours)."""
    start = parse_day(start_text, "date_debut")
    end = parse_day(end_text, "date_fin")
    if end < start:
        raise ToolError("date_fin doit être postérieure ou égale à date_debut.")
    if (end - start).days > MAX_RANGE_DAYS:
        raise ToolError(f"La période ne peut pas dépasser {MAX_RANGE_DAYS} jours.")
    return start, end


def describe_period(start: date, end: date) -> str:
    """Période en texte, jours inclus."""
    return f"du {start.isoformat()} au {end.isoformat()} ({(end - start).days + 1} jours)"


def exactly_one(subject: str | None, dossier: str | None) -> str:
    """Requête issue de `sujet` ou `dossier` (un seul des deux)."""
    if (subject is None) == (dossier is None):
        raise ToolError("Indiquez soit `sujet`, soit `dossier` (un seul des deux).")
    return subject if subject is not None else str(dossier)


def choose(subject: str | None, days: int | None) -> None:
    """Vérifie qu'un seul critère de sélection (`sujet` ou `periode_jours`) est donné."""
    if (subject is None) == (days is None):
        raise ToolError("Indiquez soit `sujet`, soit `periode_jours` (un seul des deux).")


def sample_notes(sample: gather.Sample, count: int, *, regular: bool) -> list[str]:
    """Notes expliquant comment l'échantillon a été constitué."""
    notes: list[str] = []
    if regular and sample.matching > len(sample.chosen):
        notes.append(
            f"Échantillon régulier : {len(sample.chosen)} scrutins répartis sur la période "
            f"parmi {sample.matching}."
        )
    if not regular and sample.matching > count:
        notes.append(f"Seuls les {count} scrutins les plus récents ont été analysés.")
    if sample.note:
        notes.append(sample.note)
    return notes


async def resolve_depute(client: CivixClient, name: str) -> Depute | str:
    """Député visé, ou texte de réponse si le nom est introuvable ou ambigu."""
    candidates = await lookup.find_deputes(client, name)
    if not candidates:
        return format_deputes([], f"Député « {name} »")
    chosen = pick_depute(candidates, name)
    if chosen is None:
        return format_depute_candidates(name, candidates, MAX_CANDIDATES)
    return chosen


def group_names(rows_stances: list[GroupStances]) -> list[str]:
    """Sigles de groupes présents, par ordre alphabétique."""
    return sorted({name for row in rows_stances for name in row.stances})


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'analyse."""
    analytics = limited(ANALYTICS_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    listing = limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)

    async def period_sample(
        days: int, count: int, kind: KindName
    ) -> tuple[gather.Sample, date, date, int]:
        end = gather.current_day()
        start = end - timedelta(days=days)
        sample, found = await gather.sample_from_period(
            client, days, count, today=end, kind=KIND_VALUES[kind]
        )
        return sample, start, end, len(found.items)

    @listing
    async def tendances_scrutins(
        periode_jours: PeriodTrends = 30,
        legislature: LegislatureNumber | None = None,
    ) -> str:
        """Tendances générales des scrutins de l'Assemblée sur une période récente.

        À utiliser pour les questions d'ensemble (« que s'est-il passé à l'Assemblée ce mois-ci ? »,
        « combien de votes, quelle part d'adoption ? ») plutôt que pour un vote précis. Donne le
        volume de scrutins par semaine, la part de scrutins adoptés au total, par type
        (amendements, articles, ensembles de textes) et par contexte (PLF, PLFSS, propositions
        de loi), et les jours les plus chargés.
        """
        end = gather.current_day()
        start = end - timedelta(days=periode_jours)
        found = await gather.fetch_period(client, start, end, legislature=legislature)
        result = stats.trends(found.items, start, end)
        method = Method(
            period=describe_period(start, end),
            analysed=len(found.items),
            matching=len(found.items),
            truncated=found.truncated,
            counted=(
                "chaque scrutin public est compté une fois ; part d'adoption = adoptés / "
                "(adoptés + rejetés) ; types et contextes tels que publiés par CIVIX."
            ),
            limits=[
                "un amendement, un article et un vote sur l'ensemble comptent chacun pour un "
                "scrutin : les volumes reflètent surtout les amendements.",
            ],
        )
        return render.render_trends(result, method)

    @listing
    async def textes_les_plus_votes(
        periode_jours: PeriodTrends = 30,
        limite: Annotated[int, Field(description="Nombre de textes à afficher.", ge=1, le=30)] = 10,
    ) -> str:
        """Textes (dossiers législatifs) ayant donné lieu au plus de scrutins sur une période.

        À utiliser pour savoir quels textes ont occupé l'Assemblée récemment. Pour chaque dossier :
        nombre de scrutins (dont amendements, articles et votes sur l'ensemble), adoptés/rejetés,
        date du dernier vote. Un grand nombre de scrutins reflète surtout le nombre d'amendements.
        """
        end = gather.current_day()
        start = end - timedelta(days=periode_jours)
        found = await gather.fetch_period(client, start, end)
        ranked = stats.rank_texts(found.items)
        method = Method(
            period=describe_period(start, end),
            analysed=len(found.items),
            matching=len(found.items),
            truncated=found.truncated,
            counted=(
                "scrutins regroupés par dossier législatif (référence CIVIX) ; les scrutins sans "
                "dossier sont réunis à part."
            ),
            limits=["classement par nombre de scrutins, non par importance du texte."],
            notes=[f"{len(ranked)} dossiers distincts, {min(limite, len(ranked))} affichés."],
        )
        return render.render_top_texts(ranked[:limite], method)

    @listing
    async def dossier_legislatif(
        texte: Annotated[
            str,
            Field(
                description="Mots-clés du texte (« loi de finances 2027 ») ou référence (DLR…).",
                min_length=2,
                max_length=200,
            ),
        ],
    ) -> str:
        """Chronologie de tous les scrutins d'un texte de loi (dossier législatif).

        À utiliser pour suivre un texte de bout en bout : votes sur les articles, motions et vote
        sur l'ensemble, avec les résultats ; les amendements sont comptés mais non listés un à
        un. Accepte des mots-clés ou une référence de dossier (DLR…). Si plusieurs dossiers
        correspondent, le plus voté est détaillé et les autres sont proposés.
        """
        pool = await search_scrutin_pool(client, texte)
        if not pool.items:
            return format_no_scrutin(texte)
        ranked = stats.rank_texts(pool.items)
        chosen = next((r for r in ranked if r.dossier_ref == texte), ranked[0])
        others = [r for r in ranked if r.dossier_ref != chosen.dossier_ref]
        items, total = await dossier_scrutins(chosen.dossier_ref, chosen.libelle, pool.items)
        timeline = stats.dossier_timeline(items, others)
        truncated = total > len(items)
        method = Method(
            analysed=len(items),
            matching=total,
            truncated=truncated,
            counted=(
                "tous les scrutins publics rattachés au dossier ; amendements comptés, autres "
                "scrutins listés du plus ancien au plus récent."
            ),
            limits=["les votes sur l'ensemble sont ceux de type « texte » dans CIVIX."],
            notes=[f"Recherche du dossier. {pool.note}"] if pool.note else [],
        )
        return render.render_timeline(timeline, method)

    async def dossier_scrutins(
        ref: str | None, libelle: str, fallback: list[ScrutinSummary]
    ) -> tuple[list[ScrutinSummary], int]:
        if ref is None:
            same = [i for i in fallback if i.dossier_libelle == libelle or i.dossier_ref is None]
            return same, len(same)
        first = await client.list_scrutins(ref, page=1, page_size=DOSSIER_PAGE_SIZE)
        total = first.pagination.total if first.pagination and first.pagination.total else 0
        items = list(first.attributes.results)
        pages = min(math.ceil(total / DOSSIER_PAGE_SIZE), DOSSIER_MAX_PAGES)
        for batch_start in range(2, pages + 1, DOSSIER_BATCH):
            numbers = range(batch_start, min(batch_start + DOSSIER_BATCH, pages + 1))
            responses = await asyncio.gather(
                *(client.list_scrutins(ref, page=n, page_size=DOSSIER_PAGE_SIZE) for n in numbers)
            )
            for response in responses:
                items.extend(response.attributes.results)
        return [i for i in items if i.dossier_ref == ref], total

    @listing
    async def scrutins_par_periode(
        date_debut: DateText,
        date_fin: DateText,
        type: Annotated[KindName, Field(description=KIND_DESCRIPTION)] = "tous",
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
        found = await gather.fetch_period(client, start, end)
        kept = gather.select_kind(found.items, KIND_VALUES[type])
        if resultat != "tous":
            wanted = resultat == "adopte"
            kept = [item for item in kept if item.adopted is wanted]
        first = (page - 1) * LISTING_PAGE_SIZE
        shown = kept[first : first + LISTING_PAGE_SIZE]
        pagination = stats_pagination(page, len(kept))
        method = Method(
            period=describe_period(start, end),
            analysed=len(found.items),
            matching=len(kept),
            truncated=found.truncated,
            counted="scrutins publics dont la date est dans la période, après filtres.",
        )
        lines = "\n".join(scrutin_line(item) for item in shown) or "Aucun scrutin."
        hint = pagination_hint(pagination, len(shown), "scrutin(s)")
        body = f"## Scrutins {describe_period(start, end)}\n\n{lines}\n\n{hint}"
        return render.finish_analysis(body, method)

    @limited(LISTING_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
    async def statistiques_assemblee() -> str:
        """Chiffres d'ensemble de la législature en cours : scrutins, groupes, députés.

        À utiliser pour une vue générale de l'Assemblée : nombre total de scrutins depuis le
        début de la législature, part de scrutins adoptés (estimée sur un échantillon réparti
        sur toute la législature), effectifs de chaque groupe parlementaire et nombre de
        députés.
        """
        first = await client.list_scrutins(
            legislature=CURRENT_LEGISLATURE, page=1, page_size=gather.LIST_PAGE_SIZE
        )
        total = first.pagination.total if first.pagination else None
        last_page = math.ceil(total / gather.LIST_PAGE_SIZE) if total else 1
        numbers = [
            n for n in stats.evenly_spaced(list(range(1, last_page + 1)), SAMPLE_PAGES) if n != 1
        ]
        pages, groups, deputies = await asyncio.gather(
            asyncio.gather(
                *(
                    client.list_scrutins(
                        legislature=CURRENT_LEGISLATURE, page=n, page_size=gather.LIST_PAGE_SIZE
                    )
                    for n in numbers
                )
            ),
            lookup.list_groupes(client),
            client.list_deputes(legislature=CURRENT_LEGISLATURE, page_size=1),
        )
        items = list(first.attributes.results)
        for page in pages:
            items.extend(page.attributes.results)
        result = AssemblyStats(
            legislature=CURRENT_LEGISLATURE,
            total_scrutins=total,
            sample_size=len(items),
            overall=stats.make_rate("Tous les scrutins", items),
            by_type=stats.rate_table(items, lambda item: item.type),
            groups=[
                GroupSeats(abbr=g.abbr, libelle=g.libelle, effectif=g.effectif) for g in groups
            ],
            deputies=deputies.pagination.total if deputies.pagination else None,
        )
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

    async def stance_sample(
        subject: str | None, days: int | None, count: int, kind: KindName
    ) -> tuple[gather.Sample, str | None, list[str]]:
        choose(subject, days)
        if subject is not None:
            sample = await gather.sample_from_query(client, subject, count, kind=KIND_VALUES[kind])
            return sample, None, sample_notes(sample, count, regular=False)
        assert days is not None
        sample, start, end, _ = await period_sample(days, count, kind)
        return sample, describe_period(start, end), sample_notes(sample, count, regular=True)

    @analytics
    async def positions_groupes(
        sujet: Annotated[
            str | None,
            Field(description="Sujet en mots-clés (« retraites »), avec accents.", max_length=200),
        ] = None,
        dossier: Annotated[
            DossierReference | None,
            Field(description="Référence d'un dossier législatif (DLR…), à la place de `sujet`."),
        ] = None,
        max_scrutins: Annotated[int, Field(ge=3, le=30, description="Scrutins analysés.")] = 15,
        type_scrutin: Annotated[KindName, Field(description=KIND_DESCRIPTION)] = "tous",
    ) -> str:
        """Tableau des positions majoritaires de chaque groupe sur les scrutins d'un sujet.

        À utiliser pour voir d'un coup d'œil comment les groupes parlementaires ont voté sur un
        thème ou un texte : pour chaque scrutin correspondant, la position majoritaire de chaque
        groupe (pour, contre, abstention, ou partagée). Indiquer `sujet` ou `dossier`.
        """
        query = exactly_one(sujet, dossier)
        sample = await gather.sample_from_query(
            client, query, max_scrutins, kind=KIND_VALUES[type_scrutin]
        )
        if not sample.chosen:
            return format_no_scrutin(query)
        details, abbreviations = await asyncio.gather(
            gather.fetch_details(client, sample.chosen), lookup.groupe_abbreviations(client)
        )
        rows = stats.group_stances(details, abbreviations)
        method = Method(
            analysed=len(rows),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=(
                "pour chaque groupe, la position (pour, contre, abstention) qui réunit le plus "
                "de votes exprimés de ses membres ; « partagée » en cas d'égalité."
            ),
            limits=[
                "la position majoritaire ne dit rien des votes minoritaires dans le groupe ;",
                "les décomptes par groupe sont ceux publiés par CIVIX pour chaque scrutin.",
            ],
            notes=sample_notes(sample, max_scrutins, regular=False),
        )
        return render.render_positions(rows, group_names(rows), method)

    @analytics
    async def accords_entre_groupes(
        sujet: Annotated[
            str | None,
            Field(description="Sujet en mots-clés (« budget »), avec accents.", max_length=200),
        ] = None,
        periode_jours: Annotated[
            PeriodSample | None, Field(description="Jours à analyser.")
        ] = None,
        max_scrutins: MaxScrutins = 30,
        type_scrutin: Annotated[KindName, Field(description=KIND_DESCRIPTION)] = "tous",
    ) -> str:
        """Taux d'accord entre groupes parlementaires, deux à deux, sur un échantillon de scrutins.

        À utiliser pour une vue d'ensemble des convergences entre groupes : pour chaque paire, part
        des scrutins où les deux groupes ont la même position majoritaire. Indiquer `sujet` ou
        `periode_jours` (30 au plus). Calculé sur un échantillon borné, annoncé dans la méthode.
        """
        sample, period, notes = await stance_sample(
            sujet, periode_jours, max_scrutins, type_scrutin
        )
        details, abbreviations = await asyncio.gather(
            gather.fetch_details(client, sample.chosen), lookup.groupe_abbreviations(client)
        )
        rows = stats.group_stances(details, abbreviations)
        method = Method(
            period=period,
            analysed=len(rows),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=(
                "pour chaque paire de groupes, scrutins où les deux ont une position majoritaire "
                "nette (pas d'égalité) ; accord = même position."
            ),
            limits=[
                "un accord sur un amendement ou un article n'est pas un accord sur un texte ;",
                "l'échantillon peut comporter beaucoup d'amendements.",
            ],
            notes=notes,
        )
        return render.render_agreements(stats.agreements(rows), group_names(rows), method)

    @analytics
    async def cohesion_groupes(
        sujet: Annotated[
            str | None,
            Field(description="Sujet en mots-clés (« retraites »), avec accents.", max_length=200),
        ] = None,
        periode_jours: Annotated[
            PeriodSample | None, Field(description="Jours à analyser.")
        ] = None,
        max_scrutins: MaxScrutins = 30,
        type_scrutin: Annotated[KindName, Field(description=KIND_DESCRIPTION)] = "tous",
    ) -> str:
        """Part des votes de chaque groupe qui suivent sa position majoritaire.

        À utiliser pour mesurer l'homogénéité des votes au sein de chaque groupe sur un sujet ou
        une période : part des votes exprimés (pour, contre, abstention) conformes à la position
        majoritaire du groupe, calculée sur un échantillon borné de scrutins.
        """
        sample, period, notes = await stance_sample(
            sujet, periode_jours, max_scrutins, type_scrutin
        )
        details, abbreviations = await asyncio.gather(
            gather.fetch_details(client, sample.chosen), lookup.groupe_abbreviations(client)
        )
        method = Method(
            period=period,
            analysed=len(details),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=(
                "sur chaque scrutin, votes exprimés des membres du groupe (pour, contre, "
                "abstention) ; alignés = votes identiques à la position la plus fréquente."
            ),
            limits=[
                "les non-votants et absents ne sont pas comptés ;",
                "un vote différent de la majorité du groupe peut être autorisé ou annoncé.",
            ],
            notes=notes,
        )
        return render.render_cohesion(stats.cohesion(details, abbreviations), method)

    @analytics
    async def votes_serres(
        periode_jours: PeriodSample = 30,
        max_scrutins: MaxScrutins = 30,
        ecart_max: Annotated[
            int, Field(description="Écart maximal entre pour et contre, en voix.", ge=0, le=100)
        ] = 20,
        type_scrutin: Annotated[KindName, Field(description=KIND_DESCRIPTION)] = "texte",
    ) -> str:
        """Scrutins au résultat serré (faible écart entre pour et contre) sur une période récente.

        À utiliser pour repérer les votes qui se sont joués à quelques voix. Par défaut, ne
        regarde que les votes sur l'ensemble d'un texte ; `type_scrutin` permet d'inclure les
        articles, amendements ou tous les scrutins.
        """
        sample, start, end, _ = await period_sample(periode_jours, max_scrutins, type_scrutin)
        details = await gather.fetch_details(client, sample.chosen)
        close = stats.close_votes(details, ecart_max)
        method = Method(
            period=describe_period(start, end),
            analysed=len(details),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=f"écart = |pour − contre| ; scrutins d'écart au plus {ecart_max} voix.",
            limits=["les abstentions et non-votants ne sont pas dans l'écart."],
            notes=sample_notes(sample, max_scrutins, regular=True),
        )
        return render.render_close_votes(close, ecart_max, method)

    @analytics
    async def bilan_depute(
        depute: Annotated[
            str,
            Field(
                description="Nom d'UN député (« Jérôme Guedj ») ou son `uid`.",
                min_length=2,
                max_length=100,
            ),
        ],
        sujet: Annotated[
            str | None,
            Field(description="Sujet en mots-clés (« retraites »), avec accents.", max_length=200),
        ] = None,
        periode_jours: Annotated[
            PeriodSample | None, Field(description="Jours à analyser.")
        ] = None,
        max_scrutins: MaxScrutins = 30,
    ) -> str:
        """Répartition des votes d'UN député sur un échantillon et alignement sur son groupe.

        Donne le nombre de pour, contre, abstentions, non-votants et scrutins absents de la liste
        des votes, ainsi que la part de votes conformes à la position majoritaire de son groupe.
        Indiquer `sujet` ou `periode_jours`. Sert à décrire, jamais à classer ou juger un député.
        """
        choose(sujet, periode_jours)
        found = await resolve_depute(client, depute)
        if isinstance(found, str):
            return found
        sample, period, notes = await stance_sample(sujet, periode_jours, max_scrutins, "tous")
        votes, abbreviations = await asyncio.gather(
            gather.fetch_votes(client, sample.chosen), lookup.groupe_abbreviations(client)
        )
        group_uid = reverse_lookup(abbreviations, found.groupe_abrev)
        result = stats.depute_bilan(
            found.full_name, found.uid, group_uid, found.groupe_abrev, votes
        )
        method = Method(
            period=period,
            analysed=len(votes),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=(
                "position du député dans la liste des votes de chaque scrutin ; « absent de la "
                "liste » = aucun vote enregistré pour lui ; alignement = vote exprimé identique à "
                "la position majoritaire de son groupe (scrutins sans position nette exclus)."
            ),
            limits=[
                "l'absence d'un vote enregistré ne dit rien de l'intérêt du député pour le sujet ;",
                "un vote par délégation est enregistré au nom du député ;",
                "le groupe retenu est le groupe actuel du député ;",
                "échantillon borné : ne pas généraliser à l'ensemble de l'activité du député.",
            ],
            notes=notes,
        )
        return render.render_bilan(result, method)

    @analytics
    async def comparer_deputes(
        depute_a: Annotated[
            str,
            Field(description="Nom du premier député ou son `uid`.", min_length=2, max_length=100),
        ],
        depute_b: Annotated[
            str,
            Field(description="Nom du second député ou son `uid`.", min_length=2, max_length=100),
        ],
        sujet: Annotated[
            str | None,
            Field(description="Sujet en mots-clés (« retraites »), avec accents.", max_length=200),
        ] = None,
        periode_jours: Annotated[
            PeriodSample | None, Field(description="Jours à analyser.")
        ] = None,
        max_scrutins: MaxScrutins = 30,
    ) -> str:
        """Compare les votes de DEUX députés nommés : part de scrutins votés de la même façon.

        À utiliser pour « X et Y votent-ils pareil ? ». Calcule, sur les scrutins où les deux ont
        exprimé un vote, la part de positions identiques. Indiquer `sujet` ou `periode_jours`.
        Description factuelle d'un échantillon borné, sans jugement.
        """
        choose(sujet, periode_jours)
        first, second = await asyncio.gather(
            resolve_depute(client, depute_a), resolve_depute(client, depute_b)
        )
        for found in (first, second):
            if isinstance(found, str):
                return found
        assert isinstance(first, Depute)
        assert isinstance(second, Depute)
        sample, period, notes = await stance_sample(sujet, periode_jours, max_scrutins, "tous")
        votes = await gather.fetch_votes(client, sample.chosen)
        result = stats.compare_deputes(
            first.full_name, first.uid, second.full_name, second.uid, votes
        )
        method = Method(
            period=period,
            analysed=len(votes),
            matching=sample.matching,
            truncated=sample.truncated,
            counted=(
                "scrutins où les deux députés ont exprimé un vote (pour, contre, abstention) ; "
                "accord = même position."
            ),
            limits=[
                "les scrutins où l'un des deux est absent ou non-votant sont exclus ;",
                "un accord sur un amendement ou un article n'est pas un accord sur un texte ;",
                "échantillon borné, sans valeur de classement.",
            ],
            notes=notes,
        )
        return render.render_comparison(result, method)

    functions = (
        tendances_scrutins,
        textes_les_plus_votes,
        dossier_legislatif,
        scrutins_par_periode,
        statistiques_assemblee,
        positions_groupes,
        accords_entre_groupes,
        cohesion_groupes,
        votes_serres,
        bilan_depute,
        comparer_deputes,
    )
    for function in functions:
        mcp.tool(function, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)


def reverse_lookup(abbreviations: dict[str, str], abbr: str | None) -> str | None:
    """Identifiant d'un groupe à partir de son sigle."""
    if abbr is None:
        return None
    return next((uid for uid, name in abbreviations.items() if name == abbr), None)


def stats_pagination(page: int, total: int) -> Pagination:
    """Pagination locale d'une liste filtrée."""
    return Pagination(
        page=page,
        page_size=LISTING_PAGE_SIZE,
        next_page=page + 1 if page * LISTING_PAGE_SIZE < total else None,
        count_total=total,
    )
