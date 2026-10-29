from typing import Any

import httpx
from fastmcp import Client
from mcp.types import TextContent

from assemblee_mcp import server as server_module
from assemblee_mcp.__main__ import build_parser
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.server import create_server


async def test_module_level_server_is_exposed() -> None:
    assert server_module.mcp.name == "Assemblée nationale (CIVIX)"


async def test_instructions_are_french_and_cite_neutrality() -> None:
    instructions = server_module.mcp.instructions or ""
    assert "neutres" in instructions
    assert "non officielle" in instructions
    assert "comment_a_vote" in instructions


async def test_health_route() -> None:
    app = create_server(CivixClient()).http_app(path="/mcp", stateless_http=True)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
        response = await http.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_prompts(mcp_client: Client[Any]) -> None:
    prompts = {prompt.name for prompt in await mcp_client.list_prompts()}
    assert prompts == {
        "resumer_scrutin",
        "mon_depute",
        "comparer_groupes",
        "tendances_du_mois",
        "bilan_groupe",
        "comparer_deux_deputes",
    }
    result = await mcp_client.get_prompt("resumer_scrutin", {"sujet": "retraites"})
    message = result.messages[0].content
    assert isinstance(message, TextContent)
    assert "« retraites »" in message.text
    assert "rechercher_scrutins" in message.text


def test_cli_defaults_to_stdio_and_parses_http_flags() -> None:
    parser = build_parser()
    assert parser.parse_args([]).http is False
    args = parser.parse_args(["--http", "--host", "0.0.0.0", "--port", "8765"])
    assert (args.http, args.host, args.port) == (True, "0.0.0.0", 8765)
