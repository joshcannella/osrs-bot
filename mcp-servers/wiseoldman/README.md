# Wise Old Man MCP Server

MCP server for the [Wise Old Man](https://wiseoldman.net) OSRS player progress tracker API.

## Installation

```bash
cd mcp-servers/wiseoldman
uv sync
```

## Configuration

Add to your Kiro CLI MCP settings (`~/.config/kiro-cli/mcp_settings.json`):

```json
{
  "mcpServers": {
    "wiseoldman": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/develop/github/osrs-bot/mcp-servers/wiseoldman",
        "run",
        "wiseoldman-mcp"
      ]
    }
  }
}
```

## Available Tools

### search_players
Search for OSRS players by username.
- `username` (required): Player username to search for
- `limit` (optional): Maximum results (default: 20)

### get_player_details
Get detailed stats for a specific player including all skill levels, boss kills, and activity counts.
- `username` (required): Player username

### get_player_gains
Get XP/rank gains for a player over a time period.
- `username` (required): Player username
- `period` (required): Time period - `day`, `week`, `month`, or `year`

### get_player_achievements
Get achievement diaries and quest completion status.
- `username` (required): Player username

### get_group_details
Get details about a group/clan.
- `id` (required): Group ID

### get_competition_details
Get details about a competition.
- `id` (required): Competition ID

## Usage Examples

```python
# Search for a player
search_players(username="Lynx Titan")

# Get player stats
get_player_details(username="Lynx Titan")

# Get weekly gains
get_player_gains(username="Lynx Titan", period="week")

# Get achievements
get_player_achievements(username="Lynx Titan")
```

## API Documentation

Full API docs: https://docs.wiseoldman.net/api
