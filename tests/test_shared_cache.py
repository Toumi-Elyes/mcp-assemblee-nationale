import pytest

from assemblee_mcp.civix import shared_cache
from assemblee_mcp.civix.budget import CallBudget, current_budget
from assemblee_mcp.civix.client import CivixClient, shared_kind
from assemblee_mcp.civix.shared_cache import SharedCache, hash_key, running_on_vercel
from assemblee_mcp.config import IMMUTABLE_TTL_SECONDS, Settings
from assemblee_mcp.limits import SHARED_CACHE_MAX_BYTES
from tests.conftest import SCRUTIN_UID, CivixStub
from tests.fakes import BrokenBackend, FakeBackend, HangingBackend


def instance(backend: FakeBackend, max_bytes: int = SHARED_CACHE_MAX_BYTES) -> CivixClient:
    """Une nouvelle instance Vercel : cache mémoire vide, même stockage partagé."""
    return CivixClient(
        Settings(retry_delay=0.0), shared_cache=SharedCache(backend, max_bytes=max_bytes)
    )


async def test_miss_then_hit_roundtrip() -> None:
    cache = SharedCache(FakeBackend())
    assert await cache.get("a") is None
    await cache.put("a", "test", {"x": [1, 2]}, ttl=60)
    found = await cache.get("a")
    assert found is not None
    assert found[0] == {"x": [1, 2]}
    assert 0 < found[1] <= 60


async def test_entry_expires_with_the_wall_clock() -> None:
    now = [1000.0]
    cache = SharedCache(FakeBackend(), wall_clock=lambda: now[0])
    await cache.put("a", "test", 1, ttl=60)
    now[0] = 1059.0
    assert await cache.get("a") is not None
    now[0] = 1061.0
    assert await cache.get("a") is None


async def test_keys_are_versioned(monkeypatch: pytest.MonkeyPatch) -> None:
    backend = FakeBackend()
    await SharedCache(backend).put("a", "test", 1, ttl=60)
    assert next(iter(backend.entries)).startswith("v1:")
    monkeypatch.setattr(shared_cache, "SHARED_CACHE_SCHEMA_VERSION", 2)
    assert await SharedCache(backend).get("a") is None


async def test_an_entry_stored_under_another_key_is_ignored() -> None:
    backend = FakeBackend()
    cache = SharedCache(backend)
    await cache.put("a", "test", "données de a", ttl=60)
    backend.entries["v1:b"] = backend.entries.pop("v1:a")
    assert await cache.get("b") is None


async def test_tags_name_the_kind() -> None:
    backend = FakeBackend()
    await SharedCache(backend).put("a", "scrutin-votes", 1, ttl=60)
    assert next(iter(backend.entries.values())).tags == ("civix", "civix:scrutin-votes")


async def test_oversize_items_are_skipped() -> None:
    backend = FakeBackend()
    cache = SharedCache(backend, max_bytes=100)
    await cache.put("big", "test", "x" * 200, ttl=60)
    assert backend.writes == 0
    await cache.put("small", "test", "x", ttl=60)
    assert backend.writes == 1


async def test_a_broken_backend_never_raises_and_is_paused() -> None:
    now = [0.0]
    backend = BrokenBackend()
    cache = SharedCache(backend, clock=lambda: now[0], cooldown=60.0)
    assert await cache.get("a") is None
    await cache.put("a", "test", 1, ttl=60)
    assert await cache.get("a") is None
    assert (backend.reads, backend.writes) == (1, 0)
    now[0] = 61.0
    assert await cache.get("a") is None
    assert backend.reads == 2


async def test_a_hanging_backend_times_out() -> None:
    cache = SharedCache(HangingBackend(), timeout=0.01)
    assert await cache.get("a") is None


async def test_without_a_backend_the_cache_is_inactive() -> None:
    cache = SharedCache()
    assert not cache.enabled
    await cache.put("a", "test", 1, ttl=60)
    assert await cache.get("a") is None


def test_hash_is_sha256_hex() -> None:
    assert len(hash_key("a")) == 64
    assert hash_key("a") != hash_key("b")


def test_vercel_runtime_is_detected_from_the_sdk_variables() -> None:
    on_vercel = {"RUNTIME_CACHE_ENDPOINT": "https://cache", "RUNTIME_CACHE_HEADERS": "{}"}
    assert running_on_vercel(on_vercel)
    assert not running_on_vercel({})
    assert not running_on_vercel({"RUNTIME_CACHE_ENDPOINT": "https://cache"})
    assert not running_on_vercel({**on_vercel, "CIVIX_SHARED_CACHE": "off"})


def test_from_environment_is_inactive_outside_vercel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RUNTIME_CACHE_ENDPOINT", raising=False)
    assert not SharedCache.from_environment().enabled


def test_kinds() -> None:
    assert shared_kind("/scrutins") == "scrutins"
    assert shared_kind("/scrutins/X") == "scrutin-detail"
    assert shared_kind("/scrutins/X/votes") == "scrutin-votes"
    assert shared_kind("/deputes") == "deputes"


async def test_cold_instance_is_served_from_the_shared_cache(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    warm = await instance(backend).get_scrutin(SCRUTIN_UID)
    assert civix_mock.paths() == [f"/scrutins/{SCRUTIN_UID}"]
    cold = await instance(backend).get_scrutin(SCRUTIN_UID)
    assert civix_mock.paths() == [f"/scrutins/{SCRUTIN_UID}"]
    assert cold == warm


async def test_every_response_kind_survives_the_roundtrip(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    first = instance(backend)
    expected = [
        await first.list_groupes(),
        await first.get_votes(SCRUTIN_UID),
        await first.list_scrutins("retraites"),
        await first.search("retraites"),
        await first.list_deputes(),
    ]
    calls = len(civix_mock.requests)
    second = instance(backend)
    actual = [
        await second.list_groupes(),
        await second.get_votes(SCRUTIN_UID),
        await second.list_scrutins("retraites"),
        await second.search("retraites"),
        await second.list_deputes(),
    ]
    assert len(civix_mock.requests) == calls
    assert actual == expected


async def test_shared_hits_are_free_for_the_call_budget(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    await instance(backend).get_scrutin(SCRUTIN_UID)
    budget = CallBudget(1)
    token = current_budget.set(budget)
    try:
        await instance(backend).get_scrutin(SCRUTIN_UID)
    finally:
        current_budget.reset(token)
    assert budget.used == 0


async def test_a_shared_hit_fills_the_memory_cache(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    await instance(backend).list_groupes()
    cold = instance(backend)
    await cold.list_groupes()
    await cold.list_groupes()
    assert backend.reads == 2


async def test_write_through_uses_the_memory_ttl(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    client = instance(backend)
    await client.list_groupes()
    await client.get_scrutin(SCRUTIN_UID)
    ttls = {key.split(":", 1)[1].split("?")[0]: entry.ttl for key, entry in backend.entries.items()}
    assert ttls["/groupes"] == 600
    assert ttls[f"/scrutins/{SCRUTIN_UID}"] in (600, int(IMMUTABLE_TTL_SECONDS))


async def test_a_broken_shared_cache_falls_back_to_civix(civix_mock: CivixStub) -> None:
    response = await instance(BrokenBackend()).get_scrutin(SCRUTIN_UID)
    assert response.attributes.scrutin.uid == SCRUTIN_UID
    assert civix_mock.paths() == [f"/scrutins/{SCRUTIN_UID}"]


async def test_an_entry_with_an_outdated_shape_is_ignored(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    await instance(backend).list_groupes()
    for entry in backend.entries.values():
        entry.value["data"] = {"data": "forme ancienne"}
    await instance(backend).list_groupes()
    assert civix_mock.paths() == ["/groupes", "/groupes"]


async def test_the_directory_is_shared_between_instances(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    first = await instance(backend).directory.load()
    pages = len(civix_mock.requests)
    second = await instance(backend).directory.load()
    assert len(civix_mock.requests) == pages
    assert second == first
    assert any(key.endswith("directory") for key in backend.entries)


async def test_the_directory_survives_an_oversize_skip(civix_mock: CivixStub) -> None:
    backend = FakeBackend()
    client = instance(backend, max_bytes=10)
    assert await client.directory.load()
    assert backend.writes == 0
