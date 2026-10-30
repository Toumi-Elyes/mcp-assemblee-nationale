"""Scrutins des 14e et 15e législatures complétés par l'archive de l'Assemblée nationale."""

import gzip
import importlib.util
import json
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from assemblee_mcp.civix.archive import load_archive
from assemblee_mcp.civix.models import ScrutinListResponse, ScrutinVotes
from assemblee_mcp.civix.models.kinds import classify_scrutin, type_from_title
from assemblee_mcp.civix.scrutin_archive import (
    complete_list,
    complete_scrutin,
    load_scrutins,
    search_archive,
)
from tests.conftest import load_fixture

SCRIPT = Path(__file__).parent.parent / "scripts" / "build_scrutin_data.py"


@pytest.mark.parametrize(("legislature", "expected"), [(14, 1354), (15, 4417)])
def test_archive_holds_every_scrutin_of_the_legislature(legislature: int, expected: int) -> None:
    scrutins = load_scrutins(legislature)
    assert scrutins is not None
    assert len(scrutins) == expected
    archive = load_archive(legislature)
    assert archive is not None
    groups = {row.groupe_uid for item in scrutins.values() for row in item.groups}
    assert groups <= set(archive.groupes)
    assert all(item.titre and item.sort_code in {"adopté", "rejeté"} for item in scrutins.values())


def test_archive_covers_only_the_legislatures_civix_leaves_untitled() -> None:
    assert load_scrutins(16) is None
    assert load_scrutins(13) is None


def test_dissidents_only_scrutins_are_flagged() -> None:
    l14, l15 = load_scrutins(14), load_scrutins(15)
    assert l14 is not None
    assert l15 is not None
    flagged = [item for item in l14.values() if item.dissidents_only]
    assert len(flagged) == 710
    assert max(item.day for item in flagged) == date(2014, 2, 26)
    assert not any(item.dissidents_only for item in l15.values())


def test_official_totals_replace_the_partial_count_of_civix() -> None:
    raw = load_fixture("scrutin_votes_l14_dissidents")["data"]["attributes"]
    assert raw["results_global"]["total"] == 4
    completed = complete_scrutin(ScrutinVotes.model_validate(raw))
    assert completed.archived
    assert completed.dissidents_only
    assert completed.results_global is not None
    assert (completed.results_global.pour, completed.results_global.contre) == (38, 127)
    assert sum(row.total for row in completed.results_by_group) == 167
    assert len(completed.votes) == 4


def test_scrutins_of_other_legislatures_are_left_untouched() -> None:
    raw = load_fixture("scrutin_votes")["data"]["attributes"]
    votes = ScrutinVotes.model_validate(raw)
    assert complete_scrutin(votes) is votes


def test_completed_list_gets_titles_results_and_kinds() -> None:
    response = complete_list(ScrutinListResponse.model_validate(load_fixture("scrutins_l15")))
    for item in response.attributes.results:
        assert item.titre
        assert item.adopted is not None
        assert item.kind in {"amendement", "article", "texte", "autre"}


def test_archive_search_matches_titles_without_accents_newest_first() -> None:
    found = search_archive(14, ("mariage", "meme sexe"))
    assert found[0].uid == "VTANR5L14V511"
    numbers = [item.numero or 0 for item in found]
    assert numbers == sorted(numbers, reverse=True)
    assert all(item.legislature == 14 for item in found)
    assert search_archive(14, ("zzzz",)) == []


@pytest.mark.parametrize(
    ("title", "civix_type", "kind"),
    [
        ("l'amendement n° 37 de M. Poisson à l'article 1er", "amendement", "amendement"),
        ("les amendements identiques n° 12 et 14", "amendement", "amendement"),
        ("le sous-amendment n° 992 de M. Jumel", "amendement", "amendement"),
        ("amendement n° 810 de M. Lurton et amendements identiques", "amendement", "amendement"),
        ("l'article 2 du projet de loi ouvrant le mariage", "article", "article"),
        ("l'ensemble du projet de loi ouvrant le mariage", "texte", "texte"),
        ("la motion de censure déposée par M. Jacob", "texte", "autre"),
        ("la déclaration de politique générale du Gouvernement", "scrutin", "autre"),
    ],
)
def test_type_from_title_follows_civix_types(title: str, civix_type: str, kind: str) -> None:
    assert type_from_title(title) == civix_type
    assert classify_scrutin(type_from_title(title), title) == kind


def test_group_for_a_vote_falls_back_on_a_group_civix_still_publishes() -> None:
    archive = load_archive(16)
    assert archive is not None
    rabault = next(depute for depute in archive.deputes if depute.full_name == "Valérie Rabault")
    day = date(2024, 1, 10)
    assert archive.groupes[str(archive.group_at(rabault.uid, day))].abbr == "SOC-A"
    # CIVIX publie encore les votes socialistes sous l'identifiant d'avant le renommage.
    assert archive.groups_for_vote(rabault.uid, day, {"PO800496", "PO800538"}) == "PO800496"
    assert archive.groups_for_vote(rabault.uid, day, {"PO830170"}) == "PO830170"
    assert archive.groups_for_vote(rabault.uid, day, {"PO800538"}) is None


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_scrutin_data", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_scrutin(uid: str, mode: str, groups: list[Any]) -> dict[str, Any]:
    return {
        "uid": uid,
        "dateScrutin": "2013-04-23",
        "titre": "l'ensemble du projet de loi",
        "sort": {"code": "adopté"},
        "typeVote": {"libelleTypeVote": "scrutin public solennel", "typeMajorite": "majorité"},
        "demandeur": None,
        "modePublicationDesVotes": mode,
        "syntheseVote": {"decompte": {"pour": "3", "contre": "1", "abstention": "0"}},
        "ventilationVotes": {"organe": {"groupes": {"groupe": groups}}},
    }


def test_script_builds_a_reproducible_compressed_index(tmp_path: Path) -> None:
    script = load_script()
    groups = [
        {"organeRef": "PO1", "vote": {"decompteVoix": {"pour": "3", "contre": "0"}}},
        {"organeRef": "PO2", "vote": {"decompteVoix": {"pour": "0", "contre": "0"}}},
        {"organeRef": "PO3", "vote": {"decompteVoix": {"contre": "1", "nonVotants": "2"}}},
    ]
    scrutins = [archive_scrutin("VTANR5L14V2", "DecompteDissidentsPositionGroupe", groups)]
    document = script.build_document(14, scrutins)
    first = script.write_document(document, tmp_path).read_bytes()
    second = script.write_document(document, tmp_path).read_bytes()
    assert first == second
    row = json.loads(gzip.decompress(first))["scrutins"]["VTANR5L14V2"]
    assert row[6] is True
    assert row[7] == [3, 1, 0, 0]
    assert row[8] == [["PO1", 3, 0, 0, 0], ["PO3", 0, 1, 0, 2]]
