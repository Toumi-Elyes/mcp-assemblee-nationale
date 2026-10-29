"""Éléments communs aux outils : annotations MCP, types de paramètres, conversion d'erreurs."""

import functools
from collections.abc import Awaitable, Callable
from typing import Annotated, Literal, ParamSpec

from fastmcp.exceptions import ToolError
from pydantic import Field

from assemblee_mcp.civix.errors import CivixError

READ_ONLY_ANNOTATIONS = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
}
DEFAULT_PAGE_SIZE = 10

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

P = ParamSpec("P")


def civix_tool[**P](function: Callable[P, Awaitable[str]]) -> Callable[P, Awaitable[str]]:
    """Convertit une `CivixError` en `ToolError` au message clair, sans trace d'appel."""

    @functools.wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        try:
            return await function(*args, **kwargs)
        except CivixError as error:
            raise ToolError(error.message) from error

    return wrapper
