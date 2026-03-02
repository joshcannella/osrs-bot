# osrs-bot CLI

Manage scripts, deployments, logs, and bugs.

## Install

```bash
cd cli && uv sync
```

## Usage

Run from the project root:

```bash
uv run --project cli osrs-bot <command>
```

### Commands

| Command | Description |
|---------|-------------|
| `deploy` | Sync all scripts, compile, dry-run, push |
| `deploy <id>` | Deploy a single script by spec ID |
| `run` | Pull latest, clean, launch ChromaScape |
| `run --browser` | Same, but also opens http://localhost:8080 |
| `logs pull <id>` | Copy runtime log to script's spec directory |
| `logs tail` | Show last 50 lines of runtime log |
| `logs tail -n 100` | Show last 100 lines |
| `bug <id>` | Pull log, create bug report, open editor, push |
| `complete <id>` | Move script from dev → completed |
| `upstream` | Fetch and merge upstream ChromaScape updates |
| `status` | Show active/completed scripts, pending bugs, dirty files |

### Examples

```bash
# Deploy just the restless ghost script
uv run --project cli osrs-bot deploy restless-ghost

# Deploy everything
uv run --project cli osrs-bot deploy

# Check what's in progress
uv run --project cli osrs-bot status

# Report a bug
uv run --project cli osrs-bot bug restless-ghost

# Mark a script as done
uv run --project cli osrs-bot complete restless-ghost
```
