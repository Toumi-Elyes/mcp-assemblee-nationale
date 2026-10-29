import os

import pytest

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.config import Settings

pytestmark = pytest.mark.skipif(
    os.environ.get("CIVIX_LIVE") != "1", reason="Tests réseau : définir CIVIX_LIVE=1"
)


@pytest.fixture
def live_client() -> CivixClient:
    return CivixClient(Settings.from_env())


async def test_live_groupes(live_client: CivixClient) -> None:
    groupes = await lookup.list_groupes(live_client)
    assert {groupe.abbr for groupe in groupes} >= {"RN", "SOC"}


async def test_live_scrutins_then_votes(live_client: CivixClient) -> None:
    listing = await live_client.list_scrutins("retraites", page_size=2)
    first = listing.attributes.results[0]
    votes = await live_client.get_votes(first.uid)
    assert votes.attributes.votes
    assert votes.attributes.results_global is not None
    assert votes.attributes.results_global.total >= len(votes.attributes.votes)


async def test_live_deputy_search_and_detail(live_client: CivixClient) -> None:
    found = await lookup.find_deputes(live_client, "Le Pen")
    assert any(depute.nom == "Le Pen" for depute in found)
    detail = await live_client.get_depute(found[0].uid)
    assert detail.attributes.deputy.uid == found[0].uid


async def test_live_group_members_cover_the_group(live_client: CivixClient) -> None:
    groupe = await lookup.find_groupe(live_client, "RN")
    assert groupe is not None
    members = await lookup.groupe_member_uids(live_client, "RN")
    assert groupe.effectif is not None
    assert len(members) >= groupe.effectif


async def test_live_search(live_client: CivixClient) -> None:
    response = await live_client.search("retraites")
    assert response.attributes.total > 0
