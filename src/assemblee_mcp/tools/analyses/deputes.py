"""Outils d'analyse de députés nommés : répartition des votes et comparaison."""

import asyncio
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.analytics import gather, render, stats
from assemblee_mcp.analytics.models import Method
from assemblee_mcp.analytics.stats import spread_order
from assemblee_mcp.analytics.stats.deputes import both_expressed, deputy_present
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.archive import ARCHIVED_LEGISLATURES, UNTITLED_LEGISLATURES
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Depute
from assemblee_mcp.limits import (
    ANALYTICS_DEADLINE_SECONDS,
    ANALYTICS_MAX_CALLS,
    MAX_ANALYSED_SCRUTINS,
    TARGET_USABLE_SCRUTINS,
)
from assemblee_mcp.tools.analyses.parameters import (
    MaxScrutins,
    OptionalSamplePeriodDays,
    OptionalSubject,
    require_subject_or_period,
)
from assemblee_mcp.tools.analyses.sampling import (
    SelectedSample,
    select_sample,
    small_sample_warnings,
)
from assemblee_mcp.tools.common import DeputeLegislature, ToolFunction, ToolSet, limited
from assemblee_mcp.tools.resolution import resolve_depute

analytics_tool = limited(ANALYTICS_MAX_CALLS, ANALYTICS_DEADLINE_SECONDS)

DeputeNameA = Annotated[
    str, Field(description="Nom du premier député ou son `uid`.", min_length=2, max_length=100)
]
DeputeNameB = Annotated[
    str, Field(description="Nom du second député ou son `uid`.", min_length=2, max_length=100)
]


def group_uid_of(abbreviations: dict[str, str], abbr: str | None) -> str | None:
    """Identifiant d'un groupe à partir de son sigle."""
    if abbr is None:
        return None
    return next((uid for uid, name in abbreviations.items() if name == abbr), None)


def usable_notes(scan: gather.VotesScan, noun: str) -> tuple[list[str], list[str]]:
    """Notes et avertissements sur les scrutins exploitables d'une lecture de votes."""
    notes = [f"{scan.usable} scrutin(s) {noun} sur {len(scan.votes)} examiné(s)."]
    if scan.stopped_by_budget:
        notes.append("Lecture arrêtée par le plafond d'appels : scrutins restants non lus.")
    return notes, small_sample_warnings(scan.usable, f"scrutin(s) {noun}")


def depute_method(
    selection: SelectedSample,
    scan: gather.VotesScan,
    *,
    noun: str,
    counted: str,
    limits: list[str],
    legislature: int | None = None,
) -> Method:
    """Méthode d'une analyse de député(s) sur un échantillon de scrutins."""
    sample = selection.sample
    notes, warnings = usable_notes(scan, noun)
    return Method(
        period=selection.period,
        analysed=len(scan.votes),
        matching=sample.matching,
        truncated=sample.truncated or scan.stopped_by_budget,
        counted=counted,
        limits=limits,
        notes=[*selection.notes, *notes],
        warnings=warnings,
        legislature=legislature,
    )


def group_limits(legislature: int | None) -> list[str]:
    """Limites sur le groupe retenu pour comparer le député à la position de son groupe."""
    if legislature in UNTITLED_LEGISLATURES:
        return [
            f"pour la {legislature}e législature, CIVIX ne fournit pas le décompte par groupe : "
            "l'alignement sur le groupe n'est pas calculable ;"
        ]
    if legislature in ARCHIVED_LEGISLATURES:
        return [
            f"le groupe retenu est le dernier groupe connu du député dans la {legislature}e "
            "législature (il a pu changer de groupe en cours de route) ;"
        ]
    return ["le groupe retenu est le groupe actuel du député ;"]


def bilan_method(
    selection: SelectedSample, scan: gather.VotesScan, legislature: int | None
) -> Method:
    """Méthode de `bilan_depute`."""
    return depute_method(
        selection,
        scan,
        noun="où le député figure dans la liste des votes",
        counted=(
            "position du député dans la liste des votes de chaque scrutin ; « absent de la "
            "liste » = aucun vote enregistré pour lui ; alignement = vote exprimé identique à "
            "la position majoritaire de son groupe (scrutins sans position nette exclus)."
        ),
        limits=[
            "l'absence d'un vote enregistré ne dit rien de l'intérêt du député pour le sujet "
            "(liste CIVIX tirée des données ouvertes de l'Assemblée) ;",
            "un vote par délégation est enregistré au nom du député ;",
            *group_limits(legislature),
            "échantillon borné : ne pas généraliser à l'ensemble de l'activité du député.",
        ],
        legislature=legislature,
    )


def comparison_method(
    selection: SelectedSample, scan: gather.VotesScan, legislature: int | None
) -> Method:
    """Méthode de `comparer_deputes`."""
    return depute_method(
        selection,
        scan,
        noun="comparables (les deux ont voté)",
        counted=(
            "scrutins où les deux députés ont exprimé un vote (pour, contre, abstention) ; "
            "accord = même position."
        ),
        limits=[
            "les scrutins où l'un des deux est absent ou non-votant sont exclus ;",
            "un accord sur un amendement ou un article n'est pas un accord sur un texte ;",
            "échantillon borné, sans valeur de classement.",
        ],
        legislature=legislature,
    )


class DeputeAnalyses(ToolSet):
    """Analyses de votes de députés nommés, jamais de classement."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.bilan_depute, self.comparer_deputes)

    @analytics_tool
    async def bilan_depute(
        self,
        depute: Annotated[
            str,
            Field(
                description="Nom d'UN député (« Jérôme Guedj ») ou son `uid`.",
                min_length=2,
                max_length=100,
            ),
        ],
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = MAX_ANALYSED_SCRUTINS,
        legislature: DeputeLegislature = None,
    ) -> str:
        """Répartition des votes d'UN député sur un échantillon et alignement sur son groupe.

        Donne le nombre de pour, contre, abstentions, non-votants et scrutins absents de la liste
        des votes, ainsi que la part de votes conformes à la position majoritaire de son groupe.
        Indiquer `sujet` ou `periode_jours`. Sert à décrire, jamais à classer ou juger un député.
        """
        require_subject_or_period(sujet, periode_jours)
        found = await resolve_depute(self.client, depute, legislature)
        if isinstance(found, str):
            return found
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, "tous", legislature=legislature
        )
        scan, abbreviations = await asyncio.gather(
            gather.scan_votes(
                self.client,
                spread_order(selection.sample.chosen),
                lambda votes: deputy_present(votes, found.uid),
                TARGET_USABLE_SCRUTINS,
            ),
            lookup.groupe_abbreviations(self.client, found.legislature),
        )
        group_uid = found.groupe_uid or group_uid_of(abbreviations, found.groupe_abrev)
        result = stats.depute_bilan(
            found.full_name, found.uid, group_uid, found.groupe_abrev, scan.votes
        )
        method = bilan_method(selection, scan, found.legislature)
        return render.render_bilan(result, method)

    @analytics_tool
    async def comparer_deputes(
        self,
        depute_a: DeputeNameA,
        depute_b: DeputeNameB,
        *,
        sujet: OptionalSubject = None,
        periode_jours: OptionalSamplePeriodDays = None,
        max_scrutins: MaxScrutins = MAX_ANALYSED_SCRUTINS,
        legislature: DeputeLegislature = None,
    ) -> str:
        """Compare les votes de DEUX députés nommés : part de scrutins votés de la même façon.

        À utiliser pour « X et Y votent-ils pareil ? ». Calcule, sur les scrutins où les deux ont
        exprimé un vote, la part de positions identiques. Indiquer `sujet` ou `periode_jours`.
        Description factuelle d'un échantillon borné, sans jugement.
        """
        require_subject_or_period(sujet, periode_jours)
        first, second = await asyncio.gather(
            resolve_depute(self.client, depute_a, legislature),
            resolve_depute(self.client, depute_b, legislature),
        )
        if not isinstance(first, Depute):
            return first
        if not isinstance(second, Depute):
            return second
        selection = await select_sample(
            self.client, sujet, periode_jours, max_scrutins, "tous", legislature=legislature
        )
        scan = await gather.scan_votes(
            self.client,
            spread_order(selection.sample.chosen),
            lambda votes: both_expressed(votes, first.uid, second.uid),
            TARGET_USABLE_SCRUTINS,
        )
        result = stats.compare_deputes(
            first.full_name, first.uid, second.full_name, second.uid, scan.votes
        )
        method = comparison_method(selection, scan, legislature)
        return render.render_comparison(result, method)


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre les outils d'analyse de députés."""
    DeputeAnalyses(client).register(mcp)
