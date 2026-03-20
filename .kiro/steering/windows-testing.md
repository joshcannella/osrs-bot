---
inclusion: always
---

# OSRS Bot — Windows Testing Workflow

This project uses a two-machine workflow: Linux for development, Windows for testing. When running on Windows (Kiro IDE), the user is typically testing scripts and reporting issues — not writing code.

## When the User Reports a Bug

If the user describes a problem with a script (e.g., "the fishing spot isn't being detected", "it gets stuck after banking", "colour click misses the tree"):

1. **Identify the script** — ask if unclear, or infer from context (e.g., "fishing spot" → `draynor-fish-cook`)
2. **Save any pasted images** to `.kiro/specs/scripts/<id>/` with a descriptive name (e.g., `game-view-fishing-spot.png`, `minimap-stuck.png`)
3. **Run the CLI command**:
   ```
   osrs-bot bug <id> "description" -i path/to/image1.png path/to/image2.png
   ```
   If no images, just: `osrs-bot bug <id> "description"`
4. **Push the changes**: `osrs-bot deploy --dry-run` to verify, then `osrs-bot deploy`
5. **Confirm** — tell the user the bug is tracked and will be visible on the Linux dev machine after a pull

## When the User Shares Feedback (Not a Bug)

If the user shares observations, test results, or general notes (e.g., "works for 3 cycles then slows down", "anchovies cook fine but shrimp burns"):

1. Run: `osrs-bot note <id> "message" [-i images...]`
2. Push if they want it synced: `osrs-bot deploy`

## When the User Pastes Log Output

If the user pastes ChromaScape log lines into chat:

1. Save the relevant lines as a note: `osrs-bot note <id> "Log excerpt: <key lines>"`
2. Or if it's a bug, include the log context in the bug description
3. If they want the full log saved: `osrs-bot logs pull <id>` (saves to gitignored local dir)

## When the User Wants to Check Script Status

Run: `osrs-bot show <id>` to see bugs, notes, and status. Or `osrs-bot status` for the full overview.

## Common Phrases

When the user says any of the following, they mean `osrs-bot run`:
- "run the app", "run it", "start it", "launch it", "fire it up"
- "start chromascape", "run chromascape", "launch the bot"
- "pull and run", "update and run"

Only add `--browser` if they specifically mention opening the browser.

Just run the command — no need to confirm what they meant.

- Scripts: `ChromaScape\src\main\java\com\chromascape\scripts\`
- Images: `ChromaScape\src\main\resources\images\user\`
- Logs: `ChromaScape\logs\chromascape.log`
- Specs: `.kiro\specs\scripts\<id>\`
- Tracker: `.kiro\scripts.json`

## CLI Quick Reference (Windows)

| Task | Command |
|------|---------|
| Pull latest from dev | `osrs-bot run` (pulls both repos + launches) |
| Launch with browser | `osrs-bot run --browser` |
| Report a bug | `osrs-bot bug <id> "description" [-i image.png]` |
| Add a note | `osrs-bot note <id> "message" [-i image.png]` |
| Push feedback to dev | `osrs-bot deploy` |
| Check status | `osrs-bot status` |
| View script details | `osrs-bot show <id>` |
| Save log locally | `osrs-bot logs pull <id>` |
| Extract log errors | `osrs-bot logs summary <id>` |
