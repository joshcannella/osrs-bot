# osrs-bot CLI

## Install

```bash
cd cli && uv tool install --editable .
```

## Commands

| Command | Description |
|---------|-------------|
| `osrs-bot py-generate <id>` | Generate a Python script from an SGR file |
| `osrs-bot py-fix <id>` | Fix a script using logged bugs |
| `osrs-bot py-lesson <id>` | Extract a lesson from a resolved bug |
| `osrs-bot init <id>` | Initialize a new script in the tracker |
| `osrs-bot bug <id> "msg"` | Report a bug (optionally with `-i image.png`) |
| `osrs-bot note <id> "msg"` | Add a note to a script |
| `osrs-bot resolve <id>` | Mark the latest bug as resolved |
| `osrs-bot show <id>` | Show script details, bugs, notes |
| `osrs-bot status` | Show all scripts and their state |

See the [User Guide](../docs/user-guide.md) for full documentation.
