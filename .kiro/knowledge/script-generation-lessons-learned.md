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
