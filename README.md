# osrs-bot CLI

Command-line tool for managing DreamBot scripts — deploy, test, track bugs, and iterate.

## Install

```bash
uv tool install --editable .
```

## Usage

```bash
osrs-bot --help
```

## Configuration

The CLI reads `.osrs-bot.conf` from the workspace directory (where `.kiro/` lives). Set the workspace location:

```bash
export OSRS_BOT_WORKSPACE=~/github/osrs-ai
```

Config file (`~/github/osrs-ai/.osrs-bot.conf`):
```ini
dreambot_repo=~/github/osrs-dreambot
dreambot_scripts=~/DreamBot/Scripts
dreambot_logs=~/DreamBot/BotData/logs
```

## Commands

| Command | Description |
|---------|-------------|
| `osrs-bot init <id>` | Initialize a new script |
| `osrs-bot build` | Compile all scripts |
| `osrs-bot deploy` | Compile + push to git |
| `osrs-bot run` | Windows: pull + build + copy to DreamBot |
| `osrs-bot status` | Show all scripts and latest jar |
| `osrs-bot bug <id> "msg"` | Report a bug |
| `osrs-bot live <id> "msg"` | Send live feedback during testing |
| `osrs-bot inbox` | Show unresolved bugs, notes, and live feed |
