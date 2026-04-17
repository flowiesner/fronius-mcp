import os

import click

from fronius_mcp.__init__ import __version__


@click.command()
@click.version_option(__version__, prog_name="fronius-mcp")
@click.option(
    "--transport",
    default="stdio",
    type=click.Choice(["stdio", "streamable-http", "sse"]),
    show_default=True,
    help="MCP transport protocol.",
)
@click.option("--host", default="0.0.0.0", show_default=True, help="Host for HTTP transports.")
@click.option("--port", default=None, type=int, help="Port for HTTP transports (default: $PORT or 8000).")
def main(transport: str, host: str, port: int | None) -> None:
    """MCP server for the Fronius Symo GEN24 solar system."""
    from fronius_mcp.server import build_server

    if port is None:
        port = int(os.environ.get("PORT", 8000))

    mcp = build_server()

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)
