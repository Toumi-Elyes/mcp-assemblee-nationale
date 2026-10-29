"""Éléments communs aux outils : annotations MCP, types de paramètres, conversion d'erreurs."""

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal

from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix.budget import DEFAULT_MAX_CALLS, CallBudget, current_budget
from assemblee_mcp.civix.errors import UNAVAILABLE_MESSAGE, CivixError

READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
}
DEFAULT_PAGE_SIZE = 10
TOOL_DEADLINE_SECONDS = 25
DIRECTORY_MAX_CALLS = 20
ANALYTICS_MAX_CALLS = 45
ANALYTICS_DEADLINE_SECONDS = 45.0
LISTING_MAX_CALLS = 30

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

    Le message de l'erreur est en français, sans trace d'appel.
    """

    def decorator(function: Callable[P, Awaitable[str]]) -> Callable[P, Awaitable[str]]:
        @functools.wraps(function)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
            token = current_budget.set(CallBudget(max_calls))
            try:
                async with asyncio.timeout(
                    deadline if deadline is not None else TOOL_DEADLINE_SECONDS
                ):
                    return await function(*args, **kwargs)
            except CivixError as error:
                raise ToolError(error.message) from error
            except TimeoutError as error:
                raise ToolError(UNAVAILABLE_MESSAGE) from error
            finally:
                current_budget.reset(token)

        return wrapper

    return decorator


civix_tool = limited(DEFAULT_MAX_CALLS)
