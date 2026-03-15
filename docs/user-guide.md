# User Guide

## Table of Contents

- [1. System Requirements](#1-system-requirements)
- [2. Installing Prerequisites](#2-installing-prerequisites)
- [3. Building ChromaScape](#3-building-chromascape)
- [4. CLI Setup](#4-cli-setup)
- [5. RuneLite Configuration](#5-runelite-configuration)
- [6. Workflow](#6-workflow)
- [7. CLI Reference](#7-cli-reference)
- [8. Pulling Updates](#8-pulling-updates)
- [9. Colour System Reference](#9-colour-system-reference)
- [10. Troubleshooting](#10-troubleshooting)
- [11. Tips for Best Results](#11-tips-for-best-results)

---

## 1. System Requirements

- **Windows 11** (64-bit) — ChromaScape uses KInput for remote mouse/keyboard injection via DLL
- **Java 17** (JDK, not JRE)
- **RuneLite** client installed and logged in
- **Python 3.12+** and [uv](https://docs.astral.sh/uv/) — for the CLI
- **4GB+ RAM** recommended
- **Internet connection** — required for Dax Walker pathfinding API

---

## 2. Installing Prerequisites

### Java 17

Download JDK 17 from [Eclipse Adoptium](https://adoptium.net/). Verify:

```powershell
java -version
```

### MinGW-w64 (for KInput)

1. Install [MSYS2](https://www.msys2.org/)
2. From the MSYS2 terminal: `pacman -S mingw-w64-x86_64-gcc`
3. Add `C:\msys64\mingw64\bin` to your system PATH

### Git

```powershell
winget install Git.Git
```

### RuneLite

Download from [runelite.net](https://runelite.net/). Install and log in before running ChromaScape.

### uv (Python package manager)

```powershell
pip install uv
```

---

## 3. Building ChromaScape

### Clone the repo

```powershell
git clone --recurse-submodules https://github.com/joshcannella/osrs-bot.git
cd osrs-bot
```

### Download fonts and UI templates

```powershell
cd ChromaScape
.\CVTemplates.bat
```

This downloads font bitmaps (for OCR) and UI templates (for zone detection). Required before first build.

### Build KInput native libraries

1. Edit Java include paths in `third_party\KInput\KInput\KInput\KInput.cbp` to point to your JDK 17
2. Build:
   ```powershell
   cd third_party\KInput\KInput\KInput
   mingw32-make
   cd ..\KInputCtrl
   mingw32-make
   ```

### Build ChromaScape

```powershell
cd osrs-bot\ChromaScape
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"
.\gradlew.bat build
```

---

## 4. CLI Setup

One-time install — makes `osrs-bot` available globally:

```powershell
cd osrs-bot\cli
uv tool install --editable .
```

Verify:

```powershell
osrs-bot --help
```

Since it's editable, `git pull` picks up CLI changes automatically — no reinstall needed.

---

## 5. RuneLite Configuration

### ChromaScape profile

ChromaScape auto-creates a RuneLite profile on first startup. Activate it:
1. Open RuneLite → profile selector (top-right) → select **"ChromaScape"**

### Required settings

| Setting | Value |
|---------|-------|
| Windows Display Scaling | 100% |
| RuneScape UI Mode | Fixed - Classic |
| Display Brightness | Middle (50%) |

### Object Markers plugin

This is how ChromaScape finds game objects — by detecting RuneLite's colour overlays.

1. Enable **Object Markers** in RuneLite plugins
2. Set highlight colour to **Cyan (#00FFFF)**
3. In-game: hold **Shift + right-click** an object → **Mark**

### Other useful plugins

| Plugin | Purpose |
|--------|---------|
| XP Tracker | Permanent XP bar — used by `Minimap.getXp()` |
| Ground Items | Highlights ground items — used for Marks of Grace |
| NPC Indicators | Highlights NPCs — used by combat/fishing scripts |

---

## 6. Workflow

### Creating a script

```
# 1. Research game mechanics (optional)
/agent osrs-expert
> What's the best place to mine iron for a level 45 account?

# 2. Generate requirements
/agent osrs-dev
> I want a script that mines iron at Al Kharid and banks

# 3. Generate and deploy the script
/agent osrs-scripter
> Implement the al-kharid-iron-mining requirements
```

The scripter agent generates the Java script, downloads item images, compiles, and deploys automatically.

### Running a script

```powershell
# Pull latest and launch (opens browser too)
osrs-bot run --browser
```

Or double-click `run.bat` at the repo root.

1. Open `http://localhost:8080` in your browser
2. Select a script from the left panel
3. Click **START**
4. Monitor via the viewport and terminal output

**Important:** RuneLite must be open and logged in before starting ChromaScape.

### Debugging a script

When something goes wrong:

```powershell
# On Windows — pulls log, opens bug report editor, pushes
osrs-bot bug al-kharid-iron-mining
```

Then on Linux:

```
git pull
/agent osrs-scripter
> Read the bug report for al-kharid-iron-mining and fix it
```

The agent reads the bug report and runtime log, fixes the script, and redeploys.

### Completing a script

Once a script works correctly:

```bash
osrs-bot complete al-kharid-iron-mining
```

Moves the spec from `dev/` → completed, merges SETUP + changelog, and pushes.

---

## 7. CLI Reference

| Command | Description |
|---------|-------------|
| `osrs-bot deploy` | Sync all scripts, compile, dry-run, push |
| `osrs-bot deploy <id>` | Deploy a single script by spec ID |
| `osrs-bot run` | Pull latest, clean, launch ChromaScape |
| `osrs-bot run --browser` | Same, but also opens http://localhost:8080 |
| `osrs-bot logs pull <id>` | Copy runtime log to script's spec directory |
| `osrs-bot logs tail` | Show last 50 lines of runtime log |
| `osrs-bot logs tail -n 100` | Show last 100 lines |
| `osrs-bot bug <id>` | Pull log, create bug report, open editor, push |
| `osrs-bot complete <id>` | Move script from dev → completed |
| `osrs-bot upstream` | Fetch and merge upstream ChromaScape updates |
| `osrs-bot status` | Show active/completed scripts, pending bugs |

---

## 8. Pulling Updates

### After a deploy (on Windows)

```powershell
git pull
git submodule update --init --recursive
```

Or just use `osrs-bot run` which does this automatically.

### Upstream ChromaScape updates

When the original ChromaScape repo releases new features or patches:

```bash
osrs-bot upstream
```

This fetches from `StaticSweep/ChromaScape`, merges into your fork, and pushes.

---

## 9. Colour System Reference

ChromaScape uses OpenCV HSV colour space. Predefined colours in `colours/colours.json`:

| Name | HSV Min | HSV Max | Typical Use |
|---|---|---|---|
| Cyan | (87, 225, 226) | (105, 255, 255) | Object Markers (rocks, booths) |
| Green | (50, 200, 200) | (70, 255, 255) | Object Markers (obstacles, NPCs) |
| Red | (1, 255, 251) | (50, 255, 255) | Ground Items (Marks of Grace) |
| Yellow | (20, 255, 255) | (48, 255, 255) | NPC highlights |
| Purple | (127, 115, 181) | (151, 255, 255) | Custom highlights |

**HSV bounds**: H: 0–180 (OpenCV convention), S: 0–255, V: 0–255.

Use the built-in colour picker at `http://localhost:8080/colour` while ChromaScape is running.

---

## 10. Troubleshooting

### Common Issues

| Problem | Fix |
|---|---|
| "Script class not found" | Run `osrs-bot run` (does `clean bootRun`). Verify package is `com.chromascape.scripts` |
| "No rock found in game view" | Verify Object Markers is enabled with Cyan (#00FFFF) and objects are marked |
| "Walker error" | Check internet. Verify XP bar is visible (walker reads position via OCR) |
| "Failed to create Kinput instance" | Start RuneLite first. Window title must be "RuneLite" |
| "Missing native libraries" | Build KInput DLLs (Section 3), then rebuild ChromaScape |
| Script not in UI | Verify file ends with `Script.java` and is in `com.chromascape.scripts` |
| "Font masks" error | Run `CVTemplates.bat` in ChromaScape directory |
| Bot doesn't move mouse | Ensure 64-bit MinGW matches 64-bit Java |
| Bot clicks wrong things | Remove extra Cyan markers that aren't targets |
| Build fails: "Unable to delete directory" or "KInputCtrl.dll is being used by another process" | Kill all Java processes: `taskkill /F /IM java.exe`, then rebuild |

---

## 11. Tips for Best Results

- **Camera zoom** — keep at default so colour highlights are consistent pixel sizes
- **Don't move RuneLite** while running — coordinates are calibrated on startup
- **Fixed Mode only** — resizable mode breaks zone detection
- **Let breaks happen** — HumanBehavior pauses periodically for anti-detection
- **Watch the first few cycles** — verify clicks are correct before walking away
- **Pick quiet worlds** — less competition for resources
- **Screenshotter** — use the button in the Hub to capture game view for debugging
- **Discord notifications** — configure a webhook in `secrets.properties` for remote alerts
