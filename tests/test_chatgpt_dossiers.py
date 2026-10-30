"""Dossiers législatifs dans les outils `search` et `fetch` au format ChatGPT (issue #26)."""

import json

import pytest
from fastmcp.exceptions import ToolError

from assemblee_mcp.links import assemblee_dossier_url
from tests.conftest import CivixStub, McpClient, call, load_fixture, make_item

REFERENCE = "DLR5L17N54629"
AN_DOSSIER = f"https://www.assemblee-nationale.fr/dyn/17/dossiers/{REFERENCE}"
TITLE = "Projet de loi de finances pour 2027"


def dossier_items() -> list[dict[str, object]]:
    return [
        make_item(3, "2026-10-21", kind="texte", dossier_ref=REFERENCE, dossier=TITLE),
        make_item(2, "2026-10-20", kind="article", dossier_ref=REFERENCE, dossier=TITLE),
        make_item(1, "2026-10-19", kind="amendement", dossier_ref=REFERENCE, dossier=TITLE),
    ]


@pytest.mark.parametrize(
    ("reference", "expected"),
    [
        (REFERENCE, AN_DOSSIER),
        ("DLR5L16N49097", "https://www.assemblee-nationale.fr/dyn/16/dossiers/DLR5L16N49097"),
        ("DLR5L15N44185", "https://www.assemblee-nationale.fr/dyn/15/dossiers/DLR5L15N44185"),
        ("DLRX", None),
        ("../DLR5L17N54629", None),
        ("DLR5L17N54629/x", None),
    ],
)
def test_assemblee_dossier_url(reference: str, expected: str | None) -> None:
    assert assemblee_dossier_url(reference) == expected


async def test_search_returns_dossiers_with_their_reference_first_for_a_topic(
    mcp_client: McpClient,
) -> None:
    payload = json.loads(await call(mcp_client, "search", query="retraites"))

    first = payload["results"][0]
    assert first["id"].startswith("dossier:DLR5L")
    assert first["title"].startswith("Dossier : ")
    assert first["url"].startswith("https://www.assemblee-nationale.fr/dyn/")
    assert "/dossiers/DLR5L" in first["url"]


async def test_search_omits_dossiers_whose_reference_has_no_valid_page(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    payload = load_fixture("search_global")
    payload["data"]["attributes"]["results"]["dossiers"] = [
        {"uid": "WEIRD-REF", "titre": "Dossier étrange", "procedure_label": None},
        {"uid": REFERENCE, "titre": TITLE, "procedure_label": None},
    ]
    civix_mock.add("/search", payload, search="budget")

    found = json.loads(await call(mcp_client, "search", query="budget"))

    ids = [result["id"] for result in found["results"] if result["id"].startswith("dossier:")]
    assert ids == [f"dossier:{REFERENCE}"]


async def test_search_lists_deputes_first_for_a_name(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/search", load_fixture("search_depute"), search="Abadie")

    found = json.loads(await call(mcp_client, "search", query="Abadie"))

    assert found["results"][0]["id"] == "depute:PA793214"


async def test_fetch_dossier_returns_the_timeline(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[REFERENCE] = dossier_items()

    payload = json.loads(await call(mcp_client, "fetch", id=f"dossier:{REFERENCE}"))

    assert payload["id"] == f"dossier:{REFERENCE}"
    assert payload["title"] == f"Dossier : {TITLE}"
    assert payload["url"] == AN_DOSSIER
    assert "### Votes sur l'ensemble du texte" in payload["text"]
    assert "https://www.assemblee-nationale.fr/dyn/17/scrutins/3" in payload["text"]
    assert "/scrutins/jo" not in payload["text"]
    metadata = payload["metadata"]
    assert metadata["type"] == "dossier"
    assert metadata["reference"] == REFERENCE
    assert metadata["scrutins"] == 3
    assert metadata["amendements"] == 1
    assert metadata["votes_sur_l_ensemble"] == 1
    assert metadata["dernier_vote_sur_l_ensemble"] == "2026-10-21 : adopté"
    assert metadata["source_assemblee"] == AN_DOSSIER


async def test_fetch_dossier_without_public_scrutin_says_so(mcp_client: McpClient) -> None:
    payload = json.loads(await call(mcp_client, "fetch", id="dossier:DLR5L16N49097"))

    assert payload["metadata"]["scrutins"] == 0
    assert "Aucun scrutin public n'est rattaché" in payload["text"]
    assert payload["url"] == "https://www.assemblee-nationale.fr/dyn/16/dossiers/DLR5L16N49097"


@pytest.mark.parametrize(
    "identifier",
    ["dossier:..", "dossier:DLR17", "dossier:DLR5L17N5/../x", "dossier:dlr5l17n54629", "dossier:"],
)
async def test_fetch_dossier_rejects_invalid_references_without_calling_civix(
    mcp_client: McpClient, civix_mock: CivixStub, identifier: str
) -> None:
    with pytest.raises(ToolError, match=r"[Ii]dentifiant"):
        await call(mcp_client, "fetch", id=identifier)

    assert civix_mock.requests == []
