"""Briques communes aux outils MCP : annotations, types de paramètres et garde-fous."""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix.budget import CallBudget, current_budget
from assemblee_mcp.civix.client import CivixClient
from assemblee_mcp.civix.errors import UNAVAILABLE_MESSAGE, CivixError
from assemblee_mcp.limits import DEFAULT_MAX_CALLS, TOOL_DEADLINE_SECONDS

# Les outils ne modifient rien et interrogent un service externe : ces indications aident les
# clients MCP (Claude, ChatGPT) à les appeler sans demander de confirmation.
READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
}

type ToolFunction = Callable[..., Awaitable[str]]

Page = Annotated[int, Field(description="Numéro de page, à partir de 1.", ge=1, le=500)]
LegislatureNumber = Annotated[
    int,
    Field(description="Numéro de législature (la législature en cours est la 17e).", ge=1, le=30),
]
ScrutinUid = Annotated[
    str,
    Field(
        description=(
            "Identifiant du scrutin, par exemple « VTANR5L17V7324 » "
            "(obtenu avec rechercher_scrutins ou rechercher)."
        ),
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]
GroupeAbbreviation = Annotated[
    str,
    Field(
        description="Sigle du groupe parlementaire, par exemple « RN », « LFI-NFP » ou « SOC ».",
        min_length=1,
        max_length=32,
    ),
]
PositionName = Literal["pour", "contre", "abstention", "non_votant"]


def limited[**P](
    max_calls: int,
    deadline: float | None = None,
) -> Callable[[Callable[P, Awaitable[str]]], Callable[P, Awaitable[str]]]:
    """Plafonne les appels CIVIX et la durée d'un outil, et convertit `CivixError` en `ToolError`.

    Le message de l'erreur est en français, sans trace d'appel : il est montré tel quel au modèle.
    """

    def decorator(function: Callable[P, Awaitable[str]]) -> Callable[P, Awaitable[str]]:
        @functools.wraps(function)
        async def guarded(*args: P.args, **kwargs: P.kwargs) -> str:
            token = current_budget.set(CallBudget(max_calls))
            limit = deadline if deadline is not None else TOOL_DEADLINE_SECONDS
            try:
                async with asyncio.timeout(limit):
                    return await function(*args, **kwargs)
            except CivixError as error:
                raise ToolError(error.message) from error
            except TimeoutError as error:
                raise ToolError(UNAVAILABLE_MESSAGE) from error
            finally:
                current_budget.reset(token)

        return guarded

    return decorator


civix_tool = limited(DEFAULT_MAX_CALLS)


class ToolSet:
    """Famille d'outils MCP qui partagent un client CIVIX.

    Chaque sous-classe déclare ses outils comme méthodes asynchrones et les liste dans `tools()` ;
    le client est un attribut, donc absent du schéma montré au modèle.
    """

    def __init__(self, client: CivixClient) -> None:
        """Mémorise le client CIVIX partagé par les outils de la famille."""
        self.client = client

    def tools(self) -> tuple[ToolFunction, ...]:
        """Méthodes à exposer comme outils MCP."""
        raise NotImplementedError

    def register(self, mcp: FastMCP) -> None:
        """Enregistre chaque outil en lecture seule, avec une sortie texte."""
        for tool in self.tools():
            mcp.tool(tool, annotations=READ_ONLY_ANNOTATIONS, output_schema=None)
