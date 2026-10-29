"""Calculs purs sur les scrutins : tendances, classements de textes, positions de groupes."""

from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date, timedelta

from assemblee_mcp.analytics.models import (
    CloseVote,
    DayVolume,
    DeputeBilan,
    DeputeComparison,
    DossierTimeline,
    GroupCohesion,
    GroupStances,
    PairAgreement,
    Rate,
    ScrutinRef,
    Stance,
    TextActivity,
    TimelineEntry,
    Trends,
    WeekVolume,
)
from assemblee_mcp.civix.models import (
    Position,
    Scrutin,
    ScrutinDetail,
    ScrutinSummary,
    ScrutinVotes,
    VoteCounts,
)

UNKNOWN_LABEL = "non précisé"
NO_DOSSIER_LABEL = "Scrutins sans dossier législatif"
TYPE_AMENDEMENT = "amendement"
TYPE_ARTICLE = "article"
TYPE_ENSEMBLE = "texte"
BUSIEST_DAYS = 5
MAX_OTHER_DOSSIERS = 5
EXPRESSED = (Position.POUR, Position.CONTRE, Position.ABSTENTION)


def day_of(scrutin: ScrutinSummary | ScrutinDetail) -> date | None:
    """Jour du scrutin."""
    return scrutin.date_scrutin.date() if scrutin.date_scrutin else None


def result_text(scrutin: ScrutinSummary) -> str:
    """Résultat en un mot : adopté, rejeté ou non précisé."""
    adopted = scrutin.adopted
    if adopted is None:
        return UNKNOWN_LABEL
    return "adopté" if adopted else "rejeté"


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


def ordinal(day: date | None) -> int:
    """Numéro de jour d'une date (0 si absente), pour trier."""
    return day.toordinal() if day else 0


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
        WeekVolume(week_start=w, scrutins=totals[w], adopted=adopted[w]) for w in sorted(totals)
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
        by_type=rate_table(items, lambda item: item.type),
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
    kinds = Counter(item.type for item in items)
    rate = make_rate("", items)
    return TextActivity(
        dossier_ref=first.dossier_ref,
        libelle=first.dossier_libelle or NO_DOSSIER_LABEL,
        context=first.context,
        scrutins=len(items),
        adopted=rate.adopted,
        rejected=rate.rejected,
        amendements=kinds[TYPE_AMENDEMENT],
        articles=kinds[TYPE_ARTICLE],
        ensemble=kinds[TYPE_ENSEMBLE],
        last_date=max(days) if days else None,
    )


def rank_texts(items: Iterable[ScrutinSummary]) -> list[TextActivity]:
    """Dossiers classés par nombre de scrutins (puis par dernière activité)."""
    groups: dict[str, list[ScrutinSummary]] = {}
    for item in items:
        groups.setdefault(dossier_key(item), []).append(item)
    rows = [text_activity(members) for members in groups.values()]
    return sorted(
        rows, key=lambda r: (-r.scrutins, -(r.last_date.toordinal() if r.last_date else 0))
    )


def timeline_entry(item: ScrutinSummary) -> TimelineEntry:
    """Entrée de chronologie."""
    return TimelineEntry(
        uid=item.uid,
        numero=item.numero,
        day=day_of(item),
        kind=item.type or UNKNOWN_LABEL,
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
    amendments = [item for item in ordered if item.type == TYPE_AMENDEMENT]
    listed = [item for item in ordered if item.type != TYPE_AMENDEMENT]
    entries = [timeline_entry(item) for item in listed]
    first = ordered[0]
    return DossierTimeline(
        dossier_ref=first.dossier_ref,
        libelle=first.dossier_libelle or NO_DOSSIER_LABEL,
        context=first.context,
        total=len(ordered),
        amendements=make_rate("amendements", amendments),
        entries=entries,
        final_votes=[entry for entry in entries if entry.kind == TYPE_ENSEMBLE],
        other_dossiers=list(others)[:MAX_OTHER_DOSSIERS],
    )


def scrutin_ref(scrutin: ScrutinDetail) -> ScrutinRef:
    """Référence courte d'un scrutin détaillé."""
    return ScrutinRef(
        uid=scrutin.uid,
        numero=scrutin.numero,
        day=day_of(scrutin),
        title=scrutin.titre,
        result=(scrutin.result_label or UNKNOWN_LABEL),
    )


def stance(counts: VoteCounts) -> Stance | None:
    """Position majoritaire d'un groupe ; `PARTAGE` en cas d'égalité, `None` sans vote exprimé."""
    ranked = sorted(
        (
            (counts.pour, Stance.POUR),
            (counts.contre, Stance.CONTRE),
            (counts.abstention, Stance.ABSTENTION),
        ),
        key=lambda pair: -pair[0],
    )
    top, label = ranked[0]
    if top == 0:
        return None
    if ranked[1][0] == top:
        return Stance.PARTAGE
    return label


def expressed(counts: VoteCounts) -> int:
    """Nombre de votes exprimés (pour, contre, abstention)."""
    return counts.pour + counts.contre + counts.abstention


def group_stances(
    scrutins: Sequence[Scrutin], abbreviations: Mapping[str, str]
) -> list[GroupStances]:
    """Position majoritaire de chaque groupe sur chaque scrutin."""
    rows: list[GroupStances] = []
    for scrutin in scrutins:
        stances = {
            abbreviations.get(group.groupe_uid, group.groupe_uid): stance(group)
            for group in scrutin.results_by_group
        }
        rows.append(GroupStances(scrutin=scrutin_ref(scrutin.scrutin), stances=stances))
    return rows


def agreements(rows: Sequence[GroupStances]) -> list[PairAgreement]:
    """Accord entre groupes, deux à deux, sur les scrutins où chacun a une position nette."""
    shared: Counter[tuple[str, str]] = Counter()
    agreed: Counter[tuple[str, str]] = Counter()
    for row in rows:
        clear = sorted(
            (name, value)
            for name, value in row.stances.items()
            if value is not None and value is not Stance.PARTAGE
        )
        for index, (name_a, stance_a) in enumerate(clear):
            for name_b, stance_b in clear[index + 1 :]:
                shared[(name_a, name_b)] += 1
                agreed[(name_a, name_b)] += 1 if stance_a == stance_b else 0
    return [
        PairAgreement(group_a=a, group_b=b, shared=count, agreed=agreed[(a, b)])
        for (a, b), count in sorted(shared.items())
    ]


def cohesion(scrutins: Sequence[Scrutin], abbreviations: Mapping[str, str]) -> list[GroupCohesion]:
    """Part des votes exprimés de chaque groupe conformes à sa position majoritaire."""
    scrutin_count: Counter[str] = Counter()
    expressed_count: Counter[str] = Counter()
    aligned_count: Counter[str] = Counter()
    for scrutin in scrutins:
        for group in scrutin.results_by_group:
            total = expressed(group)
            if total == 0:
                continue
            name = abbreviations.get(group.groupe_uid, group.groupe_uid)
            scrutin_count[name] += 1
            expressed_count[name] += total
            aligned_count[name] += max(group.pour, group.contre, group.abstention)
    return [
        GroupCohesion(
            group=name,
            scrutins=scrutin_count[name],
            expressed=expressed_count[name],
            aligned=aligned_count[name],
        )
        for name in sorted(scrutin_count)
    ]


def close_votes(scrutins: Sequence[Scrutin], max_margin: int) -> list[CloseVote]:
    """Scrutins dont l'écart entre pour et contre est au plus `max_margin`, du plus serré."""
    rows = [
        CloseVote(
            scrutin=scrutin_ref(scrutin.scrutin),
            pour=scrutin.results_global.pour,
            contre=scrutin.results_global.contre,
            abstention=scrutin.results_global.abstention,
        )
        for scrutin in scrutins
        if scrutin.results_global is not None
    ]
    kept = [row for row in rows if row.margin <= max_margin]
    return sorted(kept, key=lambda row: (row.margin, -ordinal(row.scrutin.day)))


def evenly_spaced[Item](items: Sequence[Item], count: int) -> list[Item]:
    """`count` éléments régulièrement répartis (ordre conservé) ; tous si `count` suffit."""
    if count >= len(items):
        return list(items)
    if count <= 0:
        return []
    step = len(items) / count
    return [items[int(index * step)] for index in range(count)]


def vote_of(votes: ScrutinVotes, deputy_uid: str) -> tuple[Position, bool] | None:
    """Position (et délégation) d'un député dans un scrutin ; `None` s'il n'y figure pas."""
    for vote in votes.votes:
        if vote.deputy_uid == deputy_uid:
            return vote.position, vote.par_delegation
    return None


def group_stance_of(votes: ScrutinVotes, group_uid: str | None) -> Stance | None:
    """Position majoritaire d'un groupe, d'après la ventilation d'un scrutin."""
    if group_uid is None:
        return None
    for group in votes.results_by_group:
        if group.groupe_uid == group_uid:
            return stance(group)
    return None


def stance_matches(position: Position, majority: Stance | None) -> bool | None:
    """Compare un vote exprimé à la position majoritaire ; `None` si non comparable."""
    if position not in EXPRESSED or majority is None or majority is Stance.PARTAGE:
        return None
    return majority.value == position.value


def depute_bilan(
    name: str,
    deputy_uid: str,
    group_uid: str | None,
    group_abbr: str | None,
    sample: Sequence[ScrutinVotes],
) -> DeputeBilan:
    """Positions d'un député et alignement sur la position majoritaire de son groupe."""
    counts: Counter[Position] = Counter()
    absent = delegated = comparable = aligned = 0
    for votes in sample:
        found = vote_of(votes, deputy_uid)
        if found is None:
            absent += 1
            continue
        position, by_delegation = found
        counts[position] += 1
        delegated += 1 if by_delegation else 0
        match = stance_matches(position, group_stance_of(votes, group_uid))
        if match is not None:
            comparable += 1
            aligned += 1 if match else 0
    return DeputeBilan(
        name=name,
        group=group_abbr,
        scrutins=len(sample),
        pour=counts[Position.POUR],
        contre=counts[Position.CONTRE],
        abstention=counts[Position.ABSTENTION],
        non_votant=counts[Position.NON_VOTANT] + counts[Position.UNKNOWN],
        absent=absent,
        by_delegation=delegated,
        comparable=comparable,
        aligned=aligned,
    )


def compare_deputes(
    name_a: str,
    uid_a: str,
    name_b: str,
    uid_b: str,
    sample: Sequence[ScrutinVotes],
) -> DeputeComparison:
    """Accord entre deux députés sur les scrutins où tous deux ont exprimé un vote."""
    shared = agreed = only_a = only_b = 0
    for votes in sample:
        a = vote_of(votes, uid_a)
        b = vote_of(votes, uid_b)
        expressed_a = a is not None and a[0] in EXPRESSED
        expressed_b = b is not None and b[0] in EXPRESSED
        only_a += 1 if expressed_a and not expressed_b else 0
        only_b += 1 if expressed_b and not expressed_a else 0
        if a is not None and b is not None and expressed_a and expressed_b:
            shared += 1
            agreed += 1 if a[0] == b[0] else 0
    return DeputeComparison(
        name_a=name_a,
        name_b=name_b,
        scrutins=len(sample),
        shared=shared,
        agreed=agreed,
        only_a=only_a,
        only_b=only_b,
    )
