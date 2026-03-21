#!/usr/bin/env python3
"""OSRS Wiki MCP Server — provides tools for querying the Old School RuneScape Wiki APIs."""

import json
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIKI_API = "https://oldschool.runescape.wiki/api.php"
PRICES_API = "https://prices.runescape.wiki/api/v1/osrs"
USER_AGENT = "osrswiki-mcp-server/2.0 (https://github.com/joshcannella/osrs-bot)"

# ---------------------------------------------------------------------------
# Shared HTTP client (lifespan-managed)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT}, timeout=30.0
    ) as client:
        yield {"client": client}


mcp = FastMCP("osrswiki_mcp", lifespan=app_lifespan)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Page or resource not found. Check the name/ID and try again."
        if status == 429:
            return "Error: Rate limit exceeded. Wait a moment and retry."
        return f"Error: Wiki API returned status {status}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The wiki may be slow — try again."
    return f"Error: {type(e).__name__}: {e}"


def _fmt(data: object) -> str:
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class QueryBucketInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    query: str = Field(
        ...,
        description="Bucket query string, e.g. bucket('infobox_item').select('item_id','examine').where('item_name','Iron ore').run()",
        min_length=1,
    )


class SearchWikiInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    query: str = Field(..., description="Search query", min_length=1)
    limit: Optional[int] = Field(default=10, description="Maximum results", ge=1, le=50)


class GetPageContentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    page: str = Field(..., description="Page name (e.g., 'Iron ore')", min_length=1)
    section: Optional[int] = Field(
        default=None,
        description="Section index to retrieve (0 = lead). Omit for full page.",
        ge=0,
    )


class GetItemPricesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: Optional[int] = Field(
        default=None,
        description="Item ID. Omit to get all latest prices (preferred for bulk lookups).",
        ge=0,
    )


class GetItemMappingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GetItemImageUrlInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    item_name: str = Field(..., description="Item name (e.g., 'Iron ore')", min_length=1)


class Timestep(str, Enum):
    FIVE_MIN = "5m"
    ONE_HOUR = "1h"
    SIX_HOUR = "6h"
    TWENTY_FOUR_HOUR = "24h"


class GetPriceAveragesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interval: Timestep = Field(
        ..., description="Averaging interval: '5m' or '1h'"
    )
    timestamp: Optional[int] = Field(
        default=None,
        description="Unix timestamp for the period to query. Omit for the most recent period.",
    )

    @field_validator("interval")
    @classmethod
    def restrict_to_averages(cls, v: Timestep) -> Timestep:
        if v not in (Timestep.FIVE_MIN, Timestep.ONE_HOUR):
            raise ValueError("interval must be '5m' or '1h' for averages")
        return v


class GetPriceTimeseriesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: int = Field(..., description="Item ID to get time-series for", ge=0)
    timestep: Timestep = Field(
        ..., description="Data resolution: '5m', '1h', '6h', or '24h'. Higher = more history (max 365 points)."
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="query_bucket",
    annotations={
        "title": "Query Bucket API",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def query_bucket(params: QueryBucketInput) -> str:
    """Query the OSRS Wiki Bucket API for structured data about items, monsters, and more.

    Common buckets: infobox_item, infobox_monster.
    Browse all: https://oldschool.runescape.wiki/w/Special:AllPages?namespace=9592

    Query syntax: bucket('{name}').select('{field1}','{field2}').where('{field}','{value}').limit({n}).run()
    """
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(WIKI_API, params={"action": "bucket", "query": params.query, "format": "json"})
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="search_wiki",
    annotations={
        "title": "Search Wiki Pages",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def search_wiki(params: SearchWikiInput) -> str:
    """Search for pages on the OSRS Wiki by name or topic."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(
            WIKI_API,
            params={"action": "opensearch", "search": params.query, "limit": params.limit, "format": "json"},
        )
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_page_content",
    annotations={
        "title": "Get Wiki Page Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_page_content(params: GetPageContentInput) -> str:
    """Get the parsed content of a wiki page. Optionally retrieve a single section by index."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        api_params: dict = {"action": "parse", "page": params.page, "format": "json", "prop": "wikitext"}
        if params.section is not None:
            api_params["section"] = params.section
        resp = await client.get(WIKI_API, params=api_params)
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_item_prices",
    annotations={
        "title": "Get Latest GE Prices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_item_prices(params: GetItemPricesInput) -> str:
    """Get the latest Grand Exchange high/low prices and timestamps.

    Omit item_id to fetch all ~3700 items in one request (preferred for bulk lookups).
    """
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        api_params = {}
        if params.item_id is not None:
            api_params["id"] = params.item_id
        resp = await client.get(f"{PRICES_API}/latest", params=api_params)
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_item_mapping",
    annotations={
        "title": "Get Item ID Mapping",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_item_mapping(params: GetItemMappingInput) -> str:
    """Get the full item ID-to-name mapping with metadata (examine text, alch values, buy limits, icon filenames)."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"{PRICES_API}/mapping")
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_item_image_url",
    annotations={
        "title": "Get Item Image URL",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_item_image_url(params: GetItemImageUrlInput) -> str:
    """Get the canonical wiki image URL for an item. Useful for downloading item icons."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(
            WIKI_API,
            params={
                "action": "query",
                "titles": f"File:{params.item_name}.png",
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json",
            },
        )
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_price_averages",
    annotations={
        "title": "Get Price Averages (5m / 1h)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_price_averages(params: GetPriceAveragesInput) -> str:
    """Get 5-minute or 1-hour average high/low prices and trade volumes for all items.

    Useful for spotting short-term price trends and detecting active trading.
    """
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        api_params: dict = {}
        if params.timestamp is not None:
            api_params["timestamp"] = params.timestamp
        resp = await client.get(f"{PRICES_API}/{params.interval.value}", params=api_params)
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_price_timeseries",
    annotations={
        "title": "Get Price Time-Series",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_price_timeseries(params: GetPriceTimeseriesInput) -> str:
    """Get historical price time-series for a single item (up to 365 data points).

    Use higher timesteps (6h, 24h) for longer history. Useful for price trend analysis.
    """
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(
            f"{PRICES_API}/timeseries",
            params={"id": params.item_id, "timestep": params.timestep.value},
        )
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    mcp.run()


if __name__ == "__main__":
    main()
