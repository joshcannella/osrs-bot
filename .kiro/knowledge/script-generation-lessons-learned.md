# Script Generation Lessons Learned

## Ground Item Detection
**Problem**: Scripts walked to item spawn tiles and blindly clicked screen center, causing the bot to miss small ground items and walk back and forth hopelessly.

**Solution**: Always use template matching to detect ground items before clicking:
```java
Point itemLoc = findImageInGameView(ITEM_IMAGE);
if (itemLoc != null) {
    controller().mouse().moveTo(itemLoc, "medium");
    controller().mouse().leftClick();
} else {
    logger.warn("Item not found, retrying...");
}
```

**Rule**: Use `findImageInGameView()` for all ground spawns (pots, buckets, eggs, etc.). Only use center-clicking for tall/large objects (wheat, trees, rocks, NPCs).

---

## State Progression Guards
**Problem**: Scripts advanced to the next step without verifying the action succeeded, causing them to skip critical steps.

**Solution**: Wrap actions in item checks and only advance when successful:
```java
case GET_ITEM -> {
    if (!hasItem(ITEM_IMAGE)) {
        // perform action
    } else {
        step = Step.NEXT_STEP;
    }
}
```

**Rule**: Every item-gathering step must check `if (!hasItem())` before acting and `else { advance }` after.

---

## Item Transformation Tracking
**Problem**: Scripts checked for original item (bucket) but the item transformed (bucket → bucket of milk), breaking skip logic.

**Solution**: Track all forms of an item in skip conditions:
```java
if (hasItem(BUCKET_IMAGE) || hasItem(MILK_IMAGE)) {
    step = Step.NEXT_STEP;
}
```

**Rule**: When items transform (bucket→milk, pot→flour, logs→fire), check for BOTH forms in skip logic.

---

## Implicit Retry Pattern
**Problem**: Scripts needed explicit retry counters and complex error handling.

**Solution**: Let the cycle loop provide natural retries by not advancing until success:
```java
// Bad: advances regardless
doAction();
if (success) step = NEXT;

// Good: stays on step until success
if (!hasResult()) {
    doAction();
} else {
    step = NEXT;
}
```

**Rule**: Structure steps as "check completion → perform action → advance only when complete" to get automatic retries.

---

## Template Matching for Inventory Actions
**Problem**: Scripts assumed items were in specific inventory slots or didn't verify presence before using.

**Solution**: Always search inventory before using items:
```java
private void clickInventoryItem(String templatePath) {
    for (int i = 0; i < 28; i++) {
        Rectangle slot = controller().zones().getInventorySlots().get(i);
        BufferedImage slotImg = ScreenManager.captureZone(slot);
        if (TemplateMatching.match(templatePath, slotImg, THRESHOLD).success()) {
            // click it
            return;
        }
    }
    logger.error("Item not found");
    stop();
}
```

**Rule**: Never assume inventory slot positions. Always scan and match.

---

## Ground vs Inventory Image Differences
**Problem**: Template matching failed for ground items even though the image existed, because ground items render differently than inventory icons.

**Solution**: Use relaxed thresholds and fallback strategies for ground items:
```java
Point itemLoc = findImageInGameView(ITEM_IMAGE, 0.15); // relaxed threshold
if (itemLoc == null) {
    logger.warn("Item not detected, clicking center as fallback");
    clickGameCenter();
}
```

**Rule**: Ground items need higher thresholds (0.10-0.15) than inventory items (0.05-0.07). Always provide a fallback (center-click) for common spawn points. Only advance when item appears in inventory.

---

## API Differences Between Projects
**Problem**: Code compiled in scriptgen but failed in ChromaScape due to API differences (e.g., `match.boundingBox()` vs `match.bounds()`).

**Solution**: Always test compilation in the target environment:
```bash
osrs-bot build
```

**Rule**: Use `osrs-bot build` to compile scripts and sync to ChromaScape. Scripts now use `package com.chromascape.scripts` directly — no package rewriting needed. The sync is a straight rsync copy.

Check the ChromaScape API when using framework classes - don't assume method names match between projects.

---

## ~~Package Declaration Rewrite in Sync Script~~ (Obsolete)
Scripts now use `package com.chromascape.scripts` directly in scriptgen — no rewriting needed. The sync is a straight rsync copy.

---

## NPC Access Obstacles (Quest Scripts)
**Problem**: Script walked directly to the starting NPC's tile and clicked, but the NPC was behind a closed door (e.g., Father Aereck inside Lumbridge Church). The walker reached the door tile, the click did nothing useful, and dialog inputs fired at nothing.

**Solution**: Add an explicit step before the NPC interaction to handle any access obstacle (door, gate, ladder, etc.):
```java
case ENTER_BUILDING -> {
    walkTo(DOOR_TILE, "door");
    clickGameCenter();
    waitMillis(HumanBehavior.adjustDelay(1500, 2500));
    step = Step.TALK_NPC;
}
```

**Rule**: When planning quest scripts, always check whether the starting NPC (or any NPC/object) is behind a door, gate, or other obstacle that must be interacted with first. Add a dedicated step for it rather than assuming the walker will path through.

---

## PointSelector OpenCV Crash on Invalid Contours
**Problem**: `PointSelector.getRandomPointByColourObj()` crashed with `OpenCV Assertion failed: total >= 0 && (depth == CV_32S || depth == CV_32F) in function 'cv::pointPolygonTest'`. This happens when `ColourContours.isPointInContour()` receives a contour `Mat` with invalid depth or empty data — even though `getChromaObjsInColour()` returned a non-empty list.

**Solution**: Bypass `PointSelector` and work with contours directly:
```java
List<ChromaObj> objs = ColourContours.getChromaObjsInColour(gameView, COLOUR);
Point clickLoc = null;
if (!objs.isEmpty()) {
    try {
        clickLoc = ClickDistribution.generateRandomPoint(
            ColourContours.getChromaObjClosestToCentre(objs).boundingBox());
    } catch (Exception e) {
        logger.warn("Failed to generate point from contour: {}", e.getMessage());
    } finally {
        for (ChromaObj obj : objs) {
            obj.release();
        }
    }
}
```

**Rule**: Don't call `PointSelector.getRandomPointByColourObj()` directly — it can crash on malformed contours. Instead, get contours via `ColourContours`, extract the bounding box, and generate a click point with `ClickDistribution.generateRandomPoint()`. Always release `ChromaObj` Mats in a finally block.

---

## XP-Based Kill Detection: Don't Use Single Hit
**Problem**: Using `Minimap.getXp()` to detect kills by waiting for *any* XP change caused the bot to think the target was dead after the first hit. XP is granted per hit, not on the killing blow, so the bot moved to looting while the NPC was still alive.

**Solution**: Calculate the total XP a kill is worth and wait for that full amount. For chickens: 3 HP × 4 XP per damage = 12 XP total.
```java
private static final int CHICKEN_XP = 12;
// After attacking:
while (LocalDateTime.now().isBefore(deadline)) {
    int currentXp = Minimap.getXp(this);
    if (currentXp - previousXp >= CHICKEN_XP) {
        // Kill confirmed
        break;
    }
    waitMillis(300);
}
```

**Rule**: When using XP to confirm kills, always wait for the full XP amount (NPC HP × 4), not just any XP change. Snapshot XP before attacking and compare the delta.

---

## Minimap OCR Reads Garbage Text
**Problem**: `Minimap.getXp()` threw `NumberFormatException: For input string: Chicken` because the OCR read NPC name overlays or right-click menu text instead of the XP number. This happens when UI elements overlap the XP display area.

**Solution**: Always wrap `Minimap.getXp()` in try-catch and abort/retry the cycle on failure rather than proceeding with a bad value:
```java
int previousXp;
try {
    previousXp = Minimap.getXp(this);
} catch (Exception e) {
    logger.warn("Could not read XP, retrying next cycle");
    return;
}
```

**Rule**: Never trust OCR reads unconditionally. If the XP snapshot fails, skip the entire action rather than fighting with `previousXp = -1` (which would cause instant false-positive kill confirmation since `currentXp - (-1)` is always large).

---

## Loot Colour Detection vs Template Matching
**Problem**: Template matching inventory sprites against the game view never worked for ground item detection because ground items render completely differently than inventory icons (different scale, angle, lighting, stacking).

**Solution**: Use RuneLite's Ground Items plugin to highlight loot in a distinct colour (e.g., purple), then detect that colour with `ColourContours`. This is the same pattern used by the agility script for marks of grace.

**Rule**: For ground item detection, prefer colour-based detection via RuneLite plugin highlights over template matching. Use the Colour Picker utility to get exact HSV values from the highlight.

---

## Adjacent Loot Tiles Merge Into One Contour
**Problem**: When multiple loot piles are on adjacent tiles, their colour highlights merge into one large contour. `getChromaObjClosestToCentre()` returns this merged blob, and clicking its center lands between tiles where there's no actual item.

**Solution**: Select the smallest contour instead of the closest-to-center, as it's most likely a single tile's highlight:
```java
ChromaObj smallest = objs.get(0);
for (ChromaObj obj : objs) {
    if (obj.boundingBox().width * obj.boundingBox().height
        < smallest.boundingBox().width * smallest.boundingBox().height) {
        smallest = obj;
    }
}
return ClickDistribution.generateRandomPoint(smallest.boundingBox(), 15.0);
```

**Rule**: When looting with colour detection, target the smallest contour to avoid merged adjacent tiles. Use tightness parameter (15.0) to cluster clicks toward the center. Re-scan after each pickup since contour shapes change as items are collected.

---

## Loot Frequency Optimization
**Problem**: Looting after every kill wastes time when kills are fast (e.g., chickens die in a few seconds). The bot spent more time walking to loot than fighting.

**Solution**: Track kills and only loot every N kills. Ground items persist for 60 seconds, so batching is safe:
```java
private static final int LOOT_EVERY_N_KILLS = 5;
private int killsSinceLoot = 0;
// After kill confirmed:
killsSinceLoot++;
if (killsSinceLoot >= LOOT_EVERY_N_KILLS) {
    state = State.LOOT;
    killsSinceLoot = 0;
}
```

**Rule**: For fast-kill NPCs, batch looting every N kills instead of after every kill. Ensure N × kill time stays under the 60-second ground item despawn timer.

---

## Post-Kill Delay for Death Animation
**Problem**: After confirming a kill via XP, the bot immediately clicked the next NPC. The previous NPC's death animation was still playing, causing "I'm already under attack" messages or misclicks.

**Solution**: Add a short delay (600-900ms) after kill confirmation to let the death animation complete:
```java
waitMillis(HumanBehavior.adjustDelay(600, 900));
```

**Rule**: After confirming a kill, wait 600-900ms before the next action. This covers the death animation and loot spawn delay without being noticeably slow.

---

## Use Idler.waitUntilIdle() for Action Completion Detection
**Problem**: Scripts polled inventory contents or XP every second in tight loops to detect when an action finished (e.g., fishing, cooking, chopping). This was expensive (many template matches per poll), unreliable (couldn't distinguish "still acting" from "brief pause between actions"), and missed edge cases like chat popups.

**Solution**: Use `Idler.waitUntilIdle()` which reads the RuneLite Idle Notifier plugin's red chatbox message via OCR. It blocks until the player goes idle or the timeout is reached:
```java
// After clicking a fishing spot:
if (Idler.waitUntilIdle(this, 120)) {
    logger.info("Player went idle.");
}
// Then check WHY — inventory full? Spot moved? Ran out of bait?
```

**Rule**: Always prefer `Idler.waitUntilIdle()` over manual polling loops when waiting for an action to complete (fishing, cooking, chopping, smelting, etc.). After it returns, check the reason for idling (inventory state, chat popups, colour visibility) to decide the next action. This requires the RuneLite Idle Notifier plugin to be enabled.

---

## Stuck Detection and Logout
**Problem**: Scripts got stuck in states where no progress was being made (e.g., fishing spot gone, fire died, tree chopped by someone else) and ran indefinitely doing nothing useful, risking detection.

**Solution**: Track consecutive failed cycles. If the bot fails to make progress N times in a row, log out and stop:
```java
private static final int MAX_STUCK_CYCLES = 10;
private int stuckCounter = 0;

// After any successful action:
stuckCounter = 0;

// After any failed/no-progress cycle:
stuckCounter++;
if (stuckCounter >= MAX_STUCK_CYCLES) {
    logger.error("Stuck for {} cycles, logging out.", MAX_STUCK_CYCLES);
    DiscordNotification.send("Script stuck, logging out.");
    pressLogout();
    stop();
    return;
}
```

**Rule**: Every script must implement stuck detection. Track a counter that increments when a cycle makes no progress and resets on success. After a threshold (e.g., 10 cycles), send a Discord notification, log out, and stop. Never let a script run indefinitely without progress.
