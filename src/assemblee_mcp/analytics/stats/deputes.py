"""Calculs sur les votes de députés nommés : répartition, alignement sur le groupe, comparaison."""

from collections import Counter
from collections.abc import Sequence

from assemblee_mcp.analytics.models import (
    DeputeBilan,
    DeputeComparison,
    Stance,
)
from assemblee_mcp.analytics.stats.groups import stance
from assemblee_mcp.civix.models import (
    Position,
    ScrutinVotes,
)

EXPRESSED = (Position.POUR, Position.CONTRE, Position.ABSTENTION)


def vote_of(votes: ScrutinVotes, deputy_uid: str) -> tuple[Position, bool] | None:
    """Position (et délégation) d'un député dans un scrutin ; `None` s'il n'y figure pas."""
    for vote in votes.votes:
        if vote.deputy_uid == deputy_uid:
            return vote.position, vote.par_delegation
    return None


def deputy_present(votes: ScrutinVotes, deputy_uid: str) -> bool:
    """Vrai si le député figure dans la liste des votes du scrutin."""
    return vote_of(votes, deputy_uid) is not None


def expressed_by(votes: ScrutinVotes, deputy_uid: str) -> bool:
    """Vrai si le député a exprimé un vote (pour, contre ou abstention) sur le scrutin."""
    found = vote_of(votes, deputy_uid)
    return found is not None and found[0] in EXPRESSED


def both_expressed(votes: ScrutinVotes, uid_a: str, uid_b: str) -> bool:
    """Vrai si les deux députés ont exprimé un vote sur le scrutin : il est comparable."""
    return expressed_by(votes, uid_a) and expressed_by(votes, uid_b)


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
