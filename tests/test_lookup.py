import pytest

from assemblee_mcp.civix import lookup
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.models import Depute
from assemblee_mcp.textutils import fold
from tests.conftest import CivixStub, load_fixture


def make_depute(prenom: str, nom: str) -> Depute:
    return Depute(uid=f"PA{abs(hash(nom)) % 10000}", prenom=prenom, nom=nom)


def test_fold_ignores_accents_case_and_hyphens() -> None:
    assert fold("Jean-Luc MÉLENCHON") == "jean luc melenchon"
    assert fold("L'Hôpital") == "l hopital"


def test_rank_by_name_requires_all_tokens_and_prefers_exact_words() -> None:
    deputes = [
        make_depute("Éric", "Martineau"),
        make_depute("Élisa", "Martin"),
        make_depute("Patrice", "Dupont"),
    ]
    ranked = lookup.rank_by_name(deputes, "martin")
    assert [d.nom for d in ranked] == ["Martin", "Martineau"]
    assert lookup.rank_by_name(deputes, "élisa martin")[0].nom == "Martin"
    assert lookup.rank_by_name(deputes, "inconnu") == []
    assert lookup.rank_by_name(deputes, "  ") == []


def test_is_exact_name_accepts_either_order() -> None:
    depute = make_depute("Audrey", "Abadie-Amiel")
    assert lookup.is_exact_name(depute, "abadie amiel audrey")
    assert not lookup.is_exact_name(depute, "Audrey")


async def test_find_deputes_uses_search_first(client: CivixClient, civix_mock: CivixStub) -> None:
    found = await lookup.find_deputes(client, "Abadie")
    assert [d.uid for d in found] == ["PA793214"]
    assert civix_mock.paths() == ["/search"]


async def test_find_deputes_falls_back_to_directory_without_accents(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    payload = load_fixture("deputes")
    payload["meta"]["pagination"]["next_page"] = None
    civix_mock.add("/deputes", payload, page="1")
    found = await lookup.find_deputes(client, "abadie amiel")
    assert [d.nom for d in found] == ["Abadie-Amiel"]
    assert civix_mock.paths() == ["/search", "/deputes"]


async def test_find_deputes_by_uid(client: CivixClient) -> None:
    found = await lookup.find_deputes(client, "pa793214")
    assert found[0].full_name == "Audrey Abadie-Amiel"


async def test_find_deputes_filters_group(client: CivixClient) -> None:
    assert await lookup.find_deputes(client, "Abadie", groupe="liot")
    result = await lookup.find_deputes(client, "Abadie", groupe="RN")
    assert result == []


async def test_group_member_uids_and_abbreviations(client: CivixClient) -> None:
    members = await lookup.groupe_member_uids(client, "LIOT")
    assert "PA719138" in members
    abbreviations = await lookup.groupe_abbreviations(client)
    assert abbreviations["PO845485"] == "LIOT"
    found = await lookup.find_groupe(client, "liot")
    assert found is not None
    assert found.abbr == "LIOT"
    assert await lookup.find_groupe(client, "ZZZ") is None


@pytest.mark.parametrize("total", [120, 151])
async def test_all_deputes_fetches_remaining_pages(
    client: CivixClient, civix_mock: CivixStub, total: int
) -> None:
    for page in ("1", "2", "3", "4"):
        payload = load_fixture("deputes_groupe_liot")
        payload["meta"]["pagination"].update(
            count_estimated=total, next_page=None if page == "4" else int(page) + 1
        )
        civix_mock.add("/deputes", payload, page=page, groupe="RN")
    per_page = len(load_fixture("deputes_groupe_liot")["data"]["attributes"]["results"])
    deputes = await lookup.all_deputes(client, groupe="RN")
    pages = sorted(r.url.params["page"] for r in civix_mock.requests)
    assert pages == [str(n) for n in range(1, (total + 49) // 50 + 1)]
    assert len(deputes) == per_page * len(pages)
