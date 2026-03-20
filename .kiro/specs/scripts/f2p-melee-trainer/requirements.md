# Script Requirements: F2P Melee Training Progression

## Script ID
`f2p-melee-trainer`

## Goal
Automatically train Attack, Strength, and Defence through melee combat in F2P, progressing through increasingly difficult monsters as stats grow.

## Game Context
- **Skill/Activity**: Melee combat training (Attack, Strength, Defence)
- **Method**: Kill monsters matched to current combat level, auto-upgrade weapons/armour at tier thresholds
- **Location**: Lumbridge → Barbarian Village → Stronghold of Security → Stronghold of Security (level 3)
- **Prerequisites**: None (fresh F2P account works). Recommended: some starting GP for initial gear from GE.

## Items Required
| Item | Purpose | Obtain From | Wiki-Verified ID |
|------|---------|-------------|------------------|
| Best available scimitar | Primary weapon (bronze→iron→steel→mithril→adamant→rune) | GE or monster drops | varies |
| Amulet of power | Offensive bonuses (+6 all attack, +6 str) | GE | 1731 |
| Best available full helm | Head armour | GE | varies |
| Best available platebody/chainbody | Body armour (chainbody for crush-attacking monsters) | GE | varies |
| Best available plateskirt | Leg armour | GE | varies |
| Best available kiteshield | Shield slot defence | GE | varies |
| Fancy/Fighting boots | Foot slot | Stronghold of Security | 9005/9006 |
| Food (jug of wine or trout/salmon) | Healing | GE or fishing | varies |

## Inventory Layout
| Slot(s) | Item | Notes |
|---------|------|-------|
| 1-24 | Food | Jugs of wine (heal 11, reduce Attack by 2) or trout/salmon |
| 25-28 | Empty | For loot if desired |

## Training Progression

The script selects a monster based on the player's lowest melee stat (Attack, Strength, or Defence):

### Tier 1: Levels 1–20 — Chickens
- **Monster**: Chicken (combat 1, 3 HP)
- **Location**: Lumbridge chicken coop, south of River Lum (Farmer Fred's farm)
- **Why**: Zero food needed, fast kills, feather drops (stackable profit)
- **Food needed**: No

### Tier 2: Levels 20–40 — Barbarians
- **Monster**: Barbarian (combat 9-17, 18-24 HP)
- **Location**: Barbarian Village
- **Why**: High HP for level, low defence, near GE/Varrock west bank, gem drop table access
- **Food needed**: Light (trout/salmon)

### Tier 3: Levels 40–60 — Flesh Crawlers
- **Monster**: Flesh Crawler (combat 28-41, 25 HP)
- **Location**: Stronghold of Security, level 2 (Catacomb of Famine)
- **Why**: Always aggressive to all levels (great AFK), max hit of 1, decent XP
- **Food needed**: Moderate (they hit frequently despite low damage)

### Tier 4: Levels 60–99 — Giant Spiders
- **Monster**: Giant Spider (combat 50, 50 HP)
- **Location**: Stronghold of Security, level 3 (Pit of Pestilence)
- **Why**: Always aggressive to all levels (best AFK training to 99), 50 HP per kill
- **Food needed**: Yes (max hit 7, bring swordfish or anchovy pizza)

## Skill Training Order
1. Train Attack first to reach the next weapon tier threshold (1→5→10→20→30→40)
2. Train Strength to match Attack level
3. Train Defence to match (for armour upgrades)
4. Repeat — keep all three within ~10 levels of each other

Attack styles used:
- **Accurate** (Attack XP) — "Chop" on scimitar
- **Aggressive** (Strength XP) — "Slash" on scimitar
- **Defensive** (Defence XP) — "Block" on scimitar

## Equipment Upgrade Thresholds

### Weapons (scimitars — best F2P DPS)
| Attack Level | Weapon |
|-------------|--------|
| 1 | Bronze scimitar |
| 5 | Steel scimitar |
| 10 | Black scimitar |
| 20 | Mithril scimitar |
| 30 | Adamant scimitar |
| 40 | Rune scimitar |

### Armour (upgrade when Defence level allows)
| Defence Level | Helm | Body | Legs | Shield |
|--------------|------|------|------|--------|
| 1 | Bronze full helm | Bronze chainbody | Bronze plateskirt | Bronze kiteshield |
| 5 | Steel full helm | Steel chainbody | Steel plateskirt | Steel kiteshield |
| 10 | Black full helm | Black chainbody | Black plateskirt | Black kiteshield |
| 20 | Mithril full helm | Mithril chainbody | Mithril plateskirt | Mithril kiteshield |
| 30 | Adamant full helm | Adamant chainbody | Adamant plateskirt | Adamant kiteshield |
| 40 | Rune full helm | Rune chainbody | Rune plateskirt | Rune kiteshield |

## State Machine

### State: CHECK_STATS
- **Condition**: Script start or after banking
- **Action**: Read current Attack, Strength, Defence levels. Determine which skill to train next (lowest of the three). Determine which monster tier to fight. Set attack style accordingly.
- **Completion**: Monster tier and attack style selected.

### State: CHECK_EQUIPMENT
- **Condition**: Stats checked, about to head to training area
- **Action**: Compare current equipment to what the player's levels allow. If upgrades are available and in bank, withdraw and equip them. If not in bank, buy from GE (if GP available).
- **Completion**: Best available gear equipped.

### State: BANK_FOR_FOOD
- **Condition**: Need food for the selected tier (tiers 2-4)
- **Action**: Walk to nearest bank. Deposit loot. Withdraw full inventory of food.
- **Completion**: Inventory full of food.

### State: WALK_TO_TRAINING
- **Condition**: Equipped and supplied
- **Action**: Walk to the training location for the current tier.
- **Completion**: Arrived at training area.

### State: FIGHT
- **Condition**: At training area
- **Action**: If not in combat, find and attack the nearest target monster. If in combat, wait. If HP is low (below 40%), eat food.
- **Completion**: Continuous loop until out of food or level threshold crossed.

### State: EAT
- **Condition**: HP below 40% during combat
- **Action**: Click food in inventory.
- **Completion**: HP restored, return to FIGHT.

### State: LEVEL_CHECK
- **Condition**: After each kill (or periodically)
- **Action**: Check if stats have crossed a tier boundary or if the training skill should switch. If tier changed, go to CHECK_STATS. If attack style should change, update it.
- **Completion**: Continue fighting or transition to new tier.

### State: OUT_OF_FOOD
- **Condition**: No food remaining and HP below 50%
- **Action**: Flee combat (walk away), go to BANK_FOR_FOOD.
- **Completion**: At bank, re-supply.

### State: AGGRO_RESET (Tier 3-4 only)
- **Condition**: Monsters stop attacking after 10 minutes
- **Action**: Run to a corner of the room (or climb ladder and return) to reset aggression timer.
- **Completion**: Monsters aggressive again, return to FIGHT.

### Recovery State
- **Condition**: Unknown state, stuck, or death
- **Action**: If dead, re-gear at bank and walk back. If stuck, walk to nearest bank as reset point.

## Detection Strategy
| Target | Method | Details |
|--------|--------|---------|
| Current combat stats | Stats tab reading | Read Attack/Strength/Defence levels from stats interface |
| HP level / current HP | HP orb or stats tab | Monitor for eating threshold |
| In combat | Animation detection | Player attack animation active |
| Monster (to attack) | NPC detection / click | Click nearest attackable NPC matching target name |
| Food in inventory | Template matching | Scan inventory for food item template |
| Attack style | Combat options tab | Verify correct style is selected |
| Aggro timer | Timer | Track 10-minute windows for aggro reset |

## Image Templates Needed
| Image | Source | Path |
|-------|--------|------|
| Jug of wine | Wiki inventory sprite | `/images/user/Jug_of_wine.png` |
| Trout | Wiki inventory sprite | `/images/user/Trout.png` |
| Salmon | Wiki inventory sprite | `/images/user/Salmon.png` |
| Swordfish | Wiki inventory sprite | `/images/user/Swordfish.png` |
| Anchovy pizza | Wiki inventory sprite | `/images/user/Anchovy_pizza.png` |

## Transportation
- All navigation via Dax walker (`controller().walker().pathTo()`)
- F2P only — use `false` for `isMembers` parameter
- Stronghold of Security: enter via hole in Barbarian Village, navigate through doors on each level
- Ladder transitions between SoS floors use center-click interaction

## Banking
- **Tier 1 (Chickens)**: No banking needed
- **Tier 2 (Barbarians)**: Varrock west bank or GE (closest to Barbarian Village)
- **Tier 3-4 (Stronghold)**: Edgeville bank (closest to SoS entrance)
- **Deposit method**: Deposit-All, then withdraw food
- **Round-trip estimate**: ~30-60 seconds from SoS to Edgeville bank and back

## Edge Cases
- **Stronghold of Security doors**: Each door asks a security question. The script must handle the dialogue by selecting the correct answer or pressing space. On first traversal, all doors must be answered. Subsequent visits remember answers.
- **Death**: Player respawns in Lumbridge. Script should detect death (HP = 0 or Lumbridge location unexpectedly), re-gear from bank, and resume.
- **World hopping**: If training spots are crowded (kills being stolen), consider world hopping. Optional feature.
- **Aggro reset timing**: Giant spiders and flesh crawlers are always aggressive but the aggro zone resets. Track time and proactively reset by running to room corners.
- **Level-up dialogue**: OSRS shows a level-up dialogue box. Script must dismiss it (press space or click) to resume combat.
- **Attack style switching**: When switching from training Attack to Strength, the combat options tab must be opened and the correct style clicked.
- **Jug of wine Attack debuff**: Wine reduces Attack by 2 temporarily. Acceptable for Strength/Defence training, but for Attack training consider using trout/salmon instead.

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
- All three melee stats reach a user-configured target level (default: 99)
- Player dies and cannot re-gear (no GP, no backup equipment)
- Unrecoverable walker error
- User manually stops the script

## Notes for Scripter
- The core loop is simple: check stats → pick monster → fight → eat → bank → repeat. The complexity is in the tier transitions and equipment upgrades.
- Flesh Crawlers (tier 3) are the sweet spot — always aggressive, max hit 1, decent XP. Players can AFK here for 20 levels.
- Giant Spiders (tier 4) are the endgame — always aggressive, 50 HP, but they hit up to 7 so food consumption is real.
- For the attack style, use the combat options interface. Scimitars have: Chop (accurate/Attack), Slash (aggressive/Strength), Lunge (controlled/shared), Block (defensive/Defence). Avoid "Lunge" — it splits XP.
- The Stronghold of Security entrance is the hole in the center of Barbarian Village. First-time entry requires answering security questions at each door.
- Consider adding a "training mode" config: XP-focused (best XP/hr path above) vs profit-hybrid (hill giants, moss giants for drops). This spec covers XP-focused only.
- Chickens at tier 1 are intentionally simple — no food, no banking, just click and kill. Good for levels 1-20 where the player is too weak for anything else.
