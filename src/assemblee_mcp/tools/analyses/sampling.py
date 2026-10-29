"""Constitution des échantillons de scrutins analysés en détail."""

from dataclasses import dataclass
from datetime import date, timedelta

from assemblee_mcp.analytics import gather
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.tools.analyses.parameters import (
    KIND_VALUES,
    KindName,
    require_subject_or_period,
)
from assemblee_mcp.tools.periods import describe_period


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


async def sample_period(
    client: CivixClient, days: int, count: int, kind: KindName
) -> tuple[gather.Sample, date, date]:
    """Échantillon régulier de scrutins des `days` derniers jours, avec les bornes de la période."""
    end = gather.current_day()
    start = end - timedelta(days=days)
    sample, _ = await gather.sample_from_period(
        client, days, count, today=end, kind=KIND_VALUES[kind]
    )
    return sample, start, end


@dataclass(frozen=True)
class SelectedSample:
    """Échantillon choisi par `sujet` ou `periode_jours`, avec sa période et ses notes."""

    sample: gather.Sample
    period: str | None
    notes: list[str]


async def select_sample(
    client: CivixClient,
    subject: str | None,
    days: int | None,
    count: int,
    kind: KindName,
) -> SelectedSample:
    """Échantillon des scrutins d'un sujet (les plus récents) ou d'une période (régulier)."""
    require_subject_or_period(subject, days)
    if days is not None:
        sample, start, end = await sample_period(client, days, count, kind)
        notes = sample_notes(sample, count, regular=True)
        return SelectedSample(sample, describe_period(start, end), notes)
    sample = await gather.sample_from_query(client, str(subject), count, kind=KIND_VALUES[kind])
    return SelectedSample(sample, None, sample_notes(sample, count, regular=False))
