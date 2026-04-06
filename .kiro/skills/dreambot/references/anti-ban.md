# Anti-Ban System

## Overview

Two components:
1. **AntiBanNode** — high-priority TaskNode that fires probabilistically for ambient human-like actions
2. **AntiBanUtil** — static utility methods for inline use within other nodes

## AntiBanNode

Located at `scripts/shared/antiban/AntiBanNode.java`. Extends DreamBot's `Leaf` class — works natively in TreeScript, also callable standalone from TaskScript/AbstractScript.

### In TreeScript
Add as first branch:
```java
addBranches(new AntiBanNode(), ...otherBranches);
```

### In TaskScript
Create a wrapper TaskNode that delegates:
```java
public class AntiBanTaskNode extends TaskNode {
    private final AntiBanNode inner = new AntiBanNode();
    @Override public boolean accept() { return inner.isValid(); }
    @Override public int execute() { return inner.onLoop(); }
    @Override public int priority() { return 100; }
}
```

### In AbstractScript
Call directly:
```java
private final AntiBanNode antiBan = new AntiBanNode();
@Override public int onLoop() {
    if (antiBan.isValid()) return antiBan.onLoop();
    // ... rest of script
}
```

### Behavior
- Priority: 100 (highest — checked before all script nodes)
- `accept()`: returns true ~8% of ticks, but only after 15+ seconds since last anti-ban action
- `execute()`: randomly picks one action:
  - Camera rotation (random yaw adjustment)
  - Check stats tab (open → pause → back to inventory)
  - Short idle pause (just returns a delay)
  - Check quest tab (open → pause → back to inventory)

### Tuning
Adjust `MIN_INTERVAL_MS` (default 15s) and the probability in `accept()` (default 0.08) based on testing. More frequent = more human-like but slower scripts.

## AntiBanUtil

Located at `scripts/shared/antiban/AntiBanUtil.java`. Use in any node.

### humanDelay(int baseMin, int baseMax)
Randomized delay with 5% chance of an outlier (up to 3x baseMax). Use instead of `Calculations.random()` for all action delays.

```java
return AntiBanUtil.humanDelay(500, 1000);
// Usually returns 500-1000, occasionally returns 1000-3000
```

### shouldHesitate() / hesitate()
~10% chance of a short pause before an action. Call before clicks:

```java
if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
target.interact("Attack");
```

### conditionSleep(String context)
Context-aware sleep time:
- `"clicking"` → 100-300ms (just clicked something)
- `"waiting"` → 500-1000ms (waiting for action to complete)
- `"idle"` → 2000-5000ms (nothing to do)

```java
return AntiBanUtil.conditionSleep("clicking");
```

## Integration Checklist

For every new script:
1. ✅ Register `AntiBanNode` in `onStart()`
2. ✅ Use `AntiBanUtil.humanDelay()` instead of `Calculations.random()` for return values
3. ✅ Add `shouldHesitate()` / `hesitate()` before important clicks
4. ✅ Use `conditionSleep()` for context-appropriate delays

## Future: BreakScheduler

Deferred until real testing data exists. Will manage longer AFK breaks (2-10 minutes) on a configurable schedule. For now, the short pauses from `AntiBanNode` provide basic break-like behavior.
