# Script Requirements: draynor-fishing

## Script ID
`draynor-fishing`

## Goal
Fish shrimp and anchovies at Draynor Village with small fishing net. Bank at Draynor bank or power-drop when inventory is full.

## Game Context
- **Skill/Activity**: Fishing (levels 1–20+)
- **Method**: Net fishing (shrimp at level 1, anchovies at level 15)
- **Location**: Draynor Village south shore fishing spot (~3087, 3228), Draynor bank (~3092, 3245)
- **Prerequisites**: None (F2P, level 1 fishing)

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Small fishing net | Tool | Draynor fishing shop or spawn in Lumbridge | 303 |

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| Any 1 slot | Small fishing net | Must always be present |
| Remaining 27 | Empty → fill with raw shrimp/anchovies | |

## State Machine

### State: FISHING
- **Condition**: Inventory not full, fishing spot visible or walkable
- **Action**: Click cyan-highlighted fishing spot, wait for idle or spot disappearance
- **Completion**: `Inventory.isFullByChat()` returns true → transition to WALK_TO_BANK (or DROP if banking disabled)
- **Edge case**: Spot not visible → walk to FISHING_TILE, retry. Spot null → increment stuck counter.

### State: WALK_TO_BANK
- **Condition**: Inventory full, bank not visible
- **Action**: Walk to BANK_TILE
- **Completion**: Bank colour visible on screen → transition to BANKING
- **Edge case**: Walk fails → increment stuck counter, retry next cycle

### State: BANKING
- **Condition**: At bank, bank colour visible
- **Action**: Click bank booth, deposit all, withdraw net, close bank
- **Completion**: Net in inventory, bank closed → transition to WALK_TO_FISH
- **Edge case**: Net not found in bank → stop script. Bank booth click fails → increment stuck counter.

### State: WALK_TO_FISH
- **Condition**: Inventory has net + empty slots
- **Action**: Walk to FISHING_TILE
- **Completion**: Arrived → transition to FISHING

### State: DROP (if banking disabled)
- **Condition**: Inventory full, banking disabled
- **Action**: Shift-drop all except net slot
- **Completion**: Inventory has space → transition to FISHING

### Recovery
- Stuck counter ≥ 10 → Discord notify, logout, stop
- No net in inventory → Discord notify, stop

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Fishing spot | Colour (cyan) | NPC Indicators: "Fishing spot" highlighted cyan (HSV 90-91, 254-255, 254-255) |
| Bank booth | Colour (red) | Object Markers: Draynor bank booth highlighted red (HSV 0-1, 254-255, 254-255) |
| Inventory full | Chat OCR | `Inventory.isFullByChat()` — reads "can't carry" / "full" from chatbox |
| Small fishing net | Template | `/images/user/Small_fishing_net.png` at 0.07 threshold |
| Raw shrimp | Template | `/images/user/Raw_shrimps.png` at 0.07 threshold |
| Raw anchovies | Template | `/images/user/Raw_anchovies.png` at 0.07 threshold |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Small fishing net | OSRS Wiki | `/images/user/Small_fishing_net.png` |
| Raw shrimps | OSRS Wiki | `/images/user/Raw_shrimps.png` |
| Raw anchovies | OSRS Wiki | `/images/user/Raw_anchovies.png` |

## Transportation
- Walk between fishing spot (3087, 3228) and Draynor bank (3092, 3245) — short distance, ~15 tiles

## Banking
- **Bank location**: Draynor Village bank (3092, 3245)
- **Deposit method**: `Bank.depositAll()` (right-click slot 0 → Deposit-All)
- **Withdraw**: Small fishing net (click in bank view via `Inventory.findInGameView()`)
- **Round-trip estimate**: ~30 tiles, ~10-15 seconds

## Edge Cases
- Fishing spot moves mid-action → Idler detects idle, re-click
- Level-up dialog → `LevelUpDismisser.dismissIfPresent()` after each fishing action
- Bank interface fails to open → stuck counter, retry next cycle
- Net lost (deposited and not found in bank) → stop script
- Chat OCR misread → secondary check via `Inventory.isFull()` with known items as fallback

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| NPC Indicators | Highlight "Fishing spot" | Cyan fill |
| Object Markers | Highlight Draynor bank booth | Red fill |
| Idle Notifier | Enabled | Default settings |
| Display Scaling | Windows | 100% |
| UI Layout | Fixed - Classic | or Resizable - Classic |
| Brightness | Middle | 50% |
| ChromaScape Profile | Activated | — |

## Stop Conditions
- No fishing net in inventory and not found in bank
- Stuck counter reaches 10 consecutive failed cycles
- Script interrupted

## Notes for Scripter
- Use `Inventory.isFullByChat()` — do NOT hand-roll chat OCR
- Use `Inventory.findInGameView()` for bank withdrawals — do NOT write private helper
- Full HumanBehavior integration on every click (slow approach, hesitate, misclick, microJitter)
- State machine with enum — each state is its own method
- Only reset stuckCounter on actual state transitions, not on every action attempt
- Add `waitMillis()` inside any polling loop to prevent hot-spinning
