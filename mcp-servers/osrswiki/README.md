# OSRS Wiki MCP Server

MCP server for the [Old School RuneScape Wiki](https://oldschool.runescape.wiki/) APIs.

## Installation

```bash
cd mcp-servers/osrswiki
uv sync
```

## Configuration

Add to your Kiro CLI MCP settings for the `osrs-expert` and `script-generator` agents:

```bash
kiro-cli mcp add --name osrswiki --agent osrs-expert --command uv --args '--directory' --args '/home/develop/github/osrs-bot/mcp-servers/osrswiki' --args 'run' --args 'osrswiki-mcp'

kiro-cli mcp add --name osrswiki --agent script-generator --command uv --args '--directory' --args '/home/develop/github/osrs-bot/mcp-servers/osrswiki' --args 'run' --args 'osrswiki-mcp'
```

## Available Tools

### query_bucket
Query the Bucket API for structured data (items, monsters, etc.).

**Parameters:**
- `query` (required): Bucket query string

**Example:**
```python
query_bucket(query="bucket('infobox_item').select('item_id','examine').where('item_name','Iron ore').run()")
```

**Query syntax:**
```
bucket('{bucket_name}')
  .select('{field1}', '{field2}', ...)
  .where('{field}', '{value}')
  .limit({number})
  .run()
```

Common buckets: `infobox_item`, `infobox_monster`

Browse all buckets: https://oldschool.runescape.wiki/w/Special:AllPages?namespace=9592

### search_wiki
Search for pages on the OSRS Wiki.

**Parameters:**
- `query` (required): Search query
- `limit` (optional): Maximum results (default: 10)

**Example:**
```python
search_wiki(query="Dragon scimitar", limit=5)
```

### get_page_content
Get the full content of a wiki page.

**Parameters:**
- `page` (required): Page name

**Example:**
```python
get_page_content(page="Iron ore")
```

### get_item_prices
Get current Grand Exchange prices.

**Parameters:**
- `item_id` (optional): Specific item ID (omit to get all prices)

**Example:**
```python
get_item_prices(item_id=440)  # Iron ore
get_item_prices()  # All items
```

### get_item_mapping
Get item ID ↔ name mapping and metadata (examine text, alch values, buy limits, icons).

**Example:**
```python
get_item_mapping()
```

### get_item_image_url
Get the canonical image URL for an item.

**Parameters:**
- `item_name` (required): Item name

**Example:**
```python
get_item_image_url(item_name="Iron ore")
```

## API Documentation

- Bucket API: https://meta.weirdgloop.org/w/Extension:Bucket
- MediaWiki API: https://www.mediawiki.org/wiki/API:Main_page
- Prices API: https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices
