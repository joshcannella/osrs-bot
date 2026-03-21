# OSRS Wiki MCP Server

MCP server for the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/) APIs.

## Installation

```bash
cd mcp-servers/osrswiki
uv sync
```

## Configuration

Add to your Kiro CLI MCP settings:

```json
{
  "mcpServers": {
    "osrswiki": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-servers/osrswiki", "run", "osrswiki-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

### osrswiki_query_bucket

Query the Bucket API for structured data (items, monsters, etc.).

- `query` (required): Bucket query string

```
bucket('infobox_item').select('item_id','examine').where('item_name','Iron ore').run()
```

Common buckets: `infobox_item`, `infobox_monster`. Browse all: https://oldschool.runescape.wiki/w/Special:AllPages?namespace=9592

### osrswiki_search_wiki

Search for pages on the OSRS Wiki.

- `query` (required): Search query
- `limit` (optional, 1–50, default 10): Maximum results

### osrswiki_get_page_content

Get the parsed wikitext content of a page.

- `page` (required): Page name (e.g., `Iron ore`)
- `section` (optional): Section index (0 = lead). Omit for full page.

### osrswiki_get_item_prices

Get latest Grand Exchange high/low prices.

- `item_id` (optional): Specific item ID. Omit to get all ~3700 items in one request.

### osrswiki_get_item_mapping

Get item ID ↔ name mapping with metadata (examine text, alch values, buy limits, icon filenames).

No parameters.

### osrswiki_get_item_image_url

Get the canonical wiki image URL for an item.

- `item_name` (required): Item name (e.g., `Iron ore`)

### osrswiki_get_price_averages

Get 5-minute or 1-hour average prices and trade volumes for all items.

- `interval` (required): `5m` or `1h`
- `timestamp` (optional): Unix timestamp for a specific period. Omit for most recent.

### osrswiki_get_price_timeseries

Get historical price time-series for a single item (up to 365 data points).

- `item_id` (required): Item ID
- `timestep` (required): `5m`, `1h`, `6h`, or `24h`. Higher = more history.

## API Documentation

- Bucket API: https://meta.weirdgloop.org/w/Extension:Bucket
- MediaWiki API: https://www.mediawiki.org/wiki/API:Main_page
- Prices API: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices
