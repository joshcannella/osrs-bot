# F2P Melee Training Progression Reference

This document captures the full training progression from the OSRS Wiki "Free-to-play melee training" guide. Use this as a reference when implementing additional tiers.

## Monster Tiers (Best XP Path)

### Tier 1: Levels 1–20
| Monster | Combat | HP | Location | Notes |
|---------|--------|----|----------|-------|
| Chicken | 1 | 3 | NE Lumbridge (Farmer Fred's coop, east of River Lum) | No food needed, drops feathers (stackable, 5-15 per kill), drops bones. Stop when hitting 4s consistently. |
| Monk | 5 | 15 | Edgeville Monastery | Free healing from monks (right-click "Heal"), no food needed. |
| Seagull | 2-3 | 6-10 | Port Sarim, Corsair Cove | Can't hit you (0 max hit). |
| Giant rat | 3-6 | 5-10 | Lumbridge Swamp, Edgeville Dungeon, Varrock Sewers | Drops raw rat meat. |

**Recommended**: Chickens (simplest, feather profit) or Monks (free healing, higher HP for more XP/kill).

### Tier 2: Levels 20–40
| Monster | Combat | HP | Location | Notes |
|---------|--------|----|----------|-------|
| Barbarian | 9-17 | 18-24 | Barbarian Village | Near GE/bank, gem drop table access. |
| Big frog | 10 | 18 | Lumbridge Swamp | Low defence, 72 XP per kill. |
| Giant frog | 13 | 23 | Lumbridge Swamp | 92 XP per kill, always drops big bones (60 Prayer XP each). |

**Recommended**: Barbarians (bank proximity, consistent XP).

### Tier 3: Levels 40–60
| Monster | Combat | HP | Location | Notes |
|---------|--------|----|----------|-------|
| Flesh Crawler | 28-41 | 25 | Stronghold of Security, Level 2 (Catacomb of Famine) | Always aggressive to ALL combat levels. Max hit 1. Great AFK. Drops herbs, fire runes, iron ore, nature runes. |
| Zombie (SoS) | 30-53 | 30-50 | Stronghold of Security, Level 2 | Aggressive up to 2× combat level + 1. Higher HP = more XP/kill. |

**Recommended**: Flesh Crawlers (always aggressive regardless of level, max hit 1 = minimal food).

### Tier 4: Levels 60–99
| Monster | Combat | HP | Location | Notes |
|---------|--------|----|----------|-------|
| Giant spider | 50 | 50 | Stronghold of Security, Level 3 (Pit of Pestilence) | Always aggressive to ALL combat levels. Best AFK training to 99. Max hit 7 — bring food. |

**Recommended**: Giant spiders (only real option for 60-99 F2P AFK).

### Alternative: Brutus (Levels 20–99)
| Monster | Combat | HP | Location | Notes |
|---------|--------|----|----------|-------|
| Brutus | 30 | 58 | Lumbridge cow field | 2× combat XP multiplier. Requires "The Ides of Milk" quest. |

## Equipment Progression

### Weapons (Scimitars — Best F2P DPS)
| Attack Level | Weapon | Notes |
|-------------|--------|-------|
| 1 | Bronze scimitar | Starting weapon |
| 5 | Steel scimitar | Skip iron — steel is cheap |
| 10 | Black scimitar | Slightly better than steel |
| 20 | Mithril scimitar | Significant upgrade |
| 30 | Adamant scimitar | |
| 40 | Rune scimitar | Best F2P weapon |

### Armour
| Defence Level | Helm | Body | Legs | Shield |
|--------------|------|------|------|--------|
| 1 | Bronze full helm | Bronze chainbody | Bronze plateskirt | Bronze kiteshield |
| 5 | Steel full helm | Steel chainbody | Steel plateskirt | Steel kiteshield |
| 10 | Black full helm | Black chainbody | Black plateskirt | Black kiteshield |
| 20 | Mithril full helm | Mithril chainbody | Mithril plateskirt | Mithril kiteshield |
| 30 | Adamant full helm | Adamant chainbody | Adamant plateskirt | Adamant kiteshield |
| 40 | Rune full helm | Rune chainbody | Rune plateskirt | Rune kiteshield |

### Body Armour Note
- **Platebody** = better stab/slash defence (use against most monsters)
- **Chainbody** = better crush defence (use against crush-attacking monsters)
- Most training monsters use melee, so platebody is generally better. Chainbody listed above as safe default since it's easier to obtain in F2P (no Dragon Slayer needed for rune).

### Accessories
| Slot | Item | Notes |
|------|------|-------|
| Neck | Amulet of power | +6 all attack, +6 str, +6 all def. Best general F2P amulet. |
| Neck | Amulet of strength | +10 str. Use if it gives a max hit over amulet of power. |
| Feet | Fancy boots / Fighting boots | From Stronghold of Security. Same stats, cosmetic difference. |
| Cape | None (F2P) | No meaningful F2P cape for melee. |

## Max Hit Breakpoints (Amulet Choice)
Use the amulet of strength (+10 str) over amulet of power (+6 str) when the +4 str bonus pushes you to a new max hit. Check max hit calculators — the breakpoints depend on current Strength level, weapon, and other bonuses.

## XP Rates (Approximate)
| Tier | Monster | XP/kill (HP × 4) | Est. XP/hr |
|------|---------|-------------------|------------|
| 1 | Chicken | 12 | 3,000-5,000 |
| 2 | Barbarian | 72-96 | 15,000-25,000 |
| 3 | Flesh Crawler | 100 | 25,000-35,000 |
| 4 | Giant Spider | 200 | 35,000-50,000 |

## Stronghold of Security Navigation
- **Entrance**: Hole in center of Barbarian Village
- **Level 1**: Vault of War — pass through to reach Level 2
- **Level 2**: Catacomb of Famine — Flesh Crawlers are here
- **Level 3**: Pit of Pestilence — Giant Spiders are here
- **Level 4**: Sepulchre of Death — not needed for training
- Each level has security doors that ask questions (first time only)
- Ladders connect levels — use center-click to climb

## Implementation Status
- [x] Tier 1: Chickens — requirements written
- [ ] Tier 2: Barbarians — not yet implemented
- [ ] Tier 3: Flesh Crawlers — not yet implemented
- [ ] Tier 4: Giant Spiders — not yet implemented
- [ ] Equipment upgrade system — not yet implemented
- [ ] GE purchasing — not yet implemented
