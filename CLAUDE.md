# OSRS Bot v2

Python automation framework for Old School RuneScape with a Claude-powered script generator.

## Project Layout

- `framework/` — Python automation library (screen capture, color detection, KInput remote input, WindMouse humanization)
- `generator/` — Claude API script generator (prompts, pipeline, validator)
- `plugin/` — RuneLite Java plugin exposing game state via shared memory (mmap)
- `scripts/` — Generated and hand-written bot scripts
- `cli/` — `osrs-bot` CLI tool
- `mcp-servers/` — OSRS Wiki and Wise Old Man MCP servers
- `knowledge/` — Lessons learned (fed into generator system prompt)
- `specs/scripts/` — Script specs and domain knowledge
- `scripts.json` — Script tracker (bugs, notes, status)
- `ChromaScape/` — Upstream fork, needed for KInput DLLs at `ChromaScape/build/dist/`

## Key Conventions

- All mouse coordinates are **canvas-relative** (0,0 = top-left of RuneLite game viewport)
- Color detection uses OpenCV HSV: H 0-179, S 0-255, V 0-255
- Phase 1 zone positions are hardcoded for **Fixed-Classic 1920x1080 at 100% scaling**
- Scripts must implement stuck detection and use `wait_random_millis()` for human-like timing
- Always null-check detection results (`get_random_point_in_color()` returns None when nothing found)

## Running Scripts

```bash
python scripts/demo_mining_bot.py --debug   # dry-run, saves annotated screenshots
python scripts/demo_mining_bot.py            # live run
```

## Generator Workflow

1. Write SGR to `generator/requests/<id>.json`
2. `osrs-bot py-generate <id>` — generates script
3. `osrs-bot py-fix <id>` — fixes script from logged bugs
4. `osrs-bot py-lesson <id>` — extracts lesson for future generation

## MCP Servers

- **osrswiki**: Item IDs, NPC data, wiki pages, GE prices
- **wiseoldman**: Player stats, XP gains, achievements
