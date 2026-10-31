import re
from typing import Any

import pytest

from assemblee_mcp.links import scrutin_page_url
from tests.conftest import CivixStub, McpClient, call, make_listing

CITED_UID = re.compile(r"`(VTANR5L\d{1,2}V\d{1,6})`")


def test_scrutin_page_url_prefers_the_assemblee_page() -> None:
    assert (
        scrutin_page_url("VTANR5L17V9231", 17, 9231)
        == "https://www.assemblee-nationale.fr/dyn/17/scrutins/9231"
    )


def test_scrutin_page_url_reads_the_uid_when_numbers_are_missing() -> None:
    assert (
        scrutin_page_url("VTANR5L14V511")
        == "https://www.assemblee-nationale.fr/dyn/14/scrutins/511"
    )


def test_scrutin_page_url_falls_back_to_civix_for_an_unknown_uid() -> None:
    assert scrutin_page_url("VTXYZ1") == "https://www.civix.fr/votes/VTXYZ1"


def uncited_lines(text: str) -> list[str]:
    """Lignes qui citent un scrutin par son identifiant sans donner son lien."""
    return [
        line
        for line in text.splitlines()
        for uid in CITED_UID.findall(line)
        if scrutin_page_url(uid) not in line and f"https://www.civix.fr/votes/{uid}" not in line
    ]


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("rechercher", {"requete": "retraites"}),
        ("rechercher_scrutins", {"mots_cles": "retraites"}),
        ("suivre_sujet", {"sujet": "mariage"}),
        ("scrutins_par_periode", {"date_debut": "2026-10-01", "date_fin": "2026-10-29"}),
    ],
)
async def test_every_listed_scrutin_carries_its_link(
    mcp_client: McpClient, civix_mock: CivixStub, tool: str, arguments: dict[str, Any]
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    text = await call(mcp_client, tool, **arguments)
    assert CITED_UID.search(text), "la réponse devrait citer au moins un scrutin"
    assert uncited_lines(text) == []
