import httpx
import pytest
import respx

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import CivixError, CivixNotFoundError, CivixUnavailableError
from assemblee_mcp.config import Settings
from tests.conftest import API, SCRUTIN_UID, CivixStub, load_fixture


async def test_get_scrutin_parses_model(client: CivixClient) -> None:
    response = await client.get_scrutin(SCRUTIN_UID)
    assert response.attributes.scrutin.uid == SCRUTIN_UID


async def test_cache_hit_avoids_second_request(client: CivixClient, civix_mock: CivixStub) -> None:
    await client.list_groupes()
    await client.list_groupes()
    assert civix_mock.paths() == ["/groupes"]


async def test_cache_key_depends_on_params(client: CivixClient, civix_mock: CivixStub) -> None:
    await client.search("retraites")
    await client.search("retraites", page=2)
    assert civix_mock.paths() == ["/search", "/search"]


async def test_cache_expires_after_ttl(settings: Settings, civix_mock: CivixStub) -> None:
    now = [0.0]
    short = CivixClient(Settings(retry_delay=0.0, cache_ttl=10.0), clock=lambda: now[0])
    await short.list_groupes()
    now[0] = 11.0
    await short.list_groupes()
    assert civix_mock.paths() == ["/groupes", "/groupes"]


async def test_cache_is_bounded(civix_mock: CivixStub) -> None:
    small = CivixClient(Settings(retry_delay=0.0, cache_max_entries=2))
    for page in (1, 2, 3):
        await small.search("retraites", page=page)
    await small.search("retraites", page=1)
    assert len(civix_mock.requests) == 4


async def test_retry_on_503_then_success(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        route = router.get("/groupes").mock(
            side_effect=[httpx.Response(503), httpx.Response(200, json=load_fixture("groupes"))]
        )
        response = await CivixClient(settings).list_groupes()
    assert route.call_count == 2
    assert response.attributes.groups


async def test_two_failures_raise_unavailable(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        route = router.get("/groupes").mock(return_value=httpx.Response(503))
        with pytest.raises(CivixUnavailableError, match="indisponible"):
            await CivixClient(settings).list_groupes()
    assert route.call_count == 2


async def test_timeout_raises_civix_error(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        router.get("/groupes").mock(side_effect=httpx.ReadTimeout("lent"))
        with pytest.raises(CivixError, match="momentanément indisponible"):
            await CivixClient(settings).list_groupes()


async def test_404_is_not_found_without_retry(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        route = router.get("/scrutins/NOPE").mock(
            return_value=httpx.Response(404, json={"error": "Scrutin not found"})
        )
        with pytest.raises(CivixNotFoundError, match="Aucune donnée trouvée"):
            await CivixClient(settings).get_scrutin("NOPE")
    assert route.call_count == 1


async def test_errors_are_not_cached(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        route = router.get("/groupes").mock(
            side_effect=[
                httpx.Response(503),
                httpx.Response(503),
                httpx.Response(200, json=load_fixture("groupes")),
            ]
        )
        client = CivixClient(settings)
        with pytest.raises(CivixError):
            await client.list_groupes()
        assert (await client.list_groupes()).attributes.groups
    assert route.call_count == 3


async def test_invalid_payload_raises_civix_error(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        router.get("/groupes").mock(return_value=httpx.Response(200, json={"inattendu": True}))
        with pytest.raises(CivixError, match="inattendue"):
            await CivixClient(settings).list_groupes()


async def test_non_json_body_raises_civix_error(settings: Settings) -> None:
    with respx.mock(base_url=API) as router:
        router.get("/groupes").mock(return_value=httpx.Response(200, text="<html>"))
        with pytest.raises(CivixError, match="inattendue"):
            await CivixClient(settings).list_groupes()


async def test_sends_user_agent_and_clean_params(
    client: CivixClient, civix_mock: CivixStub
) -> None:
    await client.list_scrutins("retraites", legislature=None, page=2, page_size=5)
    request = civix_mock.requests[0]
    assert request.headers["user-agent"].startswith("mcp-assemblee-nationale")
    assert dict(request.url.params) == {"search": "retraites", "page": "2", "page_size": "5"}


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIVIX_BASE_URL", "https://exemple.test/api/")
    monkeypatch.setenv("CIVIX_TIMEOUT", "3")
    monkeypatch.setenv("CIVIX_CACHE_TTL", "60")
    settings = Settings.from_env()
    assert settings.base_url == "https://exemple.test/api"
    assert settings.timeout == 3.0
    assert settings.cache_ttl == 60.0
