# OSRS Bot — AI-Assisted Script Generation

An AI-powered workflow for generating Old School RuneScape automation scripts using the [ChromaScape](https://github.com/StaticSweep/ChromaScape) framework. Three specialized AI agents collaborate to go from a script idea to compilable Java code.

## Quick Start

```bash
# 1. Install the CLI (one-time)
cd cli && uv tool install --editable .

# 2. Check what's available
osrs-bot status

# 3. Deploy scripts to ChromaScape
osrs-bot deploy

# 4. On Windows — pull and launch
osrs-bot run --browser
```

See the [User Guide](docs/user-guide.md) for full setup, workflow, and troubleshooting.

## Agent Architecture

```
┌─────────────┐     ┌─────────────┐     ┌───────────────┐
│ osrs-expert │     │  osrs-dev   │     │ osrs-scripter │
│  (green)    │     │  (blue)     │     │  (red)        │
│             │     │             │     │               │
│ Game        │     │ Requirements│     │ Code          │
│ Knowledge   │────▶│ Architect   │────▶│ Generator     │
│ Advisor     │     │             │     │               │
└─────────────┘     └──────┬──────┘     └───────┬───────┘
                           │                    │
                           ▼                    ▼
                    specs/scripts/        scriptgen/src/
                    <id>/requirements.md  main/java/...
```

| Agent | Purpose | Tools |
|-------|---------|-------|
| `osrs-expert` | Answers game questions — training methods, quests, items, locations, meta | Read-only + Wiki MCP |
| `osrs-dev` | Takes a script idea and produces a detailed requirements document | Read/Write + Wiki MCP |
| `osrs-scripter` | Takes a requirements doc and produces compilable Java | Full toolset + Shell |

## Workflow Overview

1. **Research** — `/agent osrs-expert` to ask game questions
2. **Requirements** — `/agent osrs-dev` to generate a requirements doc
3. **Implementation** — `/agent osrs-scripter` to generate and deploy the script
4. **Test** — `osrs-bot run --browser` on Windows
5. **Debug** — `osrs-bot bug <id>` to report issues, agent fixes them
6. **Complete** — `osrs-bot complete <id>` when the script works

## Project Structure

```
osrs-bot/
├── .kiro/
│   ├── agents/                          # Agent configs + prompts
│   ├── knowledge/                       # OSRS game data + ChromaScape docs
│   └── specs/scripts/
│       ├── dev/<id>/                    # Scripts under development
│       └── <id>/                        # Completed scripts
├── ChromaScape/                         # Framework (git submodule → your fork)
├── scriptgen/                           # Generated scripts (source of truth)
├── cli/                                 # osrs-bot CLI (Python/uv)
├── mcp-servers/                         # OSRS Wiki + Wise Old Man MCP servers
├── scripts/                             # Internal shell scripts (used by CLI)
├── docs/                                # User guide
├── run.bat                              # Windows shortcut: pull + launch
└── report-bug.bat                       # Windows shortcut: log + bug report + push
```

## Prerequisites

- [Kiro CLI](https://kiro.dev) with agent support
- Java 17 (for ChromaScape compilation)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (for CLI and MCP servers)
- ChromaScape framework (included as submodule)
