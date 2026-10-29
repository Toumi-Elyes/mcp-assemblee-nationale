from datetime import datetime

from assemblee_mcp import formatting
from assemblee_mcp.civix.models import (
    DeputeDetailResponse,
    GroupeDetailResponse,
    GroupeListResponse,
    Pagination,
    Position,
    ScrutinListResponse,
    ScrutinResponse,
    ScrutinVotesResponse,
    SearchResponse,
    StatementsResponse,
)
from tests.conftest import load_fixture


def test_format_date_french() -> None:
    assert formatting.format_date(datetime(2026, 6, 4)) == "4 juin 2026"
    assert formatting.format_date(datetime(2026, 2, 1)) == "1er février 2026"
    assert formatting.format_date(None) == "date inconnue"


def test_truncate() -> None:
    assert formatting.truncate("a" * 10, 5) == "aaaa…"
    assert formatting.truncate("  un   deux ") == "un deux"


def test_scrutin_list_has_source_footer_and_pagination() -> None:
    response = ScrutinListResponse.model_validate(load_fixture("search_scrutins"))
    text = formatting.format_scrutin_list(response, "retraites")
    assert "## Scrutins pour « retraites »" in text
    assert "uid : `VTANR5L17V7324`" in text
    assert "page 2" in text
    assert "Source : CIVIX" in text
    assert text.rstrip().endswith(formatting.FOOTER)


def test_scrutin_list_empty_suggests_accents() -> None:
    payload = load_fixture("search_scrutins")
    payload["data"]["attributes"]["results"] = []
    response = ScrutinListResponse.model_validate(payload)
    assert "accents" in formatting.format_scrutin_list(response, "chomage")


def test_format_scrutin_with_group_table() -> None:
    response = ScrutinResponse.model_validate(load_fixture("scrutin_detail"))
    text = formatting.format_scrutin(response, {"PO845485": "LIOT"})
    assert "82 pour, 1 contre, 5 abstention(s), 2 non-votant(s) (total 90)" in text
    assert "| LIOT | 1 | 0 | 0 | 0 | 1 |" in text
    assert "https://www.assemblee-nationale.fr/dyn/17/scrutins/jo7324" in text
    assert "https://www.civix.fr/votes/VTANR5L17V7324" in text


def test_select_votes_filters() -> None:
    votes = ScrutinVotesResponse.model_validate(load_fixture("scrutin_votes")).attributes.votes
    abstentions = formatting.select_votes(votes, position=Position.ABSTENTION)
    assert len(abstentions) == 5
    by_name = formatting.select_votes(votes, nom="YAEL braun")
    assert [vote.nom for vote in by_name] == ["Braun-Pivet"]
    by_group = formatting.select_votes(votes, member_uids={"PA795350", "PA719138"})
    assert {vote.nom for vote in by_group} == {"Valletoux", "Castellani"}
    combined = formatting.select_votes(
        votes, member_uids={"PA795350", "PA719138"}, position=Position.POUR
    )
    assert [vote.nom for vote in combined] == ["Castellani"]


def test_format_votes_groups_by_position_with_totals() -> None:
    response = ScrutinVotesResponse.model_validate(load_fixture("scrutin_votes"))
    votes = response.attributes.votes
    text = formatting.format_votes(response, votes, formatting.VoteFilters())
    assert "### Pour (9)" in text
    assert "### Abstention (5)" in text
    assert "### Non-votant (2)" in text
    assert "Décompte officiel : 82 pour" in text
    assert "Astrid Panosyan-Bouvet (par délégation)" in text
    assert text.index("### Pour") < text.index("### Contre") < text.index("### Abstention")


def test_format_votes_caps_names_and_reports_the_rest() -> None:
    response = ScrutinVotesResponse.model_validate(load_fixture("scrutin_votes"))
    text = formatting.format_votes(
        response, response.attributes.votes, formatting.VoteFilters(), limit=10
    )
    assert "… et 5 autres." in text
    assert "… et 2 autres." in text
    assert "### Contre (1)" in text
    assert "Affinez" in text


def test_format_votes_no_match_and_filter_description() -> None:
    response = ScrutinVotesResponse.model_validate(load_fixture("scrutin_votes"))
    filters = formatting.VoteFilters(groupe="LIOT", position=Position.CONTRE, nom="x")
    text = formatting.format_votes(response, [], filters)
    assert "groupe LIOT" in text
    assert "position « Contre »" in text
    assert "Aucun vote ne correspond" in text


def test_format_statements() -> None:
    empty = StatementsResponse.model_validate(load_fixture("scrutin_statements_empty"))
    assert "Aucune déclaration" in formatting.format_statements(empty, "UID1")
    full = StatementsResponse.model_validate(load_fixture("scrutin_statements"))
    text = formatting.format_statements(full, "UID1")
    assert "**RN**" in text
    assert "> Le groupe explique sa position publique." in text


def test_format_depute_and_groupes() -> None:
    depute = DeputeDetailResponse.model_validate(load_fixture("depute_detail"))
    text = formatting.format_depute(depute)
    assert "## Audrey Abadie-Amiel" in text
    assert "Ariège, 2e circonscription" in text
    assert "https://www.assemblee-nationale.fr/dyn/deputes/PA793214" in text
    groupes = GroupeListResponse.model_validate(load_fixture("groupes"))
    listing = formatting.format_groupes(groupes)
    assert "**LIOT**" in listing
    groupe = GroupeDetailResponse.model_validate(load_fixture("groupe_liot"))
    assert "Effectif : 23" in formatting.format_groupe(groupe)


def test_format_search_sections() -> None:
    response = SearchResponse.model_validate(load_fixture("search_global"))
    text = formatting.format_search(response, "retraites")
    assert "### Scrutins" in text
    assert "### Dossiers législatifs" in text
    assert "16 résultat(s) au total" in text


def test_pagination_hint() -> None:
    assert formatting.pagination_hint(None, 3, "x") == ""
    last = Pagination(page=2, next_page=None, count_total=12)
    assert "demandez" not in formatting.pagination_hint(last, 2, "scrutin(s)")
    more = Pagination(page=1, next_page=2, count_estimated=602)
    assert "demandez la page 2" in formatting.pagination_hint(more, 10, "député(s)")
