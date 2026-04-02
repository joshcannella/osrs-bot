# User Guide

## Table of Contents

- [1. System Requirements](#1-system-requirements)
- [2. Installation](#2-installation)
- [3. RuneLite Configuration](#3-runelite-configuration)
- [4. Running Scripts](#4-running-scripts)
- [5. Generating New Scripts](#5-generating-new-scripts)
- [6. Iteration Loop](#6-iteration-loop)
- [7. RuneLite Plugin Bridge](#7-runelite-plugin-bridge)
- [8. CLI Reference](#8-cli-reference)
- [9. Color System Reference](#9-color-system-reference)
- [10. Troubleshooting](#10-troubleshooting)
- [11. Tips](#11-tips)

---

## 1. System Requirements

- **Windows 11** (64-bit) — KInput DLLs require Windows
- **Python 3.12+** and [uv](https://docs.astral.sh/uv/)
- **RuneLite** client installed and logged in
- **ChromaScape clone** (for pre-compiled KInput DLLs)
- **ANTHROPIC_API_KEY** (for script generation via Claude API)

---

## 2. Installation

```powershell
# 1. Clone the repo
git clone https://github.com/joshcannella/osrs-bot.git
cd osrs-bot

# 2. Clone ChromaScape (needed for KInput DLLs at ChromaScape/build/dist/)
git clone https://github.com/joshcannella/ChromaScape.git

# 3. Create venv and install the Python framework
uv venv
uv pip install -e framework/

# 4. Install the CLI
cd cli && uv tool install --editable . && cd ..

# 5. Set your API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Verify:

```powershell
osrs-bot --help
python scripts/demo_mining_bot.py --debug
```

---

## 3. RuneLite Configuration

### Required settings

| Setting | Value |
|---------|-------|
| Windows Display Scaling | 100% |
| RuneScape UI Mode | Fixed - Classic |
| Display Brightness | Middle (50%) |

### Object Markers plugin

This is how the framework finds game objects — by detecting RuneLite's color overlays.

1. Enable **Object Markers** in RuneLite plugins
2. Set highlight color to **Cyan (#00FFFF)**
3. In-game: hold **Shift + right-click** an object, then **Mark**

### Other useful plugins

| Plugin | Purpose |
|--------|---------|
| NPC Indicators | Highlights NPCs — used by fishing/combat scripts |
| Ground Items | Highlights ground items with color overlays |
| Idle Notifier | Alerts when player goes idle (Phase 4: OCR detection) |

---

## 4. Running Scripts

### Debug mode (safe — no clicks)

```powershell
python scripts/demo_mining_bot.py --debug
```

This:
- Captures screenshots and saves annotated images to `debug/`
- Draws contour outlines (green) and chosen click points (red dot)
- Logs HSV mask coverage percentage
- Moves the mouse but does NOT click

Check the `debug/` folder to verify the red dot lands on the correct target.

### Live mode

```powershell
python scripts/demo_mining_bot.py
```

Press **Ctrl+C** to stop cleanly.

**Important:** RuneLite must be open and logged in before starting a script.

---

## 5. Generating New Scripts

### Step 1: Create a Script Generation Request

Start a Claude Code session. Research the task using the OSRS Wiki MCP, then write a spec:

```
generator/requests/<id>.json
```

Example:

```json
{
  "id": "catherby-lobster-fisher",
  "task": "Fish lobsters at Catherby and bank when full",
  "skill": "Fishing",
  "location": "Catherby fishing spots",
  "entities": {
    "fishing_spot": {"detection": "overlay", "color": "Cyan"}
  },
  "workflow": "bank",
  "color_requirements": [
    {"name": "Cyan", "target": "fishing spot NPC highlight"}
  ]
}
```

### Step 2: Generate

```powershell
osrs-bot py-generate catherby-lobster-fisher
```

Reads the SGR, calls Claude with the full framework API + lessons learned, validates the output, writes to `scripts/catherby_lobster_fisher_bot.py`.

### Step 3: Test

```powershell
python scripts/catherby_lobster_fisher_bot.py --debug
```

---

## 6. Iteration Loop

```
Generate → Debug → Live → Bug → Fix → Lesson → (repeat)
```

```powershell
# Something goes wrong
osrs-bot bug catherby-lobster-fisher "clicks wrong fishing spot"

# Claude reads the spec + script + bugs and generates a fix
osrs-bot py-fix catherby-lobster-fisher

# Working? Mark resolved and extract a lesson
osrs-bot resolve catherby-lobster-fisher
osrs-bot py-lesson catherby-lobster-fisher
```

Every lesson extracted with `py-lesson` is appended to `knowledge/script-generation-lessons-learned.md`. All future `py-generate` calls include these lessons in the system prompt — the generator gets better with every script.

---

## 7. RuneLite Plugin Bridge (Optional)

A Java plugin that exports game state via shared memory for more reliable scripts. Uses memory-mapped files instead of HTTP — no open ports, no unusual JVM classes.

### Building

```powershell
cd plugin
.\gradlew.bat jar
```

### Installing

Copy `plugin/build/libs/osrsbot-plugin-0.1.0.jar` to RuneLite's external plugin directory. See `plugin/SETUP.md` for details. Enable "State Export" in RuneLite's plugin panel.

### Verifying

```powershell
# Check the shared memory file exists (64KB)
ls "$env:USERPROFILE\.runelite\osrsbot_state.dat"

# Or verify from Python
python -c "from framework.game_state.client import GameStateClient; print(GameStateClient().is_available())"
```

When the plugin is running, scripts automatically use it for inventory checks, NPC positions, and stats instead of color detection alone.

---

## 8. CLI Reference

| Command | Description |
|---------|-------------|
| `osrs-bot py-generate <id>` | Generate a Python script from an SGR file |
| `osrs-bot py-fix <id>` | Fix a script using logged bugs (shows diff, confirms) |
| `osrs-bot py-lesson <id>` | Extract a lesson from a resolved bug |
| `osrs-bot init <id>` | Initialize a new script in the tracker |
| `osrs-bot bug <id> "msg"` | Report a bug (optionally with `-i image.png`) |
| `osrs-bot note <id> "msg"` | Add a note to a script |
| `osrs-bot resolve <id>` | Mark the latest bug as resolved |
| `osrs-bot show <id>` | Show script details, bugs, notes |
| `osrs-bot status` | Show all scripts and their state |

---

## 9. Color System Reference

The framework uses OpenCV HSV color space. Predefined colors in `framework/framework/colors/colors.json`:

| Name | HSV Min | HSV Max | Typical Use |
|---|---|---|---|
| Cyan | (87, 225, 226) | (105, 255, 255) | Object/NPC markers |
| Green | (50, 200, 200) | (70, 255, 255) | Object markers |
| Red | (1, 255, 251) | (50, 255, 255) | Ground item highlights |
| Yellow | (20, 255, 255) | (48, 255, 255) | NPC highlights |
| Purple | (127, 115, 181) | (151, 255, 255) | Custom highlights |

**HSV bounds**: H: 0-180 (OpenCV convention), S: 0-255, V: 0-255.

---

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| "RuneLite window not found" | Start RuneLite first. Window title must be "RuneLite" |
| "KInputCtrl.dll not found" | Clone ChromaScape and verify `ChromaScape/build/dist/KInputCtrl.dll` exists |
| "KInput_Create failed" | RuneLite must be running. Restart RuneLite and try again |
| "No rock found in game view" | Verify Object Markers is enabled with Cyan, and objects are marked |
| "Expected at least 2 SunAwtCanvas" | RuneLite not fully loaded. Wait for login, then retry |
| Debug images show wrong target | Check color values. Use RuneLite's color picker to verify HSV |
| Bot clicks wrong things | Remove extra Cyan markers that aren't targets |
| `py-generate` fails | Check `ANTHROPIC_API_KEY` is set in `.env` |

---

## 11. Tips

- **Camera zoom** — keep at default so color highlights are consistent pixel sizes
- **Don't move RuneLite** while running — canvas rect is cached on startup
- **Fixed Mode only** — resizable mode breaks hardcoded zone positions (Phase 1 limitation)
- **Watch the first few cycles** — verify clicks are correct before walking away
- **Pick quiet worlds** — less competition for resources
- **Use --debug first** — always validate targeting with annotated screenshots before going live
- **Check debug/ folder** — green outlines show all detected contours, red dot is the chosen click point
