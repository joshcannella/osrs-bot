# Draynor Fish & Cook — Setup Instructions

## RuneLite Requirements (Mandatory)
- Windows Display Scaling: **100%**
- RuneScape UI: **"Fixed - Classic"**
- Display Brightness: **middle (50%)**
- ChromaScape RuneLite Profile: **activated**

## RuneLite Plugin Configuration

### NPC Indicators
- Enable the plugin
- Add the **fishing spot** (Net/Bait) at Draynor shore to the highlight list
- Set highlight colour to **Cyan** — the script expects HSV ~90, 254-255, 254-255
- Use **Hull** or **Tile** highlight style

### Object Markers
- Tag **1-3 regular trees** near the Draynor shore in **Green** — HSV ~59-60, 254-255, 254-255
- Tag **lit fires** in **Red** — HSV ~0-1, 254-255, 254-255
- Tagging multiple trees provides fallback if one is chopped by another player

### Idle Notifier
- **Enable** this plugin — required for fishing/chopping/cooking idle detection
- The script uses `Idler.waitUntilIdle()` which reads the idle chat message

## Game Settings
- **Shift-click drop**: must be enabled (Settings → Controls → "Shift click to drop items")

## Image Templates
All auto-downloaded from the OSRS Wiki — no manual screenshots needed:
- `Raw_shrimps.png` ✓
- `Shrimps.png` (cooked) ✓
- `Burnt_shrimp.png` ✓
- `Raw_anchovies.png` ✓
- `Anchovies.png` (cooked) ✓
- `Burnt_anchovies.png` ✓
- `Logs.png` ✓
- `Tinderbox.png` ✓
- `Small_fishing_net.png` ✓

## Starting Position
- Stand near the **Draynor Village fishing spot** on the south shore (~3087, 3228)
- Regular trees are just west of the shore (~3080, 3230)

## Inventory
- **Slot 1**: Tinderbox
- **Slot 2**: Small fishing net
- **Slots 3-28**: Empty

Both items are checked at the start of every cycle — the script stops if either is missing.

## How to Run
- Script class: **DraynorFishCookScript**
- Start ChromaScape, open the web UI at `http://localhost:8080/`
- Select **DraynorFishCookScript** from the sidebar and click Start

## What It Does
1. Fishes shrimp until 26 raw shrimp in inventory (reserves 2 slots for tinderbox + net)
2. Chops a tagged tree for 1 log
3. Lights a fire with tinderbox + logs
4. Cooks all raw shrimp on the fire (presses Space for "Cook All")
5. Drops all cooked and burnt shrimp (shift-drop, excludes tinderbox + net)
6. Repeats

## Safety Features
- **Stuck detection**: If the bot makes no progress for 10 consecutive cycles, it logs out and stops
- **Discord notification**: Sends alerts on stuck detection and missing prerequisites
- **Fire retry**: If fire lighting fails ("can't light here"), walks a tile and retries
- **Cook dialog verification**: If the cook dialog doesn't open, retries instead of sitting idle
- **Fishing spot despawn**: Detects when the spot moves and re-clicks next cycle

## Notes
- At low Cooking levels, expect a lot of burnt shrimp — this is normal
- Fires despawn after ~1-2 minutes; cooking 26 shrimp takes ~47 seconds so timing is fine
- The script uses F2P pathing (no members areas)
- Tag multiple trees in case one gets chopped by another player
