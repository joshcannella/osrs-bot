---
name: chromascape
description: ChromaScape bot framework guide for writing OSRS automation scripts in Java. Use when generating scripts, debugging script issues, working with ChromaScape APIs (ColourClick, PointSelector, TemplateMatching, ZoneManager, Walker, HumanBehavior, Inventory, Bank, OCR), discussing colour detection, image template matching, state machines for botting, or anything related to the ChromaScape scripting framework — even if the user doesn't mention ChromaScape by name.
---

# ChromaScape Script Development

ChromaScape is a Java framework for OSRS automation. Scripts extend `BaseScript`, override `cycle()` (called in a loop), and use a controller to access mouse, keyboard, zones, and walker utilities.

## Architecture

```
ChromaScape/src/main/java/com/chromascape/
├── scripts/                    # Generated scripts (your output)
├── utils/actions/              # Upstream: Idler, ItemDropper, Minimap, MouseOver, MovingObject, PointSelector
└── utils/actions/custom/       # Ours: Bank, ColourClick, GameCenter, HumanBehavior, Inventory, KeyPress, LevelUpDismisser, Logout, Walk
```

- Images: `ChromaScape/src/main/resources/images/user/`
- Package: `com.chromascape.scripts`
- Custom imports: `com.chromascape.utils.actions.custom.*`
- Upstream imports: `com.chromascape.utils.actions.*`

## Script Skeleton

Every script follows this structure:

```java
public class MyScript extends BaseScript {
    private static final Logger logger = LogManager.getLogger(MyScript.class);

    @Override
    protected void cycle() {
        if (HumanBehavior.runPreCycleChecks(this)) return;
        // State machine logic here
    }
}
```

`HumanBehavior.runPreCycleChecks(this)` handles breaks, camera fidgets, idle drifts, and level-up dismissal. It must be the first line of every `cycle()`.

## Core Concepts

### Detection: Colour vs Image

Two ways to find things on screen:

1. **Colour detection** — RuneLite highlights objects in a colour (cyan, purple, etc.), then `PointSelector.getRandomPointInColour()` or `ColourContours` finds them. Best for: NPCs, bank booths, obstacles, ground items (via Ground Items plugin).

2. **Image template matching** — Compare a saved PNG against the screen. `PointSelector.getRandomPointInImage()` or `TemplateMatching.match()`. Best for: inventory items, specific UI elements.

### State Machines

Scripts use enum-based state machines. Each state checks its completion condition first (fail-fast), performs its action, and only advances when verified:

```java
case GATHER -> {
    if (Inventory.isFull(this, KNOWN_ITEMS, 0.07)) { state = State.BANK; return; }
    // perform gathering action
}
```

### HumanBehavior Integration

Before every click:
```java
String speed = HumanBehavior.shouldSlowApproach() ? "slow" : "medium";
controller().mouse().moveTo(clickLoc, speed);
if (HumanBehavior.shouldHesitate()) HumanBehavior.performHesitation();
if (HumanBehavior.shouldMisclick()) { HumanBehavior.performMisclick(this, clickLoc); controller().mouse().moveTo(clickLoc, "medium"); }
controller().mouse().microJitter();
controller().mouse().leftClick();
```

For delays: `waitMillis(HumanBehavior.adjustDelay(800, 1000));` instead of `waitRandomMillis()`.

## When to Load References

Load these based on what you're doing:

| Task | Reference |
|------|-----------|
| Writing any script code | `references/api-reference.md` — **always read first** |
| Designing state machines, recovery logic | `references/scripting-patterns.md` |
| Debugging or fixing a script | `references/lessons-learned.md` |
| Creating shared utilities | `references/extending-framework.md` |
| **Before presenting any script** | `references/code-review-checklist.md` — **mandatory, run every item** |

## Critical Rules

1. Never modify upstream ChromaScape files — only `scripts/` and `utils/actions/custom/`
2. Never hallucinate APIs — only use methods from the API reference
3. Never duplicate shared utilities as private methods — check API reference first
4. All `PointSelector`/`TemplateMatching` results must be null-checked
5. All `pathTo()` calls wrapped in try/catch (IOException, InterruptedException)
6. ColourObj HSV ranges: H:0-180, S:0-255, V:0-255, fourth channel always 0
7. Image paths start with `/images/user/`
8. Template threshold: 0.05 preferred, 0.15 max
9. Ground items need tightness parameter (15.0+)
10. Loops must have `checkInterrupted()` and `waitMillis()`
11. Log every state transition with `logger.info()`
12. `stop()` on unrecoverable errors, with `DiscordNotification.send()`

## RuneLite Requirements

Every script needs:
- Windows Display Scaling: 100%
- UI Layout: "Fixed - Classic" or "Resizable - Classic"
- Brightness: middle (50%)
- ChromaScape RuneLite Profile: activated
- XP Bar: permanent (if using `Minimap.getXp()`)
- Idle Notifier: enabled (if using `Idler.waitUntilIdle()`)
- Opponent Information: enabled (if using `Combat.isInCombat()`)
