# Wise Old Man MCP Server

MCP server for the [Wise Old Man](https://wiseoldman.net) OSRS player progress tracker API.

## Installation

```bash
cd mcp-servers/wiseoldman
uv sync
```

## Configuration

Add to your Kiro CLI MCP settings:

```json
{
  "mcpServers": {
    "wiseoldman": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-servers/wiseoldman", "run", "wiseoldman-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

### search_players

Search for OSRS players by username.

- `username` (required): Player username to search for
- `limit` (optional, 1–50, default 20): Maximum results

### get_player_details

Get detailed stats including all skill levels, boss kills, and activity counts.

- `username` (required): Player username

### get_player_gains

Get XP/rank gains for a player over a time period.

- `username` (required): Player username
- `period` (required): `day`, `week`, `month`, or `year`

### get_player_achievements

Get achievement milestones for a player.

- `username` (required): Player username

### get_player_records

Get a player's personal best records (biggest XP gains, most boss kills in a period).

- `username` (required): Player username
- `period` (optional): Filter by `day`, `week`, `month`, or `year`
- `metric` (optional): Filter by metric (e.g., `agility`, `zulrah`)

### get_player_snapshot_timeline

Get historical stat snapshots as a value/date time-series for a specific metric.

- `username` (required): Player username
- `metric` (required): Metric to track (e.g., `magic`, `zulrah`, `ehp`)
- `period` (optional): Filter by `day`, `week`, `month`, or `year`

### get_player_names

Get a player's approved name change history.

- `username` (required): Player username

### get_group_details

Get details about a group/clan.

- `id` (required): Group ID

### get_competition_details

Get details about a competition.

- `id` (required): Competition ID

## API Documentation

Full API docs: https://docs.wiseoldman.net/api
