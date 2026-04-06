---
inclusion: always
---

# OSRS Bot — Windows Testing Workflow

This project uses a two-machine workflow: Linux for development, Windows for testing. When running on Windows (Kiro IDE), the user is typically testing scripts and reporting issues — not writing code.

## How It Works

1. Linux: `osrs-bot deploy` → compiles jar, copies to Dropbox, pushes git
2. Dropbox syncs the jar to Windows automatically
3. Windows: `osrs-bot run` → copies jar from Dropbox to `~/DreamBot/Scripts/`
4. User launches DreamBot client separately and selects the script

## Rapid Iteration (Preferred)

For active testing sessions, use the watch + live workflow:

1. Windows: `osrs-bot run --watch` in one terminal (auto-copies new jars)
2. Test the script in DreamBot
3. Send feedback: `osrs-bot live <id> "message" [-i screenshot.png] [-l 10]`
4. `osrs-bot push` to sync feedback to Linux
5. Linux: `osrs-bot inbox` to see feedback → fix → `osrs-bot deploy --quick`
6. Watch terminal auto-detects new jar → stop script → refresh → restart

## When the User Reports a Bug

For formal bugs (not quick iteration feedback):

1. **Identify the script** — ask if unclear, or infer from context
2. **Save any pasted images** to `.kiro/specs/scripts/<id>/`
3. **Run**: `osrs-bot bug <id> "description" -i path/to/image1.png`
4. **Push**: `osrs-bot push`
5. **Confirm** — tell the user the bug is tracked

## When the User Sends Quick Feedback

During active testing, use the live feed instead of formal bugs:

1. `osrs-bot live <id> "message"` — quick text
2. `osrs-bot live <id> "message" -i screenshot.png` — with screenshot
3. `osrs-bot live <id> "message" -l 10` — with last 10 log errors
4. `osrs-bot push` — sync to git

## When the User Wants to Check Script Status

Run: `osrs-bot show <id>` or `osrs-bot status` for the full overview.

## Common Phrases

When the user says any of the following, they mean `osrs-bot run`:
- "run the app", "run it", "start it", "launch it", "fire it up"
- "start dreambot", "run dreambot", "launch the bot"
- "pull and run", "update and run"

Just run the command — no need to confirm what they meant.

## Key Paths

- Scripts source: `dreambot/src/main/java/scripts/`
- Built jars: `~/Dropbox/osrs-bot/builds/`
- DreamBot scripts: `~/DreamBot/Scripts/`
- Logs: `~/DreamBot/BotData/logs/`
- Specs: `.kiro/specs/scripts/<id>/`
- Live feed: `.kiro/live/<id>.md`
- Tracker: `.kiro/scripts.json`
- Config: `.osrs-bot.conf`

## CLI Quick Reference (Windows)

| Task | Command |
|------|---------|
| Copy latest jar to DreamBot | `osrs-bot run` |
| Auto-copy new jars as they arrive | `osrs-bot run --watch` |
| Quick feedback (text) | `osrs-bot live <id> "message"` |
| Quick feedback + screenshot | `osrs-bot live <id> "message" -i img.png` |
| Quick feedback + log errors | `osrs-bot live <id> "message" -l 10` |
| Report a formal bug | `osrs-bot bug <id> "description" [-i img]` |
| Add a note | `osrs-bot note <id> "message" [-i img]` |
| Push feedback to dev | `osrs-bot push` |
| Check status | `osrs-bot status` |
| View script details | `osrs-bot show <id>` |
| Save log locally | `osrs-bot logs pull <id>` |
| Extract log errors | `osrs-bot logs summary <id>` |
