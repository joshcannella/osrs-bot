# Script Requirements: Chicken Killer (Loot & Bury)

## Script ID
`chicken-killer`

## Goal
Kill chickens at Lumbridge, loot feathers and bones from each kill, and bury bones for Prayer XP.

## Game Context
- **Skill/Activity**: Melee combat training + Prayer (bone burying)
- **Method**: Kill chickens, loot feathers (stackable) and bones, bury bones immediately after looting
- **Location**: Lumbridge chicken coop — north of Lumbridge castle, east of the cow field (Farmer Fred's farm area, ~3235, 3295, 0)
- **Prerequisites**: None (level 1 account works, F2P)

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Any melee weapon (optional) | Faster kills | Equipped already or GE | varies |

No items are strictly required — chickens can be punched to death. The player should arrive with whatever weapon/armour they already have equipped.

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| 1 | Feathers (stackable) | Accumulates over time, never fills a second slot |
| 2-28 | Empty | Bones picked up one at a time and buried immediately |

Inventory stays nearly empty because bones are buried as soon as they're looted and feathers stack. The script never needs to bank.

## NPC Data
- **Name**: Chicken
- **Combat level**: 1
- **HP**: 3
- **NPC IDs**: 1017, 1018
- **Max hit**: 1
- **Attack style**: Melee
- **Aggressive**: No

## Drop Table (Relevant)
| Drop | Quantity | Notes |
|------|----------|-------|
| Feathers | 5–15 | Stackable, always dropped |
| Bones | 1 | Always dropped |
| Raw chicken | 1 | Always dropped — **not looted** by this script |

## State Machine

### State: FIND_CHICKEN
- **Condition**: Not in combat, no bones on ground nearby
- **Action**: Scan game view for a live chicken (NPC highlight colour). Click to attack.
- **Completion**: Player enters combat (animation starts or HP bar appears on target).

### State: WAIT_FOR_KILL
- **Condition**: In combat with a chicken
- **Action**: Wait for the chicken to die. No eating needed — chickens hit 0-1 and the player will almost never take damage.
- **Completion**: Chicken dies (combat ends, ground items appear).

### State: LOOT_FEATHERS
- **Condition**: Chicken dead, feathers on ground
- **Action**: Click feathers on the ground (template match or right-click loot). Feathers stack in inventory.
- **Completion**: Feathers picked up (inventory feather count increases or ground item disappears). If feathers not detected, skip to LOOT_BONES (another player may have grabbed them).

### State: LOOT_BONES
- **Condition**: Feathers looted (or skipped), bones on ground
- **Action**: Click bones on the ground (template match).
- **Completion**: Bones appear in inventory (template match `Bones.png` in any inventory slot).

### State: BURY_BONES
- **Condition**: Bones detected in inventory
- **Action**: Click bones in inventory to bury them. Wait for bury animation (~1.2s / 2 ticks).
- **Completion**: Bones no longer in inventory (template match fails). Return to FIND_CHICKEN.

### Recovery State
- **Condition**: No chicken found, no ground loot detected, not in combat
- **Action**: Walk back to chicken coop center tile (~3235, 3295, 0) to re-center. Increment a consecutive-failure counter each cycle that fails to enter combat.
- **Escalation**: If the failure counter reaches a configurable threshold (default: 10 consecutive cycles without entering combat), log out and stop the script. This covers scenarios like all chickens being killed by other players, the player being stuck on terrain, or the coop being empty.
- **Reset**: The failure counter resets to 0 any time the script successfully enters combat (transitions to WAIT_FOR_KILL).

## Attack Style Rotation

The script rotates attack styles to train all three melee stats, prioritizing Strength > Attack > Defence.

### Style Mapping (Scimitar / default weapon)
| Style | XP Gained | Combat Options Position |
|-------|-----------|------------------------|
| Aggressive (Slash) | Strength | 2nd option |
| Accurate (Chop) | Attack | 1st option |
| Defensive (Block) | Defence | 4th option |

**Avoid "Controlled" (Lunge, 3rd option)** — it splits XP across all three stats, which is inefficient.

### Rotation Logic
- Track levels gained in the current style's skill (e.g., Strength levels gained while on Aggressive)
- When the configured number of levels is gained (default: 2 for Strength, 1 for Attack, 1 for Defence), rotate to the next style in priority order: Strength → Attack → Defence → Strength → ...
- This naturally gives Strength double the training time since it needs 2 levels before rotating, while Attack and Defence rotate after 1 level each.
- To switch: open the Combat Options tab, click the correct style, then return to the Inventory tab.
- On script start, read current Attack/Strength/Defence levels and begin on Strength (Aggressive).

### Configuration Constants
- `LEVELS_PER_ROTATION_STR` — Strength levels before switching (default: 2)
- `LEVELS_PER_ROTATION_ATT` — Attack levels before switching (default: 1)
- `LEVELS_PER_ROTATION_DEF` — Defence levels before switching (default: 1)

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Live chicken (to attack) | RuneLite NPC highlight colour | Scan game view for NPC highlight colour via `ColourContours` or `PointSelector` |
| Feathers (ground) | Template matching | `findImageInGameView("Feathers.png")` with relaxed threshold (0.10-0.15 for ground items) |
| Bones (ground) | Template matching | `findImageInGameView("Bones.png")` with relaxed threshold (0.10-0.15 for ground items) |
| Bones (inventory) | Template matching | Scan inventory slots for `Bones.png` at threshold 0.07 |
| In combat | Idle detection | `Idler.waitUntilIdle()` — returns when combat ends |
| Feathers (inventory) | Template matching | `Feathers.png` in inventory — used to confirm loot pickup |
| Attack style (active) | Combat Options tab | Read which style is currently selected to verify switches |
| Skill levels (Att/Str/Def) | Stats tab or XP tracker | Read current levels to detect level-ups for style rotation |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Feathers | OSRS Wiki: `https://oldschool.runescape.wiki/images/Feather.png` | `/images/user/Feather.png` |
| Bones | OSRS Wiki: `https://oldschool.runescape.wiki/images/Bones.png` | `/images/user/Bones.png` |

Note: Ground item sprites render differently than inventory icons. Use relaxed thresholds (0.10–0.15) for ground detection per lessons learned. Inventory detection uses standard threshold (0.05–0.07).

## Transportation
- Player should start at or near the Lumbridge chicken coop
- If out of position, walk to coop via `controller().walker().pathTo(new Point(3235, 3295), false)` (F2P)
- No banking trips needed, so no travel loop

## Banking (if applicable)
Not applicable. Feathers stack infinitely and bones are buried on the spot. The script never needs to bank.

If the player eventually wants to bank feathers, the closest bank is Lumbridge castle top floor (~3208, 3220, 2) — but this is out of scope for this script.

## Edge Cases
- **Other players killing chickens**: The coop can be busy. If no live chicken is found, wait briefly and re-scan. If ground loot disappears before pickup (another player grabbed it), skip to FIND_CHICKEN.
- **Chicken wanders out of coop**: Chickens can walk through the gate. If the clicked chicken is outside the fence, the player follows — this is fine, just loot and return.
- **Level-up dialogue**: Dismiss by pressing space. Can occur for Attack, Strength, Defence, Hitpoints, or Prayer (from burying).
- **Full inventory**: Should never happen since bones are buried immediately and feathers stack. If somehow full (player started with items), bones can't be picked up — skip LOOT_BONES and go to FIND_CHICKEN. Log a warning.
- **Ground item despawn**: Items despawn after ~2 minutes. If the player is slow (e.g., long AFK drift from HumanBehavior), loot may vanish. Handle gracefully — if template match fails on ground, skip to next state.
- **Multiple ground loot piles**: If multiple chickens die nearby (from other players), the script may pick up loot from any pile. This is fine — all chickens drop the same items.
- **Raw chicken on ground**: The script intentionally ignores raw chicken. It will remain on the ground and despawn naturally.

## RuneLite Plugin Setup
| Plugin | Setting | Value |
|--------|---------|-------|
| NPC Indicators | Highlight NPCs | Enable, add "Chicken" to list |
| NPC Indicators | Highlight colour | Set to a distinct colour (e.g., cyan) — document the HSV values for `ColourObj` |
| Ground Items | Highlighted Items | Add "Feather", "Bones" |
| Ground Items | Highlight colour | Set to a distinct colour for ground loot detection |

Standard RuneLite requirements:
- Windows Display Scaling: 100%
- RuneScape UI: "Fixed - Classic"
- Display Brightness: middle (50%)
- ChromaScape RuneLite Profile: activated

## Stop Conditions
- User manually stops the script
- Unrecoverable walker error (IOException or InterruptedException)
- Failed to enter combat for N consecutive cycles (default: 10) — logs out and stops
- Configurable: stop after N bones buried, or after reaching a target Prayer level, or after a runtime duration

## Notes for Scripter
- This is a very simple loop: attack → wait → loot feathers → loot bones → bury → repeat. No banking, no eating, no equipment swaps.
- Chickens have 3 HP and die in 1-3 hits even at level 1 stats. Combat is trivial.
- Bones give 4.5 Prayer XP each when buried. At ~300 kills/hour that's ~1,350 Prayer XP/hour — slow but passive.
- Feathers are worth ~2-3 GP each. At 5-15 per kill and ~300 kills/hour, that's roughly 3,000-13,500 GP/hour. Not great, but it's free money for a new account.
- The loot order matters: pick up feathers first (they stack, no inventory pressure), then bones (take a slot), then immediately bury. This keeps inventory clear.
- Use `Idler.waitUntilIdle()` after attacking to detect when the chicken dies, rather than trying to read HP bars.
- For ground item pickup, follow the lessons learned: use `findImageInGameView()` with relaxed thresholds, don't blindly click screen center.
- Burying bones is a simple left-click on the bones in inventory. The bury animation is 2 ticks (1.2s). Use `HumanBehavior.adjustDelay()` for the wait after burying.
- The chicken coop has a small area with ~5-6 chickens that respawn every ~25 seconds. In a quiet world there's always something to kill.
- Consider adding a brief post-kill delay before looting to simulate the player noticing the drop — this is a natural HumanBehavior hesitation point.
- Attack style switching: open Combat Options tab, click the correct style position, then switch back to Inventory tab. The combat tab icon is the crossed-swords at the top of the interface. Style positions are fixed: 1st=Accurate, 2nd=Aggressive, 3rd=Controlled, 4th=Defensive.
