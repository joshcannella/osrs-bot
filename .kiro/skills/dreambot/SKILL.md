---
name: dreambot
description: DreamBot scripting framework guide for writing OSRS automation scripts in Java. Use when generating scripts, debugging script issues, working with DreamBot APIs (GameObjects, NPCs, Inventory, Bank, Walking, GrandExchange, Widgets, PlayerSettings, Combat), discussing TaskScript or AbstractScript patterns, anti-ban strategies, or anything related to the DreamBot scripting framework — even if the user doesn't mention DreamBot by name.
---

# DreamBot Script Development

DreamBot is a Java framework for OSRS automation. Scripts extend `AbstractScript` or `TaskScript`, are annotated with `@ScriptManifest`, and compile to `.jar` files placed in `~/DreamBot/Scripts/`. One jar can contain multiple scripts — DreamBot discovers all `@ScriptManifest` classes.

## Framework Selection

**Use TaskScript** (default) for any script with 3+ states, banking, walking, or multiple distinct actions. Nodes are separate classes, each with `accept()` (condition) and `execute()` (action).

**Use AbstractScript** only for trivial scripts with ≤2 states and no banking (e.g., click ore → wait → repeat).

## Architecture

```
dreambot/src/main/java/scripts/
├── shared/                       # Shared utilities
│   ├── antiban/
│   │   ├── AntiBanNode.java      # High-priority ambient anti-ban
│   │   └── AntiBanUtil.java      # Inline anti-ban utilities
│   └── ScriptContext.java        # Shared state for TaskScript nodes
└── {scriptname}/                 # Per-script package
    ├── {Name}Script.java         # Entry point
    └── nodes/                    # TaskNode classes (TaskScript only)
```

## TaskScript Skeleton

```java
package scripts.myscript;

import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.impl.TaskScript;
import org.dreambot.api.utilities.Logger;
import scripts.shared.antiban.AntiBanNode;

@ScriptManifest(name = "my-script", author = "osrs-bot", version = 0.1,
                description = "Description here", category = Category.MISC)
public class MyScript extends TaskScript {

    @Override
    public void onStart() {
        Logger.log("Starting MyScript");
        MyContext ctx = new MyContext(this);
        addNodes(new AntiBanNode(), new GatherNode(ctx), new BankNode(ctx));
    }

    @Override
    public void onExit() {
        Logger.log("Stopping MyScript");
    }
}
```

## AbstractScript Skeleton

```java
package scripts.simple;

import org.dreambot.api.script.AbstractScript;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.utilities.Logger;

@ScriptManifest(name = "simple-miner", author = "osrs-bot", version = 0.1,
                description = "", category = Category.MINING)
public class SimpleMinerScript extends AbstractScript {

    @Override
    public int onLoop() {
        // Simple: click ore, wait, repeat
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

### One Action Per Loop
Execute only one action per `onLoop()` or `execute()` call, then return. Don't chain multiple actions — any action can fail, and chaining makes scripts unreliable. Let the next loop iteration re-evaluate game state and decide the next action.

```java
// BAD — chaining actions
Bank.withdraw("Iron scimitar");
Equipment.equip(EquipmentSlot.WEAPON, "Iron scimitar");

// GOOD — one action, return, re-evaluate next loop
if (Inventory.contains(WEAPON_NAME)) {
    Equipment.equip(EquipmentSlot.WEAPON, WEAPON_NAME);
} else if (Bank.isOpen()) {
    Bank.withdraw(WEAPON_NAME);
}
```

### Validate Game State, Don't Track State Manually
Determine what to do by checking the actual game state each tick — not by setting a "next state" variable after each action. The script should work correctly even if the user pauses, does something manually, and resumes.

```java
// BAD — manually tracking state
state = "deposit";
// ...later...
if (state.equals("deposit")) { ... }

// GOOD — check actual game state
if (Inventory.isFull()) {
    if (Bank.isOpen()) { Bank.depositAllItems(); }
    else { Bank.open(); }
} else if (!playerInArea) {
    Walking.walk(targetArea.getRandomTile());
} else {
    // gather resources
}
```

### Check Return Values Before Sleeping
Most API methods return `boolean` — `true` if the action succeeded. Don't sleep after a failed action. Only sleep when the action actually fired.

```java
// BAD — sleeps even if withdraw failed
Bank.withdraw("Iron ore");
Sleep.sleepUntil(() -> Inventory.contains("Iron ore"), 3000);

// GOOD — only sleep on success
if (Bank.withdraw("Iron ore")) {
    Sleep.sleepUntil(() -> Inventory.contains("Iron ore"), 3000);
}
```

### Use Boolean Returns to Simplify State Checks
Many API methods already check the current state and return `true` immediately if the desired state is active. Use this to simplify code:

```java
// VERBOSE
if (Bank.getWithdrawMode() == BankMode.NOTE) {
    Bank.withdrawAll("Iron scimitar");
} else {
    Bank.setWithdrawMode(BankMode.NOTE);
}

// SIMPLIFIED — setWithdrawMode returns true if already set OR successfully changed
if (Bank.setWithdrawMode(BankMode.NOTE)) {
    Bank.withdrawAll("Iron scimitar");
}
```

### Sleep Until with Reset Conditions
Use `Sleep.sleepUntil` with a reset condition for actions that involve walking or variable-length waits. The reset condition extends the timeout while the player is still making progress (moving, animating):

```java
// BAD — fixed timeout may be too short if player has to walk far
NPC banker = NPCs.closest("Banker");
if (banker != null && banker.interact("Bank")) {
    Sleep.sleepUntil(Bank::isOpen, 5000);
}

// GOOD — resets timeout while player is still moving
NPC banker = NPCs.closest("Banker");
if (banker != null && banker.interact("Bank")) {
    Sleep.sleepUntil(Bank::isOpen, () -> Players.getLocal().isMoving(), 3000, 100);
}
```

For processing actions (crafting, cooking), use animation as the reset condition:
```java
if (ItemProcessing.makeAll("Leather body")) {
    Sleep.sleepUntil(() -> !Inventory.contains("Leather"),
                     () -> Players.getLocal().isAnimating(), 3000, 100);
}
```

**Important:** Always use `() -> Players.getLocal().isMoving()` (lambda), not `Players.getLocal()::isMoving` (method reference). The lambda gets a fresh player reference each poll. The method reference captures a stale reference that won't update if the client disconnects.

### Null-Check Everything
Every `.closest()` call can return null. Always check:
```java
NPC target = NPCs.closest("Cow");
if (target != null && !target.isInCombat()) {
    target.interact("Attack");
}
```

### No Magic Numbers or Repeated Literals
Extract item names, IDs, and coordinates into named constants. Makes code readable and easy to change:

```java
// BAD
if (Inventory.contains(1323)) { ... }

// GOOD
private static final String WEAPON_NAME = "Iron scimitar";
private static final int WEAPON_ID = 1323;
private static final Area FISHING_AREA = new Area(3238, 3253, 3245, 3241);
```

### Use Enums for Data Sets
When a script supports multiple options (ore types, food types, locations), use enums instead of if/else chains:

```java
public enum OreType {
    IRON("Iron ore", 440, "Iron bar"),
    MITHRIL("Mithril ore", 447, "Mithril bar");

    private final String oreName;
    private final int rockId;
    private final String barName;

    OreType(String oreName, int rockId, String barName) {
        this.oreName = oreName; this.rockId = rockId; this.barName = barName;
    }
    public String getOreName() { return oreName; }
    public int getRockId() { return rockId; }
    public String getBarName() { return barName; }
}
```

### ScriptContext for Shared State
TaskScript nodes share state via a context object passed through constructors:
```java
public class MyContext extends ScriptContext {
    public boolean needsFood = false;
    public MyContext(AbstractScript s) { super(s); }
}
```

### Anti-Ban Integration
Always register `AntiBanNode` in `onStart()`. Use `AntiBanUtil` in nodes:
```java
if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
target.interact("Attack");
return AntiBanUtil.conditionSleep("clicking");
```

## When to Load References

| Task | Reference |
|------|-----------|
| Writing any script code | `references/api-reference.md` — **always read first** |
| Designing state machines, node structure | `references/scripting-patterns.md` |
| Adding anti-ban behavior | `references/anti-ban.md` |
| Build/deploy questions | `references/build-and-deploy.md` |

## Critical Rules

1. Every script class needs `@ScriptManifest` annotation
2. Every TaskScript must call `addNodes()` in `onStart()`
3. Always register `AntiBanNode` in TaskScript
4. Null-check all `.closest()` results
5. Use `Sleep.sleepUntil()` to verify actions completed
6. Return positive int from `onLoop()`/`execute()` (negative stops script)
7. Use `AntiBanUtil.humanDelay()` instead of raw `Calculations.random()` for delays
8. Use `Logger.log()` for state transitions and important events
9. Use lambda filters for precise entity selection
10. Package per script: `scripts.{name}`, shared code in `scripts.shared`

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
