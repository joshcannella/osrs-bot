#!/usr/bin/env python3
"""Wise Old Man MCP Server — provides tools for querying the WOM OSRS player tracker API."""

import json
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_BASE = "https://api.wiseoldman.net/v2"
USER_AGENT = "wiseoldman-mcp-server/2.0 (https://github.com/joshcannella/osrs-bot)"

# ---------------------------------------------------------------------------
# Shared HTTP client (lifespan-managed)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    async with httpx.AsyncClient(
        base_url=API_BASE,
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
    ) as client:
        yield {"client": client}


mcp = FastMCP("wiseoldman_mcp", lifespan=app_lifespan)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return "Error: Player or resource not found. Check the username/ID and try again."
        if status == 400:
            body = e.response.text
            return f"Error: Bad request. {body}"
        if status == 429:
            return "Error: Rate limit exceeded. WOM allows 20 req/min (100 with API key). Wait and retry."
        return f"Error: WOM API returned status {status}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The WOM API may be slow — try again."
    return f"Error: {type(e).__name__}: {e}"


def _fmt(data: object) -> str:
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class Period(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class SearchPlayersInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(..., description="Player username to search for", min_length=1)
    limit: Optional[int] = Field(default=20, description="Maximum number of results (default: 20)", ge=1, le=50)


class PlayerUsernameInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(..., description="Player username", min_length=1)


class PlayerGainsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(..., description="Player username", min_length=1)
    period: Period = Field(..., description="Time period for gains")


class PlayerRecordsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(..., description="Player username", min_length=1)
    period: Optional[Period] = Field(default=None, description="Filter by time period")
    metric: Optional[str] = Field(default=None, description="Filter by metric (e.g., 'agility', 'zulrah')")


class PlayerSnapshotTimelineInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(..., description="Player username", min_length=1)
    metric: str = Field(..., description="Metric to get timeline for (e.g., 'magic', 'zulrah', 'ehp')")
    period: Optional[Period] = Field(default=None, description="Filter by time period")


class GroupIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(..., description="Group ID", ge=0)


class CompetitionIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(..., description="Competition ID", ge=0)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="search_players",
    annotations={
        "title": "Search Players",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def search_players(params: SearchPlayersInput) -> str:
    """Search for OSRS players by username"""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get("/players/search", params={"username": params.username, "limit": params.limit})
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_details",
    annotations={
        "title": "Get Player Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_details(params: PlayerUsernameInput) -> str:
    """Get detailed stats for a specific player including all skill levels, boss kills, and activity counts."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/players/{params.username}")
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_gains",
    annotations={
        "title": "Get Player Gains",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_gains(params: PlayerGainsInput) -> str:
    """Get XP/rank gains for a player over a time period"""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/players/{params.username}/gained", params={"period": params.period.value})
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_achievements",
    annotations={
        "title": "Get Player Achievements",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_achievements(params: PlayerUsernameInput) -> str:
    """Get achievement diaries and quest completion for a player"""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/players/{params.username}/achievements")
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_records",
    annotations={
        "title": "Get Player Records",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_records(params: PlayerRecordsInput) -> str:
    """Get a player's personal best records (biggest XP gains, most boss kills in a period, etc.)."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        api_params: dict = {}
        if params.period is not None:
            api_params["period"] = params.period.value
        if params.metric is not None:
            api_params["metric"] = params.metric
        resp = await client.get(f"/players/{params.username}/records", params=api_params)
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_snapshot_timeline",
    annotations={
        "title": "Get Player Snapshot Timeline",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_snapshot_timeline(params: PlayerSnapshotTimelineInput) -> str:
    """Get a player's historical stat snapshots as a value/date time-series for a specific metric.

    Useful for charting XP or boss kill progress over time.
    """
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        api_params: dict = {"metric": params.metric}
        if params.period is not None:
            api_params["period"] = params.period.value
        resp = await client.get(f"/players/{params.username}/snapshots/timeline", params=api_params)
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_player_names",
    annotations={
        "title": "Get Player Name Changes",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_player_names(params: PlayerUsernameInput) -> str:
    """Get a player's approved name change history."""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/players/{params.username}/names")
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_group_details",
    annotations={
        "title": "Get Group Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_group_details(params: GroupIdInput) -> str:
    """Get details about a group/clan"""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/groups/{params.id}")
        resp.raise_for_status()
        return _fmt(resp.json())
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="get_competition_details",
    annotations={
        "title": "Get Competition Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def get_competition_details(params: CompetitionIdInput) -> str:
    """Get details about a competition"""
    client: httpx.AsyncClient = mcp.get_context().request_context.lifespan_context["client"]
    try:
        resp = await client.get(f"/competitions/{params.id}")
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
