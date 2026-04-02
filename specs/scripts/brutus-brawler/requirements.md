# Script Requirements: Brutus Brawler

## Script ID
`brutus-brawler`

## Goal
Farm the Brutus cow boss for melee combat XP (+100% bonus) and loot, banking when inventory is full.

## Game Context
- **Skill/Activity**: Melee combat training + loot collection
- **Method**: East-positioning slam-dodge strategy — stand east of Brutus's spawn so charge attack never fires, only dodge slams
- **Location**: Lumbridge cow field instanced encounter (~3263, 3297, 0). Enter via gate at ~(3263, 3298).
- **Prerequisites**: Completion of "The Ides of Milk" quest, cowbell amulet (charged with air runes), any melee weapon + armour, food

## NPC Data
- **Name**: Brutus
- **Combat level**: 30
- **HP**: 58
- **NPC IDs**: 15626, 15627
- **Size**: 3×3
- **Max hit**: 3 (basic melee), 19 (specials — dodged)
- **Attack style**: Crush melee, speed 5 ticks
- **Defence**: -7 all melee, -3 magic, 25% earth elemental weakness
- **Respawn**: 36 ticks natural, 13 ticks with cowbell amulet "Ring"
- **XP bonus**: +100% (58 HP × 4 XP × 2 = 464 XP per kill in chosen style, ~154 HP XP)
- **Aggressive**: Yes (aggros automatically when in range)

## Fight Mechanics
- Basic melee attack (max 3) every 5 ticks
- After 4-5 basic attacks, uses a special (alternating after first random one)
- **Charge** (`*growls*` overhead): 3-tick dodge window. Will NOT fire if player stands east of spawn (hits wall). Eliminated by east positioning.
- **Slam** (`*snorts*` overhead): 4-tick dodge window, 3 consecutive slams. Sidestep 1 tile perpendicular, move back for free hit.
- **Anti-safespot** (`*huff*` overhead): After 15 ticks out of range, paths around obstacles.
- **Death** (`m-moo...` overhead): Brutus dies.

## Overhead Text Cues
| Text | Meaning |
|------|---------|
| `Moo` | Regular/idle |
| `*growls*` | Charge incoming (eliminated by east positioning) |
| `*snorts*` | Slam incoming — dodge |
| `*huff*` | Smart-pathing anti-safespot |
| `m-moo...` | Death |

## Detection Approach
Detect presence of yellow overhead text colour (`#FFFF00`) in a fixed screen region above Brutus. No need to distinguish charge vs slam since east positioning eliminates charge entirely. Yellow text present = special incoming = dodge.

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Cowbell amulet (charged) | Teleport to cow field + Ring for fast respawn | The Ides of Milk quest reward, charge with air runes | 33104 |
| Food (trout) | Sustain through basic attacks (max hit 3) | GE or fishing | 333 |
| Melee weapon | Kill Brutus | Equipped | varies |
| Melee armour | Reduce damage taken | Equipped | varies |

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| 0-27 | Trout (or other food) | All 28 slots start as food. Loot fills slots as food is eaten. |

Cowbell amulet stays equipped in neck slot permanently (0 combat stats, no swapping needed).

## State Machine

### State: TRAVEL_TO_GATE
- **Condition**: Not inside Brutus instance (gate colour visible or need to walk there)
- **Action**: Cowbell amulet teleport to (3259, 3277), walk north to gate at ~(3263, 3298)
- **Completion**: Red-highlighted gate is visible on screen

### State: ENTER_INSTANCE
- **Condition**: Gate is visible on screen
- **Action**: Click red-highlighted gate
- **Completion**: Screen transitions to instance (gate colour disappears, Brutus colour appears or player position changes)

### State: POSITION_EAST
- **Condition**: Inside instance, not at attack tile
- **Action**: Walk to east attack tile ~(3266, 3297) via ground marker (green)
- **Completion**: Player is on the green-marked attack tile

### State: ATTACKING
- **Condition**: Brutus is alive (cyan highlight visible), player at attack tile
- **Action**: Click Brutus to engage. Eat food if HP ≤ threshold. Monitor for yellow text in overhead zone.
- **Completion**: Yellow text detected → transition to DODGING. Brutus highlight disappears → transition to LOOTING.

### State: DODGING
- **Condition**: Yellow overhead text detected (slam incoming)
- **Action**: Click orange dodge tile (1 tile north or south). Wait ~1.2s for slam to land. Click green attack tile to return. Repeat for 3 slams total.
- **Completion**: 3 dodge cycles complete → transition to ATTACKING (re-engage Brutus)

### State: LOOTING
- **Condition**: Brutus dead (cyan highlight gone, kill confirmed via XP)
- **Action**: Pick up ground items (purple loot colour). Eat if needed.
- **Completion**: No more purple loot visible, or inventory full → check food count

### State: CHECK_SUPPLIES
- **Condition**: Looting complete
- **Action**: Check food count. If food < MIN_FOOD_TO_FIGHT or inventory full → BANKING. Otherwise → ring cowbell (right-click amulet → Ring) and wait for respawn → ATTACKING.
- **Completion**: Decision made, transition to BANKING or back to waiting for respawn

### State: BANKING
- **Condition**: Need food or inventory full
- **Action**: Exit instance (walk south to gate, click gate). Walk to Lumbridge Castle bank ~(3208, 3220, 2). Open bank, deposit all, withdraw 28 food, close bank. Cowbell teleport back.
- **Completion**: Full inventory of food, back at cow field → TRAVEL_TO_GATE

### Recovery State
- **Condition**: Nothing detected, stuck counter exceeds threshold
- **Action**: Cowbell teleport to reset position. If repeated failures, Discord notify + logout + stop.

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Brutus (alive) | Colour — cyan NPC highlight | `ColourClick.isVisible(this, BRUTUS_COLOUR)` |
| Brutus (dead) | Colour gone + XP delta | Cyan disappears AND XP gained ≥ 464 |
| Special incoming | Yellow pixel scan | Scan fixed rectangle above Brutus for `#FFFF00` (HSV ~30, 255, 255) |
| Gate (entry) | Colour — red object highlight | `ColourClick.getClickPoint(this, GATE_COLOUR)` |
| Ground loot | Colour — purple ground items | `ColourClick.getClickPoint(this, LOOT_COLOUR)` |
| Attack tile | Colour — green ground marker | `ColourClick.getClickPoint(this, ATTACK_TILE_COLOUR)` |
| Dodge tile | Colour — orange ground marker | `ColourClick.getClickPoint(this, DODGE_TILE_COLOUR)` |
| Food in inventory | Template — Trout.png | `Inventory.countItem(this, FOOD_IMAGE, 0.07)` |
| Inventory full | Template — all known items | `Inventory.isFull(this, KNOWN_ITEMS, 0.07)` |
| HP level | Minimap OCR | `Minimap.getHp(this)` |

## Positioning
| Tile | Coordinates | Ground Marker Colour | Purpose |
|------|-------------|---------------------|---------|
| Attack tile | ~(3266, 3297) | Green | East of Brutus, melee range, charge-safe |
| North dodge | ~(3266, 3296) | Orange | Sidestep target for slam dodge |
| South dodge | ~(3266, 3298) | Orange | Alternate sidestep target |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Trout | Already exists | `/images/user/Trout.png` |
| Raw t-bone steak | OSRS Wiki | `/images/user/Raw_t-bone_steak.png` |

## Drops to Collect
| Drop | Quantity | Notes |
|------|----------|-------|
| Raw t-bone steak | 1 (always) | Tradeable, ID 33106 |
| Coins | 60-120 | Auto-stack |
| Runes (air/mind/chaos) | varies | Auto-stack |
| Iron armour pieces | varies | Occasional |
| Cowhide | 1 | Occasional |
| Beginner clue | 1/15 | Tertiary |
| Easy clue | 1/40 | Tertiary |
| Mooleta | 5/150 | Pre-roll unique |

## Transportation
- **To Brutus**: Cowbell amulet teleport → (3259, 3277), walk north to gate
- **To bank**: Walk south from cow field to Lumbridge Castle bank (top floor)
- **Return from bank**: Cowbell amulet teleport back

## Banking
- **Bank location**: Lumbridge Castle top floor ~(3208, 3220, 2)
- **Deposit method**: `Bank.depositAll(this)` — right-click slot 0 → Deposit-All
- **Withdraw**: 28 trout (or configured food)
- **Round-trip estimate**: ~30-40 seconds (walk to bank + bank + teleport back)

## Edge Cases
- **Death**: Player respawns at Lumbridge. Detect via position check near spawn ~(3222, 3218). Recover by re-gearing (if lost items) or just teleport back. Low risk since basic attacks only hit 3 and specials are dodged.
- **Failed dodge**: If slam lands, max hit scales with player HP (~30-40% of max HP). At low levels this is survivable. Eat immediately after.
- **Loot despawn**: Items persist 60 seconds. With ~45-60s kill times, loot from previous kill may despawn if not picked up promptly. Always loot immediately after kill.
- **Instance exit**: If player disconnects or logs out inside instance, they respawn outside. Need to re-enter.
- **Cowbell amulet charges**: 1 air rune per teleport, max 1000 charges. At ~20 kills/trip, 1000 charges lasts a very long time. Script should check if teleport fails (0 charges) and stop.
- **Other players**: Instance is solo — no competition for kills or loot.
- **Level-up dialogue**: Handled by `HumanBehavior.runPreCycleChecks(this)` which includes `LevelUpDismisser`.
- **Camera zoom drift**: Lock zoom via RuneLite Camera plugin. Yellow text detection zone depends on consistent zoom.

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| NPC Indicators | Highlight NPCs | Add "Brutus", colour Cyan |
| NPC Indicators | Highlight style | Hull |
| Object Markers | Highlight objects | Mark gate with Red |
| Ground Items | Highlighted items | "Raw t-bone steak", "Cowhide", "Mooleta" |
| Ground Items | Highlight colour | Purple |
| Ground Markers | Marked tiles | Attack tile (green), dodge tiles (orange) |
| Camera | Inner zoom limit / Outer zoom limit | Lock to a fixed value (TBD — measure in-game) |
| Idle Notifier | Enabled | Yes |

## Stop Conditions
- User manually stops
- Out of food and can't bank (walker error)
- Cowbell amulet out of charges (teleport fails)
- Stuck for 10+ consecutive cycles without progress
- Unrecoverable walker error

## Notes for Scripter
- **Yellow text detection** is the core mechanic. Define a `Rectangle` above where Brutus renders on screen. Scan for yellow pixels using `ColourContours` or raw pixel sampling. This zone must be calibrated with locked camera zoom.
- **Dodge timing is tight**: 4 ticks = 2.4 seconds from `*snorts*` text appearing to slam landing. Script needs to detect yellow → click dodge tile → wait → click attack tile, repeated 3 times. Minimize detection latency.
- **No HumanBehavior hesitation/misclick during dodges** — this is a time-critical combat mechanic. Only apply human-like delays during non-critical actions (looting, banking, eating between kills).
- **Ring cowbell** after each kill to get 13-tick respawn instead of 36-tick. This is a right-click option on the equipped cowbell amulet — need to right-click neck slot in equipment tab, or use the worn equipment interface.
- **XP-based kill detection**: Brutus gives 464 XP in chosen style. Use `Minimap.getXp()` delta ≥ 464 to confirm kill, same pattern as ChickenKillerScript.
- **Ground marker clicking**: The green/orange ground markers are always visible inside the instance. Clicking them is reliable for tile-precise movement during dodges.
- **Food threshold**: `MIN_FOOD_TO_FIGHT` should be ~3 trout (heals 21 total). Brutus deals ~12-18 damage per kill from basic attacks at low levels. 3 trout covers one kill with margin.
