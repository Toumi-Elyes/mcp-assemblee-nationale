"""Calculs sur les positions des groupes : majorité, accords, cohésion et résultats serrés."""

from collections import Counter
from collections.abc import Mapping, Sequence

from assemblee_mcp.analytics.models import (
    CloseVote,
    GroupCohesion,
    GroupStances,
    PairAgreement,
    Stance,
)
from assemblee_mcp.analytics.stats.shared import ordinal, scrutin_ref
from assemblee_mcp.civix.models import (
    Scrutin,
    VoteCounts,
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
