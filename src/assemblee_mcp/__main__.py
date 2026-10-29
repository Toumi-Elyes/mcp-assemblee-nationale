"""Ligne de commande : stdio par défaut, `--http` pour le HTTP streamable sans état."""

import argparse
import os
from collections.abc import Sequence

from assemblee_mcp.server import mcp

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MCP_PATH = "/mcp"


def build_parser() -> argparse.ArgumentParser:
    """Arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        prog="mcp-assemblee-nationale",
        description="Serveur MCP des votes de l'Assemblée nationale (données CIVIX).",
    )
    parser.add_argument("--http", action="store_true", help="HTTP streamable au lieu de stdio")
    parser.add_argument("--host", default=os.environ.get("HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", DEFAULT_PORT)))
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Lance le serveur."""
    args = build_parser().parse_args(argv)
    if args.http:
        mcp.run(
            transport="http",
            host=args.host,
            port=args.port,
            path=MCP_PATH,
            stateless_http=True,
            host_origin_protection="auto",
        )
        return
    mcp.run()


if __name__ == "__main__":
    main()
