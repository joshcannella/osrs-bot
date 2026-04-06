# OSRS Bot User Guide

## Prerequisites

- **Java 11+** — DreamBot requires Java 11 or later
- **DreamBot client** — Download from [dreambot.org](https://dreambot.org/)
- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) — for the CLI
- **Dropbox desktop client** — for syncing jars between machines

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
# Deploy scripts (compile + copy to Dropbox + push)
osrs-bot deploy

# Quick deploy during iteration (skip full git push)
osrs-bot deploy --quick

# Check inbox for bugs/feedback from testing
osrs-bot inbox
```

### On Windows (Testing)

```powershell
# One-shot: copy latest jar to DreamBot
osrs-bot run

# Or: watch mode — auto-copies new jars as they arrive
osrs-bot run --watch

# Then: Launch DreamBot → Local Scripts → Refresh → Select script → Start
```

## Rapid Iteration Loop

The fastest way to iterate on a script:

```
Windows terminal 1:  osrs-bot run --watch
Windows terminal 2:  (send feedback as you test)

  osrs-bot live my-script "stuck at bank"
  osrs-bot live my-script "NPC targeting wrong" -i screenshot.png
  osrs-bot live my-script "crashed" -l 10
  osrs-bot push

Linux:
  osrs-bot inbox          # see all feedback
  # fix the code...
  osrs-bot deploy --quick  # build + Dropbox, fast

Windows: (watch auto-detects) → stop script → refresh → restart
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
1. Check Dropbox is syncing: look for `osrs-scripts-*.jar` in `~/Dropbox/osrs-bot/builds/`
2. Run `osrs-bot run` to copy the jar
3. In DreamBot, click "Refresh" on the Local Scripts tab
4. Check `~/DreamBot/Scripts/` for the jar file

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
| `osrs-bot deploy [--quick] [--major-script <id>]` | Build + Dropbox + push |
| `osrs-bot run [--watch]` | Copy jar to DreamBot / watch for new jars |
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
