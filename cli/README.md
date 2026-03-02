# osrs-bot CLI

Manage scripts, deployments, logs, and bugs.

## Install

One-time setup — makes `osrs-bot` available globally:

```bash
cd cli
uv tool install --editable .
```

After this, run `osrs-bot` from anywhere. Since it's editable, `git pull` picks up CLI changes automatically.

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

## Usage

```bash
osrs-bot <command>
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
osrs-bot deploy restless-ghost

# Deploy everything
osrs-bot deploy

# Check what's in progress
osrs-bot status

# Report a bug
osrs-bot bug restless-ghost

# Mark a script as done
osrs-bot complete restless-ghost
```
