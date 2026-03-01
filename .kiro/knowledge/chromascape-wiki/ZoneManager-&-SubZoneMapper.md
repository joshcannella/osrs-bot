The `ZoneManager` is a **domain-level utility**, meaning it combines multiple other utilities to produce a higher level, feature specific abstraction.

Its purpose is to **dynamically map out key UI zones**, enabling more accurate and efficient detection of colour-based objects and image-based sprites on the game screen.

---

## How it works

1. **Initial Zone Detection (Template Matching)**  
   The `ZoneManager` uses **template matching** to locate core UI regions:
   - **Control panel** (inventory, tabs, etc.)
   - **Mini-map area** (orbs, compass, map)
   - **Chatbox**
   - **Game view** (calculated as the remaining screen space after subtracting the above)

2. **Zone Expansion (SubZoneMapper)**  
   Once the main regions are identified, `ZoneManager` uses the helper class `SubZoneMapper` to map additional sub-zones within each. These are derived using **hardcoded offsets** relative to the parent region.

3. **Final Output**  
   The result is a `Map<String, Rectangle>`:
   - The `String` key is a **semantic name**, e.g., `"hpText"`.
   - The `Rectangle` represents an **exact screen region**, e.g., `new Rectangle(zone.x + 4, zone.y + 55, 20, 13)`.

---

## Notable Outliers

```java
controller().zones().getGameView();
```
Returns a **cropped `BufferedImage`** of the game view region. This is not always a clean rectangle and therefore the work is done on behalf of the user.

```java
controller().zones().getInventorySlots().get(27);
```
Returns a **`List<Rectangle>`** representing each inventory slot, indexed 0–27 from **left to right**, then **top to bottom**.

---

## Usage Instructions

Access all mapped zones via `ZoneManager`'s public getters using their associated string keys.

> **Zone keys such as "hpText" are defined in `SubZoneMapper`.**

Because `ZoneManager` is **stateful** (e.g., depends on fixed vs resizable client), you must access it through the controller.

### Examples

```java
Rectangle hp = controller().zones().getCtrlPanel().get("hpText");
Rectangle runOrb = controller().zones().getMinimap().get("runOrb");
Rectangle chatbox = controller().zones().getChatTabs().get("chat");
Rectangle invSlot5 = controller().zones().getInventorySlots().get(5);

BufferedImage gameView = controller().zones().getGameView();
```

**Taking a screenshot of a zone**
```java
BufferedImage screenshot = ScreenManager.captureZone(invSlot5)
```