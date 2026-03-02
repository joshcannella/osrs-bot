# osrs-bot CLI

## Install

```bash
cd cli && uv tool install --editable .
```

## Commands

| Command | Description |
|---------|-------------|
| `osrs-bot deploy` | Sync all scripts, compile, dry-run, push |
| `osrs-bot deploy <id>` | Deploy a single script by spec ID |
| `osrs-bot run [--browser]` | Pull latest, clean, launch ChromaScape |
| `osrs-bot logs pull <id>` | Copy runtime log to script's spec directory |
| `osrs-bot logs tail [-n N]` | Show last N lines of runtime log |
| `osrs-bot bug <id>` | Pull log, create bug report, open editor, push |
| `osrs-bot complete <id>` | Move script from dev → completed |
| `osrs-bot upstream` | Fetch and merge upstream ChromaScape updates |
| `osrs-bot status` | Show active/completed scripts, pending bugs |

See the [User Guide](../docs/user-guide.md) for full documentation.
