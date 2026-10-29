"""Outils d'analyse des groupes parlementaires : positions, accords et cohésion."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.models import GroupStances, Method
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Scrutin, ScrutinSummary
from assemblee_mcp.formatting import format_no_scrutin
from assemblee_mcp.limits import ANALYTICS_DEADLINE_SECONDS, ANALYTICS_MAX_CALLS
from assemblee_mcp.tools.analyses.parameters import (
    KIND_VALUES,
    DossierReference,
    KindParameter,
    MaxScrutins,
    OptionalSamplePeriodDays,
    OptionalSubject,
    require_subject_or_dossier,
)
from assemblee_mcp.tools.analyses.sampling import SelectedSample, sample_notes, select_sample
from assemblee_mcp.tools.common import ToolFunction, ToolSet, limited

analytics_tool = limited(ANALYTICS_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)
DEFAULT_POSITIONS_SCRUTINS = 15


def group_names(rows: list[GroupStances]) -> list[str]:
    """Sigles de groupes présents, par ordre alphabétique."""
    return sorted({name for row in rows for name in row.stances})


def selection_method(
    selection: SelectedSample, analysed: int, *, counted: str, limits: list[str]
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
    )


def positions_method(sample: gather.Sample, analysed: int, max_scrutins: int) -> Method:
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
            "les décomptes par groupe sont ceux publiés par CIVIX pour chaque scrutin.",
        ],
        notes=sample_notes(sample, max_scrutins, regular=False),
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
            int, Field(ge=3, le=30, description="Scrutins analysés.")
        ] = DEFAULT_POSITIONS_SCRUTINS,
        type_scrutin: KindParameter = "tous",
    ) -> str:
        """Tableau des positions majoritaires de chaque groupe sur les scrutins d'un sujet.

        À utiliser pour voir d'un coup d'œil comment les groupes parlementaires ont voté sur un
        thème ou un texte : pour chaque scrutin correspondant, la position majoritaire de chaque
        groupe (pour, contre, abstention, ou partagée). Indiquer `sujet` ou `dossier`.
        """
        query = require_subject_or_dossier(sujet, dossier)
        sample = await gather.sample_from_query(
            self.client, query, max_scrutins, kind=KIND_VALUES[type_scrutin]
        )
        if not sample.chosen:
            return format_no_scrutin(query)
        details, abbreviations = await self._details_and_abbreviations(sample.chosen)
        rows = stats.group_stances(details, abbreviations)
        method = positions_method(sample, len(rows), max_scrutins)
        return render.render_positions(rows, group_names(rows), method)

    @analytics_tool
    async def accords_entre_groupes(
        self,
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = 30,
        type_scrutin: KindParameter = "tous",
    ) -> str:
        """Taux d'accord entre groupes parlementaires, deux à deux, sur un échantillon de scrutins.

        À utiliser pour une vue d'ensemble des convergences entre groupes : pour chaque paire, part
        des scrutins où les deux groupes ont la même position majoritaire. Indiquer `sujet` ou
        `periode_jours` (30 au plus). Calculé sur un échantillon borné, annoncé dans la méthode.
        """
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, type_scrutin
        )
        details, abbreviations = await self._details_and_abbreviations(selection.sample.chosen)
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
                "l'échantillon peut comporter beaucoup d'amendements.",
            ],
        )
        return render.render_agreements(stats.agreements(rows), group_names(rows), method)

    @analytics_tool
    async def cohesion_groupes(
        self,
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = 30,
        type_scrutin: KindParameter = "tous",
    ) -> str:
        """Part des votes de chaque groupe qui suivent sa position majoritaire.

        À utiliser pour mesurer l'homogénéité des votes au sein de chaque groupe sur un sujet ou
        une période : part des votes exprimés (pour, contre, abstention) conformes à la position
        majoritaire du groupe, calculée sur un échantillon borné de scrutins.
        """
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, type_scrutin
        )
        details, abbreviations = await self._details_and_abbreviations(selection.sample.chosen)
        method = selection_method(
            selection,
            len(details),
            counted=(
                "sur chaque scrutin, votes exprimés des membres du groupe (pour, contre, "
                "abstention) ; alignés = votes identiques à la position la plus fréquente."
            ),
            limits=[
                "les non-votants et absents ne sont pas comptés ;",
                "un vote différent de la majorité du groupe peut être autorisé ou annoncé.",
            ],
        )
        return render.render_cohesion(stats.cohesion(details, abbreviations), method)

    async def _details_and_abbreviations(
        self, chosen: list[ScrutinSummary]
    ) -> tuple[list[Scrutin], dict[str, str]]:
        """Détail des scrutins choisis et correspondance identifiant de groupe vers sigle."""
        return await asyncio.gather(
            gather.fetch_details(self.client, chosen), lookup.groupe_abbreviations(self.client)
        )


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'analyse des groupes."""
    GroupeAnalyses(client).register(mcp)
