# ChromaScape API Reference

## BaseScript (com.chromascape.base.BaseScript)

Every script extends `BaseScript` and overrides `cycle()`. The framework calls `cycle()` in a loop until `stop()` is called.

```java
protected void cycle()                              // Override — main logic
public void stop()                                  // Stop the script
public Controller controller()                      // Access all utilities
public static void waitMillis(long ms)
public static void waitRandomMillis(long min, long max)
public static void checkInterrupted()               // Call in loops
```

## Controller (com.chromascape.controller.Controller)
```java
controller().mouse()      // → VirtualMouseUtils
controller().keyboard()   // → VirtualKeyboardUtils
controller().zones()      // → ZoneManager
controller().walker()     // → Walker
```

## VirtualMouseUtils (controller().mouse())
```java
void moveTo(Point target, String speed)   // "slow", "medium", "fast"
void leftClick()
void rightClick()
void middleClick(int eventType)           // 501=press, 502=release
void microJitter()
```

## VirtualKeyboardUtils (controller().keyboard())
```java
void sendKeyChar(char keyChar)
void sendModifierKey(int eventId, String key)         // 401=press, 402=release; "shift","enter","alt","ctrl","esc","space"
void sendFunctionKey(int eventId, int functionKeyNumber)
void sendArrowKey(int eventId, String key)            // "up","down","left","right"
```

## ZoneManager (controller().zones())
```java
BufferedImage getGameView()                    // Full game viewport (UI masked out)
Map<String, Rectangle> getMinimap()            // Keys: "hpText","prayerText","runText","specText","totalXP","playerPos"
Map<String, Rectangle> getCtrlPanel()          // Control panel tabs
Map<String, Rectangle> getChatTabs()           // Keys: "Chat","Latest Message", etc.
List<Rectangle> getInventorySlots()            // 28 slots, index 0-27, left→right top→bottom
Map<String, Rectangle> getGridInfo()           // Keys: "Tile" (player world position)
Rectangle getMouseOver()                       // Mouseover tooltip text zone
```

### Converting zones to images
```java
Rectangle slot = controller().zones().getInventorySlots().get(5);
BufferedImage slotImg = ScreenManager.captureZone(slot);
```
`getGameView()` already returns a `BufferedImage`.

### Image template thresholds
- Preferred: `0.05` for accurate matching
- Maximum: `0.15` — above this produces false positives
- Stacked/banked items: crop out top 10 pixels of template

### Ground item tightness
Use `tightness` parameter (15.0+) for ground items:
```java
Point clickLoc = PointSelector.getRandomPointByColourObj(gameView, MARK_COLOUR, 15, 15.0);
```

## Walker (controller().walker())
```java
void pathTo(Point destination, boolean isMembers) throws IOException, InterruptedException
Tile getPlayerPosition()
```
**ALWAYS** wrap `pathTo()` in try/catch (IOException, InterruptedException).

## PointSelector (com.chromascape.utils.actions.PointSelector)
```java
static Point getRandomPointInColour(BufferedImage image, String colourName, int maxAttempts)
static Point getRandomPointInColour(BufferedImage image, String colourName, int maxAttempts, double tightness)
static Point getRandomPointByColourObj(BufferedImage image, ColourObj colour, int maxAttempts)
static Point getRandomPointByColourObj(BufferedImage image, ColourObj colour, int maxAttempts, double tightness)
static Point getRandomPointInImage(String templatePath, BufferedImage image, double threshold)
static Point getRandomPointInImage(String templatePath, BufferedImage image, double threshold, double tightness)
```
**All return null on failure — always null-check.**

## TemplateMatching (com.chromascape.utils.core.screen.topology.TemplateMatching)
```java
static MatchResult match(String templateImg, BufferedImage baseImg, double threshold)
```
`MatchResult`: `(Rectangle bounds, double score, boolean success, String message)`

## ColourContours (com.chromascape.utils.core.screen.topology.ColourContours)
```java
static List<ChromaObj> getChromaObjsInColour(BufferedImage image, ColourObj colourObj)
static ChromaObj getChromaObjClosestToCentre(List<ChromaObj> chromaObjs)
static boolean isPointInContour(Point point, Mat contour)
```
`ChromaObj`: `(int id, Mat contour, Rectangle boundingBox)` — call `.release()` when done.

## ColourObj (com.chromascape.utils.core.screen.colour.ColourObj)
```java
new ColourObj("name", new Scalar(H_MIN, S_MIN, V_MIN, 0), new Scalar(H_MAX, S_MAX, V_MAX, 0))
```
HSV: H:0-180, S:0-255, V:0-255. Fourth channel always 0.

## ColourInstances (com.chromascape.utils.core.screen.colour.ColourInstances)
```java
static ColourObj getByName(String name)
```

## Ocr (com.chromascape.utils.domain.ocr.Ocr)
```java
static String extractText(Rectangle zone, String font, ColourObj colour, boolean clean)
static String extractTextFromMask(Mat mask, String font, boolean clean)
```
Fonts: `"Plain 11"`, `"Plain 12"`, `"Bold 12"`, `"Quill 8"`

## MouseOver (com.chromascape.utils.actions.MouseOver)
```java
static String getText(BaseScript baseScript)
```

## Minimap (com.chromascape.utils.actions.Minimap)
```java
static int getHp(BaseScript script)       // -1 if not found
static int getPrayer(BaseScript script)
static int getRun(BaseScript script)
static int getSpec(BaseScript script)
static int getXp(BaseScript script)       // Requires permanent XP bar
```

## Idler (com.chromascape.utils.actions.Idler)
```java
static boolean waitUntilIdle(BaseScript base, int timeoutSeconds)
```

## Walk (com.chromascape.utils.actions.custom.Walk)
```java
static boolean to(BaseScript base, Point tile, String label)       // Returns false on path error
static void toOrStop(BaseScript base, Point tile, String label)    // Stops script on any failure
```

## ColourClick (com.chromascape.utils.actions.custom.ColourClick)
```java
static boolean isVisible(BaseScript base, ColourObj colour)        // Is colour object on screen?
static Point getClickPoint(BaseScript base, ColourObj colour)      // Safe click point (null if not found)
```

## Bank (com.chromascape.utils.actions.custom.Bank)
```java
static void open(BaseScript base, String colour)                   // Click highlighted bank booth
static void depositAll(BaseScript base)                            // Right-click slot 0 → Deposit-All
static void close(BaseScript base)                                 // Press Escape
```

## HumanBehavior (com.chromascape.utils.actions.custom.HumanBehavior)
```java
static boolean runPreCycleChecks(BaseScript base)   // All pre-cycle checks in one call
static long adjustDelay(long baseMin, long baseMax)  // Tempo + fatigue adjusted delay
static boolean shouldMisclick()
static boolean shouldHesitate()
static boolean shouldSlowApproach()
static void performMisclick(BaseScript script, Point intended)
static void performHesitation()
```

## Inventory (com.chromascape.utils.actions.custom.Inventory)
```java
static boolean hasItem(BaseScript base, String templatePath, double threshold)
static int countItem(BaseScript base, String templatePath, double threshold)
static int findItemSlot(BaseScript base, String templatePath, double threshold)
static boolean clickItem(BaseScript base, String templatePath, double threshold, String speed)
static boolean isFull(BaseScript base, String[] knownItems, double threshold)
```

## KeyPress (com.chromascape.utils.actions.custom.KeyPress)
```java
static void space(BaseScript base)
static void escape(BaseScript base)
static void enter(BaseScript base)
static void character(BaseScript base, char key)
```

## Logout (com.chromascape.utils.actions.custom.Logout)
```java
static void perform(BaseScript base)
```

## LevelUpDismisser (com.chromascape.utils.actions.custom.LevelUpDismisser)
```java
static boolean dismissIfPresent(BaseScript base)    // OCR chatbox, press space if level-up detected
```

## ItemDropper (com.chromascape.utils.actions.ItemDropper)
```java
static void dropAll(BaseScript baseScript)
static void dropAll(BaseScript baseScript, DropPattern pattern, int[] exclude)
// DropPattern: STANDARD (left→right), ZIGZAG (2-row vertical strip)
```

## MovingObject (com.chromascape.utils.actions.MovingObject)
```java
static boolean clickMovingObjectInColourUntilRedClick(String colour, BaseScript baseScript)
static boolean clickMovingObjectByColourObjUntilRedClick(ColourObj colour, BaseScript baseScript)
```

## ClickDistribution (com.chromascape.utils.core.input.distribution.ClickDistribution)
```java
static Point generateRandomPoint(Rectangle rect)
static Point generateRandomPoint(Rectangle rect, double tightness)
```

## ScreenManager (com.chromascape.utils.core.screen.window.ScreenManager)
```java
static BufferedImage captureWindow()
static BufferedImage captureZone(Rectangle zone)
static Rectangle getWindowBounds()
static Rectangle toClientBounds(Rectangle screenBounds)
static Point toClientCoords(Point screenPoint)
```

## DiscordNotification (com.chromascape.api.DiscordNotification)
```java
static void send(String message)
```

---

## HumanBehavior Integration

Import: `com.chromascape.utils.actions.custom.HumanBehavior`

### Top of cycle():
```java
if (HumanBehavior.runPreCycleChecks(this)) return;
```
This single call handles: tempo drift, extended breaks, short breaks, camera fidgets, idle drifts, and level-up dismissal. Returns true if the cycle should be skipped (a break was taken).

### Before clicks:
```java
String speed = HumanBehavior.shouldSlowApproach() ? "slow" : "medium";
controller().mouse().moveTo(clickLoc, speed);
if (HumanBehavior.shouldHesitate()) { HumanBehavior.performHesitation(); }
if (HumanBehavior.shouldMisclick()) { HumanBehavior.performMisclick(this, clickLoc); controller().mouse().moveTo(clickLoc, "medium"); }
controller().mouse().microJitter();
controller().mouse().leftClick();
```

### Delays:
```java
waitMillis(HumanBehavior.adjustDelay(800, 1000));
```

---

## Common Patterns

### Banking
```java
private void openBank() {
    BufferedImage gameView = controller().zones().getGameView();
    Point bankLoc = PointSelector.getRandomPointInColour(gameView, BANK_COLOUR, 15);
    if (bankLoc == null) { logger.error("Bank not found"); stop(); return; }
    String speed = HumanBehavior.shouldSlowApproach() ? "slow" : "medium";
    controller().mouse().moveTo(bankLoc, speed);
    controller().mouse().microJitter();
    controller().mouse().leftClick();
    waitMillis(HumanBehavior.adjustDelay(1200, 1800));
}

private void depositAll() {
    Rectangle firstSlot = controller().zones().getInventorySlots().get(0);
    Point slotLoc = ClickDistribution.generateRandomPoint(firstSlot);
    controller().mouse().moveTo(slotLoc, "medium");
    controller().mouse().rightClick();
    waitMillis(HumanBehavior.adjustDelay(400, 600));
    Point depositOption = new Point(slotLoc.x, slotLoc.y + 85);
    controller().mouse().moveTo(depositOption, "fast");
    controller().mouse().leftClick();
    waitMillis(HumanBehavior.adjustDelay(300, 500));
}

private void closeBank() {
    controller().keyboard().sendModifierKey(401, "esc");
    waitMillis(HumanBehavior.adjustDelay(80, 120));
    controller().keyboard().sendModifierKey(402, "esc");
    waitMillis(HumanBehavior.adjustDelay(400, 600));
}
```

### Eating
```java
private boolean shouldEat(int eatAtHp) {
    int currentHp = Minimap.getHp(this);
    return currentHp != -1 && currentHp <= eatAtHp;
}

private void eatFood() {
    for (int i = 0; i < 28; i++) {
        Rectangle slot = controller().zones().getInventorySlots().get(i);
        BufferedImage slotImg = ScreenManager.captureZone(slot);
        if (TemplateMatching.match(FOOD_IMAGE, slotImg, 0.07).success()) {
            Point clickLoc = ClickDistribution.generateRandomPoint(slot);
            controller().mouse().moveTo(clickLoc, "fast");
            controller().mouse().leftClick();
            waitMillis(HumanBehavior.adjustDelay(1600, 2000));
            return;
        }
    }
    logger.warn("No food found");
}
```

### Aggro Reset
```java
private void resetAggro() {
    logger.info("Resetting aggro timer");
    try {
        controller().walker().pathTo(new Point(COMBAT_TILE.x + 15, COMBAT_TILE.y), true);
        waitMillis(HumanBehavior.adjustDelay(2000, 3000));
        controller().walker().pathTo(COMBAT_TILE, true);
        waitMillis(HumanBehavior.adjustDelay(1000, 2000));
    } catch (IOException e) {
        logger.error("Walker error: {}", e.getMessage());
    } catch (InterruptedException e) {
        logger.error("Walker interrupted");
        stop();
    }
}
```

### Script Template
```java
package com.chromascape.scripts;

import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.*;
import com.chromascape.utils.core.input.distribution.ClickDistribution;
import com.chromascape.utils.core.screen.colour.ColourObj;
import com.chromascape.utils.core.screen.topology.*;
import com.chromascape.utils.core.screen.window.ScreenManager;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bytedeco.opencv.opencv_core.Scalar;

/**
 * [What the script does]
 *
 * <p><b>Prerequisites:</b> [skill levels, quests, items]
 * <p><b>RuneLite Setup:</b> [plugins, highlights]
 * <p><b>Inventory Layout:</b> [slot positions]
 * <p><b>Image Templates:</b> [auto-downloaded from OSRS Wiki]
 */
public class [Name]Script extends BaseScript {
    private static final Logger logger = LogManager.getLogger([Name]Script.class);

    // === Image Templates ===
    // === Colour Definitions ===
    // === Script Constants ===

    @Override
    protected void cycle() {
        // 1. Pre-cycle checks (breaks, fidgets, level-up dismissal)
        if (HumanBehavior.runPreCycleChecks(this)) return;
        // 2. State machine logic
        // 3. Idle/wait with adjusted delays
    }
}
```
