# brutus-fighter — Requirements

## Goal
Melee Brutus cow boss in Lumbridge cow field. Dodge specials, eat food, loot drops, bank when out of food.

## Framework
TreeScript — hierarchical priority: dialogue > dodge > eat > bank > loot > attack/wait

## Tree Structure
```
Root
├── AntiBanNode
├── DialogueLeaf          — handle level-up / release dialogues
├── DodgeLeaf             — detect overhead *growls*/*snorts*, walk away (HIGHEST combat priority)
├── EatLeaf               — eat food when HP < 50%
├── BankBranch            — when no food in inventory
│   ├── DepositLeaf       — deposit all items
│   └── WithdrawLeaf      — withdraw 20 food (lobster > salmon > trout)
├── LootLeaf              — pick up drops after kill, bury bull bones
├── RingCowbellLeaf       — ring cowbell for fast respawn after kill
└── AttackLeaf            — attack Brutus / wait for respawn (fallback)
```

## Constants
- BRUTUS_IDS: 15626, 15627
- COW_FIELD: Area around 3258-3270, 3290-3305
- FIGHT_TILE: east of Brutus spawn (~3266, 3297) — prevents charge
- FOOD_NAMES: "Lobster", "Salmon", "Trout"
- FOOD_COUNT: 20
- EAT_HP_PERCENT: 50
- LOOT_NAMES: "Raw t-bone steak", "Mooleta", "Cow slippers", "Bottomless milk bucket (empty)", "Clue scroll (beginner)", "Clue scroll (easy)", "Iron full helm", "Iron platebody", "Iron platelegs", "Iron plateskirt", "Iron arrow", "Air rune", "Mind rune", "Chaos rune", "Cowhide", "Oak logs", "Logs", "Coins"
- BURY_NAME: "Bull bones"

## Dodge Mechanics
- Check `npc.getOverhead()` every tick for "*growls*" or "*snorts*"
- On detection: walk 3 tiles away from Brutus (perpendicular/diagonal)
- Standing east of spawn prevents charge entirely
- Slam repeats 3 times — stay alert

## Banking
- Deposit: depositAllItems()
- Withdraw: 20 food (try lobster, fallback salmon, fallback trout)
- If no food in bank: stop script
- Travel: cowbell amulet "Teleport" (equipped neck slot) to return

## Looting
- Pick up all LOOT_NAMES items
- Bury "Bull bones" on ground (action is "Bury", not "Take")
- Skip if inventory full

## No Prayer
User opted out — don't activate any prayers.
