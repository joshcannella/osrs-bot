# OSRS Skills Reference

Source: https://oldschool.runescape.wiki/w/Skills

## Overview

- 24 skills total in OSRS
- All skills start at level 1 except Hitpoints (starts at level 10)
- Max level: 99; max XP: 200,000,000 (no further levels after 99)
- Skills can be temporarily boosted via equipment, items, Prayer, or potions
- Skills are interlaced — e.g., Woodcutting → logs → Firemaking → fire → Cooking

## XP Scaling

- XP required per level increases ~10% per level (exponential growth)
- XP doubles approximately every 7 levels
- Level 92 is approximately half the total XP needed for level 99
- Formula: `Total XP = floor(sum(floor(x + 300 * 2^(x/7)) / 4) for x = 1 to L-1)`
- Full table: https://oldschool.runescape.wiki/w/Experience

## Skill Categories (Jagex-defined)

### Combat Skills (7)

Directly integrate with the combat system.

| Skill | F2P | Description |
|-------|-----|-------------|
| Attack | Yes | Wield stronger melee weapons; determines melee accuracy |
| Strength | Yes | Determines melee max hit; equip certain weapons |
| Defence | Yes | Wear stronger armour; decreases chance of being hit (does NOT reduce damage) |
| Ranged | Yes | Equip stronger ranged weapons/armour; determines ranged accuracy and damage |
| Prayer | Yes | Activate temporary combat aids (prayers); trained by burying bones or using altars |
| Magic | Yes | Cast combat and utility spells; determines magic accuracy |
| Hitpoints | Yes | Total HP pool; starts at level 10 |

### Gathering Skills (5)

Collect resources, generally to feed Production skills.

| Skill | F2P | Description |
|-------|-----|-------------|
| Mining | Yes | Obtain ores and minerals from rocks; higher level = better pickaxes |
| Fishing | Yes | Catch fish at fishing spots |
| Woodcutting | Yes | Chop trees for logs; higher level = better axes |
| Farming | No | Plant and harvest crops (patch-based, timer-driven) |
| Hunter | No | Capture wild animals and creatures using traps |

### Production Skills (6)

Transform raw resources into useful items.

| Skill | F2P | Description |
|-------|-----|-------------|
| Cooking | Yes | Cook food to heal Hitpoints |
| Crafting | Yes | Create jewellery, pottery, ranged armour, and other items |
| Smithing | Yes | Smelt ores into bars; forge bars into armour and weapons |
| Runecraft | Yes | Create runes from rune/pure essence at altars |
| Fletching | No | Create ranged weapons (bows) and ammunition (arrows, bolts) |
| Herblore | No | Clean herbs and combine with secondaries to create potions |

### Utility Skills (6)

Enhance gameplay mechanics in unique ways.

| Skill | F2P | Description |
|-------|-----|-------------|
| Firemaking | Yes | Light logs into fires (used for Cooking, some quests) |
| Agility | No | Traverse shortcuts; improves run energy recharge and drain rate |
| Thieving | No | Steal from stalls/chests; pickpocket NPCs |
| Slayer | No | Kill specific monsters assigned by Slayer masters (otherwise undefeatable) |
| Construction | No | Build and furnish a player-owned house (POH) |
| Sailing | No | Navigate seas on boats, complete port tasks, salvage shipwrecks, sea charting. OSRS-exclusive skill (released Nov 2025) |

## F2P vs Members Breakdown

**Free-to-play (15 skills):**
Attack, Strength, Defence, Ranged, Prayer, Magic, Hitpoints, Mining, Fishing, Woodcutting, Cooking, Crafting, Smithing, Runecraft, Firemaking

**Members-only (9 skills):**
Agility, Herblore, Thieving, Fletching, Slayer, Farming, Construction, Hunter, Sailing

## Skill Interactions (Key Interlacing)

These are important for scripting — understanding which skills feed into each other:

- **Woodcutting → Firemaking → Cooking**: Cut logs, light fires, cook food
- **Mining → Smithing**: Mine ores, smelt bars, forge equipment
- **Fishing → Cooking**: Catch raw fish, cook for food
- **Farming → Herblore**: Grow herbs, make potions
- **Mining → Crafting**: Mine gems, craft jewellery
- **Woodcutting → Fletching**: Cut logs, fletch into bows/arrows
- **Hunter → Herblore**: Some hunter creatures provide herblore secondaries
- **Slayer → Combat**: Slayer tasks drive combat training against specific monsters
- **Agility → All**: Better run energy benefits every activity requiring movement
- **Construction → Many**: POH provides teleports, altars, storage, restoration pools

## Temporary Boosts

Skills can be boosted above their current level temporarily. Common methods:
- **Potions**: Most skills have associated potions (e.g., Super attack, Ranging potion)
- **Prayers**: Combat prayers boost attack/strength/defence/ranged/magic
- **Equipment**: Some items provide invisible or visible boosts
- **Pies/Stews**: Various food items boost specific skills (e.g., Spicy stew ±5)
- **Forestry**: Woodcutting gets +1 per nearby player (up to +10) on Forestry worlds

Boosts are relevant for scripting because they can unlock content above the player's base level.

## Skill Release History

| Skill | Release Date | Notes |
|-------|-------------|-------|
| Attack, Strength, Defence, Ranged, Hitpoints, Cooking, Firemaking, Mining, Smithing, Woodcutting | 4 Jan 2001 | Original batch |
| Crafting | 8 May 2001 | |
| Magic | 24 May 2001 | Originally split into GoodMagic/EvilMagic |
| Prayer | 24 May 2001 | Originally split into PrayGood/PrayEvil |
| Fishing | 11 Jun 2001 | |
| Herblore | 27 Feb 2002 | Known as "Herblaw" in RSC |
| Fletching | 25 Mar 2002 | |
| Thieving | 30 Apr 2002 | |
| Agility | 12 Dec 2002 | |
| Runecraft | 29 Mar 2004 | Released with RuneScape 2 |
| Slayer | 26 Jan 2005 | |
| Farming | 11 Jul 2005 | |
| Construction | 31 May 2006 | Originally planned as "Carpentry" |
| Hunter | 21 Nov 2006 | Last skill in the Aug 2007 archive |
| Sailing | 19 Nov 2025 | Only skill exclusive to OSRS |

## Proposed Skills (Not Added)

- **Artisan** (2014): Slayer-like tasks for skilling. Polled twice, failed.
- **Warding** (2018-2019): Magical armour crafting. Polled, failed.
- **Shamanism** (2023): Shamanistic crafting + Spirit Realm. Lost poll to Sailing but concept retained.
- **Taming** (2023): Tame and train creatures. Lost poll, concept scrapped.
