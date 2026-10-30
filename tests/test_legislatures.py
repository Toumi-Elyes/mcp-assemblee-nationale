"""Législatures closes (14e, 15e, 16e) : index embarqués, scrutins sans ventilation, outils."""

from datetime import date

import pytest
from fastmcp.exceptions import ToolError

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.archive import (
    ARCHIVED_LEGISLATURES,
    covered_legislatures,
    load_archive,
)
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import ScrutinVotes
from tests.conftest import CivixStub, McpClient, Payload, call, load_fixture

L14_SCRUTIN = "VTANR5L14V500"
L15_SCRUTIN = "VTANR5L15V4000"
ACCOYER = "PA230"  # 14e seulement
BRUNEEL = "PA720546"  # 15e seulement
ABAD = "PA605036"  # 14e, 15e, 16e et 17e


@pytest.fixture
def archived(civix_mock: CivixStub) -> CivixStub:
    """CIVIX servant de vraies réponses (réduites) de scrutins des 14e et 15e législatures."""
    for uid, tag in ((L14_SCRUTIN, "l14"), (L15_SCRUTIN, "l15")):
        civix_mock.add(f"/scrutins/{uid}", load_fixture(f"scrutin_detail_{tag}"))
        civix_mock.add(f"/scrutins/{uid}/votes", load_fixture(f"scrutin_votes_{tag}"))
    return civix_mock


def l15_listing() -> Payload:
    """Dernière page de la 15e législature : trois scrutins du 24 février 2022."""
    payload = load_fixture("scrutins_l15")
    payload["meta"]["pagination"].update(next_page=None, count_total=3)
    return payload


def l15_votes(uid: str) -> Payload:
    """Votes d'un scrutin de la 15e (fixture réelle réduite) sous un autre identifiant."""
    payload = load_fixture("scrutin_votes_l15")
    payload["data"]["attributes"]["scrutin"]["uid"] = uid
    return payload


def deputy_calls(stub: CivixStub) -> list[str]:
    return [path for path in stub.paths() if path.startswith("/deputes")]


# Index embarqués


@pytest.mark.parametrize("legislature", ARCHIVED_LEGISLATURES)
def test_each_archive_is_complete_and_consistent(legislature: int) -> None:
    archive = load_archive(legislature)
    assert archive is not None
    assert archive.legislature == legislature
    assert len(archive.deputes) >= 577
    assert len({depute.uid for depute in archive.deputes}) == len(archive.deputes)
    assert all(depute.legislature == legislature for depute in archive.deputes)
    assert all(depute.full_name and depute.circ_departement for depute in archive.deputes)
    groups = {item.groupe_uid for spans in archive.memberships.values() for item in spans}
    assert groups <= set(archive.groupes)


def test_archives_cover_only_closed_legislatures_with_scrutins() -> None:
    assert ARCHIVED_LEGISLATURES == (16, 15, 14)
    assert load_archive(13) is None
    assert load_archive(17) is None
    assert covered_legislatures() == "14e, 15e, 16e et 17e"


def test_archive_gives_seat_and_last_group() -> None:
    archive = load_archive(15)
    assert archive is not None
    bruneel = archive.depute(BRUNEEL)
    assert bruneel is not None
    assert (bruneel.full_name, bruneel.groupe_abrev) == ("Alain Bruneel", "GDR")
    assert (bruneel.circ_departement, bruneel.circ_num) == ("Nord", 16)
    assert archive.depute(ACCOYER) is None


def test_group_at_follows_membership_dates() -> None:
    archive = load_archive(15)
    assert archive is not None
    assert archive.groupes[str(archive.group_at(ABAD, date(2017, 6, 22)))].abbr == "NI"
    assert archive.groupes[str(archive.group_at(ABAD, date(2020, 1, 1)))].abbr == "LR"
    assert archive.groupes[str(archive.group_at(ABAD, date(2022, 6, 1)))].abbr == "NI"
    assert archive.group_at(ABAD, date(2016, 1, 1)) is None


def test_members_at_matches_the_official_group_size() -> None:
    archive = load_archive(15)
    assert archive is not None
    larem = next(uid for uid, groupe in archive.groupes.items() if groupe.abbr == "LAREM")
    # Ventilation officielle du scrutin n°4000 (12 octobre 2021) : 269 membres.
    assert len(archive.members_at(larem, date(2021, 10, 12))) == 269


def test_a_deputy_keeps_one_uid_across_legislatures() -> None:
    for legislature in ARCHIVED_LEGISLATURES:
        archive = load_archive(legislature)
        assert archive is not None
        abad = archive.depute(ABAD)
        assert abad is not None
        assert abad.full_name == "Damien Abad"


# Modèles : réponses CIVIX des 14e et 15e législatures


@pytest.mark.parametrize("tag", ["l14", "l15"])
def test_votes_without_group_breakdown_parse(tag: str) -> None:
    attributes = load_fixture(f"scrutin_votes_{tag}")["data"]["attributes"]
    assert attributes["results_by_group"][0]["groupe_uid"] is None
    votes = ScrutinVotes.model_validate(attributes)
    assert votes.results_by_group == []
    assert votes.results_global is not None
    assert votes.results_global.total > 0
    assert votes.votes
    assert {vote.par_delegation for vote in votes.votes} == {None}


# Outils


async def test_obtenir_scrutin_14e_explains_missing_breakdown(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "obtenir_scrutin", uid=L14_SCRUTIN)
    assert "274 pour, 244 contre, 20 abstention(s)" in text
    assert "ni le décompte par groupe des scrutins de la 14e législature" in text
    assert "None" not in text
    assert "https://www.assemblee-nationale.fr/dyn/14/scrutins/500" in text


async def test_votes_scrutin_15e_filters_by_group_at_the_vote_date(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "votes_scrutin", uid=L15_SCRUTIN, groupe="GDR")
    assert "groupe GDR (groupe à la date du scrutin des députés)" in text
    assert "Alain Bruneel" in text
    assert "Ahamada" not in text
    assert deputy_calls(archived) == []


async def test_votes_scrutin_rejects_a_group_unknown_in_that_legislature(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    with pytest.raises(ToolError, match="Groupes disponibles"):
        await call(mcp_client, "votes_scrutin", uid=L15_SCRUTIN, groupe="LFI-NFP")


async def test_comment_a_vote_14e_deduces_legislature_from_scrutin(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "comment_a_vote", depute="Accoyer", scrutin_uid=L14_SCRUTIN)
    assert "Bernard Accoyer (LES-REP)" in text
    assert "A voté : **Contre**." in text
    assert deputy_calls(archived) == []


async def test_comment_a_vote_by_subject_in_15e_explains_missing_titles(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(
        mcp_client, "comment_a_vote", depute="Bruneel", sujet="retraites", legislature=15
    )
    assert "CIVIX ne fournit pas les titres des scrutins de la 15e législature" in text
    assert archived.requests == []


async def test_rechercher_scrutins_by_keyword_in_14e_skips_civix(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "rechercher_scrutins", mots_cles="mariage", legislature=14)
    assert "CIVIX ne fournit pas les titres des scrutins de la 14e législature" in text
    assert "Essayez d'autres mots-clés" not in text
    assert archived.requests == []


async def test_rechercher_scrutins_lists_untitled_scrutins(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    archived.add("/scrutins", l15_listing(), legislature="15", page="1")
    text = await call(mcp_client, "rechercher_scrutins", legislature=15)
    assert "(titre non fourni par CIVIX)" in text
    assert "`VTANR5L15V4419`" in text


async def test_rechercher_deputes_by_name_in_each_closed_legislature(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    for legislature, name, expected in ((14, "accoyer", ACCOYER), (15, "bruneel", BRUNEEL)):
        text = await call(mcp_client, "rechercher_deputes", nom=name, legislature=legislature)
        assert f"`{expected}`" in text
        assert f"https://www.assemblee-nationale.fr/dyn/deputes/{expected}" in text
        assert "civix.fr/deputes/" not in text
    assert deputy_calls(archived) == []


async def test_rechercher_deputes_lists_a_closed_legislature_by_group(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "rechercher_deputes", legislature=15, groupe="GDR")
    assert "## Députés de la 15e législature" in text
    assert "Alain Bruneel" in text
    assert "sur 18" in text
    assert deputy_calls(archived) == []


async def test_unknown_current_name_points_to_the_closed_legislature(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "rechercher_deputes", nom="Accoyer")
    assert "aucun député trouvé" in text
    assert "législatures 14e, 15e, 16e et 17e" in text
    assert f"Bernard Accoyer (`{ACCOYER}`). Relancez avec `legislature=14`." in text


async def test_obtenir_depute_by_uid_falls_back_to_the_latest_archive(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    accoyer = await call(mcp_client, "obtenir_depute", uid=ACCOYER)
    assert "- Législature : 14" in accoyer
    assert "- Circonscription : Haute-Savoie, 1e circonscription" in accoyer
    assert "Source : Assemblée nationale https://www.assemblee-nationale.fr/dyn/deputes/PA230" in (
        accoyer
    )
    abad = await call(mcp_client, "obtenir_depute", uid=ABAD)
    assert "- Législature : 16" in abad
    assert "Renaissance (RE)" in abad


async def test_obtenir_depute_in_an_explicit_legislature(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    text = await call(mcp_client, "obtenir_depute", uid=ABAD, legislature=15)
    assert "- Législature : 15" in text
    assert "Non inscrit (NI)" in text
    assert deputy_calls(archived) == []


@pytest.mark.parametrize("legislature", [12, 13])
async def test_legislature_without_data_is_a_clear_error(
    mcp_client: McpClient, archived: CivixStub, legislature: int
) -> None:
    with pytest.raises(ToolError, match="législatures disponibles : 14e, 15e, 16e et 17e"):
        await call(mcp_client, "rechercher_deputes", nom="Abad", legislature=legislature)
    assert archived.requests == []


async def test_bilan_depute_15e_never_reports_a_false_alignment(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    archived.add("/scrutins", l15_listing(), legislature="15", page="1")
    for item in l15_listing()["data"]["attributes"]["results"]:
        archived.add(f"/scrutins/{item['uid']}/votes", l15_votes(item["uid"]))
    text = await call(mcp_client, "bilan_depute", depute="Bruneel", periode_jours=7, legislature=15)
    assert "## Votes de Alain Bruneel (GDR)" in text
    assert "| 0 | 3 | 0 | 0 | 0 |" in text
    assert "0 sur 0 votes comparables (non calculable" in text
    assert "0 %" not in text
    assert "du 2022-02-18 au 2022-02-24" in text
    assert "CIVIX ne fournit pas le décompte par groupe" in text
    assert "https://www.assemblee-nationale.fr/dyn/15/scrutins" in text


async def test_tendances_of_a_closed_legislature_end_at_its_last_scrutin(
    mcp_client: McpClient, archived: CivixStub
) -> None:
    archived.add("/scrutins", l15_listing(), legislature="15", page="1")
    text = await call(mcp_client, "tendances_scrutins", periode_jours=7, legislature=15)
    assert "du 18 février 2022 au 24 février 2022" in text
    assert "3 scrutins" in text
    assert "https://www.assemblee-nationale.fr/dyn/15/scrutins" in text


async def test_archived_lookup_never_calls_the_directory(
    client: CivixClient, archived: CivixStub
) -> None:
    for legislature in ARCHIVED_LEGISLATURES:
        found = await lookup.find_deputes(client, "Damien Abad", legislature=legislature)
        assert [depute.uid for depute in found] == [ABAD]
    assert archived.requests == []
