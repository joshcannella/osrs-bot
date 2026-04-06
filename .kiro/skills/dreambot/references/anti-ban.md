# Anti-Ban System

## Overview

Two-layer humanization system:

1. **AntiBanNode** (ambient) — Leaf node that fires probabilistically between script actions. 12 weighted actions including camera moves, tab checks, entity examination, idle pauses, and delegated utility actions. Add as first branch in any TreeScript.

2. **AntiBanUtil** (inline) — Static methods called by script nodes during normal gameplay. Reaction delays, hover-next-target, misclick recovery, mouse drift, inventory glances, and more. Also called by AntiBanNode for ambient triggering.

Both layers use a **fatigue system** — delays increase as the script runs longer, simulating a real player getting tired. Mouse speed also decreases over time via DreamBot's built-in `MouseSettings.setSpeed()`.

**Important:** DreamBot already randomizes low-level input (click positions, mouse paths, click timing, left/right click decisions). Our anti-ban focuses on high-level behavioral variation only. See `knowledge/osrs/dreambot-builtin-randomization.md` for details. Do NOT add mouse micro-drift or manual click randomization — it creates detectable double-randomization patterns.

## AntiBanNode Setup

Located at `scripts/shared/antiban/AntiBanNode.java`.

### In TreeScript (default)
```java
AntiBanNode ab = new AntiBanNode();
ab.setSkillsToCheck(Skill.FISHING, Skill.COOKING);
addBranches(ab, new GatherBranch(), new BankBranch());
```

### In TaskScript
```java
public class AntiBanTaskNode extends TaskNode {
    private final AntiBanNode inner = new AntiBanNode();
    @Override public boolean accept() { return inner.isValid(); }
    @Override public int execute() { return inner.onLoop(); }
    @Override public int priority() { return 100; }
}
```

### In AbstractScript
```java
private final AntiBanNode antiBan = new AntiBanNode();
@Override public int onLoop() {
    if (antiBan.isValid()) return antiBan.onLoop();
    // ... rest of script
}
```

## AntiBanNode Configuration

Call setters in `onStart()` before `addBranches()`:

| Setter | Default | Purpose |
|--------|---------|---------|
| `setSkillsToCheck(Skill...)` | HITPOINTS | Which skills to hover when checking stats tab |
| `setMinInterval(long ms)` | 15,000 | Minimum ms between anti-ban actions |
| `setTriggerRate(double)` | 0.08 | Probability of triggering per tick (~8%) |
| `setMaxRuntimeMinutes(int)` | 480 | Fatigue curve duration (delays reach 2x at this point) |

## AntiBanNode Actions (12 weighted)

| Action | Weight | Behavior |
|--------|--------|----------|
| Camera rotate | 25 | Rotate camera toward random nearby tile |
| Mouse off-screen | 18 | Move mouse outside game window (AFK simulation) |
| Check skill | 12 | Open Skills tab, pause, back to Inventory |
| Check tab | 8 | Open random tab (Quest/Equipment/Prayer/Combat/Friends), pause, back |
| Hover entity | 8 | Move mouse to nearby GameObject/NPC/GroundItem |
| Idle pause | 8 | Short idle, or extended idle (8-25s) every 5+ minutes |
| Examine entity | 6 | Right-click Examine on nearby entity |
| Glance inventory | 5 | Hover random occupied inventory slot |
| Right-click cancel | 3 | Right-click entity, read menu, dismiss |
| Check run energy | 3 | Toggle run based on energy level |
| Glance chat | 2 | Switch to Clan/Friends tab briefly |
| Check world map | 2 | Open world map briefly via 'M' key |

## Fatigue System

All delays scale with session duration:
- **Start of session**: delays near `baseMin`
- **After `maxRuntimeMinutes`**: delays reach ~2x `baseMax`
- **5% outlier chance**: occasional delay up to 3x (simulates distraction)

```java
// In AntiBanNode (uses instance startTime automatically)
return fatigue(300, 800);

// In script nodes (pass your own startTime)
return AntiBanUtil.fatigueDelay(startTime, 300, 800);
```

## AntiBanUtil Quick Reference

Located at `scripts/shared/antiban/AntiBanUtil.java`.

### Delays & Timing

```java
// Human-like delay with 5% outlier
return AntiBanUtil.humanDelay(500, 1000);

// Fatigue-scaled delay (increases over session)
return AntiBanUtil.fatigueDelay(startTime, 500, 1000);

// Reaction delay after event (gaussian ~400-800ms, 5% spike to 2-3s)
Sleep.sleep(AntiBanUtil.reactionDelay());

// Context-aware: "clicking" 100-300, "waiting" 500-1000, "idle" 2000-5000
return AntiBanUtil.conditionSleep("waiting");
```

### Before Clicking

```java
// ~10% hesitation before action
if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();

// ~3% misclick — clicks wrong thing, pauses, corrects
if (AntiBanUtil.shouldMisclick()) {
    AntiBanUtil.misclick(intendedTarget);
} else {
    intendedTarget.interact("Chop down");
}
```

### During Animation Wait

```java
// Wait while optionally hovering next target (replaces driftMouse)
AntiBanUtil.idleWatch(3000, nextTree);

// Or just wait without hovering
AntiBanUtil.idleWatch(3000);

// Hover next target directly
AntiBanUtil.hoverNextTarget(nextTree);
```

### After Action Completes

```java
// Reaction delay (human doesn't react instantly)
Sleep.sleep(AntiBanUtil.reactionDelay());

// Glance at new inventory item
AntiBanUtil.glanceInventory();
```

### Before Walking

```java
// ~20% chance to vary walk method
if (AntiBanUtil.shouldUseMinimap()) {
    // use minimap click
} else {
    Walking.walk(destination);
}
```

### Interaction Variation

```java
// ~15% chance to right-click instead of left-click
if (AntiBanUtil.shouldForceRightClick()) {
    target.interactForceRight("Chop down");
} else {
    target.interact("Chop down");
}
```

### Break Scheduling

```java
// Called automatically by AntiBanNode during idle.
// Can also call manually — returns 0 if no break, or break duration in ms.
int breakTime = AntiBanUtil.maybeBreak();
// Triggers ~every 20-40 min, 1-5 min AFK with mouse off-screen.
```

### Ambient (called by AntiBanNode, also callable manually)

```java
AntiBanUtil.rightClickCancel(entity);  // right-click, read menu, dismiss
AntiBanUtil.checkRunEnergy();          // toggle run if needed
AntiBanUtil.glanceChat();              // switch chat tab briefly
AntiBanUtil.checkWorldMap();           // open world map briefly
```

## Integration Guide — Typical Gather/Bank Loop

```
┌─ AntiBanNode fires between ticks (ambient) ─────────────┐
│  camera, mouse off, tab checks, examine, idle, etc.      │
└──────────────────────────────────────────────────────────┘

Gather Phase:
  1. Find target (tree, rock, fish spot)
  2. shouldMisclick() → misclick(target) OR shouldHesitate() → hesitate()
  3. target.interact("Chop down")
  4. Sleep.sleepUntil(animating, moving, timeout)
     └─ During wait: idleWatch() or hoverNextTarget(nextTarget)
  5. Action completes → Sleep.sleep(reactionDelay())
  6. Occasionally: glanceInventory()

Bank Phase:
  1. shouldUseMinimap() → vary walk method
  2. Bank.open() → Sleep.sleepUntil(Bank::isOpen, ...)
  3. shouldHesitate() → hesitate()
  4. Bank.depositAllExcept(...)
  5. Sleep.sleep(reactionDelay())
```

## Integration Checklist

For every new script:
1. ✅ Add `AntiBanNode` as first branch with `setSkillsToCheck()`
2. ✅ Use `fatigueDelay()` or `humanDelay()` for return values (never raw `Calculations.random()`)
3. ✅ Add `shouldHesitate()` / `hesitate()` before important clicks
4. ✅ Add `shouldMisclick()` / `misclick()` before primary interactions
5. ✅ Use `reactionDelay()` after detecting action completion
6. ✅ Use `idleWatch()` or `hoverNextTarget()` during animation waits
7. ✅ Call `glanceInventory()` occasionally after gaining items
8. ✅ Use `shouldUseMinimap()` before walking
