# DreamBot Scripting Patterns

## The Tree Pattern (Primary Architecture)

Your script IS a decision tree. Don't fight it with state variables — make the tree explicit using DreamBot's built-in `TreeScript` framework.

### Why Not State Variables?
State variables disconnect decision logic from execution logic. A `getState()` function that returns an enum, followed by a `switch` on that enum, is just an obfuscated if/else chain. It's harder to read, harder to debug, and the source of most bugs. The decision and the action should live together.

### TreeScript Framework

DreamBot provides `TreeScript` → `Root` → `Branch` → `Leaf`:
- `Leaf`: has `isValid()` + `onLoop()`. The atomic unit.
- `Branch extends Leaf`: has children (leaves or more branches). Its `onLoop()` finds the first valid child and runs it.
- `Root`: top-level branch, created automatically by `TreeScript`.
- `TreeScript extends AbstractScript`: handles the loop, tracks current branch/leaf names.

```java
@ScriptManifest(name = "woodcutter", author = "osrs-bot", version = 0.1,
                description = "Chops and banks", category = Category.WOODCUTTING)
public class WoodcutterScript extends TreeScript {
    @Override
    public void onStart() {
        addBranches(
            new AntiBanNode(),
            new FullInventoryBranch(),
            new ChopLeaf()
        );
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.drawString("Branch: " + getCurrentBranchName(), 25, 170);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 185);
    }
}
```

### Writing Leaf Nodes

Leaves are the actions. Override `isValid()` and `onLoop()`:

```java
public class ChopLeaf extends Leaf {
    private static final Area TREE_AREA = new Area(3138, 3220, 3150, 3235);

    @Override
    public boolean isValid() {
        return !Inventory.isFull();
    }

    @Override
    public int onLoop() {
        if (!TREE_AREA.contains(Players.getLocal())) {
            if (Walking.shouldWalk()) Walking.walk(TREE_AREA);
            return 600;
        }
        GameObject tree = GameObjects.closest("Tree");
        if (tree != null && !Players.getLocal().isAnimating()) {
            if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
            tree.interact("Chop down");
        }
        return 600;
    }
}
```

### Writing Branch Nodes

Branches group related leaves. Override `isValid()` and add children:

```java
public class FullInventoryBranch extends Branch {
    public FullInventoryBranch() {
        addLeaves(new BankLeaf(), new DropLeaf());
    }

    @Override
    public boolean isValid() {
        return Inventory.isFull();
    }
}
```

The branch's `onLoop()` is handled automatically — it finds the first valid child leaf and runs it.

### Reusable Parameterized Leaves

Make leaves generic so one class handles many cases:

```java
public class GenericGatherLeaf extends Leaf {
    private final Filter<GameObject> objectFilter;
    private final Area area;
    private final Filter<Item> dropFilter;
    private final boolean shouldBank;

    public GenericGatherLeaf(String objectName, Area area,
                             Filter<Item> dropFilter, boolean shouldBank) {
        this.objectFilter = o -> o.getName().equals(objectName);
        this.area = area;
        this.dropFilter = dropFilter;
        this.shouldBank = shouldBank;
    }

    @Override
    public boolean isValid() {
        return !Inventory.isFull();
    }

    @Override
    public int onLoop() {
        if (!area.contains(Players.getLocal())) {
            if (Walking.shouldWalk()) Walking.walk(area);
            return 600;
        }
        GameObject target = GameObjects.closest(objectFilter);
        if (target != null && !Players.getLocal().isAnimating()) {
            target.interact();
        }
        return 600;
    }
}
```

### Progressive Scripts with Branches

Branches checked in order — first valid wins. Perfect for level progression:

```java
public class WoodcuttingScript extends TreeScript {
    @Override
    public void onStart() {
        addBranches(
            new AntiBanNode(),
            new FullInventoryBranch(),  // bank when full (always valid if inv full)
            new NormalTreeBranch(),     // valid if WC < 15
            new OakBranch(),           // valid if WC < 30
            new YewBranch()            // valid if WC >= 30 (fallback)
        );
    }
}

public class NormalTreeBranch extends Branch {
    public NormalTreeBranch() {
        addLeaves(new GenericGatherLeaf("Tree", LUMBRIDGE_TREES, logFilter, false));
    }
    @Override
    public boolean isValid() {
        return Skills.getRealLevel(Skill.WOODCUTTING) < 15;
    }
}
```

### Shared State via getTree()

Every `Leaf` can access the parent script via `getTree()`:

```java
@Override
public int onLoop() {
    // Access script-level fields
    WoodcutterScript script = (WoodcutterScript) getTree();
    // ... use script.someField
    return 600;
}
```

## TaskScript Pattern (Alternative)

Use for flat independent concerns — each node checks independently, highest priority wins:

```java
public class CombatScript extends TaskScript {
    @Override
    public void onStart() {
        addNodes(new EatNode(), new LootNode(), new AttackNode());
    }
}

public class EatNode extends TaskNode {
    @Override
    public int priority() { return 10; } // higher = checked first
    @Override
    public boolean accept() {
        return Combat.getHealthPercent() < 50 && Inventory.contains("Lobster");
    }
    @Override
    public int execute() {
        Inventory.interact("Lobster", "Eat");
        return 600;
    }
}
```

Good for combat because eat/loot/attack are independent concerns that don't form a natural hierarchy.

## Key Coding Practices

### Always Return 600 (One Game Tick)
OSRS runs on 600ms ticks. Returning less means spam-clicking. Return 600 as the baseline.

```java
// BAD — spam clicks
return 1;

// GOOD — one action per tick
return 600;
```

### One Action Per Loop
Execute ONE action then return. Don't chain actions — any can fail. Let the next tick re-evaluate.

```java
// BAD — chaining
Bank.withdraw("Iron scimitar");
Equipment.equip(EquipmentSlot.WEAPON, "Iron scimitar");

// GOOD — one action, return, re-evaluate
if (Inventory.isFull()) {
    if (!Bank.isOpen()) { Bank.open(); return 600; }
    Bank.depositAll(logFilter); return 600;
}
```

### Bank.open() Walks For You
Never manually walk to a bank. `Bank.open()` handles walking automatically.

```java
// BAD
Walking.walk(bankTile);
// ...later...
Bank.open();

// GOOD
if (Walking.shouldWalk()) Bank.open();
```

### Walking.shouldWalk() Guard
Don't call `Walking.walk()` every tick — check first:

```java
if (Walking.shouldWalk()) Walking.walk(area);
```

### Check Return Values Before Sleeping
Most API methods return boolean. Only sleep on success:

```java
if (Bank.withdraw("Iron ore")) {
    Sleep.sleepUntil(() -> Inventory.contains("Iron ore"), 3000);
}
```

### Use Boolean Returns to Simplify
Many methods return true if already in desired state:

```java
// setWithdrawMode returns true if already NOTE or successfully changed
if (Bank.setWithdrawMode(BankMode.NOTE)) {
    Bank.withdrawAll("Iron scimitar");
}
```

### Sleep Until with Reset Conditions
For actions involving walking, use reset conditions:

```java
// Resets timeout while player is still moving
NPC banker = NPCs.closest("Banker");
if (banker != null && banker.interact("Bank")) {
    Sleep.sleepUntil(Bank::isOpen, () -> Players.getLocal().isMoving(), 3000, 100);
}
```

**Always use lambdas, not method references for reset conditions:**
```java
// BAD — captures stale player reference
Sleep.sleepUntil(Bank::isOpen, Players.getLocal()::isMoving, 3000, 100);

// GOOD — gets fresh reference each poll
Sleep.sleepUntil(Bank::isOpen, () -> Players.getLocal().isMoving(), 3000, 100);
```

### No Magic Numbers or Repeated Literals
```java
private static final String WEAPON_NAME = "Iron scimitar";
private static final Area TREE_AREA = new Area(3138, 3220, 3150, 3235);
```

### Use Enums for Data Sets
```java
public enum OreType {
    IRON("Iron ore", 440), MITHRIL("Mithril ore", 447);
    private final String name; private final int rockId;
    OreType(String name, int rockId) { this.name = name; this.rockId = rockId; }
    public String getName() { return name; }
    public int getRockId() { return rockId; }
}
```

### Always Null-Check
```java
NPC target = NPCs.closest("Cow");
if (target != null && !target.isInCombat()) {
    target.interact("Attack");
}
```

### Validate Game State, Don't Track It
Check actual game state each tick. Don't set a "next state" variable:

```java
// BAD
state = "deposit";

// GOOD — check reality
if (Inventory.isFull()) { ... }
```

### Paint the Decision Path
Always paint `TweeNode.decisionPath` so you can see what the script is doing:

```java
@Override
public void onPaint(Graphics2D g) {
    g.drawString("Path: " + TweeNode.decisionPath, 25, 180);
}
```

## Reusable Node Design Goals

1. **Traceable** — paint the decision path, log from every node with `log()`
2. **Minimal code** — parameterize nodes with filters, areas, conditions. One class handles many cases.
3. **Readable** — the tree structure in `onStart()` should read like a flowchart. Anyone can see what the script does at a glance.
