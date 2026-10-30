"""Suivi d'un sujet d'une législature à l'autre."""

from assemblee_mcp.civix.scrutin_archive import search_archive
from tests.conftest import CivixStub, McpClient, call, load_fixture, make_item


async def test_suivre_sujet_reads_the_archive_for_the_14th_and_15th(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    text = await call(mcp_client, "suivre_sujet", sujet="mariage")
    in_14 = search_archive(14, ("mariage",))
    assert f"| 14e (2012 à 2017) | {len(in_14)} | 100 |" in text
    assert "(`VTANR5L14V511`)" in text
    assert "### 16e législature (2022 à 2024)\n\nAucun scrutin trouvé." in text
    assert "### Méthode" in text
    assert "ne mesure ni l'importance du sujet" in text
    listings = [
        request for request in civix_mock.requests if request.url.path.endswith("/scrutins")
    ]
    asked = {request.url.params.get("legislature") for request in listings}
    assert asked == {"16", "17"}


async def test_suivre_sujet_merges_civix_and_the_archive(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    item = make_item(9100, "2026-06-04", kind="texte", dossier="sur les pensions de retraite")
    listing = civix_mock.paged([item], {"page": "1", "page_size": "50"})
    civix_mock.add("/scrutins", listing, search="retraite", legislature="17")
    text = await call(mcp_client, "suivre_sujet", sujet="retraite")
    assert "| 17e (depuis 2024) | 1 | 1 | 1 | 1 | 0 | 4 juin 2026 |" in text
    assert "`VTANR5L17V9100`" in text
    for legislature in (14, 15):
        assert len(search_archive(legislature, ("retraite",))) > 0
    assert "Source : CIVIX https://www.civix.fr/api/v1/scrutins — Assemblée nationale" in text


async def test_suivre_sujet_without_any_match(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    text = await call(mcp_client, "suivre_sujet", sujet="zzzz introuvable")
    assert "Aucun scrutin trouvé de 2012 à aujourd'hui" in text


async def test_suivre_sujet_gives_group_stances_on_whole_text_votes(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    for number in (511, 259):
        detail = load_fixture("scrutin_detail_l14")
        detail["data"]["attributes"]["scrutin"].update(uid=f"VTANR5L14V{number}", numero=number)
        civix_mock.add(f"/scrutins/VTANR5L14V{number}", detail)
    text = await call(mcp_client, "suivre_sujet", sujet="mariage aux couples")
    section = text.split("### 14e législature")[1]
    assert "Position majoritaire des groupes sur ces votes :" in section
    assert "| Vote | ECOLO | GDR | NI | RRDP | SRC | UDI | UMP |" in section
    # La fixture réutilise le détail du scrutin n°500 : seule la date diffère du vrai n°511.
    assert "| n°511 (17 avril 2013) | P | P | C | P | P | C | C |" in section
    assert "Légende : P = pour, C = contre" in text
    assert "elle ne dit rien des votes minoritaires" in text
