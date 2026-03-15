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
./scripts/sync-and-compile.sh
```

**Rule**: Use the sync script to copy from scriptgen → ChromaScape. It handles:
- Package name changes (com.scriptgen.behavior → com.chromascape.scripts)
- Import statement updates
- Compilation verification in ChromaScape

Check the ChromaScape API when using framework classes - don't assume method names match between projects.

---

## Package Declaration Rewrite in Sync Script
**Problem**: Scripts synced to ChromaScape retained `package com.scriptgen.scripts;` instead of `package com.chromascape.scripts;`. The source files appeared in the correct directory and the UI listed them, but `Class.forName()` failed at runtime because the compiled `.class` files were under the wrong package.

**Solution**: The `sync-and-compile.sh` script must rewrite package declarations in addition to import statements:
```bash
find "$CHROMASCAPE_SCRIPTS" -name "*.java" -type f -exec sed -i 's/package com.scriptgen.scripts;/package com.chromascape.scripts;/g' {} \;
```

**Rule**: After any sync script change, verify the compiled `.class` files land in `build/classes/java/main/com/chromascape/scripts/`, not `com/scriptgen/scripts/`.

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
