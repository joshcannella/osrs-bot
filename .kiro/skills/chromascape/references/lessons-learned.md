# Lessons Learned

Hard-won patterns from past script generation. Read this before debugging or fixing scripts.

---

## Detection

### Ground Items: Use Colour, Not Templates
Ground items render differently than inventory icons (scale, angle, lighting). Template matching fails. Use RuneLite Ground Items plugin to highlight in a distinct colour, then detect with `ColourContours`. Same pattern as marks of grace in agility.

### Ground Items: Use Tightness
Ground item tiles are large. Without tightness, clicks land outside the item. Use `tightness` 15.0+.

### Adjacent Loot Tiles Merge
Multiple loot piles on adjacent tiles merge into one contour. Target the smallest contour, not closest-to-center. Re-scan after each pickup.

### PointSelector OpenCV Crash
`PointSelector.getRandomPointByColourObj()` can crash on malformed contours. Bypass it — get contours via `ColourContours`, extract bounding box, generate point with `ClickDistribution.generateRandomPoint()`. Always release `ChromaObj` Mats in finally blocks.

### Template Thresholds
- Inventory items: 0.05-0.07
- Ground items (if you must): 0.10-0.15 with fallback
- Stacked/banked items: crop out top 10 pixels of template

---

## State Management

### Always Verify Before Advancing
Never advance state without confirming the action succeeded:
```java
case GET_ITEM -> {
    if (!hasItem(ITEM_IMAGE)) { performAction(); }
    else { step = Step.NEXT_STEP; }
}
```

### Track Item Transformations
Items transform (bucket→milk, pot→flour). Check for ALL forms in skip logic:
```java
if (hasItem(BUCKET_IMAGE) || hasItem(MILK_IMAGE)) { step = Step.NEXT; }
```

### Implicit Retry via Cycle Loop
Don't build explicit retry counters. Structure steps as "check completion → act → advance only when complete" — the cycle loop retries naturally.

### Never Assume Inventory Slot Positions
Always scan and match. Items shift when others are used/dropped.

---

## XP & Kill Detection

### Full XP for Kill Confirmation
XP is granted per hit, not on kill. Wait for `NPC_HP × 4` total XP, not any change.

### OCR Reads Garbage
`Minimap.getXp()` can read NPC name overlays as text. Always try-catch. If XP read fails, skip the cycle — don't proceed with -1 (causes instant false-positive kill confirmation).

### Post-Kill Delay
Wait 600-900ms after kill confirmation for death animation before next action.

---

## Combat

### Health Bar > Chat for Combat State
`Combat.isInCombat()` detects the Opponent Information health bar overlay — instant, visual, no OCR. Use it for:
- **Engagement confirmation** after clicking an NPC (replaces XP/position polling)
- **Fast-path skip** at top of cycle when still fighting (avoids Idler OCR cost)
- **Mid-fight validation** when Idler fires ANIMATION/MOVEMENT events (confirm still in combat before continuing to wait)

Keep `Idler.waitUntilIdleType()` for the authoritative "combat ended" signal — the chat message is the definitive event.

### Always Target Closest NPC
Use `ColourClick.getClickPoint()` instead of `MovingObject` for NPC targeting. `ColourClick` uses `getChromaObjClosestToCentre` which picks the nearest mob to the player. `MovingObject` picks randomly, causing the player to run past nearby mobs to reach distant ones.

### Verify Red Click Before Waiting
After clicking an NPC, call `ColourClick.wasRedClick(point)` ~120ms later. If no red X, skip to next attempt immediately — don't waste 8s polling for combat that will never start.

### NPC Access Obstacles
NPCs behind doors/gates/ladders need an explicit step to handle the obstacle first. Don't assume the walker paths through.

### Loot Frequency
For fast-kill NPCs, batch looting every N kills. Ground items persist 60 seconds. Ensure `N × kill_time < 60s`.

---

## Action Completion

### Use Idler Over Polling
`Idler.waitUntilIdle()` beats manual inventory/XP polling loops. Less expensive, more reliable. Requires Idle Notifier plugin.

### Stuck Detection is Mandatory
Track consecutive failed cycles. After threshold (10), Discord notify + logout + stop. Never let a script run indefinitely without progress.

---

## Build & Deploy

### Always Compile in ChromaScape
API differences between projects cause silent failures. Use `osrs-bot build`.

### Don't Duplicate Utilities
Check API reference before writing any private helper. If `Inventory`, `KeyPress`, `Bank`, etc. already does it, use it. Run `osrs-bot lint` to catch duplicates.

### LevelUpDismisser DIALOG_BLUE Was Wrong
The "Click here to continue" text in OSRS level-up dialogs is `RGB(0, 0, 128)` → OpenCV HSV `H=120, S=255, V=128`. The original `DIALOG_BLUE` range `H=125-135, S=200-255, V=150-255` missed on both H (too high) and V (floor too high). Fixed to `H=118-122, S=200-255, V=100-255`. Always verify HSV ranges against actual RGB values using `colorsys.rgb_to_hsv()` conversion.

### Left-Click Bank Deposit Only Deposits 1
Left-clicking an item in the bank inventory deposits 1 item by default (unless the player has manually set the quantity to "All" via the bank UI buttons). Don't rely on left-click deposit loops — they deposit 1 per click and are extremely slow. Use `Bank.depositAll()` + withdraw tools instead. The bank quantity setting persists per-account but can't be detected or set programmatically.

### Always Verify Image Templates Exist
Before deploying a script, verify every image template in `/images/user/` actually exists as a PNG file. Missing templates cause `Resource not found` exceptions at runtime. Download from OSRS Wiki and verify with `file` command.
