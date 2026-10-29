"""Régressions de l'audit externe des outils (30 octobre 2026)."""

import re
from datetime import date

import pytest
from fastmcp.exceptions import ToolError

from assemblee_mcp import limits
from assemblee_mcp.analytics import gather
from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.budget import CallBudget, current_budget
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import ScrutinSummary
from assemblee_mcp.civix.models.envelope import Source
from assemblee_mcp.civix.models.kinds import classify_scrutin
from assemblee_mcp.civix.search import search_everything
from assemblee_mcp.formatting import format_search
from assemblee_mcp.links import assemblee_scrutin_url
from tests.conftest import (
    PANOSYAN,
    SCRUTIN_UID,
    CivixStub,
    DeputeStub,
    McpClient,
    Payload,
    call,
    deputes_payload,
    load_fixture,
    make_item,
    make_listing,
    search_with_deputes,
)

THIEBAUT = DeputeStub("PA722336", "Vincent", "Thiébaut", "HOR")
TROUVE = DeputeStub("PA795164", "Aurélie", "Trouvé", "LFI-NFP")
TODAY = date(2026, 10, 29)
FINANCE_QUERY = "projet de loi de finances 2027"
PLF_REF = "DLR5L17N54629"
PLF_TITLE = "Projet de loi de finances pour 2027"
MOTION_TITLE = (
    "la motion de rejet préalable, déposée par Mme Panot, du projet de loi (première lecture)."
)


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gather, "current_day", lambda: TODAY)


def with_directory(stub: CivixStub, *deputes: DeputeStub) -> None:
    stub.add("/deputes", deputes_payload(*deputes), page="1")


def deputes_only_search() -> Payload:
    """Réponse de `/search` qui ne renvoie que des députés sans rapport avec la requête."""
    payload = load_fixture("search_depute")
    results = payload["data"]["attributes"]["results"]
    results.update(scrutins=[], dossiers=[], groupes=[])
    return payload


def empty_search_payload() -> Payload:
    payload = load_fixture("search_global")
    payload["data"]["attributes"]["total"] = 0
    payload["data"]["attributes"]["results"] = {
        "deputes": [],
        "scrutins": [],
        "groupes": [],
        "dossiers": [],
    }
    return payload


# --- 1. Un seul résolveur de députés, insensible aux accents -----------------------------------


def test_name_search_variants_cover_accents_words_and_stems() -> None:
    assert lookup.name_search_variants("Thiébaut") == ["Thiébaut", "Thiebaut", "Thi"]
    variants = lookup.name_search_variants("Aurélie Trouvé")
    assert variants == ["Aurélie Trouvé", "Aurelie Trouve", "Aur", "Trouv"]
    assert len(variants) <= limits.MAX_NAME_SEARCHES


@pytest.mark.parametrize(
    "written",
    ["Thiébaut", "Thiebaut", "thiébaut", "THIEBAUT", "Vincent Thiebaut", "thiebaut vincent"],
)
async def test_find_deputes_finds_an_accented_name_however_it_is_typed(
    client: CivixClient, civix_mock: CivixStub, written: str
) -> None:
    with_directory(civix_mock, THIEBAUT, TROUVE)

    found = await lookup.find_deputes(client, written)

    assert [depute.uid for depute in found] == ["PA722336"]


@pytest.mark.parametrize("written", ["Trouvé", "Trouve", "Aurélie Trouvé", "aurelie trouve"])
async def test_find_deputes_finds_trouve_with_or_without_accents(
    client: CivixClient, civix_mock: CivixStub, written: str
) -> None:
    with_directory(civix_mock, THIEBAUT, TROUVE)

    found = await lookup.find_deputes(client, written)

    assert [depute.uid for depute in found] == ["PA795164"]


async def test_the_directory_is_read_once_and_then_replaces_the_search(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    with_directory(civix_mock, THIEBAUT, TROUVE)
    await lookup.find_deputes(client, "Thiebaut")
    requests_after_first = len(civix_mock.requests)

    await lookup.find_deputes(client, "Trouve")

    assert len(civix_mock.requests) == requests_after_first


async def test_a_truncated_search_is_completed_from_the_directory(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    martins = [DeputeStub(f"PA{n}", "Anne", f"Martin{n:02d}", "RN") for n in range(10)]
    civix_mock.add(
        "/search", search_with_deputes(*martins[: limits.SEARCH_CATEGORY_CAP]), search="Martin"
    )
    with_directory(civix_mock, *martins)

    found = await lookup.find_deputes(client, "Martin")

    assert len(found) == 10


@pytest.mark.parametrize("name", ["Thiebaut", "Thiébaut", "Trouvé", "Trouve"])
async def test_comment_a_vote_resolves_the_names_of_the_audit(
    mcp_client: McpClient, civix_mock: CivixStub, name: str
) -> None:
    with_directory(civix_mock, THIEBAUT, TROUVE)

    text = await call(mcp_client, "comment_a_vote", depute=name, sujet="retraites")

    assert "aucun député trouvé" not in text
    assert text.startswith("## Votes de ")


async def test_every_tool_taking_a_deputy_shares_the_resolver(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    with_directory(civix_mock, THIEBAUT, TROUVE)

    listed = await call(mcp_client, "rechercher_deputes", nom="Thiebaut")
    civix_mock.add("/deputes/PA722336", load_fixture("depute_detail"))
    profile = await call(mcp_client, "obtenir_depute", nom="Thiebaut")
    review = await call(mcp_client, "bilan_depute", depute="Thiebaut", periode_jours=30)
    comparison = await call(
        mcp_client, "comparer_deputes", depute_a="Thiebaut", depute_b="Trouve", periode_jours=30
    )

    assert "Vincent Thiébaut" in listed
    assert "## Audrey Abadie-Amiel" in profile
    assert "Votes de Vincent Thiébaut" in review
    assert "Vincent Thiébaut et Aurélie Trouvé" in comparison


async def test_obtenir_depute_needs_exactly_one_of_uid_and_name(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="soit `uid`, soit `nom`"):
        await call(mcp_client, "obtenir_depute")
    with pytest.raises(ToolError, match="soit `uid`, soit `nom`"):
        await call(mcp_client, "obtenir_depute", uid="PA793214", nom="Abadie")


async def test_obtenir_depute_still_accepts_an_uid(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "obtenir_depute", uid="PA793214")

    assert "Audrey Abadie-Amiel" in text


# --- 2. Recherche globale par catégories -------------------------------------------------------


async def test_global_search_drops_deputes_that_do_not_match_the_words(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/search", deputes_only_search(), search=FINANCE_QUERY)
    civix_mock.listings["finances"] = [
        make_item(
            n,
            "2026-10-20",
            dossier_ref="DLR5L17N54629",
            dossier="Projet de loi de finances pour 2027",
        )
        for n in range(3)
    ]

    found = await search_everything(client, FINANCE_QUERY)

    assert found.results.deputes == []
    assert len(found.results.scrutins) == 3
    assert [hit.uid for hit in found.results.dossiers] == [PLF_REF]
    assert found.note is not None
    assert found.note.startswith("Recherche élargie")


async def test_topic_queries_list_dossiers_with_their_reference_before_scrutins(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/search", deputes_only_search(), search=FINANCE_QUERY)
    civix_mock.listings["finances"] = [
        make_item(
            n,
            "2026-10-20",
            dossier_ref="DLR5L17N54629",
            dossier="Projet de loi de finances pour 2027",
        )
        for n in range(3)
    ]

    text = await call(mcp_client, "rechercher", requete=FINANCE_QUERY)

    assert text.index("### Dossiers législatifs") < text.index("### Scrutins")
    assert f"dossier `{PLF_REF}`" in text
    assert "dossier_legislatif" in text
    assert "### Députés" not in text


async def test_name_queries_list_deputes_first(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/search", load_fixture("search_depute"), search="Abadie")

    text = await call(mcp_client, "rechercher", requete="Abadie")

    assert text.index("### Députés") < text.index("### Scrutins")


async def test_scrutins_are_listed_newest_first_and_say_so(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    text = await call(mcp_client, "rechercher", requete="retraites")

    assert "### Scrutins (du plus récent au plus ancien)" in text
    dates = re.findall(r"- (\d+ \w+ \d{4}) · ", text.split("### Scrutins")[1])
    assert dates


async def test_a_deputy_missed_by_search_is_added_from_the_cached_directory(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    with_directory(civix_mock, THIEBAUT, TROUVE)
    await lookup.find_deputes(client, "Thiebaut")

    found = await search_everything(client, "Thiebaut")

    assert [hit.uid for hit in found.results.deputes] == ["PA722336"]
    assert "Vincent Thiébaut" in format_search(found, "Thiebaut")


# --- 3. Classement des scrutins : une motion n'est pas un vote sur l'ensemble ------------------


CLASSIFICATION_CASES = [
    ("texte", MOTION_TITLE, "autre"),
    ("texte", "l'ensemble du projet de loi de finances pour 2027 (première lecture).", "texte"),
    ("texte", "l'ensemble de la proposition de loi visant à créer un corps.", "texte"),
    ("texte", "la proposition de loi organique visant à adapter la justice.", "texte"),
    ("texte", "la demande de suspension de séance formulée par M. Piquemal.", "autre"),
    ("texte", "la proposition du Gouvernement de prolonger la séance.", "autre"),
    ("motion_censure", "la motion de censure déposée en application de l'article 49.", "autre"),
    ("scrutin", "la proposition de résolution invitant le Gouvernement à agir.", "autre"),
    ("amendement", "l'amendement n° 5 de M. Bazin de suppression de l'article 6.", "amendement"),
    ("article", "l'article 38 du projet de loi de finances pour 2027.", "article"),
    (None, "l'ensemble du projet de loi", "autre"),
]


@pytest.mark.parametrize(("civix_type", "title", "expected"), CLASSIFICATION_CASES)
def test_classify_scrutin(civix_type: str | None, title: str, expected: str) -> None:
    assert classify_scrutin(civix_type, title) == expected


def motion_listing() -> list[Payload]:
    motion = make_item(1, "2026-10-20", kind="texte", dossier_ref="DLR1", dossier="PLFSS 2027")
    motion["titre"] = MOTION_TITLE
    whole = make_item(2, "2026-10-21", kind="texte", dossier_ref="DLR2", dossier="Autre texte")
    return [whole, motion]


async def test_a_motion_is_not_returned_as_a_vote_on_the_whole_text(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = motion_listing()

    text = await call(
        mcp_client,
        "scrutins_par_periode",
        date_debut="2026-10-15",
        date_fin="2026-10-29",
        type="texte",
    )
    other = await call(
        mcp_client,
        "scrutins_par_periode",
        date_debut="2026-10-15",
        date_fin="2026-10-29",
        type="autre",
    )

    assert "motion de rejet" not in text
    assert "motion de rejet" in other


async def test_counts_stay_consistent_between_trends_and_texts(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = motion_listing()

    trends = await call(mcp_client, "tendances_scrutins", periode_jours=14)
    texts = await call(mcp_client, "textes_les_plus_votes", periode_jours=14)

    assert "| votes sur l'ensemble d'un texte | 1 |" in trends
    assert "| autres scrutins (motions, résolutions, suspensions de séance…) | 1 |" in trends
    assert re.search(r"PLFSS 2027 .*\| 1 \| 0 / 0 / 0 \|", texts)
    assert re.search(r"Autre texte .*\| 1 \| 0 / 0 / 1 \|", texts)


# --- 4. Fenêtres de dates et vocabulaire de l'échantillon --------------------------------------


@pytest.mark.parametrize(
    ("days", "first_day"), [(14, "2026-10-16"), (7, "2026-10-23"), (30, "2026-09-30")]
)
async def test_periode_jours_covers_exactly_that_many_days_ending_today(
    mcp_client: McpClient, civix_mock: CivixStub, days: int, first_day: str
) -> None:
    civix_mock.listings[None] = make_listing(40, 2)

    text = await call(mcp_client, "tendances_scrutins", periode_jours=days)

    assert f"du {first_day} au 2026-10-29 ({days} jours)" in text


async def test_scrutins_par_periode_does_not_mix_up_read_and_matching_counts(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(10, 5)

    text = await call(
        mcp_client,
        "scrutins_par_periode",
        date_debut="2026-10-20",
        date_fin="2026-10-29",
        type="texte",
    )

    assert "correspondant(s)" not in text
    assert "10 scrutin(s) correspondent aux filtres (type, résultat)." in text
    assert "50 scrutin(s) analysé(s)" in text


# --- 5. exporter_votes -------------------------------------------------------------------------


async def test_exporter_votes_accepts_the_same_maximum_as_exporter_scrutins(
    mcp_client: McpClient,
) -> None:
    with pytest.raises(ToolError):
        await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID, max_lignes=1001)
    text = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID, max_lignes=1000)
    assert "Export CSV : 17 ligne(s)." in text


# --- 6. Échantillons assez grands, et honnêtes quand ils ne le sont pas ------------------------


async def test_the_votes_scan_stops_as_soon_as_enough_scrutins_are_usable(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    summaries = [ScrutinSummary.model_validate(make_item(n, "2026-10-20")) for n in range(40)]

    scan = await gather.scan_votes(client, summaries, lambda votes: True, target=10)

    assert scan.usable == 2 * limits.VOTES_BATCH
    assert len(scan.votes) == 2 * limits.VOTES_BATCH
    assert not scan.stopped_by_budget


async def test_the_votes_scan_keeps_what_it_read_when_the_budget_runs_out(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    summaries = [ScrutinSummary.model_validate(make_item(n, "2026-10-20")) for n in range(40)]
    token = current_budget.set(CallBudget(limits.VOTES_BATCH + 3))
    try:
        scan = await gather.scan_votes(client, summaries, lambda votes: False, target=100)
    finally:
        current_budget.reset(token)

    assert scan.stopped_by_budget
    assert len(scan.votes) >= limits.VOTES_BATCH


async def test_comparing_deputes_who_never_voted_together_explains_why(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    absent = DeputeStub("PA000001", "Absent", "Toujours", "RN")
    with_directory(civix_mock, PANOSYAN, absent)

    text = await call(
        mcp_client,
        "comparer_deputes",
        depute_a="Panosyan",
        depute_b="Toujours",
        periode_jours=30,
    )

    assert "Échantillon trop faible pour conclure" in text
    assert "non calculable : aucun scrutin où les deux ont voté" in text
    assert "n/d" not in text
    assert text.index("Attention") < text.index("## ")


async def test_comparison_keeps_scanning_until_enough_comparable_scrutins(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(40, 8)
    with_directory(civix_mock, PANOSYAN, DeputeStub("PA795350", "Frédéric", "Valletoux", "HOR"))

    text = await call(
        mcp_client,
        "comparer_deputes",
        depute_a="Panosyan",
        depute_b="Valletoux",
        periode_jours=30,
        max_scrutins=60,
    )

    assert "Échantillon trop faible" not in text
    examined = int(re.search(r"Scrutins de l'échantillon : (\d+)", text).group(1))  # type: ignore[union-attr]
    assert limits.TARGET_USABLE_SCRUTINS <= examined < 60


async def test_close_votes_without_result_say_what_was_scanned(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(30, 3)

    text = await call(mcp_client, "votes_serres", periode_jours=30)

    assert "Aucun des 30 scrutin(s) parcourus n'a un écart de 20 voix ou moins" in text
    assert "Le plus serré était de 81 voix" in text
    assert "Pour élargir" in text


async def test_group_analyses_warn_when_the_sample_is_small(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(1, 4)

    text = await call(mcp_client, "accords_entre_groupes", periode_jours=30)

    assert "Échantillon trop faible pour conclure" in text
    assert "paire(s) de groupes ont moins de" in text


async def test_heaviest_analyses_stay_within_the_call_budget(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings[None] = make_listing(45, 10)
    with_directory(civix_mock, PANOSYAN, DeputeStub("PA000001", "Absent", "Toujours", "RN"))

    await call(
        mcp_client,
        "comparer_deputes",
        depute_a="Panosyan",
        depute_b="Toujours",
        periode_jours=30,
        max_scrutins=limits.MAX_ANALYSED_SCRUTINS,
    )

    assert len(civix_mock.requests) <= limits.ANALYTICS_MAX_CALLS + limits.MAX_DIRECTORY_PAGES


# --- 7. Lien de l'Assemblée nationale ----------------------------------------------------------


def test_assemblee_scrutin_url_is_built_from_legislature_and_number() -> None:
    assert (
        assemblee_scrutin_url(17, 9231) == "https://www.assemblee-nationale.fr/dyn/17/scrutins/9231"
    )
    assert (
        assemblee_scrutin_url(16, 1234) == "https://www.assemblee-nationale.fr/dyn/16/scrutins/1234"
    )
    assert assemblee_scrutin_url(None, 9231) is None
    assert assemblee_scrutin_url(17, None) is None


def test_civix_scrutin_links_with_the_jo_prefix_are_ignored() -> None:
    source = Source(
        source_urls=[
            "https://www.assemblee-nationale.fr/dyn/17/scrutins/jo9231",
            "https://www.assemblee-nationale.fr/dyn/deputes/PA793214",
        ]
    )

    assert source.assemblee_url == "https://www.assemblee-nationale.fr/dyn/deputes/PA793214"


SCRUTIN_TOOL_CALLS = [
    ("obtenir_scrutin", {"uid": SCRUTIN_UID}),
    ("votes_scrutin", {"uid": SCRUTIN_UID}),
    ("exporter_votes", {"scrutin_uid": SCRUTIN_UID}),
    ("comment_a_vote", {"depute": "Abadie", "scrutin_uid": SCRUTIN_UID}),
    ("comment_a_vote", {"depute": "Abadie", "sujet": "retraites"}),
    ("fetch", {"id": f"scrutin:{SCRUTIN_UID}"}),
    ("rechercher_scrutins", {"mots_cles": "retraites"}),
    ("declarations_groupes", {"uid": SCRUTIN_UID}),
    ("bilan_depute", {"depute": "Abadie", "sujet": "retraites", "max_scrutins": 3}),
]


@pytest.mark.parametrize(("tool", "arguments"), SCRUTIN_TOOL_CALLS)
async def test_no_output_contains_a_broken_assemblee_scrutin_link(
    mcp_client: McpClient, tool: str, arguments: dict[str, object]
) -> None:
    text = await call(mcp_client, tool, **arguments)

    assert "/scrutins/jo" not in text


async def test_scrutin_outputs_link_to_the_working_assemblee_page(
    mcp_client: McpClient,
) -> None:
    expected = "https://www.assemblee-nationale.fr/dyn/17/scrutins/7324"

    detail = await call(mcp_client, "obtenir_scrutin", uid=SCRUTIN_UID)
    votes = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID)
    export = await call(mcp_client, "exporter_votes", scrutin_uid=SCRUTIN_UID)
    metadata = await call(mcp_client, "fetch", id=f"scrutin:{SCRUTIN_UID}")

    assert all(expected in text for text in (detail, votes, export, metadata))


async def test_without_number_or_legislature_only_the_civix_page_is_given(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    payload = load_fixture("scrutin_detail")
    payload["data"]["attributes"]["scrutin"]["numero"] = None
    civix_mock.add(f"/scrutins/{SCRUTIN_UID}", payload)

    text = await call(mcp_client, "obtenir_scrutin", uid=SCRUTIN_UID)

    assert f"Source : CIVIX https://www.civix.fr/votes/{SCRUTIN_UID}\n" in text
    assert "assemblee-nationale.fr" not in text


# --- « Non testé » de l'audit -----------------------------------------------------------------


async def test_rechercher_scrutins_second_page(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings["budget"] = [
        make_item(n, "2026-10-20", dossier="Budget") for n in range(15)
    ]

    first = await call(mcp_client, "rechercher_scrutins", mots_cles="budget")
    second = await call(mcp_client, "rechercher_scrutins", mots_cles="budget", page=2)

    assert first.count("uid : `") == limits.DEFAULT_PAGE_SIZE
    assert second.count("uid : `") == 5
    assert "demandez la page 2" in first


async def test_invalid_identifiers_give_clean_french_errors(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="Aucune donnée trouvée"):
        await call(mcp_client, "obtenir_scrutin", uid="NOPE")
    with pytest.raises(ToolError, match="Aucune donnée trouvée"):
        await call(mcp_client, "obtenir_depute", uid="PA000000")


async def test_rechercher_scrutins_legislature_16(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    text = await call(mcp_client, "rechercher_scrutins", mots_cles="retraites", legislature=16)

    assert "legislature=16" in str(civix_mock.requests[0].url)
    assert text.startswith("## Scrutins")
