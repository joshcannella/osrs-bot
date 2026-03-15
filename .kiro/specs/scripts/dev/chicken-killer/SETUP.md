# Chicken Killer — Setup Instructions

## RuneLite Requirements (Mandatory)
- Windows Display Scaling: **100%**
- RuneScape UI: **"Fixed - Classic"**
- Display Brightness: **middle (50%)**
- ChromaScape RuneLite Profile: **activated**

## RuneLite Plugin Configuration

### NPC Indicators
- Enable the plugin
- Add **"Chicken"** to the NPC list
- Set highlight colour to **Cyan** — the script expects HSV ~90, 254-255, 254-255
- Use **Hull** or **Tile** highlight style (both work, hull is more reliable)

### Idle Notifier
- **Enable** this plugin — required for combat idle detection
- The script uses `Idler.waitUntilIdle()` which reads the "You are now idle" chat message

## Image Templates
Both auto-downloaded from the OSRS Wiki — no manual screenshots needed:
- `Feather.png` ✓
- `Bones.png` ✓

## Starting Position
- Stand at or near the **Lumbridge chicken coop** (north of Lumbridge castle, east of cow field, near Farmer Fred's farm)
- The script will walk back to the coop center if it gets lost

## Inventory
- **Empty inventory** recommended
- Feathers stack, bones are buried immediately — no banking needed

## Equipment
- Wear whatever melee weapon/armour you have
- No specific gear required — chickens are level 1

## How to Run
- Script class: **ChickenKillerScript**
- Start ChromaScape, open the web UI at `http://localhost:8080/`
- Select **ChickenKillerScript** from the sidebar and click Start

## What It Does
1. Attacks chickens via NPC highlight colour detection
2. Waits for kill (idle detection)
3. Loots feathers (template matching, stackable)
4. Loots bones (template matching)
5. Buries bones immediately (Prayer XP)
6. Rotates attack styles: Strength (2 levels) → Attack (1 level) → Defence (1 level) → repeat
7. Logs out if it can't find chickens for 10 consecutive cycles
