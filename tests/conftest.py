import json
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx
from fastmcp import Client, FastMCP

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.config import Settings
from assemblee_mcp.server import create_server

FIXTURES = Path(__file__).parent / "fixtures"
API = "https://www.civix.fr/api/v1"
SCRUTIN_UID = "VTANR5L17V7324"

Payload = dict[str, Any]


def load_fixture(name: str) -> Payload:
    payload: Payload = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    return payload


def empty_search(query: str) -> Payload:
    payload = load_fixture("search_global")
    payload["data"]["attributes"]["query"] = query
    payload["data"]["attributes"]["total"] = 0
    payload["data"]["attributes"]["results"] = {
        "deputes": [],
        "scrutins": [],
        "groupes": [],
        "dossiers": [],
    }
    return payload


@dataclass
class CivixStub:
    """Faux CIVIX : sert les fixtures, permet de surcharger une route et trace les appels."""

    requests: list[httpx.Request] = field(default_factory=list)
    overrides: list[tuple[str, dict[str, str], httpx.Response]] = field(default_factory=list)

    def add(self, path: str, payload: Payload, status: int = 200, **params: str) -> None:
        self.overrides.append((path, params, httpx.Response(status, json=payload)))

    def paths(self) -> list[str]:
        return [request.url.path.removeprefix("/api/v1") for request in self.requests]

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path.removeprefix("/api/v1")
        params = dict(request.url.params)
        for override_path, expected, response in self.overrides:
            if override_path == path and expected.items() <= params.items():
                return response
        return self.default(path, params)

    def default(self, path: str, params: dict[str, str]) -> httpx.Response:
        if path == "/search":
            return httpx.Response(200, json=self.search(params.get("search", "")))
        if path == "/scrutins":
            return httpx.Response(200, json=self.scrutins(params.get("search")))
        if path == "/deputes":
            return httpx.Response(200, json=self.deputes(params.get("groupe")))
        fixed = {
            "/groupes": "groupes",
            "/groupes/LIOT": "groupe_liot",
            "/deputes/PA793214": "depute_detail",
            f"/scrutins/{SCRUTIN_UID}": "scrutin_detail",
            f"/scrutins/{SCRUTIN_UID}/votes": "scrutin_votes",
            f"/scrutins/{SCRUTIN_UID}/statements": "scrutin_statements",
        }
        if path in fixed:
            return httpx.Response(200, json=load_fixture(fixed[path]))
        if path.startswith("/scrutins/") and path.endswith("/votes"):
            return httpx.Response(200, json=load_fixture("scrutin_votes"))
        return httpx.Response(404, json={"error": "not found"})

    def search(self, query: str) -> Payload:
        named = {"retraites": "search_global", "Abadie": "search_depute"}
        return load_fixture(named[query]) if query in named else empty_search(query)

    def scrutins(self, query: str | None) -> Payload:
        if query == "retraites":
            return load_fixture("search_scrutins")
        payload = load_fixture("search_scrutins")
        payload["data"]["attributes"]["results"] = []
        payload["meta"]["pagination"].update(count_total=0, count_returned=0, next_page=None)
        return payload

    def deputes(self, groupe: str | None) -> Payload:
        if groupe == "LIOT":
            return load_fixture("deputes_groupe_liot")
        if groupe == "HOR":
            return load_fixture("deputes_groupe_hor")
        payload = load_fixture("deputes")
        if groupe is not None:
            payload["data"]["attributes"]["results"] = []
            payload["meta"]["pagination"].update(count_estimated=0, next_page=None)
        return payload


@pytest.fixture
def stub() -> CivixStub:
    return CivixStub()


@pytest.fixture
def civix_mock(stub: CivixStub) -> Iterator[CivixStub]:
    with respx.mock(base_url=API, assert_all_called=False) as router:
        router.route().mock(side_effect=stub.handle)
        yield stub


@pytest.fixture
def settings() -> Settings:
    return Settings(retry_delay=0.0)


@pytest.fixture
def client(settings: Settings, civix_mock: CivixStub) -> CivixClient:
    return CivixClient(settings)


@pytest.fixture
def server(client: CivixClient) -> FastMCP:
    return create_server(client)


@pytest.fixture
async def mcp_client(server: FastMCP) -> AsyncIterator[Client[Any]]:
    async with Client(server) as connected:
        yield connected
