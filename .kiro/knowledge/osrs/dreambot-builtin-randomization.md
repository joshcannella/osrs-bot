# DreamBot Built-in Randomization

DreamBot already randomizes a significant amount of low-level input behavior internally. Scripts should NOT duplicate this — focus anti-ban on high-level behavioral variation instead.

## What DreamBot Randomizes Automatically

### Mouse Movement
- `StandardMouseAlgorithm` generates curved, human-like mouse paths (not straight lines)
- Acceleration, deceleration, and overshoot are built in (`MouseSettings`)
- `Mouse.getMouseSettings().setSpeed(int)` controls speed (1-100)
- Click positions are randomized within entity bounds (`getClickablePoint()` returns a random point, not center)
- `MouseTiming` randomizes delay between mouse press and release

### Interaction (`entity.interact()`)
- Automatically decides left-click vs right-click based on `getLeftClickAction()`
- If the action IS the left-click default → left-clicks directly
- If the action is NOT the default → right-clicks, opens menu, selects from menu
- `InteractionSetting` enum allows overriding: `FORCE_LEFT_CLICK`, `FORCE_RIGHT_CLICK`, `ROTATE_CAMERA`, `ZOOM_CAMERA`
- `interactForceLeft(action)` / `interactForceRight(action)` for explicit control

### Dialogues
- `Dialogues.continueDialogue()` — profiles mouse distance to decide click vs spacebar
- `Dialogues.chooseOption(int)` — profiles mouse distance to decide click vs key press
- These are NOT just clicking — they simulate how a real player would respond based on where their mouse already is

### Keyboard
- `Keyboard.type()` uses `KeyboardTypingAlgorithm` with configurable WPM
- Typing speed varies per character naturally

## What DreamBot Does NOT Randomize

These are the script's responsibility:

- **Which action to take** — DreamBot executes what you tell it, it doesn't decide for you
- **Delays between actions** — no built-in delay between your `onLoop()` calls
- **Ambient idle behavior** — no tab checking, camera moves, or AFK simulation
- **Action variation** — won't sometimes bank differently or take alternate paths
- **Session-level patterns** — no fatigue, break scheduling, or session duration awareness

## Rules for Script Authors

1. **Use `interact(action)` not raw `Mouse.move()` + `Mouse.click()`** — let DreamBot handle click type, position, and mouse path
2. **Use `Dialogues.continueDialogue()` not `Keyboard.type(" ")`** — it profiles automatically
3. **Don't add mouse micro-drift** — DreamBot's mouse algorithm already produces natural movement. Adding jitter on top creates unnatural double-randomization
4. **Don't randomize click positions manually** — `getClickablePoint()` already does this
5. **DO vary mouse speed over session** — `Mouse.getMouseSettings().setSpeed()` (fatigue = slower)
6. **DO vary high-level behavior** — which tab to check, when to idle, whether to examine something
7. **DO add delays between actions** — DreamBot handles intra-action timing, but inter-action timing is yours

## Useful Settings to Tweak

```java
// Vary mouse speed (1=slow, 100=fast) — good for fatigue simulation
Mouse.getMouseSettings().setSpeed(Calculations.random(70, 90));

// Force interaction style occasionally
entity.interact("Chop down", true, true);  // force right-click menu
entity.interactForceLeft("Chop down");     // force left-click

// InteractionSettings for advanced control
// FORCE_LEFT_CLICK, FORCE_RIGHT_CLICK, ROTATE_CAMERA, ZOOM_CAMERA
```

## Source
Discovered by inspecting the scraped DreamBot 4.0.0-SNAPSHOT javadocs and forum discussion about AI-generated scripts being detected due to bypassing DreamBot's built-in randomization.
