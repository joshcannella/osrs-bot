# OSRS Bot — AI-Assisted Script Generation

An AI-powered workflow for generating Old School RuneScape automation scripts using the [ChromaScape](https://github.com/StaticSweep/ChromaScape) framework. Three specialized AI agents collaborate to go from a script idea to compilable Java code.

## Agent Architecture

```
┌─────────────┐     ┌─────────────┐     ┌───────────────┐
│ osrs-expert  │     │  osrs-dev   │     │ osrs-scripter  │
│  (green)     │     │  (blue)     │     │  (red)         │
│              │     │             │     │                │
│ Game         │     │ Requirements│     │ Code           │
│ Knowledge    │────▶│ Architect   │────▶│ Generator      │
│ Advisor      │     │             │     │                │
└─────────────┘     └──────┬──────┘     └───────┬────────┘
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

## Workflow

### Step 1: Ask the Expert (optional)

If you need to research game mechanics before committing to a script idea:

```
/agent osrs-expert
```

> "What's the best place to mine iron for a level 45 mining account?"

The expert draws from pre-loaded OSRS knowledge files and can query the OSRS Wiki for specifics. It helps you decide *what* to script before you start building.

### Step 2: Generate Requirements

Switch to the requirements architect:

```
/agent osrs-dev
```

> "I want a script that mines iron ore at the Al Kharid mine and banks at the Al Kharid bank"

The dev agent will:
1. Ask clarifying questions if needed (drop or bank? what pickaxe? any prerequisites?)
2. Research game data — item IDs, tile coordinates, NPC/object details via the OSRS Wiki
3. Design a state machine with detection strategies, edge cases, and recovery logic
4. Save the requirements to `.kiro/specs/scripts/al-kharid-iron-mining/requirements.md`

### Step 3: Generate the Script

Switch to the code generator:

```
/agent osrs-scripter
```

> "Implement the al-kharid-iron-mining requirements"

The scripter agent will:
1. Read the requirements doc from `.kiro/specs/scripts/al-kharid-iron-mining/requirements.md`
2. Read the API reference (`.kiro/knowledge/chromascape-wiki/api-reference.md`)
3. Download item images from the OSRS Wiki
4. Generate a complete Java script at `scriptgen/src/main/java/com/scriptgen/scripts/`
5. Compile and fix any errors
6. Print setup instructions (RuneLite config, inventory layout, prerequisites)

### Step 4: Deploy and Test

The scripter syncs everything to ChromaScape automatically. To launch:

```bash
./scripts/deploy.sh
```

This runs `sync-and-compile.sh` (copies scripts, fixes packages, syncs images, compiles in ChromaScape) then starts the web UI at `http://localhost:8080`. Select your script and hit Start.

Use `./scripts/deploy.sh --no-launch` to just sync and compile without launching.

### Step 5: Debug

When something goes wrong at runtime, create a bug report:

```
cp .kiro/specs/scripts/BUG-TEMPLATE.md .kiro/specs/scripts/al-kharid-iron-mining/bug-report.md
# Fill in what happened, expected behavior, terminal output
```

Then tell the scripter:

```
/agent osrs-scripter
> Read the bug report for al-kharid-iron-mining and fix it
```

The scripter reads the bug report + script source + requirements, makes a targeted fix, re-compiles, and syncs to ChromaScape. Run `./scripts/deploy.sh` again to test.

## Example: Fly Fishing Script

Here's a complete walkthrough of creating a fly fishing script.

### 1. Research (osrs-expert)

```
/agent osrs-expert
> What level do I need for fly fishing and what do I need?
```

Response: Level 20 Fishing. You need a fly fishing rod and feathers. Barbarian Village (south of Edgeville) has fishing spots. You'll catch raw trout (20-30) and raw salmon (30+).

### 2. Requirements (osrs-dev)

```
/agent osrs-dev
> I want a script that fly fishes at Barbarian Village and drops everything
```

The agent produces a requirements doc at `.kiro/specs/scripts/barbarian-fly-fishing/requirements.md`:

```markdown
# Script Requirements: Barbarian Village Fly Fishing

## Script ID
`barbarian-fly-fishing`

## Goal
Fly fish at Barbarian Village and drop all caught fish.

## Game Context
- **Skill/Activity**: Fishing
- **Method**: Fly fishing (rod + feathers)
- **Location**: Barbarian Village fishing spots (tile ~3104, 3433)
- **Prerequisites**: 20 Fishing

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Fly fishing rod | Tool | Grand Exchange / Port Sarim shop | 309 |
| Feathers | Bait (consumed) | Grand Exchange | 314 |

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| 0 | Fly fishing rod | Never drop |
| 1 | Feathers | Never drop |
| 2-27 | Empty → Raw trout/salmon | Drop when full |

## State Machine

### State 1: FISHING
- **Condition**: Inventory not full, fishing spot visible
- **Action**: Click fishing spot (colour-based via RuneLite NPC Indicator)
- **Completion**: Wait until idle (Idler.waitUntilIdle)

### State 2: DROPPING
- **Condition**: Inventory full
- **Action**: Drop all items except slots 0-1 (rod + feathers)
- **Completion**: Inventory slots 2-27 empty

### Recovery State
- **Condition**: Fishing spot not visible
- **Action**: Wait 2-3 seconds for spot to respawn. If still not visible
  after 10s, walk to reset tile.

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Fishing spot | Colour-based | RuneLite NPC Indicator → Cyan highlight |
| Inventory full | Slot check | Template match slot 27 for fish image |

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| NPC Indicators | Highlight NPCs | "Rod Fishing spot" → Cyan, Hull |

## Stop Conditions
- Out of feathers (no feathers detected in inventory)
- Unrecoverable error after 3 retries
```

### 3. Implementation (osrs-scripter)

```
/agent osrs-scripter
> Implement the barbarian-fly-fishing requirements
```

The agent reads the requirements, downloads fish images from the wiki, generates `BarbarianFlyFishingScript.java`, compiles it, and provides setup instructions.

### 4. Run It

Follow the setup instructions from the scripter, then run the script through ChromaScape. See [docs/user-guide.md](docs/user-guide.md) for detailed runtime instructions.

## Project Structure

```
osrs-bot/
├── .kiro/
│   ├── agents/                          # Agent configs + prompts
│   │   ├── osrs-expert.json + .md       # Game knowledge advisor
│   │   ├── osrs-dev.json + .md          # Requirements architect
│   │   └── osrs-scripter.json + .md     # Code generator
│   ├── knowledge/
│   │   ├── osrs/                        # OSRS game knowledge (10 files)
│   │   └── chromascape-wiki/            # Framework docs + API reference
│   └── specs/
│       └── scripts/                     # Requirements docs per script
│           ├── TEMPLATE.md              # Requirements template
│           └── <script-id>/             # One directory per script
│               ├── requirements.md      # From osrs-dev
│               └── implementation-notes.md  # From osrs-scripter (if issues)
├── ChromaScape/                         # Framework (read-only submodule)
├── scriptgen/                           # Generated scripts (your code)
│   └── src/main/java/com/scriptgen/
│       ├── behavior/HumanBehavior.java  # Anti-detection patterns
│       └── scripts/                     # Generated script files
├── mcp-servers/                         # OSRS Wiki + Wise Old Man MCP servers
├── scripts/                             # Dev utility scripts
└── docs/                                # User guide + documentation
```

## Context Optimization

The agents are designed to minimize context window usage:

| Agent | Pre-loaded | On-demand |
|-------|-----------|-----------|
| osrs-expert | ~80KB (10 OSRS knowledge files) | Wiki MCP |
| osrs-dev | ~30KB (ChromaScape docs + lessons) | OSRS files, Wiki MCP, template |
| osrs-scripter | ~30KB (ChromaScape docs + lessons) | API reference, OSRS files, requirements doc |

The requirements document serves as a persistent handoff artifact — if a scripter session runs long, start a fresh conversation and point it at the requirements file.

## Feedback Loop

Knowledge grows over time:
- **Implementation notes**: When the scripter hits issues, it writes `.kiro/specs/scripts/<id>/implementation-notes.md`. The dev agent reads these when revising requirements.
- **Lessons learned**: When the scripter discovers new patterns or fixes non-obvious bugs, it appends to `.kiro/knowledge/script-generation-lessons-learned.md`. Both dev and scripter load this on every session.

## Prerequisites

- [Kiro CLI](https://kiro.dev) with agent support
- Java 17 (for ChromaScape compilation)
- Python + uv (for MCP servers)
- ChromaScape framework (included as submodule)
