---
name: dreambot
description: DreamBot scripting framework guide for writing OSRS automation scripts in Java. Use when generating scripts, debugging script issues, working with DreamBot APIs (GameObjects, NPCs, Inventory, Bank, Walking, GrandExchange, Widgets, PlayerSettings, Combat), discussing TaskScript or AbstractScript patterns, anti-ban strategies, or anything related to the DreamBot scripting framework — even if the user doesn't mention DreamBot by name.
---

# DreamBot Script Development

DreamBot is a Java framework for OSRS automation. Scripts extend `AbstractScript` or `TaskScript`, are annotated with `@ScriptManifest`, and compile to `.jar` files placed in `~/DreamBot/Scripts/`. One jar can contain multiple scripts — DreamBot discovers all `@ScriptManifest` classes.

## Framework Selection

**TreeScript** (default) — DreamBot's built-in decision tree. Your script IS a decision tree — make it explicit. `Root` → `Branch`es → `Leaf`s. Each node has `isValid()` (condition) and `onLoop()` (action). First valid child runs. Built-in decision path tracking via `getCurrentBranchName()`/`getCurrentLeafName()`.

**TaskScript** — flat priority-based node list. Good for scripts where actions don't have a natural hierarchy (e.g., combat with independent eat/loot/attack nodes that all check independently).

**AbstractScript** — raw `onLoop()`. For trivial scripts with no branching (≤2 actions).

### When to Use What
- **TreeScript**: gathering + banking, progression scripts, anything with "if X then (A or B), else (C or D)" logic
- **TaskScript**: combat scripts, scripts where multiple independent concerns run in parallel (eat if low HP, loot if items nearby, attack if idle)
- **AbstractScript**: single-action scripts (power mine, alch)

## Architecture

```
dreambot/src/main/java/scripts/
├── shared/                       # Shared utilities
│   ├── antiban/
│   │   ├── AntiBanNode.java      # Anti-ban Leaf (works in TreeScript, also callable standalone)
│   │   └── AntiBanUtil.java      # Inline anti-ban utilities
│   └── ScriptContext.java        # Shared state base class
└── {scriptname}/                 # Per-script package
    ├── {Name}Script.java         # Entry point
    └── nodes/                    # Branch/Leaf classes (TreeScript) or TaskNode classes (TaskScript)
```

## TreeScript Skeleton (Default)

```java
package scripts.myscript;

import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import scripts.shared.antiban.AntiBanNode;

@ScriptManifest(name = "my-script", author = "osrs-bot", version = 0.1,
                description = "Description here", category = Category.MISC)
public class MyScript extends TreeScript {

    @Override
    public void onStart() {
        addBranches(
            new AntiBanNode(),
            new GatherBranch(),
            new BankBranch()
        );
    }

    @Override
    public void onPaint(java.awt.Graphics2D g) {
        g.drawString("Branch: " + getCurrentBranchName(), 25, 170);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 185);
    }
}
```

Branches contain leaves. First valid child at each level runs. The tree is the script — no state variables needed.

## TaskScript Skeleton (Alternative)

For flat independent concerns (combat with eat/loot/attack):

```java
@ScriptManifest(name = "my-combat", author = "osrs-bot", version = 0.1,
                description = "", category = Category.COMBAT)
public class MyCombatScript extends TaskScript {
    @Override
    public void onStart() {
        addNodes(new EatNode(), new LootNode(), new AttackNode());
    }
}
```

## Simple Script Skeleton (AbstractScript)

For truly trivial scripts only — single action, no branching:

```java
@ScriptManifest(name = "simple-miner", author = "osrs-bot", version = 0.1,
                description = "", category = Category.MINING)
public class SimpleMinerScript extends AbstractScript {
    @Override
    public int onLoop() {
        if (Inventory.isFull()) { Inventory.dropAll(); return 600; }
        GameObject rock = GameObjects.closest("Rocks");
        if (rock != null && !Players.getLocal().isAnimating()) {
            rock.interact("Mine");
        }
        return 600;
    }
}
```

## Return Value Convention

`onLoop()` and `execute()` return sleep time in ms. Use condition-based returns with randomness:

```java
// Actively clicking something
return Calculations.random(100, 300);

// Waiting for an action to complete (fishing, cooking, etc.)
return Calculations.random(500, 1000);

// Idle / nothing to do right now
return Calculations.random(2000, 5000);
```

Always use `AntiBanUtil.humanDelay(min, max)` instead of raw `Calculations.random()` for action delays — it adds occasional outlier delays for human-like timing.

## Core Patterns

### Use the Tree, Not State Variables
Your script is a decision tree. Build it with DreamBot's `TreeScript` → `Branch` → `Leaf`. Don't use state enums, `getState()` functions, or `switch` statements — they disconnect decisions from actions and are the root of bugs. See `references/scripting-patterns.md` for the full tree pattern.

### Always Return 600 (One Game Tick)
OSRS runs on 600ms ticks. Returning less means spam-clicking (worst case: 599 clicks before the next tick). Return 600 as baseline.

### One Action Per Loop
Execute ONE action then return. Let the next tick re-evaluate game state.

### Bank.open() Walks For You
Never manually walk to a bank. `Bank.open()` handles walking automatically. Guard with `Walking.shouldWalk()`:
```java
if (Walking.shouldWalk()) Bank.open();
```

### Walking.shouldWalk() Guard
Don't call `Walking.walk()` every tick:
```java
if (Walking.shouldWalk()) Walking.walk(area);
```

### Check Return Values Before Sleeping
```java
if (Bank.withdraw("Iron ore")) {
    Sleep.sleepUntil(() -> Inventory.contains("Iron ore"), 3000);
}
```

### Sleep Until with Reset Conditions
Use lambdas (not method references) for reset conditions — gets fresh player reference each poll:
```java
Sleep.sleepUntil(Bank::isOpen, () -> Players.getLocal().isMoving(), 3000, 100);
```

### Null-Check Everything
```java
NPC target = NPCs.closest("Cow");
if (target != null && !target.isInCombat()) {
    target.interact("Attack");
}
```

### No Magic Numbers — Use Constants and Enums
```java
private static final String WEAPON_NAME = "Iron scimitar";
private static final Area TREE_AREA = new Area(3138, 3220, 3150, 3235);
```

### Anti-Ban Integration
Add `AntiBanNode` as first leaf in your tree root (TreeScript), or first node in `addNodes()` (TaskScript). Use `AntiBanUtil` in leaf/node code:
```java
if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
```

### Paint Debug Info
TreeScript: use built-in `getCurrentBranchName()`/`getCurrentLeafName()`:
```java
@Override
public void onPaint(Graphics2D g) {
    g.drawString("Branch: " + getCurrentBranchName(), 25, 170);
    g.drawString("Leaf: " + getCurrentLeafName(), 25, 185);
}
```

## When to Load References

| Task | Reference |
|------|-----------|
| Writing any script code | `references/api-reference.md` — **always read first** (index + key class signatures) |
| Need full API for a specific domain | `references/api/{domain}.md` — see domain list below |
| Designing tree structure, reusable nodes | `references/scripting-patterns.md` |
| Adding anti-ban behavior | `references/anti-ban.md` |
| Build/deploy questions | `references/build-and-deploy.md` |

### API Domain Files (load on demand)

When you need the full method list for a specific API, load the relevant file from `references/api/`:

| Domain | File | Key Classes |
|--------|------|-------------|
| Interactables | `api/interactive.md` | GameObjects, NPCs, Players, GroundItems |
| Containers | `api/containers.md` | Bank, Inventory, Equipment, Shop, DepositBox |
| Walking/Map | `api/walking.md`, `api/map.md` | Walking, Tile, Area |
| Combat | `api/combat.md` | Combat, CombatStyle |
| Magic | `api/magic.md` | Magic, Normal, Ancient, Lunar, Arceuus |
| Prayer | `api/prayer.md` | Prayers, Prayer |
| Dialogues | `api/dialogues.md` | Dialogues |
| Skills | `api/skills.md` | Skills, Skill, SkillTracker |
| Grand Exchange | `api/grandexchange.md` | GrandExchange, GrandExchangeItem |
| Widgets | `api/widgets.md` | Widgets, ItemProcessing, Smithing |
| World/Hopping | `api/world.md` | Worlds, WorldHopper |
| Entity wrappers | `api/wrappers-entities.md` | Character, Entity, NPC, Player, GameObject |
| Item wrappers | `api/wrappers-items.md` | Item, GroundItem |
| Widget wrappers | `api/wrappers-widgets.md` | WidgetChild, Menu, MenuRow |
| Script framework | `api/script-frameworks.md` | TreeScript, Branch, Leaf, TaskScript |
| Settings/Vars | `api/settings.md` | PlayerSettings, VarBit, VarPlayer |
| Utilities | `api/utilities.md` | Sleep, Logger, Timer |

Load `api-reference.md` first for the index. Only load specific domain files when you need exact method signatures beyond the key classes.

## Critical Rules

1. Every script class needs `@ScriptManifest` annotation
2. Prefer TreeScript (decision tree) — use TaskScript for flat independent concerns, AbstractScript for trivial scripts
3. No state variables — no state enums, no `getState()`, no `switch` on state
4. Always add `AntiBanNode` as first leaf/node
5. Always return 600 from `onLoop()` / leaf nodes (one game tick) — never return 1
6. One action per loop — don't chain actions
7. `Bank.open()` walks for you — never manually walk to banks
8. `Walking.shouldWalk()` before every `Walking.walk()` or `Bank.open()`
9. Null-check all `.closest()` results
10. Check return values before sleeping
11. Use lambdas (not method references) in `Sleep.sleepUntil` reset conditions
12. Paint debug info in `onPaint()` — branch/leaf names for TreeScript
13. Log from every leaf/node
14. Package per script: `scripts.{name}`, shared code in `scripts.shared`

## CLI Commands

| Command | Purpose |
|---|---|
| `osrs-bot init <id>` | Initialize new script (TaskScript default, `--simple` for AbstractScript) |
| `osrs-bot build` | Compile all scripts |
| `osrs-bot deploy` | Bump version, compile, copy to Dropbox, push |
| `osrs-bot deploy --quick` | Build + Dropbox only, skip full git push (fast iteration) |
| `osrs-bot deploy --major-script <id>` | Bump major version for specific script(s) |
| `osrs-bot run` | Windows: copy jar to DreamBot. Linux: git pull |
| `osrs-bot run --watch` | Windows: auto-copy new jars as they arrive |
| `osrs-bot live <id> "msg"` | Quick feedback during testing (text, screenshots, logs) |
| `osrs-bot push` | Lightweight git sync (no build) |
| `osrs-bot inbox` | Show unresolved bugs, notes, and live feed |
| `osrs-bot lint` | Check for missing annotations and addNodes |
| `osrs-bot status` | Show all scripts and latest jar |
| `osrs-bot show <id>` | Show script details |
