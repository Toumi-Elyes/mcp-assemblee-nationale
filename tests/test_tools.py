import json

import pytest
from fastmcp.exceptions import ToolError

from tests.conftest import (
    PANOSYAN,
    SCRUTIN_UID,
    VALLETOUX,
    CivixStub,
    DeputeStub,
    McpClient,
    call,
    load_fixture,
    search_with_deputes,
)

EXPECTED_TOOLS = {
    "rechercher",
    "rechercher_scrutins",
    "obtenir_scrutin",
    "votes_scrutin",
    "declarations_groupes",
    "rechercher_deputes",
    "obtenir_depute",
    "comment_a_vote",
    "lister_groupes",
    "obtenir_groupe",
    "search",
    "fetch",
    "tendances_scrutins",
    "suivre_sujet",
    "textes_les_plus_votes",
    "dossier_legislatif",
    "scrutins_par_periode",
    "statistiques_assemblee",
    "positions_groupes",
    "accords_entre_groupes",
    "cohesion_groupes",
    "votes_serres",
    "bilan_depute",
    "comparer_deputes",
    "exporter_scrutins",
    "exporter_votes",
}


async def test_all_tools_are_registered_read_only(mcp_client: McpClient) -> None:
    tools = await mcp_client.list_tools()
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
    for tool in tools:
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.open_world_hint is True
        assert tool.annotations.idempotent_hint is True
        assert tool.description


async def test_tool_schemas_are_documented_in_french(mcp_client: McpClient) -> None:
    tools = {tool.name: tool for tool in await mcp_client.list_tools()}
    schema = tools["votes_scrutin"].input_schema
    assert "Identifiant du scrutin" in schema["properties"]["uid"]["description"]
    assert schema["properties"]["position"]["anyOf"][0]["enum"] == [
        "pour",
        "contre",
        "abstention",
        "non_votant",
    ]
    assert schema["required"] == ["uid"]
    assert tools["rechercher_scrutins"].input_schema["properties"]["page"]["minimum"] == 1


async def test_rechercher(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher", requete="retraites")
    assert "### Scrutins" in text
    assert "Source : CIVIX" in text


async def test_rechercher_scrutins(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher_scrutins", mots_cles="retraites")
    assert "VTANR5L17V7324" in text
    assert "demandez la page 2" in text


async def test_rechercher_scrutins_empty(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher_scrutins", mots_cles="zzzz")
    assert "Aucun scrutin trouvé" in text


async def test_obtenir_scrutin_includes_group_names(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "obtenir_scrutin", uid=SCRUTIN_UID)
    assert "| RN |" in text
    assert "Décompte : 82 pour" in text


async def test_obtenir_scrutin_survives_group_list_failure(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/groupes", {"error": "boom"}, status=500)
    text = await call(mcp_client, "obtenir_scrutin", uid=SCRUTIN_UID)
    assert "| PO845401 |" in text


async def test_unknown_scrutin_gives_clean_french_error(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match="Aucune donnée trouvée"):
        await call(mcp_client, "obtenir_scrutin", uid="NOPE")


async def test_upstream_down_gives_clean_french_error(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add(f"/scrutins/{SCRUTIN_UID}", {}, status=503)
    with pytest.raises(ToolError, match="momentanément indisponible") as error:
        await call(mcp_client, "obtenir_scrutin", uid=SCRUTIN_UID)
    assert "Traceback" not in str(error.value)


async def test_invalid_uid_is_rejected_by_schema(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError):
        await call(mcp_client, "obtenir_scrutin", uid="../etc/passwd")


async def test_votes_scrutin_unfiltered(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID)
    assert "Décompte officiel : 82 pour" in text
    assert "### Contre (1)\nCarole Guillerm" in text


async def test_votes_scrutin_by_group_and_position(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID, groupe="hor")
    assert "groupe HOR" in text
    assert "### Abstention (3)" in text
    assert "Valletoux" in text
    assert "Castellani" not in text
    none = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID, groupe="HOR", position="pour")
    assert "Aucun vote ne correspond" in none


async def test_votes_scrutin_by_accentless_name(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID, nom="yael")
    assert "Yaël Braun-Pivet" in text
    assert "1 vote(s)" in text


async def test_votes_scrutin_unknown_group_lists_groups(mcp_client: McpClient) -> None:
    with pytest.raises(ToolError, match=r"Groupes disponibles : .*RN"):
        await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID, groupe="XYZ")


async def test_votes_scrutin_caps_names_at_sixty(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    payload = load_fixture("scrutin_votes")
    payload["data"]["attributes"]["votes"] = [
        {"deputy_uid": f"PA{n}", "prenom": "Anne", "nom": f"Nom{n:03d}", "position": "pour"}
        for n in range(100)
    ]
    civix_mock.add(f"/scrutins/{SCRUTIN_UID}/votes", payload)
    text = await call(mcp_client, "votes_scrutin", uid=SCRUTIN_UID)
    assert "### Pour (100)" in text
    assert "Nom059" in text
    assert "Nom060" not in text
    assert "… et 40 autres." in text
    assert "Décompte officiel" in text


async def test_declarations_groupes(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "declarations_groupes", uid=SCRUTIN_UID)
    assert "**RN**" in text
    assert "> Le groupe explique sa position publique." in text


async def test_declarations_groupes_empty(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.add(f"/scrutins/{SCRUTIN_UID}/statements", load_fixture("scrutin_statements_empty"))
    text = await call(mcp_client, "declarations_groupes", uid=SCRUTIN_UID)
    assert "Aucune déclaration" in text


async def test_rechercher_deputes_by_name(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher_deputes", nom="Abadie")
    assert "Audrey Abadie-Amiel" in text
    assert "`PA793214`" in text


async def test_rechercher_deputes_listing(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher_deputes", groupe="LIOT")
    assert "Michel Castellani" in text


async def test_rechercher_deputes_not_found(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "rechercher_deputes", nom="Zzzzz")
    assert "aucun député trouvé" in text


async def test_obtenir_depute(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "obtenir_depute", uid="PA793214")
    assert "Audrey Abadie-Amiel" in text
    assert "Source : CIVIX https://www.civix.fr/deputes/PA793214" in text


async def test_groupes_tools(mcp_client: McpClient) -> None:
    listing = await call(mcp_client, "lister_groupes")
    assert "**RN**" in listing
    detail = await call(mcp_client, "obtenir_groupe", abbr="liot")
    assert "Libertés, Indépendants" in detail
    with pytest.raises(ToolError, match="lister_groupes"):
        await call(mcp_client, "obtenir_groupe", abbr="ZZZ")


async def test_comment_a_vote_on_subject(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.add("/search", search_with_deputes(VALLETOUX), search="Frédéric Valletoux")
    text = await call(mcp_client, "comment_a_vote", depute="Frédéric Valletoux", sujet="retraites")
    assert "## Votes de Frédéric Valletoux (HOR)" in text
    assert text.count("A voté : **Abstention**") == 3
    assert "https://www.civix.fr/votes/VTANR5L17V7324" in text
    assert "https://www.assemblee-nationale.fr/dyn/17/scrutins/7324" in text
    assert civix_mock.paths()[:2] == ["/search", "/scrutins"]
    votes_calls = [path for path in civix_mock.paths() if path.endswith("/votes")]
    assert len(votes_calls) == 3
    assert len(civix_mock.requests) == 5


async def test_comment_a_vote_by_delegation(mcp_client: McpClient, civix_mock: CivixStub) -> None:
    civix_mock.add("/search", search_with_deputes(PANOSYAN), search="Panosyan-Bouvet")
    text = await call(
        mcp_client, "comment_a_vote", depute="Panosyan-Bouvet", scrutin_uid=SCRUTIN_UID
    )
    assert "A voté : **Abstention** (par délégation)." in text


async def test_comment_a_vote_without_recorded_vote(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "comment_a_vote", depute="Abadie", scrutin_uid=SCRUTIN_UID)
    assert "Aucun vote enregistré" in text


async def test_comment_a_vote_ambiguous_deputy_lists_candidates(
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
    text = await call(mcp_client, "comment_a_vote", depute="Martin", sujet="retraites")
    assert "Plusieurs députés correspondent" in text
    assert "Élisa Martin" in text
    assert "Patrice Martin" in text
    assert not any(path.endswith("/votes") for path in civix_mock.paths())


async def test_comment_a_vote_exact_name_resolves_ambiguity(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add(
        "/search",
        search_with_deputes(
            DeputeStub("PA1", "Élisa", "Martin", "LFI-NFP"),
            DeputeStub("PA2", "Élisabeth", "Martineau", "RN"),
        ),
        search="élisa martin",
    )
    text = await call(mcp_client, "comment_a_vote", depute="élisa martin", scrutin_uid=SCRUTIN_UID)
    assert "## Votes de Élisa Martin" in text


async def test_comment_a_vote_unknown_deputy(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "comment_a_vote", depute="Zzzzz Yyyyy", sujet="retraites")
    assert "aucun député trouvé" in text


async def test_comment_a_vote_unknown_subject(mcp_client: McpClient) -> None:
    text = await call(mcp_client, "comment_a_vote", depute="Abadie", sujet="zzzz")
    assert "Aucun scrutin trouvé" in text


async def test_comment_a_vote_tolerates_one_failing_scrutin(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    civix_mock.add("/scrutins/VTANR5L17V7323/votes", {}, status=503)
    text = await call(mcp_client, "comment_a_vote", depute="Abadie", sujet="retraites")
    assert "momentanément indisponibles" in text
    assert "Aucun vote enregistré" in text


@pytest.mark.parametrize("arguments", [{}, {"sujet": "a", "scrutin_uid": SCRUTIN_UID}])
async def test_comment_a_vote_needs_exactly_one_target(
    mcp_client: McpClient, arguments: dict[str, str]
) -> None:
    with pytest.raises(ToolError, match="soit `sujet`, soit `scrutin_uid`"):
        await call(mcp_client, "comment_a_vote", depute="Abadie", **arguments)


async def test_search_returns_chatgpt_json(mcp_client: McpClient) -> None:
    payload = json.loads(await call(mcp_client, "search", query="retraites"))
    results = payload["results"]
    assert results
    assert all(set(result) == {"id", "title", "url"} for result in results)
    scrutins = [result for result in results if result["id"].startswith("scrutin:")]
    assert scrutins
    assert scrutins[0]["url"].startswith("https://www.civix.fr/votes/")


async def test_search_includes_deputes_and_groups(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    payload = load_fixture("search_depute")
    payload["data"]["attributes"]["results"]["groupes"] = [
        {"uid": "PO845485", "libelle": "LIOT", "abbr": "LIOT"}
    ]
    civix_mock.add("/search", payload, search="Abadie")
    found = json.loads(await call(mcp_client, "search", query="Abadie"))
    ids = [item["id"] for item in found["results"]]
    assert "depute:PA793214" in ids
    assert "groupe:LIOT" in ids


@pytest.mark.parametrize(
    ("identifier", "expected_type"),
    [
        (f"scrutin:{SCRUTIN_UID}", "scrutin"),
        ("depute:PA793214", "depute"),
        ("groupe:LIOT", "groupe"),
    ],
)
async def test_fetch(mcp_client: McpClient, identifier: str, expected_type: str) -> None:
    payload = json.loads(await call(mcp_client, "fetch", id=identifier))
    assert set(payload) == {"id", "title", "text", "url", "metadata"}
    assert payload["id"] == identifier
    assert payload["metadata"]["type"] == expected_type
    assert payload["text"]
    assert payload["url"].startswith("https://www.civix.fr/")


async def test_fetch_scrutin_metadata(mcp_client: McpClient) -> None:
    payload = json.loads(await call(mcp_client, "fetch", id=f"scrutin:{SCRUTIN_UID}"))
    assert payload["metadata"]["date"] == "2026-06-04"
    assert payload["metadata"]["adopte"] is True
    assert "| RN |" in payload["text"]


@pytest.mark.parametrize("identifier", ["VTANR5L17V7324", "truc:123", "scrutin:"])
async def test_fetch_rejects_bad_ids(mcp_client: McpClient, identifier: str) -> None:
    with pytest.raises(ToolError, match=r"[Ii]dentifiant"):
        await call(mcp_client, "fetch", id=identifier)


async def test_rechercher_scrutins_broadened_search_is_announced(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    empty = load_fixture("search_scrutins")
    empty["data"]["attributes"]["results"] = []
    empty["meta"]["pagination"].update(count_total=0, next_page=None)
    civix_mock.add("/scrutins", empty, search="pensions de retraites agricoles")
    text = await call(
        mcp_client, "rechercher_scrutins", mots_cles="pensions de retraites agricoles"
    )
    assert "Recherche élargie" in text
    assert "VTANR5L17V7324" in text


async def test_comment_a_vote_uses_broadened_subject(
    mcp_client: McpClient, civix_mock: CivixStub
) -> None:
    empty = load_fixture("search_scrutins")
    empty["data"]["attributes"]["results"] = []
    empty["meta"]["pagination"].update(count_total=0, next_page=None)
    civix_mock.add("/scrutins", empty, search="pensions de retraites agricoles")
    text = await call(
        mcp_client, "comment_a_vote", depute="Abadie", sujet="pensions de retraites agricoles"
    )
    assert "Recherche élargie" in text
    assert "Aucun vote enregistré" in text
