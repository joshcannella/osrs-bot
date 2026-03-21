# Scripting Patterns

## Table of Contents
- [State Machine Design](#state-machine-design)
- [XP-Based Progress Tracking](#xp-based-progress-tracking)
- [Moving Object Interaction](#moving-object-interaction)
- [Ground Item Clicking](#ground-item-clicking)
- [Recovery Logic](#recovery-logic)
- [Stuck Detection](#stuck-detection)
- [Idle-Based Action Completion](#idle-based-action-completion)
- [ZoneManager & SubZoneMapper](#zonemanager--subzonemapper)
- [Colour Picker Usage](#colour-picker-usage)
- [Discord Notifications](#discord-notifications)

---

## State Machine Design

Think through every state the bot can be in. Apply fail-fast, defensive programming.

### Example: Agility Course States

1. **Obstacle AND Mark of Grace** — Click obstacle (don't click mark yet, pathing breaks)
2. **Obstacle only** — Standard progression, click obstacle
3. **Mark of Grace only** — Landed on roof with mark, plugin hid obstacle highlight. Pick up mark.
4. **Nothing detected** — Fell off course or misclicked. Walk to reset tile.

### Pseudocode Pattern

```
REPEAT EVERY CYCLE:
  1. [GET STATE] current_xp = get_minimap_xp()
  2. [EVALUATE ENVIRONMENT]
     IF obstacle NOT visible:
       IF mark visible: pick up mark, wait for obstacle
       ELSE: walk to course start
       EXIT CYCLE
  3. [EXECUTE] Click obstacle (repeat until red click)
  4. [VERIFY] Wait until XP changes or timeout
  5. [HUMANIZE] Small chance of extended break
```

### Fail-Fast Pattern

Check edge cases BEFORE the main action:
```java
@Override
protected void cycle() {
    if (HumanBehavior.runPreCycleChecks(this)) return;

    // Check edge cases first
    if (!isObstacleVisible()) {
        if (clickMarkOfGraceIfPresent()) {
            waitForObstacleToAppear();
        } else {
            recoverToResetTile();
        }
        return;
    }

    // Main action only after all guards pass
    clickObstacle();
    waitForProgress();
}
```

---

## XP-Based Progress Tracking

Use `Minimap.getXp()` to detect when actions complete. Agility obstacles have varying animation lengths — static waits don't work.

```java
int previousXp = Minimap.getXp(this);
if (previousXp == -1) {
    logger.warn("Could not read XP, retrying next cycle");
    return;
}

performAction();

// Wait for XP change with timeout
LocalDateTime endTime = LocalDateTime.now().plusSeconds(TIMEOUT_SECONDS);
while (previousXp == Minimap.getXp(this) && LocalDateTime.now().isBefore(endTime)) {
    waitMillis(300);
}
```

### Kill Detection: Use Full XP Amount

Don't wait for *any* XP change — XP is granted per hit, not on kill. Calculate total: `NPC_HP × 4`.

```java
private static final int CHICKEN_XP = 12; // 3 HP × 4
while (LocalDateTime.now().isBefore(deadline)) {
    if (Minimap.getXp(this) - previousXp >= CHICKEN_XP) break;
    waitMillis(300);
}
```

### OCR Safety

Always wrap `Minimap.getXp()` in try-catch — OCR can read NPC name overlays as garbage:
```java
int previousXp;
try {
    previousXp = Minimap.getXp(this);
} catch (Exception e) {
    logger.warn("Could not read XP, retrying next cycle");
    return;
}
```

---

## Moving Object Interaction

Objects can move when you click them. Use `MovingObject` to retry until a red interaction click:

```java
if (!MovingObject.clickMovingObjectByColourObjUntilRedClick(OBSTACLE_COLOUR, this)) {
    logger.error("Couldn't click moving object within standard attempts.");
    DiscordNotification.send("Couldn't click moving object.");
    stop();
}
```

---

## Ground Item Clicking

Ground items are highlighted by RuneLite's Ground Items plugin. Use tightness to avoid clicking between tiles:

```java
Point clickLoc = PointSelector.getRandomPointByColourObj(gameView, MARK_COLOUR, 15, 15.0);
if (clickLoc != null) {
    controller().mouse().moveTo(clickLoc, "medium");
    controller().mouse().leftClick();
}
```

### Adjacent Loot Merging

Multiple loot piles on adjacent tiles merge into one contour. Target the smallest contour:
```java
List<ChromaObj> objs = ColourContours.getChromaObjsInColour(gameView, LOOT_COLOUR);
try {
    ChromaObj smallest = objs.get(0);
    for (ChromaObj obj : objs) {
        if (obj.boundingBox().width * obj.boundingBox().height
            < smallest.boundingBox().width * smallest.boundingBox().height) {
            smallest = obj;
        }
    }
    Point clickLoc = ClickDistribution.generateRandomPoint(smallest.boundingBox(), 15.0);
} finally {
    for (ChromaObj obj : objs) obj.release();
}
```

### Colour vs Template for Ground Items

Ground items render differently than inventory icons (scale, angle, lighting). **Always prefer colour-based detection** via RuneLite plugin highlights over template matching for ground items.

---

## Recovery Logic

When the bot is lost (nothing detected), double-check then walk to a reset tile:

```java
private void recoverToResetTile() {
    waitMillis(HumanBehavior.adjustDelay(600, 800));
    if (!isObstacleVisible()) {
        int attempts = 0;
        while (attempts < 5) {
            try {
                logger.info("Lost. Walking to reset tile.");
                controller().walker().pathTo(RESET_TILE, true);
                waitMillis(HumanBehavior.adjustDelay(4000, 6000));
                break;
            } catch (IOException e) {
                logger.error("Walker error: {}", e.getMessage());
                attempts++;
            } catch (InterruptedException e) {
                DiscordNotification.send("Walker interrupted.");
                stop();
                return;
            }
        }
    }
}
```

---

## Stuck Detection

Every script must track consecutive failed cycles:

```java
private static final int MAX_STUCK_CYCLES = 10;
private int stuckCounter = 0;

// After successful action:
stuckCounter = 0;

// After failed/no-progress cycle:
stuckCounter++;
if (stuckCounter >= MAX_STUCK_CYCLES) {
    logger.error("Stuck for {} cycles, logging out.", MAX_STUCK_CYCLES);
    DiscordNotification.send("Script stuck, logging out.");
    Logout.perform(this);
    stop();
}
```

---

## Idle-Based Action Completion

Prefer `Idler.waitUntilIdle()` over manual polling for skilling actions (fishing, cooking, chopping, smelting):

```java
// After clicking fishing spot:
if (Idler.waitUntilIdle(this, 120)) {
    logger.info("Player went idle.");
}
// Then check WHY — inventory full? Spot moved?
```

Requires RuneLite Idle Notifier plugin enabled.

---

## ZoneManager & SubZoneMapper

`ZoneManager` dynamically maps UI zones using template matching, then `SubZoneMapper` derives sub-zones with hardcoded offsets.

### Key Zones

```java
controller().zones().getGameView()           // BufferedImage (complex shape, pre-cropped)
controller().zones().getInventorySlots()      // List<Rectangle>, 0-27, left→right top→bottom
controller().zones().getMinimap()             // Map: "hpText","prayerText","runText","specText","totalXP","playerPos"
controller().zones().getCtrlPanel()           // Control panel tabs
controller().zones().getChatTabs()            // "Chat","Latest Message", etc.
controller().zones().getGridInfo()            // "Tile" = player world position
controller().zones().getMouseOver()           // Mouseover tooltip zone
```

### Converting Zones to Images

```java
Rectangle slot = controller().zones().getInventorySlots().get(5);
BufferedImage slotImg = ScreenManager.captureZone(slot);
```

---

## Colour Picker Usage

1. Open ChromaScape web UI → click Screenshotter → saves `output/original.png`
2. Click Colour Picker button
3. Push `min` HSV sliders up until colour almost disappears
4. Push `max` HSV sliders down until colour is isolated
5. Name and submit — or copy the code output for direct use

---

## Discord Notifications

Send alerts on significant events:
```java
DiscordNotification.send("Script stuck, logging out.");
```

Setup: Create `secrets.properties` in ChromaScape root with:
```
discord.webhook.url=https://discord.com/api/webhooks/{id}/{token}
```
