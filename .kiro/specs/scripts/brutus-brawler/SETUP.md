# Brutus Brawler — Setup Instructions

## RuneLite Requirements (Mandatory)
- Windows Display Scaling: **100%**
- RuneScape UI: **"Fixed - Classic"**
- Display Brightness: **middle (50%)**
- ChromaScape RuneLite Profile: **activated**

## RuneLite Plugin Configuration

### NPC Indicators
- Add **"Brutus"** to the NPC list
- Highlight colour: **Cyan** (HSV ~90, 254-255, 254-255)
- Highlight style: **Hull**

### Object Markers
- Shift+right-click the **cow field gate** (~3263, 3298) and mark it
- Colour: **Red** (HSV ~0, 254-255, 254-255)

### Ground Items
- Add to highlighted items: **"Raw t-bone steak"**, **"Cowhide"**, **"Mooleta"**
- Highlight colour: **Purple** (HSV ~140, 237-255, 205-255)

### Ground Markers
- Mark **attack tile** ~(3266, 3297): **Green**
- Mark **north dodge tile** ~(3266, 3296): **Orange**
- Mark **south dodge tile** ~(3266, 3298): **Orange**

### Camera
- Lock zoom to a fixed level (TBD — calibrate so yellow overhead text zone is consistent)

### Idle Notifier
- **Enable** — required for combat idle detection

## Image Templates
- `Trout.png` ✓ (already exists)
- `Raw_t-bone_steak.png` — download from OSRS Wiki before first run

## Equipment
- **Neck**: Cowbell amulet (charged with air runes) — stays equipped permanently
- **Weapon**: Best melee weapon available (mithril/adamant/rune scimitar)
- **Armour**: Best melee armour available — prefer chainbodies (higher crush defence vs Brutus)

## Inventory
- **All 28 slots**: Trout (or other food)
- Loot fills slots as food is eaten

## Prerequisites
- **Quest**: "The Ides of Milk" completed
- **Cowbell amulet**: Charged with air runes (1 charge per teleport, max 1000)
- **"Don't ask again"**: Enter the Brutus instance once manually and select "Yes and don't ask again" to skip the dialogue prompt permanently

## Starting Position
- Anywhere — the script cowbell-teleports to the cow field on startup

## How to Run
- Script class: **BrutusBrawlerScript**
- Start ChromaScape, open the web UI at `http://localhost:8080/`
- Select **BrutusBrawlerScript** from the sidebar and click Start
