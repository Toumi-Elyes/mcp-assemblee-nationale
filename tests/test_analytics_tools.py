import csv
import io
import json
import re
from datetime import UTC, date, datetime

import pytest
from fastmcp.exceptions import ToolError

from assemblee_mcp import limits
from assemblee_mcp.analytics import gather
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.config import Settings
from assemblee_mcp.formatting import FOOTER
from tests.conftest import (
    PANOSYAN,
    SCRUTIN_UID,
    VALLETOUX,
    CivixStub,
    DeputeStub,
    McpClient,
    call,
    load_fixture,
    make_item,
    make_listing,
    search_with_deputes,
)

TODAY = date(2026, 10, 29)
LIST_BUDGET = limits.LISTING_MAX_CALLS
ANALYTICS_BUDGET = limits.ANALYTICS_MAX_CALLS


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gather, "current_day", lambda: TODAY)


def scanned_count(pattern: str, text: str) -> int:
    """Nombre lu dans `text` ; il doit rester entre la cible et la cible plus un lot de lecture."""
    found = re.search(pattern, text)
    assert found is not None
    count = int(found.group(1))
    assert (
        limits.TARGET_USABLE_SCRUTINS <= count <= limits.TARGET_USABLE_SCRUTINS + limits.VOTES_BATCH
    )
    return count


def assert_analysis_shape(text: str) -> None:
    assert "### Méthode" in text
    assert "- Échantillon :" in text
    assert "Source : CIVIX" in text
    assert text.rstrip().endswith(FOOTER)


async def test_tendances_scrutins(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    text = await call(mcp_client, "tendances_scrutins", periode_jours=30)
    assert_analysis_shape(text)
    assert "## Tendances des scrutins" in text
    assert "### Volume par semaine" in text
    assert "| amendements |" in text
    assert "votes sur l'ensemble d'un texte" in text
    assert len(civix_mock.requests) <= 20


async def test_tendances_dense_period_stays_within_budget_and_reports_truncation(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(90, 14)
    text = await call(mcp_client, "tendances_scrutins", periode_jours=90)
    assert "Échantillon tronqué" in text
    assert len(civix_mock.requests) <= LIST_BUDGET


async def test_textes_les_plus_votes(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    items = [
        make_item(
            n, "2026-10-20", dossier_ref="DLR1" if n % 3 else "DLR2", dossier=f"Texte {n % 3}"
        )
        for n in range(30)
    ]
    civix_mock.listings[None] = items
    text = await call(mcp_client, "textes_les_plus_votes", periode_jours=30, limite=2)
    assert_analysis_shape(text)
    first_row = text.split("|---|---|---|---|---|---|\n")[1].splitlines()[0]
    assert "DLR1" in first_row
    assert "20" in first_row
    assert "2 dossiers distincts, 2 affichés" in text


async def test_dossier_legislatif_timeline(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    items = [
        make_item(3, "2026-10-03", kind="texte", dossier_ref="DLR9", dossier="Mon texte"),
        make_item(2, "2026-10-02", kind="article", dossier_ref="DLR9", dossier="Mon texte"),
        make_item(1, "2026-10-01", kind="amendement", dossier_ref="DLR9", dossier="Mon texte"),
    ]
    civix_mock.listings["mon texte"] = items
    civix_mock.listings["DLR9"] = items
    text = await call(mcp_client, "dossier_legislatif", texte="mon texte")
    assert_analysis_shape(text)
    assert "## Dossier : Mon texte (`DLR9`)" in text
    assert "### Votes sur l'ensemble du texte" in text
    assert "3 scrutins, dont 1 sur des amendements" in text
    timeline = text.split("### Chronologie")[1]
    assert timeline.index("n°2") < timeline.index("n°3")


async def test_dossier_legislatif_unknown_text(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "dossier_legislatif", texte="zzzz")
    assert "Aucun scrutin trouvé" in text


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        ("2026-13-01", "2026-10-02", "n'est pas une date"),
        ("hier", "2026-10-02", "pattern"),
        ("2026-10-05", "2026-10-02", "postérieure"),
        ("2026-01-01", "2026-10-02", "90 jours"),
    ],
)
async def test_scrutins_par_periode_validates_dates(
    mcp_client: McpClient, civix_mock: CivixStub, start: str, end: str, message: str
) -> None:
    with pytest.raises(ToolError, match=message):
        await call(mcp_client, "scrutins_par_periode", date_debut=start, date_fin=end)
    assert civix_mock.requests == []


async def test_scrutins_par_periode_filters_and_paginates(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    base = {"date_debut": "2026-10-01", "date_fin": "2026-10-29"}
    first = await call(mcp_client, "scrutins_par_periode", **base)
    assert_analysis_shape(first)
    assert "demandez la page 2" in first
    textes = await call(mcp_client, "scrutins_par_periode", type="texte", **base)
    assert textes.count("uid : `") == 20
    assert "29 scrutin(s)" in textes or "sur 29" in textes
    rejected = await call(mcp_client, "scrutins_par_periode", resultat="rejete", page=2, **base)
    assert "uid : `" in rejected
    assert len(civix_mock.requests) <= LIST_BUDGET


async def test_scrutins_par_periode_past_range_uses_few_calls(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(200, 5)
    text = await call(
        mcp_client, "scrutins_par_periode", date_debut="2026-05-01", date_fin="2026-05-10"
    )
    assert text.count("uid : `") == 20
    assert len(civix_mock.requests) <= LIST_BUDGET


async def test_statistiques_assemblee(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(200, 5)
    text = await call(mcp_client, "statistiques_assemblee")
    assert_analysis_shape(text)
    assert "Scrutins publics depuis le début de la législature : 1000" in text
    assert "Députés recensés : 602" in text
    assert "| RN |" in text
    assert len(civix_mock.requests) <= LIST_BUDGET


async def test_positions_groupes(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    text = await call(mcp_client, "positions_groupes", sujet="retraites", max_scrutins=3)
    assert_analysis_shape(text)
    assert "| Scrutin | DEM | DR | ECOS |" in text
    assert "Légende" in text
    assert "Échantillon : 3 scrutin(s) analysé(s) sur" in text


async def test_positions_groupes_needs_exactly_one_criterion(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="soit `sujet`, soit `dossier`"):
        await call(mcp_client, "positions_groupes")
    with pytest.raises(ToolError, match="soit `sujet`, soit `dossier`"):
        await call(mcp_client, "positions_groupes", sujet="a b", dossier="DLR5L17N1")


async def test_accords_entre_groupes_with_maximum_parameters_fits_budget(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    text = await call(mcp_client, "accords_entre_groupes", periode_jours=30, max_scrutins=30)
    assert_analysis_shape(text)
    assert "## Accords entre groupes" in text
    assert "Échantillon régulier" in text
    assert len(civix_mock.requests) <= ANALYTICS_BUDGET


async def test_group_analyses_need_exactly_one_criterion(mcp_client: McpClient) -> None:
    for name in ("accords_entre_groupes", "cohesion_groupes"):
        with pytest.raises(ToolError, match="soit `sujet`, soit `periode_jours`"):
            await call(mcp_client, name)
        with pytest.raises(ToolError, match="soit `sujet`, soit `periode_jours`"):
            await call(mcp_client, name, sujet="retraites", periode_jours=30)


async def test_cohesion_groupes(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "cohesion_groupes", sujet="retraites", max_scrutins=3)
    assert_analysis_shape(text)
    assert "| RN |" in text
    assert "Part alignée" in text


async def test_votes_serres(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(30, 3)
    none = await call(mcp_client, "votes_serres", periode_jours=30)
    assert "parcourus n'a un écart" in none
    wide = await call(mcp_client, "votes_serres", periode_jours=30, ecart_max=100)
    assert "| Écart |" in wide
    assert "| 81 |" in wide
    assert len(civix_mock.requests) <= ANALYTICS_BUDGET


async def test_bilan_depute(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    civix_mock.add("/search", search_with_deputes(PANOSYAN), search="Astrid Panosyan-Bouvet")
    text = await call(mcp_client, "bilan_depute", depute="Astrid Panosyan-Bouvet", periode_jours=30)
    assert_analysis_shape(text)
    assert "(EPR)" in text
    scanned = scanned_count(r"\| 0 \| 0 \| (\d+) \| 0 \| 0 \|", text)
    assert f"Votes exprimés par délégation : {scanned}" in text
    assert f"0 sur {scanned} votes comparables" in text
    assert "ne dit rien de l'intérêt" in text
    assert len(civix_mock.requests) <= ANALYTICS_BUDGET


async def test_bilan_depute_on_subject_counts_absence(mcp_client: McpClient) -> None:
    text = await call(
        mcp_client, "bilan_depute", depute="Abadie", sujet="retraites", max_scrutins=3
    )
    assert "| 0 | 0 | 0 | 0 | 3 |" in text


async def test_bilan_depute_ambiguous_name_asks_to_choose(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add(
        "/search",
        search_with_deputes(
            DeputeStub("PA1", "Élisa", "Martin", "LFI-NFP"),
            DeputeStub("PA2", "Patrice", "Martin", "RN"),
        ),
        search="Martin",
    )
    text = await call(mcp_client, "bilan_depute", depute="Martin", periode_jours=30)
    assert "Plusieurs députés correspondent" in text
    assert not any(path.endswith("/votes") for path in civix_mock.paths())


async def test_bilan_depute_needs_exactly_one_criterion(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="soit `sujet`, soit `periode_jours`"):
        await call(mcp_client, "bilan_depute", depute="Abadie")


async def test_comparer_deputes_fits_budget(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    civix_mock.add("/search", search_with_deputes(PANOSYAN), search="Astrid Panosyan-Bouvet")
    civix_mock.add("/search", search_with_deputes(VALLETOUX), search="Frédéric Valletoux")
    text = await call(
        mcp_client,
        "comparer_deputes",
        depute_a="Astrid Panosyan-Bouvet",
        depute_b="Frédéric Valletoux",
        periode_jours=30,
    )
    assert_analysis_shape(text)
    shared = scanned_count(r"Scrutins où les deux ont exprimé un vote : (\d+)", text)
    assert f"Même position sur : {shared} (100 %)" in text
    assert len(civix_mock.requests) <= ANALYTICS_BUDGET


async def test_exporter_scrutins_csv(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    items = make_listing(3, 4)
    items[0]["titre"] = '=HYPERLINK("http://evil")'
    civix_mock.listings[None] = items
    text = await call(
        mcp_client,
        "exporter_scrutins",
        date_debut="2026-10-20",
        date_fin="2026-10-29",
        max_lignes=5,
    )
    assert "Export limité à 5 lignes" in text
    block = text.split("```csv\n")[1].split("\n```")[0]
    rows = list(csv.reader(io.StringIO(block)))
    assert rows[0][:4] == ["uid", "numero", "date", "legislature"]
    assert len(rows) == 6
    assert rows[1][rows[0].index("titre")].startswith("'=")
    assert rows[1][rows[0].index("url_civix")].startswith("https://www.civix.fr/votes/")


async def test_exporter_scrutins_json_by_subject(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "exporter_scrutins", sujet="retraites", format="json")
    data = json.loads(text.split("```json\n")[1].split("\n```")[0])
    assert data[0]["uid"] == "VTANR5L17V7324"
    assert set(data[0]) >= {"uid", "date", "resultat", "dossier_ref"}


async def test_exporter_scrutins_needs_one_selection(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="soit `date_debut`"):
        await call(mcp_client, "exporter_scrutins")
    with pytest.raises(ToolError, match="vont ensemble"):
        await call(mcp_client, "exporter_scrutins", date_debut="2026-10-01")


async def test_exporter_votes(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID)
    block = text.split("```csv\n")[1].split("\n```")[0]
    rows = list(csv.reader(io.StringIO(block)))
    assert rows[0] == [
        "scrutin_uid",
        "depute_uid",
        "prenom",
        "nom",
        "groupe",
        "position",
        "par_delegation",
    ]
    assert len(rows) == 18
    assert "Export CSV : 17 ligne(s)." in text
    as_json = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID, format="json")
    data = json.loads(as_json.split("```json\n")[1].split("\n```")[0])
    assert data[0]["position"] in {"pour", "contre", "abstention", "non_votant"}
    assert isinstance(data[0]["par_delegation"], bool)


async def test_old_scrutins_are_cached_for_a_day_and_recent_ones_for_ten_minutes(
    civix_mock: CivixStub,
) -> None:
    now = [0.0]
    client = CivixClient(Settings(retry_delay=0.0), clock=lambda: now[0])
    await client.get_votes(SCRUTIN_UID)
    recent = load_fixture("scrutin_votes")
    stamp = datetime.now(UTC).isoformat()
    recent["data"]["attributes"]["scrutin"]["date_scrutin"] = stamp
    civix_mock.add("/scrutins/VTANR5L17V1/votes", recent)
    await client.get_votes("VTANR5L17V1")
    now[0] = 3600.0
    await client.get_votes(SCRUTIN_UID)
    await client.get_votes("VTANR5L17V1")
    assert civix_mock.paths().count(f"/scrutins/{SCRUTIN_UID}/votes") == 1
    assert civix_mock.paths().count("/scrutins/VTANR5L17V1/votes") == 2


async def test_exporter_votes_adds_the_group_and_limits_lines(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    directory = load_fixture("deputes_groupe_hor")
    directory["meta"]["pagination"]["next_page"] = None
    civix_mock.add("/deputes", directory, page="1")

    text = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID, max_lignes=3)

    block = text.split("```csv\n")[1].split("\n```")[0]
    rows = list(csv.DictReader(io.StringIO(block)))
    assert len(rows) == 3
    assert "Export limité à 3 lignes (`max_lignes`) sur 17 votes." in text
    full = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID)
    by_name = {
        row["nom"]: row
        for row in csv.DictReader(io.StringIO(full.split("```csv\n")[1].split("\n```")[0]))
    }
    assert by_name["Valletoux"]["groupe"] == "HOR"
    assert by_name["Braun-Pivet"]["groupe"] == ""
