#!/usr/bin/env python3
import asyncio
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

WIKI_API = "https://oldschool.runescape.wiki/api.php"
PRICES_API = "https://prices.runescape.wiki/api/v1/osrs"
USER_AGENT = "ChromaScape-MCP/1.0 (https://github.com/osrs-bot)"

app = Server("osrswiki-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_bucket",
            description="Query the OSRS Wiki Bucket API for structured data (items, monsters, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Bucket query string (e.g., bucket('infobox_item').select('item_id','examine').where('item_name','Iron ore').run())",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_wiki",
            description="Search for pages on the OSRS Wiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default: 10)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_page_content",
            description="Get the full content of a wiki page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": "Page name (e.g., 'Iron ore')",
                    },
                },
                "required": ["page"],
            },
        ),
        Tool(
            name="get_item_prices",
            description="Get current Grand Exchange prices for items",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "number",
                        "description": "Item ID (optional - omit to get all prices)",
                    },
                },
            },
        ),
        Tool(
            name="get_item_mapping",
            description="Get item ID to name mapping and metadata (examine text, alch values, buy limits, icons)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_item_image_url",
            description="Get the canonical image URL for an item from the wiki",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_name": {
                        "type": "string",
                        "description": "Item name (e.g., 'Iron ore')",
                    },
                },
                "required": ["item_name"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        try:
            if name == "query_bucket":
                response = await client.get(
                    WIKI_API,
                    params={
                        "action": "bucket",
                        "query": arguments["query"],
                        "format": "json",
                    },
                    headers=headers,
                )
                data = response.json()
                
            elif name == "search_wiki":
                limit = arguments.get("limit", 10)
                response = await client.get(
                    WIKI_API,
                    params={
                        "action": "opensearch",
                        "search": arguments["query"],
                        "limit": limit,
                        "format": "json",
                    },
                    headers=headers,
                )
                data = response.json()
                
            elif name == "get_page_content":
                response = await client.get(
                    WIKI_API,
                    params={
                        "action": "parse",
                        "page": arguments["page"],
                        "format": "json",
                    },
                    headers=headers,
                )
                data = response.json()
                
            elif name == "get_item_prices":
                params = {}
                if "item_id" in arguments:
                    params["id"] = arguments["item_id"]
                response = await client.get(
                    f"{PRICES_API}/latest",
                    params=params,
                    headers=headers,
                )
                data = response.json()
                
            elif name == "get_item_mapping":
                response = await client.get(
                    f"{PRICES_API}/mapping",
                    headers=headers,
                )
                data = response.json()
                
            elif name == "get_item_image_url":
                item_name = arguments["item_name"]
                filename = f"File:{item_name}.png"
                response = await client.get(
                    WIKI_API,
                    params={
                        "action": "query",
                        "titles": filename,
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "format": "json",
                    },
                    headers=headers,
                )
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
