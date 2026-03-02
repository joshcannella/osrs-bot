#!/usr/bin/env python3
import asyncio
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

API_BASE = "https://api.wiseoldman.net/v2"

app = Server("wiseoldman-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_players",
            description="Search for OSRS players by username",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Player username to search for",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (default: 20)",
                    },
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_player_details",
            description="Get detailed stats for a specific player",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Player username",
                    },
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_player_gains",
            description="Get XP/rank gains for a player over a time period",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Player username",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["day", "week", "month", "year"],
                        "description": "Time period for gains",
                    },
                },
                "required": ["username", "period"],
            },
        ),
        Tool(
            name="get_player_achievements",
            description="Get achievement diaries and quest completion for a player",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Player username",
                    },
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="get_group_details",
            description="Get details about a group/clan",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number",
                        "description": "Group ID",
                    },
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="get_competition_details",
            description="Get details about a competition",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number",
                        "description": "Competition ID",
                    },
                },
                "required": ["id"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with httpx.AsyncClient() as client:
        try:
            if name == "search_players":
                limit = arguments.get("limit", 20)
                response = await client.get(
                    f"{API_BASE}/players/search",
                    params={"username": arguments["username"], "limit": limit},
                )
                data = response.json()
                
            elif name == "get_player_details":
                response = await client.get(
                    f"{API_BASE}/players/username/{arguments['username']}"
                )
                data = response.json()
                
            elif name == "get_player_gains":
                response = await client.get(
                    f"{API_BASE}/players/username/{arguments['username']}/gained",
                    params={"period": arguments["period"]},
                )
                data = response.json()
                
            elif name == "get_player_achievements":
                response = await client.get(
                    f"{API_BASE}/players/username/{arguments['username']}/achievements"
                )
                data = response.json()
                
            elif name == "get_group_details":
                response = await client.get(f"{API_BASE}/groups/{arguments['id']}")
                data = response.json()
                
            elif name == "get_competition_details":
                response = await client.get(f"{API_BASE}/competitions/{arguments['id']}")
                data = response.json()
                
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            import json
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def main():
    asyncio.run(_run())

if __name__ == "__main__":
    main()
