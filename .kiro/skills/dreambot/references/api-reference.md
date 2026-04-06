# DreamBot API Reference

## GameObjects

Find and interact with in-game objects (trees, rocks, doors, banks, etc.).

```java
// By name
GameObject tree = GameObjects.closest("Tree");
if (tree != null) tree.interact("Chop down");

// By ID
GameObject rock = GameObjects.closest(11360);
if (rock != null) rock.interact("Mine");

// Lambda filter
GameObject oak = GameObjects.closest(t -> "Oak tree".equalsIgnoreCase(t.getName()) && t.distance() < 10);
if (oak != null) oak.interact("Chop down");
```

**Pitfalls:** Objects can despawn between `.closest()` and `.interact()`. Always null-check. Use `distance()` filters to avoid clicking far-away objects.

## NPCs

Find and interact with NPCs (monsters, shopkeepers, fishing spots, etc.).

```java
// By name — check combat state
NPC cow = NPCs.closest("Cow");
if (cow != null && !cow.isInCombat()) cow.interact("Attack");

// Lambda with multiple conditions
NPC target = NPCs.closest(n -> "Goblin".equalsIgnoreCase(n.getName())
    && !n.isInCombat()
    && n.getHealthPercent() > 0);

// Fishing spots (they're NPCs)
NPC spot = NPCs.closest("Fishing spot");
if (spot != null) spot.interact("Net");
```

**Key methods:** `isInCombat()`, `getHealthPercent()`, `isInteracting(Players.getLocal())`, `distance()`, `getID()`, `getName()`

**Pitfalls:** Fishing spots move — re-query each loop. NPCs can die between query and click.

## GroundItems

Pick up items on the ground.

```java
// Single item
GroundItem bones = GroundItems.closest("Bones");
if (bones != null) bones.interact("Take");

// Multiple names — finds closest match from any
GroundItem loot = GroundItems.closest("Coins", "Bones", "Cowhide");
if (loot != null) loot.interact("Take");

// By ID
GroundItem item = GroundItems.closest(995);
if (item != null) item.interact("Take");
```

**Pitfalls:** Ground items despawn. Other players can pick them up. Always null-check.

## Inventory

Check and manipulate inventory contents.

```java
// Queries
Inventory.isFull()                    // true if 28 items
Inventory.contains("Coins")          // has at least one
Inventory.count("Coins")             // exact count
Inventory.get("Bronze axe")          // get Item object

// Dropping
Inventory.drop("Raw shrimps");       // drop one
Inventory.dropAll("Raw shrimps");    // drop all of this item
Inventory.dropAll("Raw shrimps", "Raw anchovies");  // drop multiple types
Inventory.dropAll();                 // drop everything

// Filter drop — drop everything except tools
Inventory.dropAll(i -> i != null && !i.getName().contains("axe"));
```

**Pitfalls:** `drop()` drops one item. `dropAll()` drops all matching. Filter carefully to keep tools.

## Bank

Open, deposit, and withdraw. `Bank.open()` auto-walks to nearest bank.

```java
// Open (walks automatically if not nearby)
if (Bank.open()) {
    Sleep.sleepUntil(Bank::isOpen, 5000);
}

// Deposit
Bank.deposit("Coins");               // deposit 1
Bank.deposit("Coins", 10);           // deposit 10
Bank.depositAll("Coins");            // deposit all of item
Bank.depositAllItems();              // deposit entire inventory
Bank.depositAllEquipment();          // deposit all worn items

// Withdraw
Bank.withdraw("Coins");              // withdraw 1
Bank.withdraw("Coins", 10);          // withdraw 10
Bank.withdrawAll("Coins");           // withdraw all

// Close
Bank.close();
```

**Pitfalls:** Always `Sleep.sleepUntil(Bank::isOpen, ...)` after `Bank.open()` before depositing/withdrawing. Bank may not open instantly.

## Walking

Web walking — automatically pathfinds across the map.

```java
import org.dreambot.api.methods.map.Tile;

Tile destination = new Tile(3182, 3436);
Walking.walk(destination);

// Check if at location
if (Players.getLocal().getTile().distance(destination) < 5) {
    // arrived
}
```

**Pitfalls:** `walk()` starts walking but doesn't block. Use `Sleep.sleepUntil()` to wait for arrival.

## Combat

Check player combat state.

```java
Players.getLocal().isInCombat()
Players.getLocal().getHealthPercent()
Players.getLocal().isMoving()
Players.getLocal().isAnimating()
```

## WorldHopper

Hop worlds programmatically.

```java
import org.dreambot.api.methods.world.World;
import org.dreambot.api.methods.world.Worlds;
import org.dreambot.api.methods.worldhopper.WorldHopper;

// Specific world
WorldHopper.hopWorld(301);

// Random F2P, non-PVP, no level requirement
World world = Worlds.getRandomWorld(w -> w.isF2P() && !w.isPVP() && w.getMinimumLevel() == 0);
WorldHopper.hopWorld(world);
```

## GrandExchange

Buy and sell items. Must be standing near a GE booth.

```java
// Open
GrandExchange.open();

// Buy
if (GrandExchange.buyItem("Cowhide", 100, 200)) {
    if (Sleep.sleepUntil(GrandExchange::isReadyToCollect, 15000)) {
        GrandExchange.collect();
    }
}

// Sell
if (GrandExchange.sellItem("Cowhide", 100, 5)) {
    if (Sleep.sleepUntil(GrandExchange::isReadyToCollect, 15000)) {
        GrandExchange.collect();
    }
}
```

## Widgets

Interact with UI elements (crafting menus, skill dialogs, etc.). Use DreamBot's Game Explorer (Ctrl+G) to find parent/child IDs.

```java
import org.dreambot.api.wrappers.widgets.WidgetChild;

WidgetChild widget = Widgets.getWidgetChild(270, 15);  // parentID, childID
if (widget != null && widget.interact()) {
    Sleep.sleepUntil(() -> !Inventory.contains("Leather"), 30000);
}
```

## PlayerSettings

Read game state via Varps and Varbits. Read-only, set by server.

```java
// Varps (VarPlayers) — e.g., attack style
int attackStyle = PlayerSettings.getConfig(43);  // 0=Stab, 1=Lunge, 2=Slash, 3=Block

// Varbits — e.g., auto-cast spell
int autoCast = PlayerSettings.getBitValue(276);  // 0=None, 1=Wind Strike, etc.

// Quest state
int questState = PlayerSettings.getBitValue(8063);  // X Marks the Spot: 0-7=in progress, 8=complete
```

**Finding IDs:** Use Game Explorer (Ctrl+G → Player Settings tab). Change something in-game and watch the "Recent Updates" pane. Also check OSRS Wiki Varbit pages.

## Sleep & Timing

```java
// Fixed sleep
Sleep.sleep(1000);

// Sleep until condition or timeout
Sleep.sleepUntil(() -> Inventory.isFull(), 60000);
Sleep.sleepUntil(Bank::isOpen, 5000);

// Method reference style
Sleep.sleepUntil(Inventory::isFull, 60000);

// Random number
int delay = Calculations.random(500, 1500);
```

## Logging

```java
Logger.log("Starting script");       // SCRIPT level
Logger.info("Found target");         // INFO level
Logger.error("Failed to find NPC");  // ERROR level
Logger.debug("Debug info");          // DEBUG level (only if debug enabled)
```


## Equipment

Manage worn items. Uses `EquipmentSlot` enum (HEAD, CAPE, AMULET, WEAPON, BODY, SHIELD, LEGS, GLOVES, BOOTS, RING, AMMO).

```java
// Check what's equipped
Equipment.contains("Iron scimitar");
Equipment.getItemInSlot(EquipmentSlot.WEAPON);
Equipment.getNameForSlot(EquipmentSlot.WEAPON);
Equipment.isSlotEmpty(EquipmentSlot.SHIELD);

// Equip from inventory (returns true if already equipped OR successfully equipped)
Equipment.equip(EquipmentSlot.WEAPON, "Iron scimitar");
Equipment.equip(EquipmentSlot.WEAPON, 1323);

// Unequip
Equipment.unequip(EquipmentSlot.WEAPON);

// Open equipment tab
Equipment.open();
```

**Pitfalls:** `equip()` returns true if already equipped — use this to simplify checks. Item must be in inventory to equip.

## Combat

Player combat state, special attacks, combat styles.

```java
// Health & status
Combat.getHealthPercent();           // 0-100
Combat.isPoisoned();
Combat.isEnvenomed();

// Special attack
Combat.getSpecialPercentage();       // 0-100
Combat.toggleSpecialAttack(true);    // returns true if toggled or already active
Combat.isSpecialActive();

// Combat style
Combat.getCombatStyle();             // returns CombatStyle enum
Combat.setCombatStyle(CombatStyle.ATTACK);

// Auto-retaliate
Combat.isAutoRetaliateOn();
Combat.toggleAutoRetaliate(true);

// Location checks
Combat.isInWild();
Combat.getWildernessLevel();
Combat.isInMultiCombat();

// Potion checks
Combat.isAntiFireEnabled();
Combat.hasPoisonImmunity();
```

## Prayers

Toggle prayers, manage quick prayers.

```java
// Toggle individual prayer
Prayers.toggle(true, Prayer.PROTECT_FROM_MELEE);
Prayers.isActive(Prayer.PROTECT_FROM_MELEE);

// Quick prayers
Prayers.toggleQuickPrayer(true);
Prayers.isQuickPrayerActive();
Prayers.setupQuickPrayers(Prayer.PROTECT_FROM_MELEE, Prayer.PIETY);

// Prayer flicking
Prayers.flick(Prayer.PROTECT_FROM_MELEE, 600);

// Get active prayers
Prayer[] active = Prayers.getActive();
```

## Magic

Cast spells, manage autocast. Spell enums: `Normal`, `Ancient`, `Lunar`, `Arceuus`.

```java
// Cast a spell
Magic.castSpell(Normal.HIGH_LEVEL_ALCHEMY);

// Cast on entity or item
Magic.castSpellOn(Normal.FIRE_STRIKE, npc);
Magic.castSpellOn(Normal.HIGH_LEVEL_ALCHEMY, item);

// Check if can cast (checks level + runes, accounts for staves)
Magic.canCast(Normal.FIRE_STRIKE);

// Autocast
Magic.setAutocastSpell(Normal.FIRE_STRIKE);
Magic.getAutocastSpell();
Magic.isAutocasting();

// Spell selection state
Magic.isSpellSelected();
Magic.deselect();

// Spellbook
Magic.getSpellbook();  // returns Spellbook enum
```

## Dialogues

Handle NPC conversations, option selection, input prompts.

```java
// Check dialogue state
Dialogues.inDialogue();
Dialogues.canContinue();
Dialogues.areOptionsAvailable();
Dialogues.canEnterInput();

// Continue through dialogue
Dialogues.continueDialogue();    // clicks or presses space (profiled)
Dialogues.clickContinue();       // always clicks
Dialogues.spaceToContinue();     // always presses space

// Choose options
Dialogues.chooseOption("Yes");                    // exact match, case-insensitive
Dialogues.chooseOption(1);                        // by index (starts at 1!)
Dialogues.chooseFirstOption("Yes", "Sure", "OK"); // first available match

// Get dialogue info
String[] options = Dialogues.getOptions();
String npcText = Dialogues.getNPCDialogue();
```

**Pitfalls:** Option indices start at 1, not 0. `chooseOption()` auto-decides between clicking and typing based on mouse distance.

## Shop

Buy/sell items at NPC shops.

```java
// Open/close
Shop.isOpen();
Shop.close();

// Buy items
Shop.purchase("Iron ore", 10);       // buy 10
Shop.purchaseOne("Iron ore");
Shop.purchaseFive("Iron ore");
Shop.purchaseTen("Iron ore");
Shop.purchaseFifty("Iron ore");

// Sell items from inventory
Shop.sell("Iron ore", 10);
Shop.sellOne("Iron ore");
Shop.sellFive("Iron ore");

// Check stock
Shop.contains("Iron ore");
Shop.count("Iron ore");
Shop.get("Iron ore");                // returns Item
```

## Skills

Check skill levels and XP.

```java
Skills.getRealLevel(Skill.ATTACK);       // base level (no boosts)
Skills.getBoostedLevel(Skill.ATTACK);    // current level (with boosts)
Skills.getExperience(Skill.ATTACK);      // total XP
Skills.getExperienceForLevel(75);        // XP needed for level 75
```

## Players

Local player and other players.

```java
// Local player state
Players.getLocal().isMoving();
Players.getLocal().isAnimating();
Players.getLocal().isInCombat();
Players.getLocal().getHealthPercent();
Players.getLocal().getTile();

// Find other players
Player target = Players.closest("PlayerName");
Player nearby = Players.closest(p -> p.getCombatLevel() < 50);
```

## Camera

Control the game camera.

```java
Camera.rotateTo(int yaw, int pitch);
Camera.getYaw();
Camera.getPitch();
Camera.rotateToEntity(entity);
Camera.rotateToTile(tile);
```

## Keyboard

Type text and press keys.

```java
Keyboard.type("Hello");
Keyboard.type("Hello", true);    // true = press Enter after
Keyboard.pressEnter();
```


## DepositBox

For deposit-only boxes (no withdrawals). Similar to Bank but deposit-only.

```java
DepositBox.isOpen();
DepositBox.open();                    // interacts with nearest deposit box
DepositBox.openClosest();
DepositBox.close();

DepositBox.depositAllItems();
DepositBox.depositAllEquipment();
DepositBox.depositAllLoot();
DepositBox.deposit("Iron ore", 10);
DepositBox.depositAll("Iron ore");
DepositBox.depositAllExcept("Bronze axe", "Tinderbox");
```

## ItemProcessing

Handle "Make X" interfaces (crafting, cooking, smithing, fletching).

```java
// Check if make interface is open
ItemProcessing.isOpen();

// Make all of an item
ItemProcessing.makeAll("Leather body");
ItemProcessing.makeAll(1741);  // by ID

// Make specific quantity
ItemProcessing.make("Leather body", 10);

// Get/set quantity
ItemProcessing.getSelectedQuantity();
ItemProcessing.setSelectedQuantity(14);
```

**Note:** `ItemProcessing` is at `org.dreambot.api.methods.widget.helpers.ItemProcessing`, not in the `methods` root.

## Mouse

Direct mouse control. Rarely needed — most interactions go through entity `.interact()`.

```java
import org.dreambot.api.input.Mouse;

Mouse.click();                        // left click at current position
Mouse.click(true);                    // right click
Mouse.move(entity);                   // move to entity
Mouse.move(new Point(x, y));
Mouse.moveOutsideScreen();            // move mouse off screen
Mouse.isMouseInScreen();
Mouse.getPosition();                  // returns Point
Mouse.hop(new Point(x, y));           // instant move (no path)
```

**Note:** `Mouse` is at `org.dreambot.api.input.Mouse`, and `Keyboard` is at `org.dreambot.api.input.Keyboard`.

## Important Import Corrections

Some classes are NOT where you'd expect:
```java
import org.dreambot.api.input.Keyboard;                              // NOT org.dreambot.api.methods.input
import org.dreambot.api.input.Mouse;                                 // NOT org.dreambot.api.methods.input.mouse
import org.dreambot.api.methods.widget.helpers.ItemProcessing;       // NOT org.dreambot.api.methods.item
```


## Entity Wrappers (NPC, Player, GameObject, GroundItem, Item)

These are the objects returned by `.closest()`, `.all()`, etc. They share common methods from the `Character` and `Entity` base classes.

### Common Entity Methods (all interactables)
```java
entity.interact("Action");           // right-click action (e.g., "Attack", "Chop down", "Net")
entity.interact();                   // left-click default action
entity.getName();                    // entity name
entity.getID();                      // entity ID
entity.distance();                   // tile distance from local player
entity.distance(Tile);               // tile distance from specific tile
entity.getTile();                    // entity's current Tile
entity.isOnScreen();                 // visible in viewport
entity.exists();                     // still exists in game
entity.hasAction("Action");          // has this right-click option
```

### Character Methods (NPC, Player)
```java
character.isInCombat();
character.isMoving();
character.isAnimating();
character.getHealthPercent();        // 0-100
character.isInteracting(entity);     // interacting with specific entity
character.getInteractingCharacter(); // who they're interacting with
character.getAnimation();            // animation ID (-1 if idle)
character.isStandingStill();
```

### NPC-Specific
```java
npc.getID();                         // NPC ID (composition ID)
npc.getName();
npc.getActions();                    // String[] of right-click options
npc.isInCombat();
npc.getHealthPercent();
```

### GameObject-Specific
```java
gameObject.getID();
gameObject.getName();
gameObject.hasAction("Action");
gameObject.getOrientation();
```

### Item-Specific (inventory/bank/equipment items)
```java
item.getName();
item.getID();
item.getAmount();                    // stack size
item.isNoted();
item.isStackable();
item.getNotedId();
item.getActions();                   // String[] of right-click options
```

### GroundItem-Specific
```java
groundItem.getName();
groundItem.getID();
groundItem.getAmount();
groundItem.getTile();
groundItem.isOnScreen();
groundItem.interact("Take");
```

## Tile

Represents a world coordinate.

```java
// Constructors
Tile tile = new Tile(3182, 3436);          // x, y
Tile tile = new Tile(3182, 3436, 0);       // x, y, z (plane)

// Methods
tile.getX();
tile.getY();
tile.getZ();                               // plane (0 = ground)
tile.distance(otherTile);                  // distance to another tile
tile.distance();                           // distance from local player
tile.getRandomizedTile(radius);            // random tile within radius
tile.isOnScreen();
```

## Area

Defines a rectangular or polygonal region.

```java
// Rectangular area (SW corner, NE corner)
Area area = new Area(3238, 3241, 3245, 3253);

// With plane
Area area = new Area(3238, 3241, 3245, 3253, 0);

// From tiles
Area area = new Area(new Tile(3238, 3241), new Tile(3245, 3253));

// Polygon (varargs Tile)
Area area = new Area(new Tile(x1,y1), new Tile(x2,y2), new Tile(x3,y3));

// Methods
area.contains(entity);                     // is entity inside area
area.contains(tile);                       // is tile inside area
area.contains(Players.getLocal());
area.getRandomTile();                      // random tile within area
area.getCenter();                          // center tile
area.getTiles();                           // all tiles in area
area.setPlane(int);
```

## Tabs

Open game interface tabs.

```java
import org.dreambot.api.methods.tabs.Tab;
import org.dreambot.api.methods.tabs.Tabs;

Tabs.open(Tab.INVENTORY);
Tabs.open(Tab.EQUIPMENT);
Tabs.open(Tab.PRAYER);
Tabs.open(Tab.MAGIC);
Tabs.open(Tab.COMBAT);
Tabs.open(Tab.SKILLS);
Tabs.open(Tab.QUEST);
Tabs.open(Tab.FRIENDS);
Tabs.open(Tab.CLAN);
Tabs.open(Tab.SETTINGS);
Tabs.open(Tab.EMOTES);
Tabs.open(Tab.MUSIC);
Tabs.open(Tab.LOGOUT);

Tabs.isOpen(Tab.INVENTORY);               // check if tab is open
Tabs.getOpen();                            // get currently open tab
```

## SkillTracker

Track XP gains and rates during script runtime.

```java
SkillTracker.start(Skill.FISHING);         // start tracking
SkillTracker.getGainedExperience(Skill.FISHING);
SkillTracker.getGainedExperiencePerHour(Skill.FISHING);
SkillTracker.getGainedLevels(Skill.FISHING);
SkillTracker.getTimeToLevel(Skill.FISHING); // ms until next level at current rate
```

## Useful Enums

### Skill
```java
Skill.ATTACK, Skill.STRENGTH, Skill.DEFENCE, Skill.RANGED, Skill.PRAYER,
Skill.MAGIC, Skill.RUNECRAFTING, Skill.HITPOINTS, Skill.CRAFTING,
Skill.MINING, Skill.SMITHING, Skill.FISHING, Skill.COOKING,
Skill.FIREMAKING, Skill.WOODCUTTING, Skill.AGILITY, Skill.HERBLORE,
Skill.THIEVING, Skill.FLETCHING, Skill.SLAYER, Skill.FARMING,
Skill.CONSTRUCTION, Skill.HUNTER
```

### EquipmentSlot
```java
EquipmentSlot.HEAD, EquipmentSlot.CAPE, EquipmentSlot.AMULET,
EquipmentSlot.WEAPON, EquipmentSlot.BODY, EquipmentSlot.SHIELD,
EquipmentSlot.LEGS, EquipmentSlot.GLOVES, EquipmentSlot.BOOTS,
EquipmentSlot.RING, EquipmentSlot.AMMO
```

### Normal Spells (Standard Spellbook)
```java
Normal.WIND_STRIKE, Normal.WATER_STRIKE, Normal.EARTH_STRIKE, Normal.FIRE_STRIKE,
Normal.WIND_BOLT, Normal.WATER_BOLT, Normal.EARTH_BOLT, Normal.FIRE_BOLT,
Normal.WIND_BLAST, Normal.WATER_BLAST, Normal.EARTH_BLAST, Normal.FIRE_BLAST,
Normal.WIND_WAVE, Normal.WATER_WAVE, Normal.EARTH_WAVE, Normal.FIRE_WAVE,
Normal.WIND_SURGE, Normal.WATER_SURGE, Normal.EARTH_SURGE, Normal.FIRE_SURGE,
Normal.HIGH_LEVEL_ALCHEMY, Normal.LOW_LEVEL_ALCHEMY,
Normal.TELEKINETIC_GRAB, Normal.BONES_TO_BANANAS, Normal.BONES_TO_PEACHES,
Normal.SUPERHEAT_ITEM, Normal.ENCHANT_CROSSBOW_BOLT
// Teleports
Normal.VARROCK_TELEPORT, Normal.LUMBRIDGE_TELEPORT, Normal.FALADOR_TELEPORT,
Normal.CAMELOT_TELEPORT, Normal.ARDOUGNE_TELEPORT
```

### Prayer
```java
Prayer.THICK_SKIN, Prayer.BURST_OF_STRENGTH, Prayer.CLARITY_OF_THOUGHT,
Prayer.SHARP_EYE, Prayer.MYSTIC_WILL,
Prayer.ROCK_SKIN, Prayer.SUPERHUMAN_STRENGTH, Prayer.IMPROVED_REFLEXES,
Prayer.RAPID_RESTORE, Prayer.RAPID_HEAL, Prayer.PROTECT_ITEM,
Prayer.HAWK_EYE, Prayer.MYSTIC_LORE,
Prayer.STEEL_SKIN, Prayer.ULTIMATE_STRENGTH, Prayer.INCREDIBLE_REFLEXES,
Prayer.PROTECT_FROM_MAGIC, Prayer.PROTECT_FROM_MISSILES, Prayer.PROTECT_FROM_MELEE,
Prayer.EAGLE_EYE, Prayer.MYSTIC_MIGHT,
Prayer.RETRIBUTION, Prayer.REDEMPTION, Prayer.SMITE,
Prayer.CHIVALRY, Prayer.PIETY, Prayer.RIGOUR, Prayer.AUGURY,
Prayer.PRESERVE
```

### Category (for @ScriptManifest)
```java
Category.AGILITY, Category.COMBAT, Category.COOKING, Category.CRAFTING,
Category.FARMING, Category.FIREMAKING, Category.FISHING, Category.FLETCHING,
Category.HERBLORE, Category.HUNTER, Category.MAGIC, Category.MINING,
Category.MONEYMAKING, Category.PRAYER, Category.QUEST, Category.RANGED,
Category.RUNECRAFTING, Category.SLAYER, Category.SMITHING, Category.THIEVING,
Category.WOODCUTTING, Category.MISC
```
