# OSRS Bot v2 — Python Automation Framework + AI Script Generator

A Python-native automation framework for Old School RuneScape with a Claude-powered script generator. Color-based detection via RuneLite overlays, remote input via KInput DLLs, and an iteration loop that gets better with every script.

## Quick Start

```powershell
# 1. Clone
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot
git clone https://github.com/joshcannella/ChromaScape.git  # needed for KInput DLLs

# 2. Install the framework
uv venv && uv pip install -e framework/

# 3. Install the CLI
cd cli && uv tool install --editable . && cd ..

# 4. Run the demo (debug mode — no clicks, saves annotated screenshots)
python scripts/demo_mining_bot.py --debug
```

## Architecture

```
                   Claude Code + MCP Servers
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         osrswiki    wiseoldman    native tools
         (items,     (player       (file read/
          NPCs,      stats,        write)
          wiki)      gains)
              │           │           │
              └───────────┼───────────┘
                          ▼
              generator/requests/<id>.json   ← Script Generation Request
                          │
                          ▼
              osrs-bot py-generate <id>      ← Claude API generates script
                          │
                          ▼
              scripts/<id>_bot.py             ← Run with --debug, then live
                          │
                          ▼
              osrs-bot bug / py-fix / py-lesson  ← Iterate until working
```

## Project Structure

```
osrs-bot/
├── framework/              Python automation library
│   └── framework/
│       ├── bot.py          BaseBot with cycle() loop
│       ├── controller.py   Wires capture, input, detection, zones, actions
│       ├── capture.py      Screen capture (mss + win32gui)
│       ├── humanize.py     WindMouse + random delays
│       ├── colors.py       HSV color registry
│       ├── detection/      Color contour detection (OpenCV)
│       ├── input/          KInput DLL remote mouse/keyboard
│       ├── zones/          UI zone positions (inventory, minimap)
│       ├── actions/        Dropper, idler
│       └── game_state/     RuneLite plugin bridge client
│
├── generator/              Claude API script generator
│   ├── prompts.py          System prompt with API reference + lessons
│   ├── client.py           Anthropic SDK wrapper
│   ├── pipeline.py         Generate + fix workflows
│   ├── validator.py        AST-based script validation
│   └── requests/           Script Generation Request JSON files
│
├── plugin/                 RuneLite bridge plugin (Java)
│   └── src/.../osrsbot/    Game state via shared memory (mmap)
│
├── scripts/                Generated + hand-written bot scripts
├── cli/                    osrs-bot CLI
├── mcp-servers/            OSRS Wiki + Wise Old Man MCP servers
├── knowledge/              Lessons learned (fed into generator prompt)
├── specs/scripts/          Script specs and domain knowledge
├── scripts.json            Script tracker (bugs, notes, status)
├── CLAUDE.md               Project instructions for Claude Code
└── ChromaScape/            Upstream fork (KInput DLLs, gitignored)
```

## CLI Commands

| Command | What it does |
|---------|-------------|
| `osrs-bot py-generate <id>` | Generate a script from `generator/requests/<id>.json` |
| `osrs-bot py-fix <id>` | Fix a script using logged bugs (versioned, shows diff) |
| `osrs-bot py-lesson <id>` | Extract a lesson from a resolved bug |
| `osrs-bot bug <id> "msg"` | Log a bug against a script |
| `osrs-bot resolve <id>` | Mark latest bug as resolved |
| `osrs-bot status` | Show all scripts and their state |
| `osrs-bot show <id>` | Show script details, bugs, notes |

## How It Works

1. **Framework** — Python replaces ChromaScape as the runtime. Captures the RuneLite canvas, detects colored overlays via OpenCV HSV thresholding, injects mouse/keyboard events via KInput DLLs (no physical mouse hijack).

2. **Generator** — Claude reads a Script Generation Request (JSON spec with task, entities, colors, workflow) and produces a complete Python bot script. The system prompt includes the full framework API and all lessons learned from prior bugs.

3. **Iteration Loop** — Run `--debug` to verify targeting with annotated screenshots. Go live. Report bugs with `osrs-bot bug`. Fix with `osrs-bot py-fix`. Extract lessons with `osrs-bot py-lesson`. Every lesson improves future script generation.

4. **Plugin Bridge** (optional) — A RuneLite Java plugin exports structured game state (inventory, NPCs, stats) via shared memory. No open ports — uses a memory-mapped file at `~/.runelite/osrsbot_state.dat`. Framework uses it when available, falls back to color detection only.

## Prerequisites

- Windows 11 (KInput DLLs require Windows)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- RuneLite client
- ChromaScape clone (for `KInput.dll` and `KInputCtrl.dll` in `ChromaScape/build/dist/`)
- `ANTHROPIC_API_KEY` in `.env` (for script generation)
