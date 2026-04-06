# DreamBot Scripting Patterns

## TaskScript: Main Class Wiring

```java
@ScriptManifest(name = "fisher", author = "osrs-bot", version = 0.1,
                description = "Fishes and banks", category = Category.FISHING)
public class FisherScript extends TaskScript {
    @Override
    public void onStart() {
        FishContext ctx = new FishContext(this);
        addNodes(
            new AntiBanNode(),           // priority 100 — ambient anti-ban
            new EatFoodNode(ctx),        // priority 50  — emergency: eat if low HP
            new BankNode(ctx),           // priority 0   — bank when full
            new FishNode(ctx),           // priority 0   — main action
            new WalkToSpotNode(ctx)      // priority 0   — walk if not at spot
        );
    }
}
```

### Priority Tiers
- **100**: Anti-ban (fires probabilistically)
- **50**: Emergency/recovery (eat food, handle random events)
- **0**: Main script actions (all equal priority — first to `accept()` wins)

## TaskScript: Node Structure

```java
public class FishNode extends TaskNode {
    private final FishContext ctx;

    public FishNode(FishContext ctx) { this.ctx = ctx; }

    @Override
    public boolean accept() {
        return !Inventory.isFull()
            && NPCs.closest("Fishing spot") != null
            && !Players.getLocal().isAnimating();
    }

    @Override
    public int execute() {
        NPC spot = NPCs.closest("Fishing spot");
        if (spot == null) return AntiBanUtil.conditionSleep("idle");

        if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
        spot.interact("Net");
        Sleep.sleepUntil(() -> Players.getLocal().isAnimating(), 5000);
        ctx.resetStuck();
        return AntiBanUtil.conditionSleep("waiting");
    }
}
```

## ScriptContext: Shared State

Extend `ScriptContext` per script. Nodes receive it via constructor.

```java
public class FishContext extends ScriptContext {
    public Area fishingArea = new Area(3238, 3253, 3245, 3241);
    public String[] fishNames = {"Raw shrimps", "Raw anchovies"};

    public FishContext(AbstractScript script) { super(script); }
}
```

## AbstractScript: Enum State Machine

For simple scripts only (≤2 states, no banking):

```java
@ScriptManifest(name = "simple-miner", author = "osrs-bot", version = 0.1,
                description = "", category = Category.MINING)
public class SimpleMinerScript extends AbstractScript {
    private enum State { MINE, DROP }
    private State state = State.MINE;

    @Override
    public int onLoop() {
        switch (state) {
            case MINE:
                if (Inventory.isFull()) { state = State.DROP; return 100; }
                GameObject rock = GameObjects.closest("Rocks");
                if (rock != null) {
                    rock.interact("Mine");
                    Sleep.sleepUntil(() -> Players.getLocal().isAnimating(), 5000);
                }
                return AntiBanUtil.conditionSleep("waiting");
            case DROP:
                Inventory.dropAll();
                state = State.MINE;
                return AntiBanUtil.conditionSleep("clicking");
        }
        return 600;
    }
}
```

## Common Flows

### Banking Flow (TaskNode)
```java
public class BankNode extends TaskNode {
    private final MyContext ctx;
    public BankNode(MyContext ctx) { this.ctx = ctx; }

    @Override
    public boolean accept() { return Inventory.isFull(); }

    @Override
    public int execute() {
        if (!Bank.isOpen()) {
            Bank.open();
            Sleep.sleepUntil(Bank::isOpen, 10000);
            return AntiBanUtil.conditionSleep("waiting");
        }
        Bank.depositAllItems();
        Sleep.sleepUntil(() -> Inventory.count() == 0, 3000);
        Bank.close();
        ctx.resetStuck();
        return AntiBanUtil.conditionSleep("clicking");
    }
}
```

### Combat Flow (TaskNode)
```java
public class AttackNode extends TaskNode {
    @Override
    public boolean accept() {
        return !Players.getLocal().isInCombat()
            && !Inventory.isFull();
    }

    @Override
    public int execute() {
        NPC target = NPCs.closest(n -> "Cow".equalsIgnoreCase(n.getName())
            && !n.isInCombat() && n.getHealthPercent() > 0);
        if (target == null) return AntiBanUtil.conditionSleep("idle");

        if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
        target.interact("Attack");
        Sleep.sleepUntil(() -> Players.getLocal().isInCombat(), 5000);
        return AntiBanUtil.conditionSleep("waiting");
    }
}
```

### Loot Flow (TaskNode)
```java
public class LootNode extends TaskNode {
    private static final String[] LOOT = {"Bones", "Cowhide"};

    @Override
    public int priority() { return 10; } // slightly above main actions

    @Override
    public boolean accept() {
        return !Players.getLocal().isInCombat()
            && GroundItems.closest(LOOT) != null
            && !Inventory.isFull();
    }

    @Override
    public int execute() {
        GroundItem item = GroundItems.closest(LOOT);
        if (item != null) {
            item.interact("Take");
            Sleep.sleepUntil(() -> !item.exists(), 5000);
        }
        return AntiBanUtil.conditionSleep("clicking");
    }
}
```

### Walking Flow
```java
public class WalkToAreaNode extends TaskNode {
    private final MyContext ctx;
    public WalkToAreaNode(MyContext ctx) { this.ctx = ctx; }

    @Override
    public boolean accept() {
        return !ctx.area.contains(Players.getLocal());
    }

    @Override
    public int execute() {
        Walking.walk(ctx.area.getRandomTile());
        Sleep.sleepUntil(() -> ctx.area.contains(Players.getLocal()), 15000);
        return AntiBanUtil.conditionSleep("waiting");
    }
}
```

## Stuck Detection

Built into `ScriptContext`. Call from nodes:

```java
@Override
public int execute() {
    NPC target = NPCs.closest("Fishing spot");
    if (target == null) {
        if (ctx.incrementStuck()) {
            Logger.error("Stuck for too long, stopping");
            ctx.getScript().stop();
        }
        return AntiBanUtil.conditionSleep("idle");
    }
    ctx.resetStuck();
    // ... perform action
}
```

## Error Handling

```java
@Override
public int execute() {
    try {
        // risky action
    } catch (Exception e) {
        Logger.error("Error: " + e.getMessage());
        ctx.getScript().stop();
    }
    return 600;
}
```
