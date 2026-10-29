import pytest

from assemblee_mcp import limits
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.search import broaden, contains_all, search_everything, search_scrutins
from tests.conftest import CivixStub, Payload, load_fixture


def scrutin_items(titles: list[str]) -> list[Payload]:
    template = load_fixture("search_scrutins")["data"]["attributes"]["results"][0]
    return [
        {**template, "uid": f"VTANR5L17V{n}", "titre": title, "objet": {"libelle": title}}
        for n, title in enumerate(titles)
    ]


def scrutins_payload(titles: list[str], *, next_page: int | None = None) -> Payload:
    payload = load_fixture("search_scrutins")
    payload["data"]["attributes"]["results"] = scrutin_items(titles)
    payload["meta"]["pagination"].update(
        count_total=len(titles), count_returned=len(titles), next_page=next_page
    )
    return payload


def empty_scrutins() -> Payload:
    return scrutins_payload([])


def test_broaden_drops_stopwords_and_keeps_year_as_filter() -> None:
    broad = broaden("la loi de finances 2027")
    assert broad is not None
    assert broad.term == "finances"
    assert broad.required == ("finances", "2027")


def test_broaden_keeps_accented_term_and_ignores_single_words() -> None:
    broad = broaden("réforme de l'assurance chômage")
    assert broad is not None
    assert broad.term == "assurance"
    assert broad.required == ("reforme", "assurance", "chomage")
    assert broaden("finances") is None
    assert broaden("de la") is None


def test_broaden_uses_year_when_it_is_the_only_content() -> None:
    broad = broaden("de 2027")
    assert broad is not None
    assert broad.term == "2027"


def test_contains_all_ignores_accents_and_case() -> None:
    assert contains_all("Projet de LOI de finances pour 2027", ("finances", "2027"))
    assert contains_all("assurance chômage", ("chomage",))
    assert not contains_all("loi de finances rectificative", ("2027",))


async def test_exact_query_hit_makes_one_call(client: CivixClient, civix_mock: CivixStub) -> None:
    found = await search_scrutins(client, "retraites")
    assert found.note is None
    assert len(found.results) == 3
    assert civix_mock.paths() == ["/scrutins"]


async def test_fallback_filters_pool_and_notes_it(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings["finances"] = scrutin_items(
        [
            "le projet de loi de finances pour 2027",
            "le projet de loi de finances pour 2026",
            "l'article 2 du projet de loi de finances pour 2027",
        ]
    )
    found = await search_scrutins(client, "loi de finances 2027")
    assert [s.uid for s in found.results] == ["VTANR5L17V0", "VTANR5L17V2"]
    assert found.note is not None
    assert found.note.startswith("Recherche élargie")
    assert found.pagination is not None
    assert found.pagination.total == 2
    assert len(civix_mock.requests) == 2


async def test_fallback_reads_only_the_announced_pages_up_to_the_limit(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    civix_mock.listings["finances"] = scrutin_items(["loi de finances pour 2027"] * 700)
    found = await search_scrutins(client, "loi de finances 2027")
    assert len(civix_mock.requests) == 1 + limits.BROAD_POOL_PAGES
    assert found.note is not None
    assert (
        f"{limits.CIVIX_PAGE_SIZE * limits.BROAD_POOL_PAGES} scrutins les plus récents"
        in found.note
    )


async def test_fallback_paginates_locally(client: CivixClient, civix_mock: CivixStub) -> None:
    titles = [f"loi de finances pour 2027 n°{n}" for n in range(12)]
    civix_mock.listings["finances"] = scrutin_items(titles)
    first = await search_scrutins(client, "loi de finances 2027", page_size=10)
    assert len(first.results) == 10
    assert first.pagination is not None
    assert first.pagination.next_page == 2
    second = await search_scrutins(client, "loi de finances 2027", page=2, page_size=10)
    assert len(second.results) == 2
    assert second.pagination is not None
    assert second.pagination.next_page is None


async def test_still_nothing_after_fallback(client: CivixClient, civix_mock: CivixStub) -> None:
    civix_mock.add("/scrutins", empty_scrutins(), search="zzz yyy")
    civix_mock.add("/scrutins", empty_scrutins(), search="zzz")
    found = await search_scrutins(client, "zzz yyy")
    assert found.results == []
    assert found.note is not None


async def test_single_word_never_falls_back(client: CivixClient, civix_mock: CivixStub) -> None:
    civix_mock.add("/scrutins", empty_scrutins(), search="zzz")
    found = await search_scrutins(client, "zzz")
    assert found.results == []
    assert found.note is None
    assert len(civix_mock.requests) == 1


async def test_global_search_fallback(client: CivixClient, civix_mock: CivixStub) -> None:
    empty = load_fixture("search_global")
    empty["data"]["attributes"]["total"] = 0
    empty["data"]["attributes"]["results"] = {
        "deputes": [],
        "scrutins": [],
        "groupes": [],
        "dossiers": [],
    }
    civix_mock.add("/search", empty, search="réformer les retraites agricoles")
    civix_mock.add("/search", empty, search="retraites", page="2")
    found = await search_everything(client, "réformer les retraites agricoles")
    assert found.note is not None
    assert found.results.scrutins == []
    civix_mock.overrides.clear()
    civix_mock.add("/search", empty, search="pensions retraites agricoles")
    broad = await search_everything(client, "pensions retraites agricoles")
    assert broad.note is not None
    assert broad.total > 0
    assert all("agricoles" in s.titre for s in broad.results.scrutins)


@pytest.mark.parametrize("query", ["retraites", "Abadie"])
async def test_global_search_exact_hit(client: CivixClient, query: str) -> None:
    found = await search_everything(client, query)
    assert found.note is None
    assert found.total > 0
