import os
from typing import Any

import pytest
from fastmcp import Client

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.config import Settings
from assemblee_mcp.server import create_server

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


async def test_live_natural_phrase_falls_back(live_client: CivixClient) -> None:
    found = await search_scrutins(live_client, "loi de finances 2027")
    assert len(found.results) >= 1
    assert found.note is not None
    assert found.note.startswith("Recherche élargie")


@pytest.fixture
def live_mcp_client() -> Client[Any]:
    return Client(create_server(CivixClient(Settings.from_env())))


async def test_live_tendances_scrutins(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("tendances_scrutins", {"periode_jours": 30})
    text = str(result.content[0].text)
    assert "## Tendances des scrutins" in text
    assert "### Méthode" in text


async def test_live_textes_les_plus_votes(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("textes_les_plus_votes", {"periode_jours": 30})
    text = str(result.content[0].text)
    assert "Textes comptant le plus de scrutins" in text


async def test_live_accords_entre_groupes(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "accords_entre_groupes", {"periode_jours": 30, "max_scrutins": 10}
        )
    text = str(result.content[0].text)
    assert "## Accords entre groupes" in text
    assert "| RN |" in text
