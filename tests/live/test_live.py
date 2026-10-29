import os
from typing import Any

import httpx
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


@pytest.mark.parametrize("name", ["Thiébaut", "Thiebaut", "Trouvé", "Trouve", "Aurélie Trouvé"])
async def test_live_comment_a_vote_resolves_accented_names(
    live_mcp_client: Client[Any], name: str
) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("comment_a_vote", {"depute": name, "sujet": "retraites"})
    assert str(result.content[0].text).startswith("## Votes de ")


async def test_live_global_search_of_a_topic_lists_dossiers_with_their_reference(
    live_mcp_client: Client[Any],
) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "rechercher", {"requete": "projet de loi de finances 2027"}
        )
    text = str(result.content[0].text)
    assert "### Dossiers législatifs" in text
    assert "dossier `DLR" in text
    assert "### Scrutins (du plus récent au plus ancien)" in text


async def test_live_motions_are_not_votes_on_the_whole_text(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "scrutins_par_periode",
            {"date_debut": "2026-06-01", "date_fin": "2026-07-31", "type": "texte"},
        )
    text = str(result.content[0].text)
    assert "motion de rejet" not in text
    assert "l'ensemble" in text


async def test_live_period_covers_exactly_the_requested_days(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("tendances_scrutins", {"periode_jours": 14})
    assert "(14 jours)" in str(result.content[0].text)


async def test_live_exporter_votes_has_a_group_column(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "exporter_votes", {"scrutin_uid": "VTANR5L17V7324", "max_lignes": 5}
        )
    text = str(result.content[0].text)
    assert "nom,groupe,position" in text
    assert "Export limité à 5 lignes" in text


async def test_live_comparison_of_deputes_who_rarely_vote_together_is_explained(
    live_mcp_client: Client[Any],
) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "comparer_deputes",
            {"depute_a": "Mathilde Panot", "depute_b": "Marine Le Pen", "periode_jours": 30},
        )
    text = str(result.content[0].text)
    assert "Échantillon trop faible pour conclure" in text
    assert "n/d" not in text


async def test_live_assemblee_scrutin_links_work(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("obtenir_scrutin", {"uid": "VTANR5L17V7324"})
    text = str(result.content[0].text)
    link = "https://www.assemblee-nationale.fr/dyn/17/scrutins/7324"
    assert link in text
    assert "/scrutins/jo" not in text
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as http:
        response = await http.get(link, headers={"User-Agent": "Mozilla/5.0"})
    assert response.status_code == 200
