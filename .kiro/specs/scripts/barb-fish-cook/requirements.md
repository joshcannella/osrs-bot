# Script Requirements: barb-fish-cook

## Script ID
`barb-fish-cook`

## Goal
Fly fish trout/salmon at Barbarian Village, cook on the permanent fire, bank cooked fish at Edgeville, repeat.

## Game Context
- **Skill/Activity**: Fishing + Cooking
- **Method**: Fly fishing (Lure) at Barbarian Village river, cooking on permanent fire
- **Location**: Barbarian Village fishing spots (~3104, 3424) / (~3110, 3434), permanent fire (~3100, 3426), Edgeville bank (~3094, 3492)
- **Prerequisites**: Fishing ≥ 20 (trout) / ≥ 30 (salmon), Cooking ≥ 15 (trout) / ≥ 25 (salmon), combat level ≥ 29 (barbarians stop aggro)

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Fly fishing rod | Fishing tool (stays in inventory) | GE / fishing shops | 309 |
| Feather | Bait — consumed 1 per catch (stackable) | GE | 314 |

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| Any | Fly fishing rod | Must remain in inventory at all times |
| Any | Feather (stack) | Consumed 1 per fish; bring thousands |
| Remaining 26 | Empty → raw fish → cooked fish | Fills during fishing, transforms during cooking |

## State Machine

### State 1: FISHING
- **Condition**: Inventory not full, feathers present
- **Action**:
  - If fishing spot (Cyan) not visible → `Walk.to(FISHING_TILE)` to get spot on screen
  - Click fishing spot via `ColourClick.getClickPoint()`
  - Polling idle loop: `while` not deadline (120s), call `Idler.waitUntilIdle(this, 3)` — break if idle fires OR if fishing spot colour disappears (spot moved)
  - `LevelUpDismisser.dismissIfPresent()`
  - Check chat for "can't carry" / "full" via OCR
- **Completion**: Chat says "can't carry" → transition to COOK_TROUT. Otherwise (spot moved / idle timeout) → stay in FISHING, re-click next cycle.

### State 2: COOK_TROUT
- **Condition**: Raw trout in inventory (`Inventory.hasItem(this, RAW_TROUT, threshold)`)
- **Action**:
  - If fire (Red) not visible → `Walk.to(FIRE_TILE)` as fallback
  - `Inventory.clickItem(this, RAW_TROUT, threshold, "medium")` — select raw trout
  - Wait ~300ms for "Use" cursor
  - `ColourClick.getClickPoint(this, FIRE_COLOUR)` → click fire
  - Wait ~1200ms for cooking interface
  - `KeyPress.space(this)` — press Space to start "Cook All"
  - `Idler.waitUntilIdle(this, 120)` — wait for cooking to finish
  - `LevelUpDismisser.dismissIfPresent()` — level-up interrupts cooking
  - Re-check `Inventory.hasItem(RAW_TROUT)` — if still has raw trout, repeat (level-up interrupted mid-cook)
- **Completion**: `!Inventory.hasItem(this, RAW_TROUT, threshold)` → transition to COOK_SALMON

### State 3: COOK_SALMON
- **Condition**: Raw salmon in inventory (`Inventory.hasItem(this, RAW_SALMON, threshold)`)
- **Action**: Same sequence as COOK_TROUT but with RAW_SALMON template
- **Completion**: `!Inventory.hasItem(this, RAW_SALMON, threshold)` → transition to DROP_BURNT
- **Skip**: If no raw salmon in inventory, pass through immediately to DROP_BURNT

### State 4: DROP_BURNT
- **Condition**: Burnt fish in inventory (`Inventory.hasItem(this, BURNT_FISH, threshold)`)
- **Action**: Drop all burnt fish (shift-click drop)
- **Completion**: No burnt fish remaining → transition to WALK_TO_BANK
- **Skip**: If no burnt fish in inventory (high cooking level), pass through immediately to WALK_TO_BANK

### State 5: WALK_TO_BANK
- **Condition**: All fish cooked, burnt fish handled
- **Action**: `Walk.to(BANK_TILE)` to Edgeville bank
- **Completion**: Bank booth (Green) visible on screen → transition to BANKING

### State 6: BANKING
- **Condition**: Bank booth visible
- **Action**:
  - Click Green booth via `ColourClick.getClickPoint()` → wait ~1200-1800ms for bank to open
  - `Bank.depositAll(this)` → wait ~300-500ms
  - `Inventory.findInGameView(this, ROD, threshold)` → click to withdraw rod. If not found → Discord notify + stop
  - Wait ~300-500ms
  - `Inventory.findInGameView(this, FEATHER, threshold)` → click to withdraw feathers. If not found → Discord notify + stop
  - Wait ~300-500ms
  - `Bank.close(this)`
- **Completion**: Rod + feathers in inventory, bank closed → transition to WALK_TO_FISH

### State 7: WALK_TO_FISH
- **Condition**: Bank closed, rod + feathers in inventory
- **Action**: `Walk.to(FISHING_TILE)`
- **Completion**: Arrive at fishing area → transition to FISHING

### Recovery State
- **Condition**: Nothing detected / stuck counter ≥ 10
- **Action**: Discord notify → logout → stop

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Fishing spot | Colour (Cyan) | NPC Indicators highlight "Rod Fishing spot" |
| Permanent fire | Colour (Red) | Object Markers highlight the fire west of fishing spots |
| Edgeville bank booth | Colour (Green) | Object Markers highlight bank booth |
| Raw trout | Template match | `/images/user/Raw_trout.png` in inventory |
| Raw salmon | Template match | `/images/user/Raw_salmon.png` in inventory |
| Burnt fish | Template match | `/images/user/Burnt_fish.png` in inventory |
| Fly fishing rod | Template match | `/images/user/Fly_fishing_rod.png` in inventory + bank view |
| Feather | Template match | `/images/user/Feather.png` in inventory + bank view |
| Inventory full | Chat OCR | Read chatbox for "can't carry" / "full" |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Fly fishing rod | OSRS Wiki (ID 309) | `/images/user/Fly_fishing_rod.png` |
| Feather | OSRS Wiki (ID 314) | `/images/user/Feather.png` |
| Raw trout | OSRS Wiki (ID 335) | `/images/user/Raw_trout.png` |
| Raw salmon | OSRS Wiki (ID 331) | `/images/user/Raw_salmon.png` |
| Burnt fish | OSRS Wiki (ID 343) | `/images/user/Burnt_fish.png` |

## Walker Tiles
| Name | Coordinates | Purpose |
|------|-------------|---------|
| FISHING_TILE | (3104, 3424) | Fishing spot area |
| FIRE_TILE | (3100, 3426) | Permanent fire fallback |
| BANK_TILE | (3094, 3492) | Edgeville bank |

## Transportation
- Fishing spots → fire: ~4 tiles west, fire usually on screen already. `Walk.to(FIRE_TILE)` as fallback only
- Fire → Edgeville bank: ~70 tiles north, use `Walk.to(BANK_TILE)`
- Edgeville bank → fishing spots: ~70 tiles south, use `Walk.to(FISHING_TILE)`

## Banking
- **Bank location**: Edgeville bank (~3094, 3492)
- **Deposit method**: `Bank.depositAll()` (right-click slot 0 → Deposit-All)
- **Withdraw**: Use `Inventory.findInGameView()` for rod then feathers — searches full game view for template match
- **Round-trip estimate**: ~140 tiles round trip, ~15-20 seconds with running

## Edge Cases
1. **Fishing spot moves** — Idler fires but chat doesn't say "can't carry" → stay in FISHING, re-click next cycle. Polling loop also breaks if spot colour disappears.
2. **Feathers depleted** — `!Inventory.hasItem(FEATHER)` → Discord notify + stop
3. **Burnt fish** — DROP_BURNT state handles dropping before banking. If none exist (high cooking), state is a no-op pass-through.
4. **Deposit removes rod/feathers** — BANKING state withdraws both back via `Inventory.findInGameView()` + click
5. **Level-up during fishing** — `LevelUpDismisser.dismissIfPresent()` after idle loop
6. **Level-up during cooking** — `LevelUpDismisser.dismissIfPresent()` after cook idle. Re-check for remaining raw fish and re-initiate cooking if interrupted.
7. **Barbarian aggro** — prerequisite is combat ≥ 29; not handled in script
8. **Two fish types in cooking interface** — cook trout first (COOK_TROUT), then salmon (COOK_SALMON) as separate states
9. **Cooking interaction is "use item on fire"** — click raw fish in inventory first, then click fire (two-step)
10. **Rod/feathers not found in bank after deposit** — Discord notify + stop
11. **Fire not visible after fishing** — `Walk.to(FIRE_TILE)` fallback before cooking

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| NPC Indicators | Highlight "Rod Fishing spot" | Cyan (Hull or Tile) |
| Object Markers | Tag permanent fire (west of fishing spots) | Red |
| Object Markers | Tag Edgeville bank booth | Green |
| Idle Notifier | Enabled | Yes |
| Shift-click drop | Enabled | Yes (Settings → Controls) |

## Colour Definitions
| Name | Use | HSV Min | HSV Max |
|------|-----|---------|---------|
| FISHING_SPOT | Cyan — fishing spot NPC | (90, 254, 254, 0) | (91, 255, 255, 0) |
| FIRE | Red — permanent fire | (0, 254, 254, 0) | (1, 255, 255, 0) |
| BANK | Green — Edgeville bank booth | (60, 254, 254, 0) | (61, 255, 255, 0) |
| CHAT_BLACK | Black — chat text OCR | (0, 0, 0, 0) | (0, 0, 0, 0) |

## Burn Levels (on fire)
| Fish | Stop burning at |
|------|-----------------|
| Trout | Cooking 49 |
| Salmon | Cooking 58 |

## Stop Conditions
- Feathers run out (can't fish)
- Rod or feathers not found in bank after deposit
- Stuck for 10+ consecutive cycles
- Any unrecoverable error (walker failure, etc.)

## Notes for Scripter
- Fire is permanent scenery, not a player-lit fire — it never goes out
- Cooking on fire uses "Use item on" interaction, not left-click — must click fish first then fire
- Two fish types means two separate cook cycles per trip (trout then salmon)
- `Bank.depositAll()` dumps everything including rod/feathers — must withdraw both back
- Fishing spots are NPC type "Rod Fishing spot" — they move every 2.5-5 min
- DraynorFishingScript is the closest reference pattern for the fishing + banking loop
- Burnt fish from trout/salmon shares item ID 343
- Bank withdrawals use `Inventory.findInGameView()` (shared utility searching full game view), NOT `Inventory.clickItem()`
- Fishing idle detection uses a polling loop with 3s timeout + spot-visibility check, not a single blocking `waitUntilIdle()` call
- Cooked fish templates are NOT needed — you never need to detect cooked fish in inventory (they just get banked with deposit-all)
