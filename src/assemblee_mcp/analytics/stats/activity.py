"""Calculs sur l'activité de vote : tendances, classement des textes, chronologie d'un dossier."""

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from datetime import date, timedelta

from assemblee_mcp.analytics.models import (
    DayVolume,
    DossierTimeline,
    Rate,
    TextActivity,
    TimelineEntry,
    Trends,
    WeekVolume,
)
from assemblee_mcp.analytics.stats.shared import UNKNOWN_LABEL, day_of, result_text
from assemblee_mcp.civix.models import (
    ScrutinSummary,
)
from assemblee_mcp.civix.models.kinds import KIND_AMENDEMENT, KIND_ARTICLE, KIND_ENSEMBLE

NO_DOSSIER_LABEL = "Scrutins sans dossier législatif"


BUSIEST_DAYS = 5


MAX_OTHER_DOSSIERS = 5


def make_rate(label: str, items: Sequence[ScrutinSummary]) -> Rate:
    """Effectifs d'une catégorie de scrutins."""
    adopted = sum(1 for item in items if item.adopted is True)
    rejected = sum(1 for item in items if item.adopted is False)
    return Rate(label=label, total=len(items), adopted=adopted, rejected=rejected)


def rate_table(
    items: Iterable[ScrutinSummary], key: Callable[[ScrutinSummary], str | None]
) -> list[Rate]:
    """Effectifs et part d'adoption par catégorie, de la plus fréquente à la moins fréquente."""
    groups: dict[str, list[ScrutinSummary]] = {}
    for item in items:
        groups.setdefault(key(item) or UNKNOWN_LABEL, []).append(item)
    rows = [make_rate(label, members) for label, members in groups.items()]
    return sorted(rows, key=lambda row: (-row.total, row.label))


def monday_of(day: date) -> date:
    """Lundi de la semaine d'un jour."""
    return day - timedelta(days=day.weekday())


def weekly_volumes(items: Iterable[ScrutinSummary]) -> list[WeekVolume]:
    """Nombre de scrutins par semaine, de la plus ancienne à la plus récente."""
    totals: Counter[date] = Counter()
    adopted: Counter[date] = Counter()
    for item in items:
        day = day_of(item)
        if day is None:
            continue
        week = monday_of(day)
        totals[week] += 1
        adopted[week] += 1 if item.adopted is True else 0
    return [
        WeekVolume(week_start=week, scrutins=totals[week], adopted=adopted[week])
        for week in sorted(totals)
    ]


def busiest_days(items: Iterable[ScrutinSummary], limit: int = BUSIEST_DAYS) -> list[DayVolume]:
    """Jours comptant le plus de scrutins (à égalité, le plus récent d'abord)."""
    counts = Counter(day for item in items if (day := day_of(item)) is not None)
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], -pair[0].toordinal()))
    return [DayVolume(day=day, scrutins=count) for day, count in ranked[:limit]]


def in_period(items: Iterable[ScrutinSummary], start: date, end: date) -> list[ScrutinSummary]:
    """Scrutins dont le jour est compris entre `start` et `end` inclus."""
    return [item for item in items if (day := day_of(item)) is not None and start <= day <= end]


def trends(items: Sequence[ScrutinSummary], start: date, end: date) -> Trends:
    """Tendances générales sur une période (les scrutins doivent déjà être filtrés)."""
    return Trends(
        start=start,
        end=end,
        total=len(items),
        overall=make_rate("Tous les scrutins", items),
        weeks=weekly_volumes(items),
        by_type=rate_table(items, lambda item: item.kind),
        by_context=rate_table(items, lambda item: item.context),
        busiest_days=busiest_days(items),
    )


def dossier_key(item: ScrutinSummary) -> str:
    """Clé de regroupement par dossier législatif."""
    return item.dossier_ref or item.dossier_libelle or NO_DOSSIER_LABEL


def text_activity(items: Sequence[ScrutinSummary]) -> TextActivity:
    """Activité de vote d'un ensemble de scrutins d'un même dossier."""
    first = items[0]
    days = [day for item in items if (day := day_of(item)) is not None]
    kinds = Counter(item.kind for item in items)
    rate = make_rate("", items)
    return TextActivity(
        dossier_ref=first.dossier_ref,
        libelle=first.dossier_libelle or NO_DOSSIER_LABEL,
        context=first.context,
        scrutins=len(items),
        adopted=rate.adopted,
        rejected=rate.rejected,
        amendements=kinds[KIND_AMENDEMENT],
        articles=kinds[KIND_ARTICLE],
        ensemble=kinds[KIND_ENSEMBLE],
        last_date=max(days) if days else None,
    )


def rank_texts(items: Iterable[ScrutinSummary]) -> list[TextActivity]:
    """Dossiers classés par nombre de scrutins (puis par dernière activité)."""
    groups: dict[str, list[ScrutinSummary]] = {}
    for item in items:
        groups.setdefault(dossier_key(item), []).append(item)
    rows = [text_activity(members) for members in groups.values()]
    return sorted(
        rows, key=lambda row: (-row.scrutins, -(row.last_date.toordinal() if row.last_date else 0))
    )


def timeline_entry(item: ScrutinSummary) -> TimelineEntry:
    """Entrée de chronologie."""
    return TimelineEntry(
        uid=item.uid,
        numero=item.numero,
        day=day_of(item),
        kind=item.kind,
        result=result_text(item),
        title=item.titre,
    )


def chronological(items: Iterable[ScrutinSummary]) -> list[ScrutinSummary]:
    """Scrutins du plus ancien au plus récent."""
    return sorted(items, key=lambda item: (day_of(item) or date.min, item.numero or 0))


def dossier_timeline(
    items: Sequence[ScrutinSummary], others: Sequence[TextActivity]
) -> DossierTimeline:
    """Chronologie des scrutins d'un dossier ; amendements comptés, autres scrutins listés."""
    ordered = chronological(items)
    amendments = [item for item in ordered if item.kind == KIND_AMENDEMENT]
    listed = [item for item in ordered if item.kind != KIND_AMENDEMENT]
    entries = [timeline_entry(item) for item in listed]
    first = ordered[0]
    return DossierTimeline(
        dossier_ref=first.dossier_ref,
        libelle=first.dossier_libelle or NO_DOSSIER_LABEL,
        context=first.context,
        total=len(ordered),
        amendements=make_rate("amendements", amendments),
        entries=entries,
        final_votes=[entry for entry in entries if entry.kind == KIND_ENSEMBLE],
        other_dossiers=list(others)[:MAX_OTHER_DOSSIERS],
    )
