# OSRS Bot — AI-Assisted Script Generation

An AI-powered workflow for generating Old School RuneScape automation scripts using the [ChromaScape](https://github.com/StaticSweep/ChromaScape) framework. Three specialized AI agents collaborate to go from a script idea to compilable Java code.

## Quick Start (Windows)

First-time setup:

```powershell
# 1. Clone both repos
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot
git clone https://github.com/joshcannella/ChromaScape.git
cd ChromaScape
git remote add upstream https://github.com/StaticSweep/ChromaScape.git
cd ..

# 2. Download fonts and UI templates (required before first build)
cd ChromaScape; .\CVTemplates.bat; cd ..

# 3. Build ChromaScape (requires Java 17 + MinGW for KInput)
cd ChromaScape; .\gradlew.bat build; cd ..

# 4. Install the CLI
cd cli; uv tool install --editable .; cd ..
```

Daily use:

```powershell
# Pull latest and launch (opens browser too)
osrs-bot run --browser
```

See the [User Guide](docs/user-guide.md) for full setup (KInput, RuneLite config, etc.) and troubleshooting.

## Quick Start (Linux — Development)

```bash
# 1. Clone both repos
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot
git clone https://github.com/joshcannella/ChromaScape.git
cd ChromaScape && git remote add upstream https://github.com/StaticSweep/ChromaScape.git && cd ..

# 2. Install the CLI
cd cli && uv tool install --editable . && cd ..

# 3. Check what's available
osrs-bot status

# 4. Deploy scripts (compile + push)
osrs-bot deploy
```

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
                    specs/scripts/        ChromaScape/src/
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
│       └── complete/<id>/              # Completed scripts
├── ChromaScape/                         # Framework (your fork, separate git repo)
│   └── src/main/java/com/chromascape/
│       ├── scripts/                     # Generated scripts live here
│       └── utils/actions/custom/        # Shared utilities
├── cli/                                 # osrs-bot CLI (Python/uv)
├── mcp-servers/                         # OSRS Wiki + Wise Old Man MCP servers
├── scripts/                             # Internal shell scripts
├── build.gradle.kts                     # Compile-check via composite build
├── settings.gradle.kts                  # References ChromaScape
└── docs/                                # User guide
```

## Architecture

ChromaScape is a separate git repository (your fork of StaticSweep/ChromaScape) cloned inside the project root. It is **not** a submodule — it's its own independent repo listed in `.gitignore`.

- **Scripts** are written directly into `ChromaScape/src/main/java/com/chromascape/scripts/`
- **Images** go into `ChromaScape/src/main/resources/images/user/`
- **Compile-check** uses the root `build.gradle.kts` with Gradle composite build
- **Deploy** compiles and pushes ChromaScape, then pushes the parent repo

This means: no file copying, no sync scripts, no submodule ceremony. Edit a `.java` file, run `osrs-bot deploy`, done.

## Prerequisites

- [Kiro CLI](https://kiro.dev) with agent support
- Java 17 (for ChromaScape compilation)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (for CLI and MCP servers)
- ChromaScape fork (cloned inside project root)
