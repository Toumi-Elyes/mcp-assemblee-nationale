"""Outils `search` et `fetch` attendus par ChatGPT (recherche approfondie et connecteurs)."""

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.search import search_everything
from assemblee_mcp.tools.chatgpt_documents import SearchPayload, fetch_document, search_items
from assemblee_mcp.tools.common import ToolFunction, ToolSet, civix_tool


class ChatGPTTools(ToolSet):
    """Outils nommés `search` et `fetch`, selon la convention de ChatGPT."""

    def tools(self) -> tuple[ToolFunction, ...]:
        """Outils exposés."""
        return (self.search, self.fetch)

    @civix_tool
    async def search(
        self,
        query: Annotated[
            str,
            Field(
                description="Mots-clés : sujet de vote, nom de député ou de groupe.",
                min_length=2,
                max_length=200,
            ),
        ],
    ) -> str:
        """Cherche des scrutins, députés et groupes de l'Assemblée nationale (données CIVIX).

        Renvoie un JSON `{"results": [{"id", "title", "url"}]}` ; les identifiants
        (`scrutin:<uid>`, `depute:<uid>`, `groupe:<sigle>`) se passent à `fetch`.
        """
        found = await search_everything(self.client, query)
        return SearchPayload(results=search_items(found.results)).model_dump_json()

    @civix_tool
    async def fetch(
        self,
        id: Annotated[
            str,
            Field(
                description=(
                    "Identifiant renvoyé par `search` : "
                    "scrutin:<uid>, depute:<uid> ou groupe:<sigle>."
                ),
                min_length=3,
                max_length=100,
            ),
        ],
    ) -> str:
        """Récupère le contenu complet d'un résultat de `search` (scrutin, député ou groupe).

        Renvoie un JSON `{"id", "title", "text", "url", "metadata"}` ; `text` est du markdown
        français avec décomptes, sources et liens.
        """
        payload = await fetch_document(self.client, id)
        return payload.model_dump_json()


def register(mcp: FastMCP, client: CivixClient) -> None:
    """Enregistre `search` et `fetch`."""
    ChatGPTTools(client).register(mcp)
