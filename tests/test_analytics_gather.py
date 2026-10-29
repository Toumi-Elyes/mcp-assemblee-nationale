import csv
import io
import json
from datetime import date

from assemblee_mcp.analytics import exporting, gather, render
from assemblee_mcp.analytics.models import Method, Rate, Stance
from assemblee_mcp.analytics.stats import trends
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import ScrutinSummary
from tests.conftest import CivixStub, make_item, make_listing


async def test_fetch_period_scans_from_the_newest_page(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(60, 10)
    found = await gather.fetch_period(client, date(2026, 10, 20), date(2026, 10, 29))
    assert len(found.items) == 100
    assert not found.truncated
    assert len(civix_mock.requests) <= 1 + gather.BATCH_PAGES + 1


async def test_fetch_period_in_the_past_jumps_with_a_binary_search(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(300, 10)
    found = await gather.fetch_period(client, date(2026, 3, 1), date(2026, 3, 5))
    days = {item.date_scrutin.date() for item in found.items if item.date_scrutin}
    assert days == {date(2026, 3, day) for day in range(1, 6)}
    assert len(civix_mock.requests) <= 15


async def test_fetch_period_caps_pages_and_flags_truncation(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(200, 20)
    found = await gather.fetch_period(client, date(2026, 1, 1), date(2026, 10, 29))
    assert found.truncated
    assert found.pages == gather.MAX_LIST_PAGES
    assert len(found.items) == gather.MAX_LIST_PAGES * gather.LIST_PAGE_SIZE


async def test_fetch_period_with_no_scrutin(client: CivixClient, civix_mock: CivixStub) -> None:
    civix_mock.listings[None] = make_listing(10, 5)
    found = await gather.fetch_period(client, date(2025, 1, 1), date(2025, 1, 31))
    assert found.items == []
    assert not found.truncated


def test_select_kind() -> None:
    items = [
        ScrutinSummary.model_validate(make_item(1, "2026-10-01", kind="texte")),
        ScrutinSummary.model_validate(make_item(2, "2026-10-01", kind="amendement")),
    ]
    assert [i.numero for i in gather.select_kind(items, "texte")] == [1]
    assert len(gather.select_kind(items, None)) == 2


def test_csv_export_uses_real_newlines_and_neutralises_formulas() -> None:
    rows: list[exporting.Row] = [{"a": "=1+1", "b": 'ok, "quoted"'}, {"a": "-5", "b": None}]
    text = exporting.to_csv(("a", "b"), rows)
    assert "\\n" not in text
    parsed = list(csv.reader(io.StringIO(text)))
    assert parsed == [["a", "b"], ["'=1+1", 'ok, "quoted"'], ["'-5", ""]]


def test_json_export_keeps_types_and_strips_hidden_characters() -> None:
    rows: list[exporting.Row] = [{"a": "x\u200b\x00y", "b": 3, "c": True}]
    assert json.loads(exporting.to_json(("a", "b", "c"), rows)) == [{"a": "xy", "b": 3, "c": True}]


def test_method_block_flags_truncation_and_limits() -> None:
    method = Method(
        period="p",
        analysed=3,
        matching=10,
        counted="c",
        limits=["l1"],
        truncated=True,
        notes=["n1"],
    )
    text = render.method_block(method)
    assert "3 scrutin(s) analysé(s) sur 10 correspondant(s)" in text
    assert "Échantillon tronqué" in text
    assert "- Limite : l1" in text
    assert "- n1" in text


def test_renders_use_factual_wording_only() -> None:
    items = [ScrutinSummary.model_validate(make_item(n, "2026-10-01")) for n in range(3)]
    method = Method(analysed=3, counted="c")
    text = render.render_trends(trends(items, date(2026, 10, 1), date(2026, 10, 7)), method)
    for word in ("meilleur", "pire", "fidèle", "loyal", "déloyal", "absentéiste"):
        assert word not in text.casefold()


def test_percent_and_symbols() -> None:
    assert render.percent(0.666) == "67 %"
    assert render.percent(None) == "n/d"
    assert Rate(label="x", total=0, adopted=0, rejected=0).rate is None
    assert set(render.STANCE_SYMBOLS) == set(Stance)
