"""Serveur MCP : objet `mcp` et fabrique `create_server`."""

from importlib.metadata import PackageNotFoundError, version

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from assemblee_mcp import prompts
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.tools import chatgpt, deputes, groupes, recherche, scrutins

SERVER_NAME = "Assemblée nationale (CIVIX)"
PACKAGE_NAME = "mcp-assemblee-nationale"
INSTRUCTIONS = """\
Ce serveur donne accès aux votes de l'Assemblée nationale française (scrutins publics, \
députés, groupes parlementaires) via l'API ouverte CIVIX.

Règles :
- Les données sont factuelles et neutres : ne les interprète pas politiquement et ne prête \
aucune intention aux députés ou aux groupes.
- Cite toujours le lien « Source » renvoyé par les outils.
- CIVIX est une interface indépendante et non officielle des données ouvertes de \
l'Assemblée nationale ; dis-le si l'on te demande l'origine des données.
- Seule la législature en cours (17e) est bien couverte pour les députés.

Enchaînements typiques :
- « Comment a voté X sur Y ? » : utilise directement comment_a_vote.
- Résumer un vote : rechercher_scrutins, puis obtenir_scrutin (décomptes par groupe).
- Qui a voté quoi : rechercher_scrutins, puis votes_scrutin (filtres groupe, position, nom).
- Identifier un député ou un groupe : rechercher_deputes, lister_groupes.
Un même texte donne plusieurs scrutins (amendements, articles, vote sur l'ensemble) : précise \
lequel tu cites. Utilise les accents français dans les mots-clés.
"""


def package_version() -> str:
    """Version du paquet installé."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0"


def create_server(client: CivixClient | None = None) -> FastMCP:
    """Construit le serveur ; un client peut être injecté (tests)."""
    civix = client or CivixClient()
    server = FastMCP(name=SERVER_NAME, instructions=INSTRUCTIONS, version=package_version())
    for module in (recherche, scrutins, deputes, groupes, chatgpt):
        module.register(server, civix)
    prompts.register(server)

    @server.custom_route("/health", methods=["GET"])
    async def health(request: Request) -> Response:
        return JSONResponse({"status": "ok"})

    return server


mcp = create_server()
