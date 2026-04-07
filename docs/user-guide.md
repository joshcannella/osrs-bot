# OSRS Bot User Guide

## Prerequisites

- **Java 11+** — DreamBot requires Java 11 or later (needed on both machines)
- **DreamBot client** — Download from [dreambot.org](https://dreambot.org/)
- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) — for the CLI
- **Git** — for syncing code between machines

## First-Time Setup

### Linux (Development Machine)

```bash
# 1. Clone the repo
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot

# 2. Install the CLI
cd cli && uv tool install --editable . && cd ..

# 3. Configure paths (edit if your Dropbox path differs)
cat .osrs-bot.conf

# 4. Verify
osrs-bot status
```

### Windows (Testing Machine)

```powershell
# 1. Clone the repo
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot

# 2. Install the CLI
cd cli; uv tool install --editable .; cd ..

# 3. Configure paths
# Edit .osrs-bot.conf if your Dropbox or DreamBot paths differ

# 4. Install DreamBot
# Download from https://dreambot.org/ and run the installer

# 5. Verify
osrs-bot status
```

## Daily Workflow

### On Linux (Development)

```bash
# Deploy scripts (compile + push)
osrs-bot deploy

# Quick deploy during iteration (skip full git push)
osrs-bot deploy --quick

# Check inbox for bugs/feedback from testing
osrs-bot inbox
```

### On Windows (Testing)

```powershell
# Pull, build, and copy jar to DreamBot
osrs-bot run

# Then: Launch DreamBot → Local Scripts → Refresh → Select script → Start
```

## Rapid Iteration Loop

The fastest way to iterate on a script:

```
Linux:
  # fix the code...
  osrs-bot deploy --quick  # build + push

Windows:
  osrs-bot run             # pull + build + copy
  # stop script → refresh → restart in DreamBot
```

## Creating a New Script

```bash
# Initialize (creates scaffold + tracker entry)
osrs-bot init my-fishing-script

# For simple scripts (AbstractScript instead of TaskScript):
osrs-bot init simple-miner --simple

# Then use the osrs-scripter agent to generate the code
```

## Reporting Issues

### Quick feedback (during active testing)
```powershell
osrs-bot live my-script "description"
osrs-bot live my-script "description" -i screenshot.png
osrs-bot live my-script "description" -l 10
osrs-bot push
```

### Formal bugs (persistent, tracked)
```powershell
osrs-bot bug my-script "Gets stuck after banking"
osrs-bot bug my-script "Wrong NPC targeted" -i screenshot.png
osrs-bot push
```

### Notes (observations, not bugs)
```powershell
osrs-bot note my-script "Works great for 30 minutes then slows down"
osrs-bot push
```

## Troubleshooting

### Jar not appearing in DreamBot
1. On Windows, run `osrs-bot run` to pull, build, and copy the jar
2. In DreamBot, click "Refresh" on the Local Scripts tab
3. Check `~/DreamBot/Scripts/` for the jar file

### Compile errors
```bash
osrs-bot build
# If DreamBot API changed:
cd dreambot && gradle --refresh-dependencies && cd ..
```

### Log files
```powershell
osrs-bot logs tail              # view recent output
osrs-bot logs pull my-script    # save log locally
osrs-bot logs summary my-script # extract errors as a note
```

## CLI Reference

| Command | Purpose |
|---------|---------|
| `osrs-bot init <id> [--simple]` | Scaffold new script |
| `osrs-bot build` | Compile check |
| `osrs-bot deploy [--quick] [--major-script <id>]` | Build + push |
| `osrs-bot run` | Windows: pull + build + copy to DreamBot. Linux: git pull |
| `osrs-bot live <id> "msg" [-i img] [-l N]` | Quick feedback during testing |
| `osrs-bot bug <id> "msg" [-i img]` | Report a formal bug |
| `osrs-bot note <id> "msg" [-i img]` | Add a note |
| `osrs-bot push` | Lightweight git sync (no build) |
| `osrs-bot inbox` | Show bugs, notes, and live feed |
| `osrs-bot status` | Overview of everything |
| `osrs-bot show <id>` | Script details |
| `osrs-bot resolve <id>` | Mark latest bug fixed |
| `osrs-bot complete <id>` | Mark script done |
| `osrs-bot lint` | Check annotations |
| `osrs-bot logs tail/pull/summary` | Log management |
| `osrs-bot live --tail` | View all live feeds |
| `osrs-bot live --clear` | Clear all live feeds |
