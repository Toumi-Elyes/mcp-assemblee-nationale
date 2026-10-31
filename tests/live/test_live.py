import json
import os
import re
from collections import Counter
from typing import Any

import httpx
import pytest
from fastmcp import Client

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.archive import load_archive
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Position
from assemblee_mcp.civix.scrutin_archive import load_scrutins
from assemblee_mcp.civix.search import search_scrutins
from assemblee_mcp.civix.shared_cache import SharedCache
from assemblee_mcp.config import Settings
from assemblee_mcp.server import create_server
from tests.fakes import FakeBackend

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


async def test_live_search_then_fetch_a_dossier(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        found = await connected.call_tool("search", {"query": "projet de loi de finances 2027"})
        results = json.loads(str(found.content[0].text))["results"]
        dossier = next(item for item in results if item["id"].startswith("dossier:"))
        fetched = await connected.call_tool("fetch", {"id": dossier["id"]})
    payload = json.loads(str(fetched.content[0].text))
    assert payload["id"] == dossier["id"]
    assert payload["metadata"]["scrutins"] > 0
    assert "### Chronologie" in payload["text"]
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as http:
        response = await http.get(dossier["url"], headers={"User-Agent": "Mozilla/5.0"})
    assert response.status_code == 200


async def test_live_responses_roundtrip_through_the_shared_cache() -> None:
    backend = FakeBackend()
    first = CivixClient(Settings.from_env(), shared_cache=SharedCache(backend))
    listing = await first.list_scrutins(page_size=5)
    uid = listing.attributes.results[0].uid
    detail = await first.get_scrutin(uid)
    votes = await first.get_votes(uid)
    directory = await first.directory.load()
    second = CivixClient(Settings.from_env(), shared_cache=SharedCache(backend))
    assert await second.list_scrutins(page_size=5) == listing
    assert await second.get_scrutin(uid) == detail
    assert await second.get_votes(uid) == votes
    assert await second.directory.load() == directory


@pytest.mark.parametrize(
    ("legislature", "numbers"),
    [(14, (1, 500, 1354)), (15, (1, 2000, 4419)), (16, (1, 2000, 4105))],
)
async def test_live_every_voter_of_a_closed_legislature_is_in_its_index(
    live_client: CivixClient, legislature: int, numbers: tuple[int, ...]
) -> None:
    archive = load_archive(legislature)
    assert archive is not None
    known = {depute.uid for depute in archive.deputes}
    for number in numbers:
        votes = await live_client.get_votes(f"VTANR5L{legislature}V{number}")
        voters = {vote.deputy_uid for vote in votes.attributes.votes}
        assert voters
        assert voters <= known


@pytest.mark.parametrize("uid", ["VTANR5L14V500", "VTANR5L15V4000"])
async def test_live_scrutins_of_14th_and_15th_are_completed(
    live_mcp_client: Client[Any], uid: str
) -> None:
    async with live_mcp_client as connected:
        detail = await connected.call_tool("obtenir_scrutin", {"uid": uid})
        votes = await connected.call_tool("votes_scrutin", {"uid": uid, "position": "contre"})
    assert "### Décompte par groupe" in str(detail.content[0].text)
    assert "archive des scrutins de l'Assemblée nationale" in str(detail.content[0].text)
    assert "### Contre" in str(votes.content[0].text)


async def test_live_former_deputy_of_the_14th_votes(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "comment_a_vote", {"depute": "Bernard Accoyer", "scrutin_uid": "VTANR5L14V500"}
        )
    assert "A voté : **Contre**." in str(result.content[0].text)


async def test_live_group_filter_uses_the_group_at_the_vote_date(
    live_mcp_client: Client[Any],
) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "votes_scrutin", {"uid": "VTANR5L16V1000", "groupe": "SOC"}
        )
    text = str(result.content[0].text)
    assert "groupe à la date du scrutin" in text
    assert "Valérie Rabault" in text


@pytest.mark.parametrize("legislature", [14, 15])
async def test_live_archive_totals_match_civix_on_fully_published_scrutins(
    live_client: CivixClient, legislature: int
) -> None:
    scrutins = load_scrutins(legislature)
    assert scrutins is not None
    complete = [item for item in scrutins.values() if not item.dissidents_only]
    for item in complete[:: len(complete) // 8]:
        votes = await live_client.get_votes(item.uid)
        positions = Counter(vote.position for vote in votes.attributes.votes)
        assert (positions[Position.POUR], positions[Position.CONTRE]) == (
            item.totals.pour,
            item.totals.contre,
        )
        assert votes.attributes.scrutin.date_scrutin is not None
        assert votes.attributes.scrutin.date_scrutin.date() == item.day


async def test_live_subject_search_in_the_14th(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "comment_a_vote",
            {"depute": "Bernard Accoyer", "sujet": "mariage aux couples", "legislature": 14},
        )
    text = str(result.content[0].text)
    assert "VTANR5L14V511" in text or "n°511" in text
    assert "A voté : **Contre**." in text


async def test_live_suivre_sujet_covers_every_legislature(live_mcp_client: Client[Any]) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool("suivre_sujet", {"sujet": "retraite"})
    text = str(result.content[0].text)
    for legislature in ("17e", "16e", "15e", "14e"):
        assert f"### {legislature} législature" in text
    assert "Aucun scrutin trouvé de 2012" not in text


ASSEMBLEE_SCRUTIN_LINK = re.compile(
    r"https://www\.assemblee-nationale\.fr/dyn/(\d+)/scrutins/(\d+)"
)
BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; mcp-assemblee-nationale tests)"}


@pytest.mark.parametrize("legislature", [17, 16, 15, 14])
async def test_live_listed_scrutin_links_open_the_right_page(
    live_mcp_client: Client[Any], legislature: int
) -> None:
    async with live_mcp_client as connected:
        result = await connected.call_tool(
            "rechercher_scrutins", {"mots_cles": "retraite", "legislature": legislature}
        )
    links = ASSEMBLEE_SCRUTIN_LINK.findall(str(result.content[0].text))[:5]
    assert links
    async with httpx.AsyncClient(headers=BROWSER_HEADERS, follow_redirects=True) as http:
        for number_of_legislature, numero in links:
            url = (
                f"https://www.assemblee-nationale.fr/dyn/{number_of_legislature}/scrutins/{numero}"
            )
            page = await http.get(url, timeout=30)
            # Une page absente répond aussi par un titre générique : on vérifie le numéro affiché.
            assert f"Analyse du scrutin n°{numero} " in page.text, url
