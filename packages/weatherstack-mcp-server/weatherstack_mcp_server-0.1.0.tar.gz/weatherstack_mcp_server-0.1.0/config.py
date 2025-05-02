import argparse
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP


@dataclass
class AppContext:
    api_key: str


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    parser = argparse.ArgumentParser(description="MCP app for Weatherstack.")
    parser.add_argument(
        "--api-key", dest="api_key", help="The api key from Weatherstack."
    )
    args = parser.parse_args()

    if not args.api_key:
        raise Exception("The --app-key arg was not provided!")

    yield AppContext(api_key=args.api_key)


mcp = FastMCP("Weatherstack MCP server", lifespan=app_lifespan)
