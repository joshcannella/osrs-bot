# ChromaScape ScriptGen User Guide

A comprehensive guide to setting up and running generated scripts in Old School RuneScape using the ChromaScape framework. This guide uses the **Al Kharid Iron Mining Script** as a walkthrough example, but the same process applies to any generated script.

---

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. RuneLite Plugin Configuration](#2-runelite-plugin-configuration)
- [3. In-Game Setup](#3-in-game-setup)
- [4. Understanding the Script Flow](#4-understanding-the-script-flow)
- [5. Image Templates](#5-image-templates)
- [6. Compiling the Script](#6-compiling-the-script)
- [7. Running the Script](#7-running-the-script)
- [8. Troubleshooting](#8-troubleshooting)
- [9. Tips for Best Results](#9-tips-for-best-results)

---

## 1. Prerequisites

Before anything else, make sure you have:

- **Java 17** installed
- **Windows 11** — ChromaScape uses KInput for remote mouse input, which is Windows-only
- **RuneLite client** installed and logged in — ChromaScape operates on top of RuneLite
- **ChromaScape built and running** — follow the [Installation Guide](https://github.com/StaticSweep/ChromaScape/wiki/Pre%E2%80%90requisite-installations) if you haven't already

For the Al Kharid Iron Mining script specifically:

- **15 Mining** (minimum level to mine iron ore)
- **Any pickaxe equipped** (not in inventory — all 28 slots need to be free for ore)
- **Members or F2P world** — Al Kharid mine is accessible on both

---

## 2. RuneLite Plugin Configuration

ChromaScape is colour-based — it finds things on screen by looking for specific pixel colours. You tell RuneLite to highlight the objects the bot needs to see.

### Object Markers Plugin

1. Open RuneLite and go to the **Plugin Hub** (wrench icon → search "Object Markers")
2. Make sure **Object Markers** is enabled
3. Set the highlight colour to **Cyan (#00FFFF)**
4. In-game, hold **Shift** and **right-click** each of the following objects, then select **"Mark"**:
   - The **3 clustered iron rocks** at Al Kharid mine (around tile 3298, 3293 — the southeast cluster is ideal)
   - The **bank booth** at Al Kharid bank (around tile 3269, 3167)
5. All marked objects should now glow Cyan

Both the rocks and the bank booth use the same Cyan colour. The script knows which is which based on context — it only looks for the bank booth after walking to the bank tile.

### XP Tracker (Optional but Recommended)

1. Enable the **XP Tracker** plugin in RuneLite
2. This isn't strictly required for the mining script, but it's useful for monitoring progress

### Client Settings

- Set the client to **Fixed Mode** (not resizable) — ChromaScape's zone detection is calibrated for fixed mode
- Don't minimize RuneLite or move it entirely off-screen. You *can* cover it with other windows though — the remote input still works

---

## 3. In-Game Setup

Before starting the script:

1. **Equip your pickaxe** — the script expects all 28 inventory slots to be empty for ore
2. **Stand at the Al Kharid mine** — near the 3 clustered iron rocks you marked
3. **Make sure your inventory is empty** — the script detects a full inventory by template-matching iron ore in slot 28 (the last slot)
4. **Verify your marked objects are visible** — you should see Cyan highlights on the iron rocks around you

---

## 4. Understanding the Script Flow

Here's what the script does each cycle:

```
1. Human behavior checks (breaks, camera fidgets, idle drift)
2. Is inventory full? (checks if slot 28 has iron ore via image template matching)
   ├── YES → Walk to bank → open booth → deposit all → close bank → walk back to mine
   └── NO  → Click a Cyan-highlighted iron rock → wait for mining to finish (idle detection)
3. Repeat
```

The script uses the **Dax Walker** to navigate between the mine and bank. It sends the player's current tile position to the Dax pathfinding API, which returns a walking path. The bot then follows that path using remote mouse input on the minimap.

Human-like behavior is woven throughout:

- Random breaks (short and extended)
- Camera fidgets (middle-mouse rotations)
- Hesitation before clicks
- Occasional misclicks that get corrected
- Variable mouse speeds
- Tempo drift (gradually speeds up or slows down over time)

---

## 5. Image Templates

The script uses one image template: `Iron_ore.png`. This is auto-downloaded from the OSRS Wiki during script generation and saved to:

```
scriptgen\src\main\resources\images\user\Iron_ore.png
```

This small 32×28px PNG of the iron ore inventory icon is used to detect whether the last inventory slot is full. You shouldn't need to do anything here — the image is already in place if the script was generated properly.

If for some reason it's missing, you can manually download it in PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "scriptgen\src\main\resources\images\user"

Invoke-WebRequest -Uri "https://oldschool.runescape.wiki/images/Iron_ore.png" `
  -Headers @{ "User-Agent" = "ChromaScape-ScriptGen/1.0" } `
  -OutFile "scriptgen\src\main\resources\images\user\Iron_ore.png"
```

---

## 6. Compiling the Script

The generated scripts live in the `scriptgen\` project, which is separate from ChromaScape (it uses ChromaScape as a read-only dependency via Gradle composite build).

To compile in PowerShell:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17"   # adjust to your actual JDK 17 path
cd scriptgen
.\gradlew.bat compileJava
```

If you're unsure where Java 17 is installed:

```powershell
Get-Command java | Select-Object -ExpandProperty Source
```

If compilation succeeds with no errors, you're good. If it fails, check the error output — it's usually a missing import or a typo.

---

## 7. Running the Script

ChromaScape uses a **web-based control panel** served locally via Spring Boot.

### Starting ChromaScape

1. Navigate to the ChromaScape directory and run the application:
   ```powershell
   cd ChromaScape
   .\gradlew.bat bootRun
   ```
2. Open your browser and go to `http://localhost:8080`
3. You'll see the **ChromaScape Hub** — a dashboard with a script list on the left, a viewport in the center, and controls on the right

### Script Class Loading

The ChromaScape web UI loads scripts from the `com.chromascape.scripts` package by default. Since generated scripts live in `com.scriptgen.scripts`, you have two options to run them:

**Option A — Copy the script into ChromaScape's scripts directory:**

```powershell
Copy-Item "scriptgen\src\main\java\com\scriptgen\scripts\AlKharidIronMiningScript.java" `
  -Destination "ChromaScape\src\main\java\com\chromascape\scripts\AlKharidIronMiningScript.java"
```

Then update the `package` declaration at the top of the copied file from `com.scriptgen.scripts` to `com.chromascape.scripts`, and copy `HumanBehavior.java` as well (or adjust the import). Rebuild ChromaScape.

**Option B — Modify the ScriptInstance class** to also search `com.scriptgen.scripts` (preferred for development — keeps ChromaScape unmodified and lets you iterate on scriptgen independently).

### Selecting and Starting

1. In the ChromaScape Hub, the **Scripts** panel on the left lists available script files
2. Click on `AlKharidIronMiningScript.java` to select it
3. Click the green **START** button in the Controls panel on the right
4. The status pill in the navbar will change from "Offline" to indicate the bot is running

### Monitoring

While the script runs:

- The **Viewport** panel shows what the bot "sees" — the game view with colour detection overlays
- The **Terminal Output** panel shows real-time logs (clicks, banking, walker paths, errors)
- The **Stats** section tracks cycles, runtime, and other metrics

### Stopping

- Click the **START** button again (it acts as a toggle), or the bot will stop itself if it encounters an unrecoverable error (e.g., can't find the bank booth, can't find any iron rocks)
- The script also stops gracefully if the thread is interrupted

---

## 8. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "No iron rock found in game view" | Cyan highlights not visible | Make sure you're standing at the mine and the Object Markers plugin is active with Cyan colour |
| "Bank booth not found" | Walker arrived at bank but booth isn't highlighted | Verify you marked the bank booth with Cyan in Object Markers |
| "Walker error" | Dax pathfinder failed | Check internet connection — the walker calls an external API. Also verify your player position is readable (XP bar visible) |
| Script doesn't appear in the UI | Script not in the right package/directory | See Section 7 above about script class loading |
| Inventory detection wrong | Iron ore template doesn't match | Re-download the template image or take a manual screenshot of iron ore in your inventory (crop tightly to the icon, no slot background) |
| Bot clicks wrong things | Other Cyan-coloured objects on screen | Remove any other Cyan Object Markers that aren't iron rocks or the bank booth |

---

## 9. Tips for Best Results

- **Zoom level matters** — keep the camera at default zoom so the colour highlights are a consistent size
- **Don't move the RuneLite window** while the bot is running — the screen coordinate system is calibrated on startup
- **Keep the game in Fixed Mode** — resizable mode changes the UI layout and breaks zone detection
- **Let the bot take breaks** — the HumanBehavior system will naturally pause the bot periodically. Don't panic when it stops clicking for 30–60 seconds; that's intentional
- **Watch the first few cycles** — make sure it's clicking the right rocks and successfully banking before walking away
- **World selection** — pick a less populated world to reduce competition for iron rocks. The 3-rock cluster at Al Kharid is popular

---

The same general process applies to any generated script — the main differences are which RuneLite plugins/colours to configure and what items to have in your inventory. Each script's Javadoc header lists its specific prerequisites, RuneLite setup, and inventory layout.
