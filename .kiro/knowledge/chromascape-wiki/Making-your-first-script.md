## Table of Contents
- [Preamble](#preamble)
- [Part 1: Template](#part-1-template)
  - [1. File placement](#1-file-placement)
  - [2. Creating the class](#2-creating-the-class)
  - [3. The Logger](#3-the-logger)
  - [4. Bot logic](#4-bot-logic)
- [Part 2: Running the script](#part-2-running-the-script)
  - [1. The entry point](#1-the-entry-point)
  - [2. Accessing the UI](#2-accessing-the-ui)
- [Part 3: Clicking an image](#part-3-clicking-an-image)
  - [1. Accessing a saved image](#1-accessing-a-saved-image)
  - [2. Creating the function](#2-creating-the-function)
- [Part 4: Clicking a colour](#part-4-clicking-a-colour)
- [Part 5: Keypresses](#part-5-keypresses)
- [Part 6: Clicking a Rectangle](#part-6-clicking-a-rectangle)
- [The finished product](#the-finished-product)
## Preamble
For this we'll use the example demo script `DemoWineScript`.

Every script in ChromaScape extends BaseScript and implements a looping method called cycle(). The web UI automatically detects and lists any classes you create in the scripts package.

Feel free to look at the complete `DemoWineScript` in the scripts folder if you get stuck.

> [!TIP]
>If you hover over a function/class in IntelliJ, it shows you its documentation and usage guidelines (JavaDocs). Take advantage of this if you feel stuck. Our developers have gone to great lengths to ensure that code is well documented.
> Make sure you've completed the [Requirements](https://github.com/StaticSweep/ChromaScape/wiki/Requirements) section before running your scripts.

# Part 1: Template

### 1. File placement
Navigate to:
```
src/main/java/com/chromascape/scripts
```
This is where all of your scripts should live. The web UI scans this directory to populate the script selection side bar.

### 2. Creating the class
Create a public class and have it extend the BaseScript. This script should be named the activity you want to bot.
```java
public class DemoWineScript extends BaseScript { 
  //Everything goes inside this from now on
}
```

### 3. The Logger
Create a logger as shown below to type something out to the UI/terminal:
```java
  private final Logger logger = LogManager.getLogger(DemoWineScript.class);
```

### 4. Bot logic
Override the cycle() routine.

```java
  private final Logger logger = LogManager.getLogger(DemoWineScript.class);
  
  @Override
  protected void cycle() {
    logger.info("Hello World!");
    waitRandomMillis(80, 100);
  }
```

All bot logic should go inside `cycle()`. This method runs repeatedly until stop()` is called.

# Part 2 Running the script
Now that you have a script file ready, we should learn how to access it and run it.

### 1. The entry point
Run:
```
src/main/java/com/chromascape/web/ChromaScapeApplication.java
```

### 2. Accessing the UI
Open a browser and go to:
```
http://localhost:8080/
```
Once the application loads (may take a minute), you should be greeted with the web UI.
This is where you'll click a script on the left hand side then click start.

# Part 3 Clicking an image
Let's walk though the idea of clicking an image somewhere on screen.
We can also make it modular as this is something often repeated.

### 1. Accessing a saved image
You should only ever need to store the path of a saved image, not load the file itself.

To store the image path as a class variable use the following structure:
```java
private static final String imageName = "/images/user/your_image.png";
```
Your image should be stored in:
```
src/main/resources/images/user
```
Because it's loaded as a resource.

You can download sprite/item images from the official OSRS wiki: https://oldschool.runescape.wiki/
> [!TIP]
> **For stacked/banked items (that have numbers over it) you need to crop out the top 10 pixels.**

### 2. Creating the function
Let's create a function that combines a few utilities to click at a random point within an image.

```java
  /**
   * Searches for the provided image template within the current game view, then clicks a random
   * point within the detected bounding box if the match exceeds the defined threshold.
   *
   * @param imagePath the BufferedImage template to locate and click within the game view
   * @param speed the speed that the mouse moves to click the image
   * @param threshold the openCV threshold to decide if a match exists
   */
  private void clickImage(String imagePath, String speed, double threshold) {
    BufferedImage gameView = controller().zones().getGameView();
    Point clickLocation = PointSelector.getRandomPointInImage(imagePath, gameView, threshold);

    if (clickLocation == null) {
      logger.error("clickImage click location is null");
      stop();
    }

    controller().mouse().moveTo(clickLocation, speed);

    controller().mouse().leftClick();
    logger.info("Clicked on image at {}", clickLocation);
  }
```
- This example shows you how to get zones from the ZoneManager (`controller().zones()`).
- The gameView specifically, is stored as a `BufferedImage` because of its complex shape. Other zones are automatically rectangles.
- If a zone is a `Rectangle` you will need to call `BufferedImage img = ScreenManager.captureZone(Rectangle zone);` to save it as a `BufferedImage`.
- The Threshold is used when the program looks for an image on the screen, a lower threshold means that the match needs to be more accurate. A threshold of `0.05` is often preferred, with the maximum being `0.15`
- You can see how the stateful utility `mouse()` must be accessed through the controller: `controller().mouse().leftClick();`

# Part 4 Clicking a colour
In this example we will assume there is a purple object on screen that we must click.

**EXAMPLES: Highlighting a bank object or NPC purple, using RuneLite's highlight feature (shift + right click)**
>[!TIP]
> Learn more about how to use the [Colour Picker utility](https://github.com/StaticSweep/ChromaScape/wiki/Colour-picker), to be able to save colours for the framework to see.

```java
  /**
   * Attempts to locate and click the purple bank object within the game view. It searches for
   * purple contours, then clicks a randomly distributed point inside the contour bounding box,
   * retrying up to a maximum number of attempts. Logs failures and stops the script if unable to
   * click successfully.
   */
  private void clickBank() {
    // Use the PointSelector to get a random point within the nearest object of a specific colour within the gameView
    Point clickLocation =
        PointSelector.getRandomPointInColour(
            controller().zones().getGameView(), "Cyan", MAX_ATTEMPTS);

    // Check if the Point was found correctly
    if (clickLocation == null) {
      logger.error("clickBank click location is null");
      stop();
    }

    // Click the point
    controller().mouse().moveTo(clickLocation, "medium");
    controller().mouse().leftClick();

    // Use the logger to tell the user
    logger.info("Clicked on purple bank object at {}", clickLocation);
  }
```

# Part 5 Keypresses
More information on specific event ID's can be found in the `VirtualKeyboardUtils` class.

```java
  /**
   * Simulates pressing the Escape key by sending the key press and release events to the client
   * keyboard controller.
   */
  private void pressEscape() {
    controller().keyboard().sendModifierKey(401, "esc");
    waitRandomMillis(80, 100);
    controller().keyboard().sendModifierKey(402, "esc");
  }
```

# Part 6 Clicking a `Rectangle`
- Most zones are saved as rectangles.
- Rectangle zones are generated dynamically created by the project. e.g. **inventory slots**, **chatbox**, **control panel**, **minimap orbs**.
- You can access the zones/rectangles through the controller as shown below.
- Learn more about accessing zones in the [ZoneManager & SubZoneMapper](./ZoneManager-&-SubZoneMapper) wiki page.

Let's use inventory slots as an example.

```java
  /**
   * Clicks a random point within the bounding box of a given inventory slot.
   *
   * @param slot the index of the inventory slot to click (0-27)
   * @param speed the speed that the mouse moves to click the image
   */
  private void clickInvSlot(int slot, String speed) {
    Rectangle boundingBox = controller().zones().getInventorySlots().get(slot);
    if (boundingBox == null || boundingBox.isEmpty()) {
      logger.info("Inventory slot {} not found.", slot);
      stop();
      return;
    }

    Point clickLocation = ClickDistribution.generateRandomPoint(boundingBox);

    if (clickLocation == null) {
      logger.error("clickInventSlot click location is null");
      stop();
    }

    controller().mouse().moveTo(clickLocation, speed);

    controller().mouse().leftClick();
    logger.info("Clicked inventory slot {} at {}", slot, clickLocation);
  }
```
This function clicks any inventory slot you want, given the number of the slot and the speed of the mouse.
Creating small and specific bits of code like this will allow you to modularise your bot and increase code reuse.

# The finished product: 
[DemoWineScript](https://github.com/StaticSweep/ChromaScape/blob/main/src/main/java/com/chromascape/scripts/DemoWineScript.java)