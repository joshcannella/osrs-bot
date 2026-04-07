# OSRS Bot — AI-Assisted Script Generation

An AI-powered workflow for generating Old School RuneScape automation scripts using the [DreamBot](https://dreambot.org/) framework. Two specialized AI agents collaborate to go from a script idea to compilable Java code.

## Quick Start (Linux — Development)

```bash
# 1. Clone the repo
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot

# 2. Install the CLI
cd cli && uv tool install --editable . && cd ..

# 3. Check what's available
osrs-bot status

# 4. Deploy scripts (compile + push)
osrs-bot deploy
```

## Quick Start (Windows — Testing)

```powershell
# 1. Clone the repo
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot

# 2. Install the CLI
cd cli; uv tool install --editable .; cd ..

# 3. Pull, build, and copy jar to DreamBot
osrs-bot run

# 4. Launch DreamBot → Local Scripts → Refresh → Select script → Start
```

See the [User Guide](docs/user-guide.md) for full setup and troubleshooting.

## Agent Architecture

```
┌─────────────┐     ┌───────────────┐
│ osrs-expert │     │ osrs-scripter │
│  (green)    │     │  (red)        │
│             │     │               │
│ Game        │     │ Requirements  │
│ Knowledge & │────▶│ + Code        │
│ Brainstorm  │     │ Generator     │
└─────────────┘     └───────┬───────┘
                            │
                            ▼
                     dreambot/src/
                     main/java/scripts/
                            │
                      gradle jar
                            │
                            ▼
                     git push / pull
                            │
                            ▼
                     Windows: osrs-bot run
                     → gradle jar
                     → ~/DreamBot/Scripts/
```

| Agent | Purpose | Tools |
|-------|---------|-------|
| `osrs-expert` | Answers game questions, brainstorms script ideas, assesses feasibility | Read-only + Wiki MCP |
| `osrs-scripter` | Takes a script idea, produces requirements doc, then generates compilable Java | Full toolset + Shell |

## Workflow Overview

1. **Research** — `/agent osrs-expert` to ask game questions and brainstorm script ideas
2. **Build** — `/agent osrs-scripter` to produce requirements doc, then generate and deploy the script
3. **Test** — `osrs-bot run` on Windows, launch DreamBot, select script
4. **Debug** — `osrs-bot bug <id>` to report issues, agent fixes them
5. **Complete** — `osrs-bot complete <id>` when the script works

## Rapid Iteration

For active testing sessions:

```
Linux:   osrs-bot deploy --quick  ← fast build + push
Windows: osrs-bot run             ← pull + build + copy to DreamBot
Windows: osrs-bot live <id> "msg" ← quick feedback
Linux:   osrs-bot inbox           ← see all feedback
```

## Project Structure

```
osrs-bot/
├── .kiro/
│   ├── agents/                          # Agent configs + prompts
│   ├── skills/dreambot/                 # DreamBot scripting skill + references
│   ├── knowledge/                       # OSRS game data
│   ├── specs/scripts/                   # Script requirements + bug tracking
│   └── live/                            # Live feed messages (cleared on deploy)
├── dreambot/                            # DreamBot script project
│   ├── build.gradle.kts                 # Gradle build (DreamBot Maven repo)
│   ├── settings.gradle.kts
│   └── src/main/java/scripts/
│       ├── shared/                      # Anti-ban, ScriptContext
│       └── {scriptname}/               # Per-script packages
├── cli/                                 # osrs-bot CLI (Python/uv)
├── mcp-servers/                         # OSRS Wiki + Wise Old Man MCP servers
├── .osrs-bot.conf                       # Configurable paths (Dropbox, DreamBot)
└── docs/                                # User guide
```

## Architecture

Scripts are written in `dreambot/src/main/java/scripts/` and compiled into a single jar. DreamBot discovers all `@ScriptManifest` classes in the jar and lists each as a separate selectable script.

- **Build**: `osrs-bot deploy` compiles via Gradle, pushes to git
- **Sync**: `git pull` on Windows
- **Run**: `osrs-bot run` on Windows pulls, builds, and copies jar to `~/DreamBot/Scripts/`
- **Rollback**: `git checkout` an older commit and re-run

## Prerequisites

- [Kiro CLI](https://kiro.dev) with agent support
- Java 11+ (for DreamBot compilation — needed on both machines)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/) (for CLI and MCP servers)
- [DreamBot client](https://dreambot.org/) (on Windows testing machine)
- Git (on both machines)
