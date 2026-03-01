# OSRS Combat Guide

Source: https://oldschool.runescape.wiki/w/Combat

## Combat Triangle

```
    Magic
    /   \
   /     \
Melee - Ranged
```

- **Melee** is strong against Ranged, weak against Magic
- **Ranged** is strong against Magic, weak against Melee  
- **Magic** is strong against Melee, weak against Ranged

## Combat Styles

### Melee
- **Accuracy**: Determined by Attack level + equipment attack bonus
- **Max Hit**: Determined by Strength level + equipment strength bonus
- **Defence**: Reduces chance of being hit (does NOT reduce damage taken)
- **Attack Styles**: Accurate (+3 Attack), Aggressive (+3 Strength), Defensive (+3 Defence), Controlled (+1 all three)

### Ranged
- **Accuracy & Damage**: Both determined by Ranged level + ammo + weapon
- **Attack Styles**: Accurate (+3 Ranged), Rapid (+3 Ranged, faster), Longrange (+3 Ranged + Defence, longer range)

### Magic
- **Accuracy**: Magic level + equipment magic attack bonus
- **Damage**: Typically from spell itself, not Magic level (exceptions: tridents, powered staves)
- **Magic Defence**: Determined by 70% Magic level + 30% Defence level
- **Attack Styles**: Accurate (+3 Magic), Longrange (+3 Magic + Defence), Defensive (+3 Magic + Defence)

## Combat XP Rates

### Standard Combat
- **Melee**: 4 XP per damage in chosen style (Attack/Strength/Defence)
- **Hitpoints**: 1.33 XP per damage dealt
- **Ranged**: 4 XP per damage
- **Magic**: Base spell XP + damage XP (base XP granted even on splash)

### Special Styles
- **Shared melee** (e.g., Abyssal whip on shared): 1.33 XP each to Attack/Strength/Defence per damage
- **Longrange ranged**: 2 Ranged XP + 2 Defence XP per damage
- **Defensive magic**: 1 Magic XP + 1 Defence XP per damage + base casting XP

## Game Tick System

- **1 game tick = 600ms (0.6 seconds)**
- All actions are tick-based
- Combat attacks happen on specific tick intervals based on weapon speed
- Weapon speeds range from 2 ticks (1.2s) to 8 ticks (4.8s)

### Weapon Speed Examples
- **Speed 2** (1.2s): Darts, knives
- **Speed 3** (1.8s): Dagger, scimitar
- **Speed 4** (2.4s): Whip, longsword
- **Speed 5** (3.0s): Battleaxe, 2h sword
- **Speed 6** (3.6s): Godswords, elder maul
- **Speed 8** (4.8s): Ballista

## DPS vs Max Hit

Don't compare weapons by max hit alone - weapon speed matters!

**Example:**
- Weapon A: Max hit 30, speed 4 (2.4s) = ~12.5 DPS
- Weapon B: Max hit 40, speed 6 (3.6s) = ~11.1 DPS

Use a DPS calculator: https://tools.runescape.wiki/osrs-dps/

## Combat Equipment Stats

### Offensive Stats
- **Attack bonuses**: Stab, Slash, Crush, Ranged, Magic - increases hit chance
- **Strength bonuses**: Melee strength, Ranged strength, Magic damage - increases max hit

### Defensive Stats
- **Defence bonuses**: Stab, Slash, Crush, Ranged, Magic - reduces hit chance
- **Prayer bonus**: Slows prayer point drain rate

## Special Attacks

Many weapons have special attacks (costs 50-100% special attack energy):
- **Dragon dagger** (25%): 2 hits with increased accuracy and damage
- **Dragon claws** (50%): 4 hits with special damage distribution
- **Armadyl godsword** (50%): Increased damage, restores prayer equal to 50% of damage
- **Dragon warhammer** (50%): Reduces target's Defence by 30%
- **Bandos godsword** (50%): Drains target's Defence, restores your hitpoints

Special attack energy regenerates at 10% per minute (1% per 6 seconds).

## Prayer

### Protection Prayers (Level 43+)
- **Protect from Melee** - Blocks 100% melee damage from NPCs, 40% from players
- **Protect from Missiles** - Blocks 100% ranged damage from NPCs, 40% from players
- **Protect from Magic** - Blocks 100% magic damage from NPCs, 40% from players

### Offensive Prayers

**Basic Prayers:**
- Burst of Strength (4): +5% Strength
- Clarity of Thought (7): +5% Attack
- Sharp Eye (8): +5% Ranged attack
- Mystic Will (9): +5% Magic attack

**Intermediate Prayers:**
- Superhuman Strength (13): +10% Strength
- Improved Reflexes (16): +10% Attack
- Hawk Eye (26): +10% Ranged attack
- Mystic Lore (27): +10% Magic attack

**Advanced Prayers:**
- Ultimate Strength (31): +15% Strength
- Incredible Reflexes (34): +15% Attack
- Eagle Eye (44): +15% Ranged attack
- Mystic Might (45): +15% Magic attack

**Piety Line (Members):**
- **Chivalry** (60): +15% Attack, +18% Strength, +20% Defence (requires Knight Waves Training Grounds)
- **Piety** (70): +20% Attack, +23% Strength, +25% Defence (requires Knight Waves Training Grounds)
- **Rigour** (74): +20% Ranged attack, +23% Ranged strength, +25% Defence (requires prayer scroll)
- **Augury** (77): +25% Magic attack, +25% Magic defence, +25% Defence (requires prayer scroll)

## Combat Potions

### Melee
- **Attack potion**: +3 to +(10% + 3) Attack
- **Strength potion**: +3 to +(10% + 3) Strength
- **Defence potion**: +3 to +(10% + 3) Defence
- **Super attack**: +5 to +(15% + 5) Attack
- **Super strength**: +5 to +(15% + 5) Strength
- **Super defence**: +5 to +(15% + 5) Defence
- **Super combat**: Combines super attack, super strength, super defence

### Ranged
- **Ranging potion**: +4 to +(10% + 4) Ranged

### Magic
- **Magic potion**: +4 Magic

### Special
- **Overload** (NMZ only): +5 to +(13% + 5) to Attack, Strength, Defence, Ranged, Magic
- **Divine potions**: Super potion effect + 5 minutes of stat restoration

## Food Healing Values

### Common Food
- **Shrimp/Chicken**: 3 HP
- **Trout**: 7 HP
- **Salmon**: 9 HP
- **Tuna**: 10 HP
- **Lobster**: 12 HP
- **Swordfish**: 14 HP
- **Monkfish**: 16 HP
- **Shark**: 20 HP
- **Manta ray**: 22 HP
- **Dark crab**: 22 HP
- **Anglerfish**: 22 HP (can overheal up to 121 HP at 99 Hitpoints)

### Combo Food
Some food can be eaten in same tick as other food:
- **Karambwan**: 18 HP (combo food)
- **Saradomin brew**: Heals 15% + 2 HP, boosts Defence, drains Attack/Strength/Magic/Ranged

## Combat Achievements

Combat achievements are tiered PvM challenges:
- **Easy**: Basic boss mechanics
- **Medium**: Intermediate challenges
- **Hard**: Advanced boss strategies
- **Elite**: Expert-level challenges
- **Master**: Hardest PvM content
- **Grandmaster**: Ultimate challenges

Rewards include combat-enhancing items and cosmetics.

## Slayer Helmet

The **Slayer helmet (i)** (imbued) provides:
- 16.67% damage boost on Slayer task (melee)
- 15% accuracy boost on Slayer task (melee)
- 15% damage and accuracy boost (ranged/magic when imbued)

This makes Slayer one of the best combat training methods.

## Wilderness Combat Levels

In the Wilderness, you can attack players within a certain combat level range:
- **Wilderness level = combat level range**
- Example: Level 10 Wilderness = can attack players ±10 combat levels
- Deeper Wilderness = wider combat level range

## Death Mechanics

### Safe Deaths
- Minigames (Nightmare Zone, Pest Control, etc.)
- Practice mode bosses
- Some quest instances

### Unsafe Deaths (Normal)
- Keep 3 most valuable items (4 with Protect Item prayer)
- Remaining items go to gravestone at death location
- Pay fee to retrieve items from gravestone
- Untradeable items may degrade or be lost

### Unsafe Deaths (Wilderness/PvP)
- Attacker gets your items
- Skulled players lose all items (keep 1 with Protect Item)
- Some untradeables always lost in Wilderness

### Hardcore Ironman
- One life only
- Death converts to regular Ironman
- Can use Ring of life to preserve status (teleports at low HP)
