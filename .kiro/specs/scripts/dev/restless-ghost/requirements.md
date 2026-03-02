# Script Requirements: The Restless Ghost

## Script ID
`restless-ghost`

## Goal
Complete The Restless Ghost quest from start to finish, earning 1 quest point and 1,125 Prayer XP.

## Game Context
- **Skill/Activity**: Quest (The Restless Ghost)
- **Method**: Linear quest completion — walk to NPCs/objects, dialogue, item pickup, item use
- **Location**: Lumbridge Church → Lumbridge Swamp → Church Graveyard → Wizards' Tower basement → Graveyard
- **Prerequisites**: None (F2P, no skill or quest requirements)

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Ghostspeak amulet | Communicate with the Restless Ghost | Father Urhney (received via dialogue during quest) | 552 |
| Ghost's skull | Return to the coffin to complete quest | Wizards' Tower basement altar (searched during quest) | 553 |

No items need to be brought beforehand. Both are obtained during the quest.

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| Any | Ghostspeak amulet | Received from Urhney, then equipped immediately |
| Any | Ghost's skull | Picked up from altar, used on coffin |

Inventory is empty at start. No specific slot layout required.

## State Machine

### Step 1: TALK_AERECK
- **Condition**: Quest not started, no ghostspeak amulet in inventory or equipped
- **Action**: Walk to Father Aereck in Lumbridge Church (3243, 3210). Click him at game center. Dialogue: press space to advance initial text, then select option `3` ("I'm looking for a quest!"), then option `1` ("Ok, let me help."), then space through remaining dialogue (~5 presses).
- **Completion**: Dialogue ends (no item to verify — advance on dialogue completion)

### Step 2: TALK_URHNEY
- **Condition**: Aereck dialogue done, no ghostspeak amulet in inventory
- **Action**: Walk to Father Urhney's hut in Lumbridge Swamp (3147, 3175). Click game center to open the door (if closed), wait, then click game center again to talk to Urhney. Dialogue: press space to advance, then select option `2` ("Father Aereck sent me to talk to you."), then space through remaining dialogue (~6 presses) until amulet is received.
- **Completion**: Ghostspeak amulet appears in inventory (template match `Ghostspeak_amulet.png`)

### Step 3: EQUIP_AMULET
- **Condition**: Ghostspeak amulet detected in inventory
- **Action**: Click the ghostspeak amulet in inventory to equip it.
- **Completion**: Ghostspeak amulet no longer detected in inventory (it's now in the equipment slot)

### Step 4: OPEN_COFFIN
- **Condition**: Amulet equipped (not in inventory)
- **Action**: Walk to the coffin in Lumbridge Church graveyard (3250, 3193). Click game center to open/search the coffin.
- **Completion**: Wait for animation (~2-3 seconds). The Restless Ghost appears.

### Step 5: TALK_GHOST
- **Condition**: Coffin opened, ghost visible
- **Action**: Click game center to talk to the ghost. Space through all dialogue (~8 presses). The ghost tells you his skull was taken to the Wizards' Tower.
- **Completion**: Dialogue ends (advance on dialogue completion)

### Step 6: WALK_TO_TOWER
- **Condition**: Ghost dialogue done, no skull in inventory
- **Action**: Walk to Wizards' Tower entrance (3109, 3162).
- **Completion**: Arrival at tile (walker completes)

### Step 7: DESCEND_TOWER
- **Condition**: At Wizards' Tower ground floor
- **Action**: Click game center to climb down the ladder to the basement.
- **Completion**: Wait for floor transition (~2.5-3.5 seconds)

### Step 8: GET_SKULL
- **Condition**: In basement, no skull in inventory
- **Action**: Walk to the altar (3120, 9567). Click game center to search it. A skeleton (level 13) will attack — ignore it, it deals minimal damage. Press space if any dialogue/warning appears.
- **Completion**: Ghost's skull appears in inventory (template match `Ghosts_skull.png`)

### Step 9: ASCEND_TOWER
- **Condition**: Skull in inventory, still in basement
- **Action**: Click game center to climb the ladder back up.
- **Completion**: Wait for floor transition (~2.5-3.5 seconds)

### Step 10: RETURN_TO_COFFIN
- **Condition**: Skull in inventory, above ground
- **Action**: Walk back to the coffin in Lumbridge graveyard (3250, 3193).
- **Completion**: Arrival at tile (walker completes)

### Step 11: USE_SKULL
- **Condition**: At coffin with skull in inventory
- **Action**: Click skull in inventory (to "use" it), then click game center (coffin) to use skull on coffin. Space through quest completion dialogue (~5 presses).
- **Completion**: Skull no longer in inventory, quest complete screen appears

### Step 12: DONE
- **Condition**: Quest complete
- **Action**: Send Discord notification, log completion, stop script.

### Recovery / Skip Logic
- If ghostspeak amulet is already in inventory at any point before EQUIP_AMULET, skip to EQUIP_AMULET.
- If skull is already in inventory at any point during GET_SKULL through ASCEND_TOWER, skip to RETURN_TO_COFFIN.
- On unrecoverable walker error (IOException or InterruptedException), log and stop.

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Ghostspeak amulet (inventory) | Template matching | Scan all 28 slots for `Ghostspeak_amulet.png` at threshold 0.07 |
| Ghost's skull (inventory) | Template matching | Scan all 28 slots for `Ghosts_skull.png` at threshold 0.07 |
| NPCs (Aereck, Urhney, Ghost) | Walker + center click | Walk to NPC tile, click game center |
| Objects (coffin, ladder, altar, door) | Walker + center click | Walk to object tile, click game center |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Ghostspeak amulet | `https://oldschool.runescape.wiki/images/Ghostspeak_amulet.png` | `/images/user/Ghostspeak_amulet.png` |
| Ghost's skull | `https://oldschool.runescape.wiki/images/Ghost%27s_skull.png` | `/images/user/Ghosts_skull.png` |

## Transportation
- All navigation via Dax walker (`controller().walker().pathTo()`)
- F2P quest — use `false` for the `isMembers` parameter on all `pathTo()` calls
- Basement transition at Wizards' Tower uses ladder (click game center, not walker)

## Banking (if applicable)
Not applicable — no banking required for this quest.

## Edge Cases
- **Father Urhney's door**: His hut door may be closed. The first click at game center after walking to his tile should open it. A second click talks to him. If the door is already open, the first click may talk to him directly — dialogue will still work.
- **Skeleton attack in basement**: A level 13 skeleton attacks when you search the altar. It deals very low damage. The script should ignore it and just grab the skull. If the player is very low level (1 HP, no armour), they could theoretically die — but this is extremely unlikely given the skeleton's low max hit (2).
- **Ghost not appearing**: If the coffin click doesn't produce the ghost, the next cycle's center click should re-interact. The dialogue step handles this naturally.
- **Dialogue option numbering**: OSRS dialogue options are selected by pressing the number key. Verify option positions match: Aereck has "quest" as option 3, Urhney has "Aereck sent me" as option 2.
- **Already started quest**: The skip logic handles partial completion — if the amulet or skull is already in inventory, the script jumps ahead.

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| None required | — | — |

Standard RuneLite requirements apply:
- Windows Display Scaling: 100%
- RuneScape UI: "Fixed - Classic"
- Display Brightness: middle (50%)
- ChromaScape RuneLite Profile: activated

## Stop Conditions
- Quest complete (DONE step reached)
- Unrecoverable walker error (IOException or InterruptedException)
- Inventory item not found when expected (e.g., `clickInventoryItem` fails)

## Notes for Scripter
- Follow the Cook's Assistant script (`CooksAssistantScript.java`) as the reference pattern — same walker + center-click + dialogue approach.
- All dialogue uses `pressSpace()` for continuation and `pressKey(char)` for numbered options.
- The ghostspeak amulet is equipped by clicking it in inventory (left-click equip) — no right-click menu needed.
- The skull is "used" on the coffin: click skull in inventory first (activates "use" cursor), then click the coffin at game center.
- The basement tile Y-coordinate is offset by ~6400 from the surface (standard OSRS basement offset: surface Y + 6400 ≈ basement Y). Walker handles this via the ladder interaction, not direct pathing.
- No colour-based detection needed — everything is walker + template matching.
