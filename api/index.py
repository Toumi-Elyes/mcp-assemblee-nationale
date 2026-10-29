"""Point d'entrée Vercel : application ASGI du serveur MCP (HTTP streamable sans état, `/mcp`).

Si la plateforme n'envoie pas les événements ASGI « lifespan », le lifespan de FastMCP est
démarré à la première requête : sans lui, le gestionnaire de sessions HTTP n'est pas prêt.
"""

import asyncio
import sys
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import Receive, Scope, Send

from assemblee_mcp.server import mcp

CORS = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

mcp_app = mcp.http_app(path="/mcp", stateless_http=True, json_response=True, middleware=[CORS])


class LazyLifespanApp:
    """Enveloppe ASGI qui garantit que le lifespan de l'application a démarré."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self._native_lifespan = False
        self._context: AbstractAsyncContextManager[Any] | None = None
        self._lock = asyncio.Lock()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            self._native_lifespan = True
            await self.inner(scope, receive, send)
            return
        if not self._native_lifespan and self._context is None:
            async with self._lock:
                if self._context is None:
                    context = self.inner.router.lifespan_context(self.inner)
                    await context.__aenter__()
                    self._context = context
        await self.inner(scope, receive, send)


app = LazyLifespanApp(mcp_app)
