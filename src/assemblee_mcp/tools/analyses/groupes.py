"""Outils d'analyse des groupes parlementaires : positions, accords et cohésion."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.models import GroupStances, Method, PairAgreement
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Scrutin, ScrutinSummary
from assemblee_mcp.civix.scrutin_archive import COMPLETED_LEGISLATURES
from assemblee_mcp.formatting import format_no_scrutin
from assemblee_mcp.limits import (
    ANALYTICS_DEADLINE_SECONDS,
    ANALYTICS_MAX_CALLS,
    DEFAULT_ANALYSED_SCRUTINS,
    MAX_ANALYSED_SCRUTINS,
    SMALL_SAMPLE_THRESHOLD,
)
from assemblee_mcp.tools.analyses.parameters import (
    KIND_VALUES,
    AnalysisLegislature,
    DossierReference,
    KindParameter,
    MaxScrutins,
    OptionalSamplePeriodDays,
    OptionalSubject,
    require_subject_or_dossier,
)
from assemblee_mcp.tools.analyses.sampling import (
    SelectedSample,
    sample_notes,
    select_sample,
    small_sample_warnings,
)
from assemblee_mcp.tools.common import ToolFunction, ToolSet, limited

analytics_tool = limited(ANALYTICS_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
DEFAULT_POSITIONS_SCRUTINS = 20


def group_names(rows: list[GroupStances]) -> list[str]:
    """Sigles de groupes présents, par ordre alphabétique."""
    return sorted({name for row in rows for name in row.stances})


def thin_pairs_warnings(pairs: list[PairAgreement]) -> list[str]:
    """Avertit quand des paires de groupes ont trop peu de scrutins en commun pour conclure."""
    thin = sum(1 for pair in pairs if pair.shared < SMALL_SAMPLE_THRESHOLD)
    if thin == 0:
        return []
    return [
        f"{thin} paire(s) de groupes ont moins de {SMALL_SAMPLE_THRESHOLD} scrutins en commun : "
        "leur taux d'accord est trop fragile pour conclure."
    ]


def selection_method(
    selection: SelectedSample,
    analysed: int,
    *,
    counted: str,
    limits: list[str],
    legislature: int | None = None,
) -> Method:
    """Méthode d'une analyse de groupes sur un échantillon choisi par sujet ou période."""
    sample = selection.sample
    return Method(
        period=selection.period,
        analysed=analysed,
        matching=sample.matching,
        truncated=sample.truncated,
        counted=counted,
        limits=limits,
        notes=selection.notes,
        warnings=small_sample_warnings(analysed, "scrutin(s) analysé(s)"),
        legislature=legislature,
    )


def breakdown_limit(legislature: int | None) -> str:
    """D'où viennent les décomptes par groupe, selon la législature."""
    if legislature in COMPLETED_LEGISLATURES:
        return (
            "les décomptes par groupe sont ceux de l'archive des scrutins de l'Assemblée "
            "nationale (CIVIX ne les publie pas pour cette législature)."
        )
    return "les décomptes par groupe sont ceux publiés par CIVIX pour chaque scrutin."


def positions_method(
    sample: gather.Sample, analysed: int, max_scrutins: int, legislature: int | None
) -> Method:
    """Méthode de `positions_groupes`."""
    return Method(
        analysed=analysed,
        matching=sample.matching,
        truncated=sample.truncated,
        counted=(
            "pour chaque groupe, la position (pour, contre, abstention) qui réunit le plus "
            "de votes exprimés de ses membres ; « partagée » en cas d'égalité."
        ),
        limits=[
            "la position majoritaire ne dit rien des votes minoritaires dans le groupe ;",
            breakdown_limit(legislature),
        ],
        notes=sample_notes(sample, max_scrutins, regular=False),
        warnings=small_sample_warnings(analysed, "scrutin(s) analysé(s)"),
        legislature=legislature,
    )


class GroupeAnalyses(ToolSet):
    """Comparaisons entre groupes parlementaires, calculées sur des échantillons bornés."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.positions_groupes, self.accords_entre_groupes, self.cohesion_groupes)

    @analytics_tool
    async def positions_groupes(
        self,
        sujet: OptionalSubject = None,
        dossier: Annotated[
            DossierReference | None,
            Field(description="Référence d'un dossier législatif (DLR…), à la place de `sujet`."),
        ] = None,
        max_scrutins: Annotated[
            int, Field(ge=3, le=MAX_ANALYSED_SCRUTINS, description="Scrutins analysés.")
        ] = DEFAULT_POSITIONS_SCRUTINS,
        type_scrutin: KindParameter = "tous",
        legislature: AnalysisLegislature = None,
    ) -> str:
        """Tableau des positions majoritaires de chaque groupe sur les scrutins d'un sujet.

        À utiliser pour voir d'un coup d'œil comment les groupes parlementaires ont voté sur un
        thème ou un texte : pour chaque scrutin correspondant, la position majoritaire de chaque
        groupe (pour, contre, abstention, ou partagée). Indiquer `sujet` ou `dossier`.
        `legislature` (14 à 17) limite la recherche à une législature.
        """
        query = require_subject_or_dossier(sujet, dossier)
        sample = await gather.sample_from_query(
            self.client,
            query,
            max_scrutins,
            kind=KIND_VALUES[type_scrutin],
            legislature=legislature,
        )
        if not sample.chosen:
            return format_no_scrutin(query)
        details, abbreviations = await self._details_and_abbreviations(sample.chosen, legislature)
        rows = stats.group_stances(details, abbreviations)
        method = positions_method(sample, len(rows), max_scrutins, legislature)
        return render.render_positions(rows, group_names(rows), method)

    @analytics_tool
    async def accords_entre_groupes(
        self,
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = DEFAULT_ANALYSED_SCRUTINS,
        type_scrutin: KindParameter = "tous",
        legislature: AnalysisLegislature = None,
    ) -> str:
        """Taux d'accord entre groupes parlementaires, deux à deux, sur un échantillon de scrutins.

        À utiliser pour une vue d'ensemble des convergences entre groupes : pour chaque paire, part
        des scrutins où les deux groupes ont la même position majoritaire. Indiquer `sujet` ou
        `periode_jours` (30 au plus). Calculé sur un échantillon borné, annoncé dans la méthode.
        Pour une législature close (`legislature`, 14 à 16), la période finit à son dernier scrutin.
        """
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, type_scrutin, legislature=legislature
        )
        details, abbreviations = await self._details_and_abbreviations(
            selection.sample.chosen, legislature
        )
        rows = stats.group_stances(details, abbreviations)
        method = selection_method(
            selection,
            len(rows),
            counted=(
                "pour chaque paire de groupes, scrutins où les deux ont une position majoritaire "
                "nette (pas d'égalité) ; accord = même position."
            ),
            limits=[
                "un accord sur un amendement ou un article n'est pas un accord sur un texte ;",
                "l'échantillon peut comporter beaucoup d'amendements ;",
                breakdown_limit(legislature),
            ],
            legislature=legislature,
        )
        pairs = stats.agreements(rows)
        method = method.model_copy(
            update={"warnings": [*method.warnings, *thin_pairs_warnings(pairs)]}
        )
        return render.render_agreements(pairs, group_names(rows), method)

    @analytics_tool
    async def cohesion_groupes(
        self,
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = DEFAULT_ANALYSED_SCRUTINS,
        type_scrutin: KindParameter = "tous",
        legislature: AnalysisLegislature = None,
    ) -> str:
        """Part des votes de chaque groupe qui suivent sa position majoritaire.

        À utiliser pour mesurer l'homogénéité des votes au sein de chaque groupe sur un sujet ou
        une période : part des votes exprimés (pour, contre, abstention) conformes à la position
        majoritaire du groupe, calculée sur un échantillon borné de scrutins. Pour une
        législature close (`legislature`, 14 à 16), la période finit à son dernier scrutin.
        """
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, type_scrutin, legislature=legislature
        )
        details, abbreviations = await self._details_and_abbreviations(
            selection.sample.chosen, legislature
        )
        method = selection_method(
            selection,
            len(details),
            counted=(
                "sur chaque scrutin, votes exprimés des membres du groupe (pour, contre, "
                "abstention) ; alignés = votes identiques à la position la plus fréquente."
            ),
            limits=[
                "les non-votants et absents ne sont pas comptés ;",
                "un vote différent de la majorité du groupe peut être autorisé ou annoncé ;",
                breakdown_limit(legislature),
            ],
            legislature=legislature,
        )
        return render.render_cohesion(stats.cohesion(details, abbreviations), method)

    async def _details_and_abbreviations(
        self, chosen: list[ScrutinSummary], legislature: int | None
    ) -> tuple[list[Scrutin], dict[str, str]]:
        """Détail des scrutins choisis et correspondance identifiant de groupe vers sigle."""
        return await asyncio.gather(
            gather.fetch_details(self.client, chosen),
            lookup.groupe_abbreviations(self.client, legislature),
        )


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'analyse des groupes."""
    GroupeAnalyses(client).register(mcp)
