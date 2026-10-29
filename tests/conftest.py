import json
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, NamedTuple

import httpx
import pytest
import respx
from fastmcp import Client, FastMCP
from mcp.types import TextContent

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.config import Settings
from assemblee_mcp.server import create_server

FIXTURES = Path(__file__).parent / "fixtures"
API = "https://www.civix.fr/api/v1"
SCRUTIN_UID = "VTANR5L17V7324"

Payload = dict[str, Any]
McpClient = Client[Any]


class DeputeStub(NamedTuple):
    """Député fictif tel que renvoyé par la recherche globale de CIVIX."""

    uid: str
    prenom: str
    nom: str
    groupe: str


VALLETOUX = DeputeStub("PA795350", "Frédéric", "Valletoux", "HOR")
PANOSYAN = DeputeStub("PA795050", "Astrid", "Panosyan-Bouvet", "EPR")


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
    listings: dict[str | None, list[Payload]] = field(default_factory=dict)

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

    def default(self, path: str, params: dict[str, str]) -> httpx.Response:  # noqa: PLR0911
        if path == "/search":
            return httpx.Response(200, json=self.search(params.get("search", "")))
        if path == "/scrutins":
            return httpx.Response(200, json=self.scrutins(params))
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
        if path.startswith("/scrutins/") and path.count("/") == 2 and path != "/scrutins/NOPE":
            detail = load_fixture("scrutin_detail")
            detail["data"]["attributes"]["scrutin"]["uid"] = path.rsplit("/", 1)[1]
            return httpx.Response(200, json=detail)
        if path.startswith("/scrutins/") and path.endswith("/votes"):
            return httpx.Response(200, json=load_fixture("scrutin_votes"))
        return httpx.Response(404, json={"error": "not found"})

    def search(self, query: str) -> Payload:
        named = {"retraites": "search_global", "Abadie": "search_depute"}
        return load_fixture(named[query]) if query in named else empty_search(query)

    def paged(self, items: list[Payload], params: dict[str, str]) -> Payload:
        page = int(params.get("page", "1"))
        size = int(params.get("page_size", "10"))
        payload = load_fixture("search_scrutins")
        window = items[(page - 1) * size : page * size]
        payload["data"]["attributes"]["results"] = window
        payload["meta"]["pagination"] = {
            "page": page,
            "page_size": size,
            "next_page": page + 1 if page * size < len(items) else None,
            "count_total": len(items),
            "count_returned": len(window),
        }
        return payload

    def scrutins(self, params: dict[str, str]) -> Payload:
        query = params.get("search")
        if query in self.listings:
            return self.paged(self.listings[query], params)
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


def make_item(
    number: int,
    day: str,
    *,
    kind: str = "amendement",
    context: str | None = "Proposition de loi",
    sort: str = "adopté",
    dossier_ref: str | None = "DLR5L17N1",
    dossier: str = "Un texte",
) -> Payload:
    item: Payload = load_fixture("search_scrutins")["data"]["attributes"]["results"][0]
    item.update(
        uid=f"VTANR5L17V{number}",
        numero=number,
        date_scrutin=f"{day}T00:00:00+00:00",
        type=kind,
        context=context,
        sort_code=sort,
        titre=(
            f"l'ensemble du projet de loi {dossier} ({number})"
            if kind == "texte"
            else f"le scrutin {number} du {dossier}"
        ),
    )
    item["objet"] = {
        "libelle": item["titre"],
        "dossierLegislatif": {"libelle": dossier, "dossierRef": dossier_ref}
        if dossier_ref
        else None,
    }
    return item


def make_listing(days: int, per_day: int, end: str = "2026-10-29") -> list[Payload]:
    """`per_day` scrutins par jour sur `days` jours, du plus récent au plus ancien."""
    last = date.fromisoformat(end)
    items: list[Payload] = []
    for offset in range(days):
        day = (last - timedelta(days=offset)).isoformat()
        for index in range(per_day):
            number = 9000 - len(items)
            kind = "texte" if index == 0 else "amendement"
            sort = "adopté" if (offset + index) % 3 == 0 else "rejeté"
            items.append(make_item(number, day, kind=kind, sort=sort))
    return items


async def call(client: McpClient, name: str, **arguments: Any) -> str:
    """Appelle un outil MCP et renvoie son texte."""
    result = await client.call_tool(name, arguments)
    content = result.content[0]
    assert isinstance(content, TextContent)
    return content.text


def search_with_deputes(*deputes: DeputeStub) -> Payload:
    """Réponse de `/search` ne contenant que les députés donnés."""
    payload = load_fixture("search_depute")
    payload["data"]["attributes"]["results"]["deputes"] = [
        {
            "acteur_uid": depute.uid,
            "prenom": depute.prenom,
            "nom": depute.nom,
            "groupe_libelle_abrev": depute.groupe,
            "circ_departement": "Paris",
            "slug": f"{depute.prenom}-{depute.nom}".lower(),
        }
        for depute in deputes
    ]
    return payload


def deputes_payload(*deputes: DeputeStub, next_page: int | None = None) -> Payload:
    """Réponse de `/deputes` (annuaire) ne contenant que les députés donnés."""
    payload = load_fixture("deputes")
    template = payload["data"]["attributes"]["results"][0]
    payload["data"]["attributes"]["results"] = [
        {
            **template,
            "uid": depute.uid,
            "prenom": depute.prenom,
            "nom": depute.nom,
            "groupe_abrev": depute.groupe,
        }
        for depute in deputes
    ]
    payload["meta"]["pagination"].update(next_page=next_page, count_estimated=len(deputes))
    return payload
