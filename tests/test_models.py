import pytest

from assemblee_mcp.civix.models import (
    CivixResponse,
    DeputeDetailResponse,
    DeputeListResponse,
    GroupeDetailResponse,
    GroupeListResponse,
    Position,
    ScrutinListResponse,
    ScrutinResponse,
    ScrutinVotes,
    ScrutinVotesResponse,
    SearchResponse,
    StatementsResponse,
)
from tests.conftest import load_fixture


def test_scrutin_list_fixture() -> None:
    response = ScrutinListResponse.model_validate(load_fixture("search_scrutins"))
    first = response.attributes.results[0]
    assert first.uid == "VTANR5L17V7324"
    assert first.date_scrutin is not None
    assert first.date_scrutin.year == 2026
    assert first.sort is not None
    assert first.sort.code == "adopté"
    assert first.type_vote is not None
    assert first.type_vote.code == "SPO"
    assert response.pagination is not None
    assert response.pagination.total == 12
    assert response.pagination.next_page == 2


def test_scrutin_detail_fixture() -> None:
    response = ScrutinResponse.model_validate(load_fixture("scrutin_detail"))
    attributes = response.attributes
    assert attributes.scrutin.is_adopted is True
    assert attributes.scrutin.result_label == "l'Assemblée nationale a adopté"
    assert attributes.results_global is not None
    assert attributes.results_global.pour == 82
    assert attributes.results_global.total == 90
    assert len(attributes.results_by_group) == 11
    assert (
        response.source.assemblee_url == "https://www.assemblee-nationale.fr/dyn/17/scrutins/jo7324"
    )
    assert response.pagination is None


def test_votes_fixture() -> None:
    response = ScrutinVotesResponse.model_validate(load_fixture("scrutin_votes"))
    votes = response.attributes.votes
    positions = {vote.position for vote in votes}
    assert positions == {Position.POUR, Position.CONTRE, Position.ABSTENTION, Position.NON_VOTANT}
    assert any(vote.par_delegation for vote in votes)


def test_statements_fixtures() -> None:
    empty = StatementsResponse.model_validate(load_fixture("scrutin_statements_empty"))
    assert empty.attributes.statements == []
    example = StatementsResponse.model_validate(load_fixture("scrutin_statements"))
    statement = example.attributes.statements[0]
    assert statement.groupe_abrev == "RN"
    assert statement.vote_position == "contre"
    assert statement.submitted_at is not None


def test_depute_fixtures() -> None:
    listing = DeputeListResponse.model_validate(load_fixture("deputes"))
    assert listing.attributes.results[0].groupe_abrev == "LIOT"
    assert listing.pagination is not None
    assert listing.pagination.total == 602
    detail = DeputeDetailResponse.model_validate(load_fixture("depute_detail"))
    assert detail.attributes.deputy.full_name == "Audrey Abadie-Amiel"


def test_groupe_fixtures() -> None:
    listing = GroupeListResponse.model_validate(load_fixture("groupes"))
    assert {groupe.abbr for groupe in listing.attributes.groups} >= {"RN", "LIOT"}
    detail = GroupeDetailResponse.model_validate(load_fixture("groupe_liot"))
    assert detail.attributes.groupe.effectif == 23


def test_search_fixtures() -> None:
    scrutins = SearchResponse.model_validate(load_fixture("search_global"))
    assert scrutins.attributes.total == 16
    assert scrutins.attributes.results.scrutins[0].type_vote == "scrutin public ordinaire"
    assert scrutins.attributes.results.dossiers
    deputes = SearchResponse.model_validate(load_fixture("search_depute"))
    hit = deputes.attributes.results.deputes[0]
    assert hit.uid == "PA793214"
    assert hit.groupe_abrev == "LIOT"
    assert hit.to_depute().full_name == "Audrey Abadie-Amiel"


@pytest.mark.parametrize("fixture", ["deputes_groupe_liot", "deputes_groupe_hor"])
def test_group_member_fixtures(fixture: str) -> None:
    response = DeputeListResponse.model_validate(load_fixture(fixture))
    assert response.attributes.results


def test_models_tolerate_extra_and_missing_fields() -> None:
    payload = {
        "data": {
            "type": "scrutin",
            "attributes": {
                "scrutin": {"uid": "X1", "champ_inconnu": 1},
                "votes": [{"deputy_uid": "PA1", "position": "nouvelle_position"}],
            },
        },
        "champ_inconnu": True,
    }
    response = CivixResponse[ScrutinVotes].model_validate(payload)
    assert response.attributes.votes[0].position is Position.UNKNOWN
    assert response.attributes.scrutin.titre == ""
    assert response.meta.pagination is None


def test_models_are_frozen() -> None:
    response = ScrutinListResponse.model_validate(load_fixture("search_scrutins"))
    with pytest.raises(ValueError, match="frozen"):
        response.attributes.results[0].titre = "autre"  # type: ignore[misc]
