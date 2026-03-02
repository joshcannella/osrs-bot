# ChromaScape ScriptGen User Guide

A comprehensive guide to setting up and running generated automation scripts for Old School RuneScape using the ChromaScape framework on Windows 11. This guide uses the **Al Kharid Iron Mining Script** as a walkthrough example, but the same process applies to any generated script.

---

## Table of Contents

- [1. System Requirements](#1-system-requirements)
- [2. Installing Prerequisites](#2-installing-prerequisites)
  - [2.1 Java 17](#21-java-17)
  - [2.2 MinGW-w64 (for KInput)](#22-mingw-w64-for-kinput)
  - [2.3 Git](#23-git)
  - [2.4 RuneLite](#24-runelite)
- [3. Building ChromaScape](#3-building-chromascape)
  - [3.1 Clone the Repository](#31-clone-the-repository)
  - [3.2 Download Fonts and UI Templates](#32-download-fonts-and-ui-templates)
  - [3.3 Build KInput Native Libraries](#33-build-kinput-native-libraries)
  - [3.4 Build ChromaScape](#34-build-chromascape)
- [4. Compiling ScriptGen Scripts](#4-compiling-scriptgen-scripts)
- [5. RuneLite Configuration](#5-runelite-configuration)
  - [5.1 ChromaScape RuneLite Profile](#51-chromascape-runelite-profile)
  - [5.2 Client Display Mode](#52-client-display-mode)
  - [5.3 Object Markers Plugin](#53-object-markers-plugin)
  - [5.4 Other Recommended Plugins](#54-other-recommended-plugins)
- [6. In-Game Setup (Al Kharid Iron Mining Example)](#6-in-game-setup-al-kharid-iron-mining-example)
- [7. Understanding the Script Flow](#7-understanding-the-script-flow)
- [8. Image Templates](#8-image-templates)
- [9. Running a Script](#9-running-a-script)
  - [9.1 Starting ChromaScape](#91-starting-chromascape)
  - [9.2 Script Class Loading](#92-script-class-loading)
  - [9.3 Selecting and Starting a Script](#93-selecting-and-starting-a-script)
  - [9.4 Monitoring](#94-monitoring)
  - [9.5 Stopping](#95-stopping)
- [10. Reporting Bugs](#10-reporting-bugs)
- [11. Completing a Script](#11-completing-a-script)
- [12. Colour System Reference](#12-colour-system-reference)
- [13. Troubleshooting](#13-troubleshooting)
- [14. Tips for Best Results](#14-tips-for-best-results)

---

## 1. System Requirements

- **Windows 11** (64-bit) — ChromaScape uses KInput for remote mouse/keyboard injection via DLL, which is Windows-only
- **Java 17** (JDK, not JRE)
- **RuneLite** client installed and logged in
- **4GB+ RAM** recommended — ChromaScape runs a Spring Boot web server, OpenCV image processing, and the game client simultaneously
- **Internet connection** — required for the Dax Walker pathfinding API and OSRS Wiki image downloads

---

## 2. Installing Prerequisites

### 2.1 Java 17

Download and install JDK 17 from [Eclipse Adoptium](https://adoptium.net/) or [Oracle](https://www.oracle.com/java/technologies/downloads/).

After installation, verify in PowerShell:

```powershell
java -version
```

You should see `openjdk version "17.x.x"` or similar. Note the installation path (e.g., `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot`) — you'll need it later.

To find it programmatically:

```powershell
Get-Command java | Select-Object -ExpandProperty Source
```

### 2.2 MinGW-w64 (for KInput)

KInput's native DLLs must be compiled from source. You need a 64-bit MinGW toolchain.

1. Install [MSYS2](https://www.msys2.org/)
2. From the MSYS2 terminal, install the toolchain:
   ```bash
   pacman -S mingw-w64-x86_64-gcc
   ```
3. Add `C:\msys64\mingw64\bin` (or your MSYS2 install path) to your system PATH

Verify:

```powershell
gcc --version
mingw32-make --version
```

### 2.3 Git

Download from [git-scm.com](https://git-scm.com/download/win) or install via winget:

```powershell
winget install Git.Git
```

### 2.4 RuneLite

Download from [runelite.net](https://runelite.net/). Install and log in to your OSRS account before proceeding.

---

## 3. Building ChromaScape

### 3.1 Clone the Repository

```powershell
cd ~\projects  # or wherever you keep code
git clone --recurse-submodules https://github.com/joshcannella/osrs-bot.git
cd osrs-bot
```

If you cloned without `--recurse-submodules`, initialize the ChromaScape submodule:

```powershell
git submodule update --init --recursive
```

### 3.2 Download Fonts and UI Templates

ChromaScape's OCR and UI detection require font bitmaps from the SRL project and UI templates from OSBC. A batch script handles this automatically:

```powershell
cd ChromaScape
.\CVTemplates.bat
```

This script:
- Clones the [SRL-Development](https://github.com/Villavu/SRL-Development) repo temporarily and copies font `.bmp` files into `src\main\resources\fonts\`
- Downloads UI template images (chat, inventory, minimap) from [OSBC](https://github.com/kelltom/OS-Bot-COLOR) into `src\main\resources\images\ui\`
- Downloads red mouse click indicator images into `src\main\resources\images\mouse_clicks\`
- Generates `.index` files for each font directory

**You must run this before the first build.** The fonts are required for OCR (reading XP, HP, prayer points, etc.) and the UI templates are required for zone detection.

### 3.3 Build KInput Native Libraries

KInput is the remote input system that lets ChromaScape send mouse/keyboard events to the RuneLite window without hijacking your physical mouse.

1. Edit the Java include paths in `third_party\KInput\KInput\KInput\KInput.cbp` to point to your JDK 17 installation:
   ```xml
   <Add directory="C:/Program Files/Eclipse Adoptium/jdk-17.0.x-hotspot/include" />
   <Add directory="C:/Program Files/Eclipse Adoptium/jdk-17.0.x-hotspot/include/win32" />
   ```

2. Build both DLLs from PowerShell:
   ```powershell
   cd third_party\KInput\KInput\KInput
   mingw32-make
   cd ..\KInputCtrl
   mingw32-make
   ```

3. The build produces:
   - `KInput\bin\Release\KInput.dll`
   - `KInputCtrl\bin\Release\KInputCtrl.dll`

4. These DLLs are automatically copied to `ChromaScape\build\dist\` during the Gradle build (the `copyNativeLibraries` task handles this).

### 3.4 Build ChromaScape

```powershell
cd ~\projects\osrs-bot\ChromaScape
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"  # adjust path
.\gradlew.bat build
```

This compiles the Java source, copies the KInput DLLs to `build\dist\`, and runs quality checks. If it succeeds, ChromaScape is ready.

---

## 4. Compiling ScriptGen Scripts

The generated scripts live in the `scriptgen\` project. On the Linux development machine, compilation and syncing to ChromaScape is handled automatically:

```bash
./scripts/deploy.sh
```

This runs `sync-and-compile.sh` which:
- Copies scripts from `scriptgen/` to `ChromaScape/src/main/java/com/chromascape/scripts/`
- Updates package declarations and imports automatically
- Copies `HumanBehavior.java` and fixes its package
- Syncs image resources from `scriptgen/src/main/resources/images/user/` to ChromaScape
- Patches `log4j2.xml` to enable file logging (`ChromaScape/logs/chromascape.log`)
- Compiles in ChromaScape
- Commits and pushes if successful

On Windows, just pull the latest and everything is ready:

```powershell
git pull
```

If you need to compile manually on Windows:

```powershell
cd ~\projects\osrs-bot\ChromaScape
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"
.\gradlew.bat compileJava
```

---

## 5. RuneLite Configuration

### 5.1 ChromaScape RuneLite Profile

On first startup, ChromaScape automatically creates a RuneLite profile called **"ChromaScape"** in your `~\.runelite\profiles2\` directory. This profile pre-configures many plugins with bot-friendly settings (ground markers, NPC highlights, XP globes, etc.).

To activate it:
1. Open RuneLite
2. Click the profile selector (top-right of the client)
3. Select **"ChromaScape"**

You can also manually switch profiles — the bot doesn't force a specific profile, but the ChromaScape profile has sensible defaults.

### 5.2 Client Display Mode

Set RuneLite to **Fixed Mode** (not resizable). ChromaScape's zone detection system (`ZoneManager`) is calibrated for the fixed-mode UI layout. The zones it maps include:

- **Game View** — the main 3D viewport with UI elements masked out
- **Minimap** — HP, Prayer, Run energy, Spec, total XP, and player position sub-zones
- **Control Panel** — the tab buttons (inventory, prayer, magic, etc.)
- **Chat Tabs** — chat box and latest message area
- **Inventory Slots** — all 28 slots, indexed 0–27 left-to-right, top-to-bottom
- **Mouseover** — the tooltip text zone

### 5.3 Object Markers Plugin

This is the most critical plugin for colour-based scripts. ChromaScape finds game objects by detecting specific pixel colours that RuneLite overlays on them.

1. Open the RuneLite plugin configuration (wrench icon)
2. Search for **"Object Markers"** and enable it
3. Set the highlight colour to **Cyan (#00FFFF)** — this is the default colour most scripts expect

To mark objects in-game:
1. Hold **Shift** and **right-click** the object
2. Select **"Mark"** from the context menu
3. The object will glow with your configured highlight colour

For the Al Kharid Iron Mining script, mark:
- The **3 clustered iron rocks** at the mine (around tile 3298, 3293)
- The **bank booth** at Al Kharid bank (around tile 3269, 3167)

### 5.4 Other Recommended Plugins

| Plugin | Purpose | Script Usage |
|---|---|---|
| **XP Tracker** | Shows permanent XP bar on screen | `Minimap.getXp()` reads total XP for detecting level-ups and obstacle completions |
| **Ground Items** | Highlights items on the ground with configurable colours | Used by agility scripts to detect Marks of Grace |
| **NPC Indicators** | Highlights NPCs with configurable colours | Used by combat scripts to detect monsters |

---

## 6. In-Game Setup (Al Kharid Iron Mining Example)

Before starting the script:

1. **Equip your pickaxe** — the script expects all 28 inventory slots free for ore
2. **Stand at the Al Kharid mine** — near the 3 clustered iron rocks you marked with Cyan
3. **Empty your inventory** — the script detects a full inventory by template-matching the iron ore image in slot 28 (the last slot)
4. **Verify highlights are visible** — you should see Cyan outlines on the iron rocks and the bank booth

For other scripts, check the SETUP.md file in `.kiro/specs/scripts/dev/<script-id>/SETUP.md` (or `.kiro/specs/scripts/<script-id>/SETUP.md` for completed scripts) — it lists prerequisites, required items, inventory layout, and RuneLite plugin configuration specific to that script.

---

## 7. Understanding the Script Flow

Every script extends `BaseScript` and overrides `cycle()`. The framework calls `cycle()` in a continuous loop until `stop()` is called or an error occurs.

Here's the Al Kharid Iron Mining cycle:

```
1. Human behavior checks
   ├── Extended break? (long AFK pause)
   ├── Short break? (brief pause)
   ├── Camera fidget? (random middle-mouse rotation)
   └── Idle drift? (small random delay)

2. Is inventory full? (template-match iron ore in slot 28)
   ├── YES:
   │   ├── Walk to bank (Dax Walker → tile 3269, 3167)
   │   ├── Click Cyan-highlighted bank booth
   │   ├── Wait for bank interface to open
   │   ├── Right-click first inventory slot → "Deposit-All"
   │   ├── Press Escape to close bank
   │   └── Walk back to mine (Dax Walker → tile 3298, 3293)
   └── NO:
       ├── Click a Cyan-highlighted iron rock
       ├── Wait ~800-1000ms (adjusted by tempo drift)
       └── Wait until idle message detected

3. Repeat
```

The **HumanBehavior** system is woven into every click action:
- Random mouse speed selection (slow vs medium approach)
- Pre-click hesitation (brief pause before clicking)
- Occasional misclicks (click slightly off-target, then correct)
- Micro-jitter (1–3px hand tremor before clicking)
- Tempo drift (gradually speeds up or slows down over the session)

---

## 8. Image Templates

Scripts use small PNG images of inventory items for template matching (detecting whether an item is in a specific inventory slot). These are auto-downloaded from the OSRS Wiki during script generation.

For the Al Kharid Iron Mining script, the template is:

```
scriptgen\src\main\resources\images\user\Iron_ore.png
```

This is a 32×28px PNG of the iron ore inventory icon with transparency. It's used by `TemplateMatching.match()` to check if the last inventory slot contains iron ore.

If a template is missing, download it manually:

```powershell
New-Item -ItemType Directory -Force -Path "scriptgen\src\main\resources\images\user"

Invoke-WebRequest -Uri "https://oldschool.runescape.wiki/images/Iron_ore.png" `
    -Headers @{ "User-Agent" = "ChromaScape-ScriptGen/1.0" } `
    -OutFile "scriptgen\src\main\resources\images\user\Iron_ore.png"
```

**When wiki images won't work** — RuneLite-specific UI overlays, custom colour-highlighted objects, and game-state indicators not on the wiki require manual screenshots. Crop tightly to the icon with no slot background.

---

## 9. Running a Script

### 9.1 Starting ChromaScape

**Important:** RuneLite must be open and logged in before starting ChromaScape. The framework locates the RuneLite window by title ("RuneLite") on startup and attaches KInput to its process.

**Easiest method — double-click `run.bat`** at the repo root. It runs `git pull` then launches ChromaScape. Use `run.bat --launch-browser` to also open `http://localhost:8080` in your browser automatically.

Or manually:

```powershell
cd ~\projects\osrs-bot
git pull
cd ChromaScape
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"
.\gradlew.bat bootRun
```

Once Spring Boot starts, open your browser to:

```
http://localhost:8080
```

You'll see the **ChromaScape Hub** dashboard with three columns:
- **Left** — Scripts list (all `.java` files in `com.chromascape.scripts`)
- **Center** — Viewport (live view of what the bot sees) and Terminal Output (real-time logs)
- **Right** — Controls (Start/Stop button, Screenshotter) and Statistics

### 9.2 Script Class Loading

Scripts are automatically synced from `scriptgen/` to `ChromaScape/src/main/java/com/chromascape/scripts/` by `deploy.sh` on the Linux development machine. Package declarations and imports are updated automatically during sync. When you `git pull` on Windows, the scripts are already in the correct location and compiled.

If you need to manually sync (e.g., you edited a script directly on Windows), run `sync-and-compile.sh` from the Linux machine or manually copy the file and update the package from `com.scriptgen.scripts` to `com.chromascape.scripts`.

### 9.3 Selecting and Starting a Script

1. In the ChromaScape Hub, click the script name in the **Scripts** panel on the left (e.g., `AlKharidIronMiningScript.java`)
2. The selected script highlights in the list
3. Click the green **START** button
4. The page reloads and the status pill changes from "Offline" to indicate the bot is running
5. The Start button changes to a red **STOP** button

### 9.4 Monitoring

While the script runs:

- **Viewport** — shows the bot's processed game view with colour detection overlays. This updates in real-time via WebSocket
- **Terminal Output** — streams log messages (INFO, ERROR, WARN) from the script. You'll see messages like "Inventory full, banking ore", "Walker error", click coordinates, etc.
- **Statistics** — tracks cycle count, runtime, and other metrics. Resets each time a script starts
- **Bot Status Pill** — the badge in the navbar shows Online/Offline state, synced via WebSocket

You can cover the RuneLite window with other applications while the bot runs — KInput's remote input doesn't require the window to be in the foreground. However, don't minimize RuneLite or move it entirely off-screen.

### 9.5 Stopping

Three ways to stop:

1. **Click the STOP button** in the Controls panel
2. **The script stops itself** on unrecoverable errors (e.g., can't find the bank booth, no iron rocks visible, XP can't be read)
3. **Close ChromaScape** — the script thread is interrupted and the Controller shuts down, releasing the KInput handle

---

## 10. Reporting Bugs

When a script misbehaves at runtime, use the `report-bug.bat` script on Windows:

```powershell
.\report-bug.bat al-kharid-iron-mining
```

This will:
1. Copy `ChromaScape\logs\chromascape.log` to the script's dev directory as `runtime.log`
2. Open the bug report template in Notepad — fill in what happened, expected behavior, and which state the bot was in
3. After you save and close Notepad, it commits and pushes automatically

On the Linux machine, pull and ask the scripter agent to fix it:

```
git pull
/agent osrs-scripter
> Read the bug report for al-kharid-iron-mining and fix it
```

### Log File

ChromaScape writes logs to `ChromaScape\logs\chromascape.log`. This file is created automatically by the patched `log4j2.xml` (applied during `deploy.sh`). The log uses the same format as the Terminal Output in the web UI.

---

## 11. Completing a Script

Once a script is working correctly, mark it as complete from the Linux machine:

```bash
./scripts/complete-script.sh al-kharid-iron-mining
```

This moves the script from `.kiro/specs/scripts/dev/al-kharid-iron-mining/` to `.kiro/specs/scripts/al-kharid-iron-mining/` with a merged `SETUP.md` (setup instructions + changelog) and a copy of the Java source. The dev directory is removed.

---

## 12. Colour System Reference

ChromaScape uses OpenCV HSV colour space for all colour detection. The framework ships with predefined colours in `colours\colours.json`:

| Name | HSV Min | HSV Max | Typical Use |
|---|---|---|---|
| **Cyan** | (87, 225, 226) | (105, 255, 255) | Object Markers (rocks, bank booths, etc.) |
| **Green** | (50, 200, 200) | (70, 255, 255) | Object Markers (obstacles, NPCs) |
| **Red** | (1, 255, 251) | (50, 255, 255) | Ground Items (Marks of Grace, loot) |
| **Yellow** | (20, 255, 255) | (48, 255, 255) | NPC highlights, warnings |
| **Purple** | (127, 115, 181) | (151, 255, 255) | Custom highlights |
| **White** | (0, 0, 255) | (0, 0, 255) | Text detection |
| **Black** | (0, 0, 0) | (0, 0, 0) | Background masking |
| **ChatRed** | (177, 229, 239) | (179, 240, 240) | Chat message detection |

Scripts can reference these by name (e.g., `PointSelector.getRandomPointInColour(image, "Cyan", 15)`) or define custom `ColourObj` instances with specific HSV ranges.

**HSV bounds**: H: 0–180 (OpenCV convention, not 0–360), S: 0–255, V: 0–255. The fourth channel is always 0.

When configuring RuneLite highlight colours, use the hex colour that maps to the HSV range the script expects. For Cyan, that's `#00FFFF`. For Green, `#00FF00`. The exact mapping depends on the HSV tolerance range defined in the `ColourObj`.

---

## 13. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "No iron rock found in game view" | Cyan highlights not visible | Verify you're at the mine, Object Markers is enabled, and colour is set to Cyan (#00FFFF) |
| "Bank booth not found" | Walker arrived at bank but booth isn't highlighted | Mark the bank booth with Cyan in Object Markers |
| "Walker error" | Dax pathfinder API failed | Check internet connection. Verify the XP bar is visible (the walker reads player position via OCR) |
| "Failed to create Kinput instance" | RuneLite not open, or wrong window title | Start RuneLite first. The window title must be exactly "RuneLite" |
| "Missing native libraries in build/dist" | KInput DLLs not built | Follow Section 3.3 to build KInput, then rebuild ChromaScape |
| Script doesn't appear in the UI | Script not in `com.chromascape.scripts` package | See Section 9.2 — copy the script or modify ScriptInstance |
| Inventory detection wrong | Iron ore template doesn't match at current zoom/UI scale | Re-download the template or take a manual screenshot of iron ore in your inventory (crop tightly, no slot background) |
| Bot clicks wrong things | Other Cyan-coloured objects on screen | Remove any Cyan Object Markers that aren't iron rocks or the bank booth |
| "Font masks" error on startup | Fonts not downloaded | Run `CVTemplates.bat` in the ChromaScape directory (Section 3.2) |
| Bot doesn't move mouse | KInput DLL architecture mismatch | Ensure you built KInput with 64-bit MinGW matching your 64-bit Java |
| "Controller accessed while bot is not running" | Script tried to use mouse/keyboard after stop | This is normal during shutdown — the script was interrupted mid-cycle |

---

## 14. Tips for Best Results

- **Camera zoom** — keep at default zoom so colour highlights are a consistent pixel size for detection
- **Don't move RuneLite** while the bot is running — screen coordinates are calibrated on startup via `ScreenManager.getWindowBounds()`
- **Fixed Mode only** — resizable mode changes the UI layout and breaks all zone detection
- **Let breaks happen** — the HumanBehavior system pauses the bot periodically (30–60 second breaks, occasional longer ones). This is intentional anti-detection behavior
- **Watch the first few cycles** — verify it clicks the right rocks and banks successfully before walking away
- **World selection** — pick a less populated world to reduce competition for resources
- **Screenshotter tool** — use the Screenshotter button in the Hub to capture the current game view. Useful for debugging colour detection or creating manual image templates
- **Colour Picker** — visit `http://localhost:8080/colour` while ChromaScape is running to use the built-in colour picker. This helps you identify exact HSV values for custom colour definitions
- **Discord notifications** — scripts can call `DiscordNotification.send()` to alert you of events (out of supplies, errors, level-ups). Configure the webhook URL in your environment if you want remote monitoring

---

## Appendix: Available Generated Scripts

| Script | Activity | Location | Key Requirements |
|---|---|---|---|
| `AlKharidIronMiningScript` | Mine iron ore + bank | Al Kharid | 15 Mining, pickaxe equipped |
| `AlKharidGoldMiningScript` | Mine gold ore + bank | Al Kharid | 40 Mining, pickaxe equipped |
| `DraynorAgilityScript` | Rooftop agility course | Draynor Village | 1 Agility, members world |
| `CooksAssistantScript` | Cook's Assistant quest | Lumbridge | New account |
| `EdgevilleJewelleryScript` | Craft jewellery at furnace | Edgeville | 5+ Crafting, gold bars + moulds |

Each script's Javadoc header contains its specific prerequisites, RuneLite plugin configuration, inventory layout, and image template details.
