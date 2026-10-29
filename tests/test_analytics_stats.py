from datetime import date

import pytest

from assemblee_mcp.analytics import stats
from assemblee_mcp.analytics.models import Stance
from assemblee_mcp.civix.models import (
    Position,
    ScrutinSummary,
    ScrutinVotes,
    VoteCounts,
)
from tests.conftest import make_item

ABBREVIATIONS = {"G1": "AAA", "G2": "BBB", "G3": "CCC"}


def summary(number: int, day: str, **kwargs: object) -> ScrutinSummary:
    return ScrutinSummary.model_validate(make_item(number, day, **kwargs))  # type: ignore[arg-type]


def groups(**counts: tuple[int, int, int]) -> list[dict[str, object]]:
    return [
        {
            "groupe_uid": uid,
            "pour": pour,
            "contre": contre,
            "abstention": abstention,
            "non_votant": 0,
            "total": pour + contre + abstention,
        }
        for uid, (pour, contre, abstention) in counts.items()
    ]


def scrutin(
    number: int, by_group: list[dict[str, object]], votes: list[dict[str, object]] | None = None
) -> ScrutinVotes:
    total = [sum(int(str(g[key])) for g in by_group) for key in ("pour", "contre", "abstention")]
    return ScrutinVotes.model_validate(
        {
            "scrutin": {
                "uid": f"U{number}",
                "numero": number,
                "date_scrutin": "2026-10-01T00:00:00+00:00",
                "titre": f"scrutin {number}",
                "sort_libelle": "adopté",
            },
            "results_global": {
                "pour": total[0],
                "contre": total[1],
                "abstention": total[2],
                "total": sum(total),
            },
            "results_by_group": by_group,
            "votes": votes or [],
        }
    )


def vote(uid: str, position: str, *, delegated: bool = False) -> dict[str, object]:
    return {
        "deputy_uid": uid,
        "prenom": "A",
        "nom": uid,
        "position": position,
        "par_delegation": delegated,
    }


def test_adopted_property() -> None:
    assert summary(1, "2026-10-01", sort="adopté").adopted is True
    assert summary(2, "2026-10-01", sort="rejeté").adopted is False
    assert summary(3, "2026-10-01", sort="inconnu").adopted is None


def test_rate_table_counts_and_sorts() -> None:
    items = [
        summary(1, "2026-10-01", kind="amendement", sort="adopté"),
        summary(2, "2026-10-01", kind="amendement", sort="rejeté"),
        summary(3, "2026-10-01", kind="amendement", sort="rejeté"),
        summary(4, "2026-10-01", kind="article", sort="adopté"),
    ]
    rows = stats.rate_table(items, lambda item: item.type)
    assert [(r.label, r.total, r.adopted, r.rejected) for r in rows] == [
        ("amendement", 3, 1, 2),
        ("article", 1, 1, 0),
    ]
    assert rows[0].rate == pytest.approx(1 / 3)
    assert stats.make_rate("vide", []).rate is None


def test_rate_table_labels_missing_values() -> None:
    items = [summary(1, "2026-10-01", context=None)]
    assert stats.rate_table(items, lambda item: item.context)[0].label == "non précisé"


def test_weekly_volumes_start_on_monday() -> None:
    items = [
        summary(1, "2026-10-04"),
        summary(2, "2026-10-05", sort="rejeté"),
        summary(3, "2026-10-11"),
    ]
    weeks = stats.weekly_volumes(items)
    assert [(w.week_start, w.scrutins, w.adopted) for w in weeks] == [
        (date(2026, 9, 28), 1, 1),
        (date(2026, 10, 5), 2, 1),
    ]


def test_busiest_days_ties_prefer_recent() -> None:
    items = [
        summary(1, "2026-10-01"),
        summary(2, "2026-10-01"),
        summary(3, "2026-10-02"),
        summary(4, "2026-10-03"),
    ]
    days = stats.busiest_days(items, limit=2)
    assert [(d.day.day, d.scrutins) for d in days] == [(1, 2), (3, 1)]


def test_in_period_is_inclusive() -> None:
    items = [summary(n, f"2026-10-0{n}") for n in (1, 2, 3, 4)]
    kept = stats.in_period(items, date(2026, 10, 2), date(2026, 10, 3))
    assert [i.numero for i in kept] == [2, 3]


def test_trends_aggregate() -> None:
    items = [
        summary(1, "2026-10-01", kind="texte", context="PLF"),
        summary(2, "2026-10-02", kind="amendement", context="PLF", sort="rejeté"),
    ]
    result = stats.trends(items, date(2026, 10, 1), date(2026, 10, 7))
    assert result.total == 2
    assert result.overall.rate == 0.5
    assert [r.label for r in result.by_context] == ["PLF"]
    assert len(result.weeks) == 1


def test_rank_texts_orders_by_scrutin_count_then_recency() -> None:
    items = [
        summary(1, "2026-10-01", dossier_ref="A", dossier="Texte A"),
        summary(2, "2026-10-02", dossier_ref="A", dossier="Texte A", kind="texte"),
        summary(3, "2026-10-05", dossier_ref="B", dossier="Texte B"),
        summary(4, "2026-10-06", dossier_ref="C", dossier="Texte C"),
        summary(5, "2026-10-07", dossier_ref=None),
    ]
    ranked = stats.rank_texts(items)
    assert [r.dossier_ref for r in ranked] == ["A", None, "C", "B"]
    top = ranked[0]
    assert (top.scrutins, top.amendements, top.ensemble) == (2, 1, 1)
    assert top.last_date == date(2026, 10, 2)
    assert ranked[1].libelle == stats.NO_DOSSIER_LABEL


def test_dossier_timeline_counts_amendments_and_highlights_final_vote() -> None:
    items = [
        summary(1, "2026-10-03", kind="texte", sort="adopté"),
        summary(2, "2026-10-01", kind="amendement", sort="rejeté"),
        summary(3, "2026-10-02", kind="article"),
        summary(4, "2026-10-02", kind="amendement"),
    ]
    timeline = stats.dossier_timeline(items, [])
    assert timeline.total == 4
    assert (timeline.amendements.total, timeline.amendements.adopted) == (2, 1)
    assert [e.numero for e in timeline.entries] == [3, 1]
    assert [e.numero for e in timeline.final_votes] == [1]


@pytest.mark.parametrize(
    ("counts", "expected"),
    [
        ((10, 2, 1), Stance.POUR),
        ((1, 7, 2), Stance.CONTRE),
        ((0, 0, 4), Stance.ABSTENTION),
        ((3, 3, 0), Stance.PARTAGE),
        ((0, 0, 0), None),
    ],
)
def test_stance(counts: tuple[int, int, int], expected: Stance | None) -> None:
    pour, contre, abstention = counts
    assert stats.stance(VoteCounts(pour=pour, contre=contre, abstention=abstention)) == expected


def test_group_stances_and_agreements() -> None:
    first = scrutin(1, groups(G1=(10, 0, 0), G2=(8, 1, 0), G3=(0, 5, 0)))
    second = scrutin(2, groups(G1=(0, 9, 0), G2=(4, 4, 0), G3=(0, 5, 1)))
    rows = stats.group_stances([first, second], ABBREVIATIONS)
    assert rows[0].stances == {"AAA": Stance.POUR, "BBB": Stance.POUR, "CCC": Stance.CONTRE}
    assert rows[1].stances["BBB"] is Stance.PARTAGE
    pairs = {(p.group_a, p.group_b): p for p in stats.agreements(rows)}
    assert (pairs[("AAA", "BBB")].shared, pairs[("AAA", "BBB")].agreed) == (1, 1)
    assert (pairs[("AAA", "CCC")].shared, pairs[("AAA", "CCC")].agreed) == (2, 1)
    assert pairs[("AAA", "CCC")].rate == 0.5


def test_unknown_group_uid_is_kept_as_label() -> None:
    rows = stats.group_stances([scrutin(1, groups(ZZ=(3, 0, 0)))], {})
    assert list(rows[0].stances) == ["ZZ"]


def test_cohesion_is_weighted_by_expressed_votes() -> None:
    sample = [
        scrutin(1, groups(G1=(9, 1, 0))),
        scrutin(2, groups(G1=(2, 6, 0), G2=(0, 0, 0))),
    ]
    rows = {r.group: r for r in stats.cohesion(sample, ABBREVIATIONS)}
    assert (rows["AAA"].scrutins, rows["AAA"].expressed, rows["AAA"].aligned) == (2, 18, 15)
    assert rows["AAA"].rate == pytest.approx(15 / 18)
    assert "BBB" not in rows


def test_close_votes_sorted_by_margin_and_filtered() -> None:
    sample = [
        scrutin(1, groups(G1=(100, 90, 0))),
        scrutin(2, groups(G1=(50, 49, 0))),
        scrutin(3, groups(G1=(10, 80, 0))),
    ]
    close = stats.close_votes(sample, 15)
    assert [(c.scrutin.numero, c.margin) for c in close] == [(2, 1), (1, 10)]
    assert stats.close_votes(sample, 0) == []


def test_evenly_spaced() -> None:
    items = list(range(10))
    assert stats.evenly_spaced(items, 5) == [0, 2, 4, 6, 8]
    assert stats.evenly_spaced(items, 20) == items
    assert stats.evenly_spaced(items, 0) == []


def test_depute_bilan_counts_alignment_absence_and_delegation() -> None:
    sample = [
        scrutin(1, groups(G1=(9, 1, 0)), [vote("D1", "pour")]),
        scrutin(2, groups(G1=(9, 1, 0)), [vote("D1", "contre", delegated=True)]),
        scrutin(3, groups(G1=(5, 5, 0)), [vote("D1", "pour")]),
        scrutin(4, groups(G1=(0, 9, 0)), [vote("D1", "non_votant")]),
        scrutin(5, groups(G1=(0, 9, 0)), [vote("D2", "contre")]),
    ]
    bilan = stats.depute_bilan("Anne D1", "D1", "G1", "AAA", sample)
    assert (bilan.pour, bilan.contre, bilan.abstention, bilan.non_votant, bilan.absent) == (
        2,
        1,
        0,
        1,
        1,
    )
    assert bilan.by_delegation == 1
    assert (bilan.comparable, bilan.aligned) == (2, 1)
    assert bilan.alignment_rate == 0.5
    assert bilan.scrutins == 5


def test_depute_bilan_without_group_has_no_alignment() -> None:
    sample = [scrutin(1, groups(G1=(9, 1, 0)), [vote("D1", "pour")])]
    bilan = stats.depute_bilan("Anne D1", "D1", None, None, sample)
    assert bilan.comparable == 0
    assert bilan.alignment_rate is None


def test_compare_deputes() -> None:
    sample = [
        scrutin(1, groups(G1=(1, 0, 0)), [vote("A", "pour"), vote("B", "pour")]),
        scrutin(2, groups(G1=(1, 0, 0)), [vote("A", "pour"), vote("B", "contre")]),
        scrutin(3, groups(G1=(1, 0, 0)), [vote("A", "pour")]),
        scrutin(4, groups(G1=(1, 0, 0)), [vote("A", "non_votant"), vote("B", "contre")]),
    ]
    result = stats.compare_deputes("A", "A", "B", "B", sample)
    assert (result.shared, result.agreed, result.only_a, result.only_b) == (2, 1, 1, 1)
    assert result.rate == 0.5
    assert Position.POUR.value == "pour"
