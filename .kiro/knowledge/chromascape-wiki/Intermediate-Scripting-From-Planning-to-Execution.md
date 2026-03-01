## Table of Contents
- [Preamble](#preamble)
- [Scenario](#scenario)
- [States](#states)
- [High-Level Pseudocode Plan](#high-level-pseudocode-plan)
- [Implementation Breakdown](#implementation-breakdown)
  - [Clicking Obstacles (Moving Objects)](#clicking-obstacles-moving-objects)
  - [Clicking Marks of Grace](#clicking-marks-of-grace)
  - [Waiting for XP Change (Progress Tracking)](#waiting-for-xp-to-change-state-tracking)
  - [What if the Obstacle isn't Visible...](#what-if-the-obstacle-isnt-visible)
  - [Recovery Logic (Lost State)](#recovery-logic-lost-state)
- [Putting It All Together: The Final cycle()](#putting-it-all-together-the-final-cycle)
- [Further Reading](#further-reading)
  - [Bibliography](#bibliography)

## Preamble
**In this guide you'll learn how to:**
- Mentally frame a botting activity, to think critically about how to solve a complex problem.
- Design a plan for a state machine, considering several conditions that the bot can expect.
- Optimise code to prevent duplication, by practicing "Clean Code" and the "Single Responsibility Principle".
- Create a robust script with reasonable error handling, as a result of considering each "state".

## Scenario
We are going to create an Agility script that clicks on obstacles and picks up Marks of Grace and works on several courses with minimal changes. 

We'll use a plugin called "**Rooftop Agility Improved**", this plugin will only highlight the next clickable obstacle and Marks of Grace.

When there is a Mark of Grace on the same roof as you, it will stop highlighting the next obstacle, therefore the bot will only see the Mark of Grace.

Presumably when neither is present -> the bot is lost, either by falling off or somehow clicking out of range (remember this).

## States

> [!TIP]
> Think what states the bot could be in while it runs.

#### State 1: Obstacle AND Mark of Grace Detected
- **Condition:** The Mark of Grace has spawned on the next roof.
- **Action:** The bot will click the Obstacle to cross over.
  - (Do not click the Mark of Grace yet, or the pathing will break)

#### State 2: Obstacle Only Detected
- **Condition:** Standard course progression; no Marks of Grace nearby.
- **Action:** The bot will click the Obstacle.

#### State 3: Mark of Grace Only Detected
- **Condition:** You have landed on a roof with a Mark of Grace. 
  - The plugin has intentionally hidden the next obstacle's highlight.
- **Action:** The bot will click the Mark of Grace to pick it up.

#### State 4: Nothing Detected
- **Condition:** The bot has fallen off the course, misclicked, or the plugin failed to render.
- **Action:** The bot is "lost" and will try to walk back to the course's reset/start tile.

## High-Level Pseudocode Plan

Now that we understand the environment and the states our bot needs to handle, we can create a clear, high level plan. 

Because Agility is a heavily animation-dependent skill (with varying traversal times depending on the obstacle), \
we cannot rely on static `wait()` timers. Instead, we need a dynamic **state-tracking mechanism**. 

We will use the game's XP drops to track state: every time a player successfully completes an agility obstacle, \
their Total XP increases. By reading this XP change, the script knows when an action is complete and when to look for the next obstacle. 

Here is the logical flow of our `cycle()` loop:

```
REPEAT EVERY CYCLE:
-----------------------------------------------------------------------
1. [GET STATE] 
   current_xp = get_minimap_xp()

2. [EVALUATE ENVIRONMENT]
   IF (Obstacle is NOT on screen):
       IF (Mark of Grace is on screen):
           Action: Pick up Mark of Grace
           Wait: Until Obstacle reappears
       ELSE:
           Action: Walk to Course Start
       EXIT CYCLE (Start over)

3. [EXECUTE MAIN ACTION]
   Action: Click Obstacle (Repeat until Red Click)
   
4. [VERIFY PROGRESS]
   Wait: Until (current_xp > old_xp) OR (Timeout reached)

5. [HUMANIZATION]
   Action: 1% chance to sleep for 2-5 minutes
-----------------------------------------------------------------------
```

## Implementation Breakdown

### Clicking Obstacles (Moving Objects)
Since obstacles can be moving when we attempt to click them, it is possible the bot will misclick. \
We will need to repeatedly attempt to click the obstacle until it triggers a red interaction cross (x). \
Red clicks happen when you successfully click an interactable object meaning you will do a special action like opening a UI or teleporting. \
Yellow clicks occur when you walk or click a non-interactable game object.
```java
    // Interact with the detected obstacle
    // Clicking continuously until the red cross (x) animation is detected
    if (!MovingObject.clickMovingObjectByColourObjUntilRedClick(OBSTACLE_COLOUR, this)) {
      logger.error("Bot wasn't able to click the moving object within standard attempts.");
      stop();
      DiscordNotification.send(
          "Bot wasn't able to click the moving object within standard attempts.");
    }
```
You can utilise the recent `MovingObject` actions utility to achieve this. \
The above snippet shows how to treat an error:
- If the bot continued rather than stopping, it would likely click hundreds of times without being able to progress.
- Logging errors to the console provides traceability, allowing you to see why it failed rather than the fact that it just failed.
- Using the `DiscordNotification` class, you can send yourself a notification immediately to check out why the bot failed.

> [!TIP]
> You should try recovering the situation upon exceptions like this. Call `stop()` to stop the script if recovering the situation fails.


### Clicking Marks of Grace
We can separate the ACT of clicking the Mark of Grace and the DECISION of when to click it. \
Lets worry about how to click the Mark of Grace first. \
Marks of Grace are ground items. The plugin highlights the whole tile. \
If we pick a random point from the tile to click -> the bot may click just outside of the Mark of Grace item whilst still clicking the tile. \
We solve this by squeezing the click distribution towards the centre of the tile. This is achieved with the `tightness` parameter.
```java
  private boolean clickMarkOfGraceIfPresent() {
    BufferedImage gameView = controller().zones().getGameView();
    // You'll see that there's an extra parameter on the point selector
    // This is "tightness", how closely grouped the click should be
    // 15.0 or more works best for ground items, best to look from a higher camera angle
    Point clickLocation = PointSelector.getRandomPointByColourObj(gameView, MARK_COLOUR, 15, 15.0);

    if (clickLocation != null) {
      controller().mouse().moveTo(clickLocation, "medium");
      controller().mouse().leftClick();
      return true;
    }
    return false;
  }
```
This is almost identical to clicking a normal `ChromaObj`, just with that added `tightness` parameter overload.

### Waiting for XP to Change (State Tracking)
You can extract the integer value of your Total XP from the screen using ChromaScape's Optical Character Recognition (OCR) functionality. \
In this specific case you can call `Minimap.getXp(this);` to get it without any further setup.

Because agility obstacles have drastically different animation lengths (a zip-line takes much longer than a small jump), \
we cannot use a fixed `waitMillis()` timer. Instead, we capture the Total XP before clicking the obstacle, \
and then hold the script in a waiting loop until that XP value increments.

We must account for failure. What if the game lags? If the OCR misreads? Or the character gets stuck? \
If we use a blind `while(XP hasn't changed)` loop, the bot could hang until it logs out. To prevent this, we introduce a timeout limit.

```java
  @Override
  protected void cycle() {
    int previousXp = Minimap.getXp(this);

    DoAction();

    waitUntilXpChange(previousXp);
  }

  private void waitUntilXpChange(int previousXp) {
    LocalDateTime endTime = LocalDateTime.now().plusSeconds(TIMEOUT_XP_CHANGE);
    // Ensure we do not hang if the initial OCR read failed and returned an empty string
    while (previousXp == Minimap.getXp(this) && LocalDateTime.now().isBefore(endTime)) {
      waitMillis(300);
    }
  }
```
### What if the Obstacle isn't visible...
With Marks of Grace we talked about splitting the Action from the Decision. This should also be true for Obstacles. \
Create a function that simply checks if the obstacle is visible and returns a boolean based on the outcome.
```java
  private boolean isObstacleVisible() {
    BufferedImage gameView = controller().zones().getGameView();
    return !ColourContours.getChromaObjsInColour(gameView, OBSTACLE_COLOUR).isEmpty();
  }
```

This will help us navigate the events we talked about at the start.

Similarly, lets create a method that makes the bot wait until an obstacle is visible.\
This will help when we click a Mark of Grace and need to wait until it's picked up.
```java
private void waitForObstacleToAppear() {
    LocalDateTime endTime = LocalDateTime.now().plusSeconds(TIMEOUT_OBSTACLE_APPEAR);
    while (!isObstacleVisible() && LocalDateTime.now().isBefore(endTime)) {
      waitMillis(300);
    }
  }
```
The implementation closely mirrors `waitUntilXpChange()`.

### Recovery Logic (Lost State)
Remember states 3 and 4, when the bot saw nothing and when it only saw a Mark of Grace? \
Firstly, we need to ensure that there aren't any obstacles visible, after which we can branch into two possibilities.
1. If there is a Mark of Grace & no obstacle: we are on the same rooftop as the Mark and should pick it up.
2. If nothing is visible: we are lost and need to walk to the reset tile.
> After everything, we will return to the start of `cycle()` to reset everything as a clean slate rather than trying to click an obstacle immediately.

> [!TIP]
> The reason we're checking all the edge cases before we click the obstacle is so we can **"Fail fast"** and program **"Defensively"**.


```java
  @Override
  protected void cycle() {
    // code above...

    // No obstacle?
    if (!isObstacleVisible()) {
      // Click Mark of Grace if it's visible
      // If not, try walking back to the reset tile
      if (clickMarkOfGraceIfPresent()) {
        waitForObstacleToAppear();
      } else {
        recoverToResetTile();
      }
      return;
    }

    // rest of cycle...
  }
  
  /**
   * Manages the scenario when nothing is visible. Firstly, confirms that it's really lost, if so ->
   * uses the walker to path back to the reset tile. Finally, waits for the player's animation to
   * settle after reaching the true tile.
   */
  private void recoverToResetTile() {
    // Double check we are actually lost to protect against lag or rendering delays
    waitRandomMillis(600, 800);

    if (!isObstacleVisible()) {

      int attempts = 0;
      int allowedAttempts = 5;

      while (attempts < allowedAttempts) {
        try {
          logger.info("We are lost. Walking to reset tile.");
          controller().walker().pathTo(RESET_TILE, true);
          // wait for camera to stabilise and walking animation to finish at true tile.
          waitRandomMillis(4000, 6000);
          break;

        } catch (IOException e) {
          // This exception refers to Timeout or transport error
          logger.error("Walker error {}", e.getMessage());
          attempts++;

        } catch (InterruptedException e) {
          // This error means that the thread was interrupted while calling Dax
          DiscordNotification.send("Walker thread interrupted, catastrophic failure.");
          logger.error("Walker thread interrupted, catastrophic failure.");
          stop();
        }
      }
    }
  }
```

## Putting It All Together: The Final cycle()
This is the final `cycle()` subroutine, which almost mirrors the pseudocode we wrote earlier.
You may also see the full [DemoAgilityScript](https://github.com/StaticSweep/ChromaScape/blob/main/src/main/java/com/chromascape/scripts/DemoAgilityScript.java).
```java
  @Override
  protected void cycle() {
    // Log the current XP before clicking obstacle for comparison later
    // The idea is to click the obstacle then wait for XP change then loop
    int previousXp = Minimap.getXp(this);

    // Make sure it's read properly
    if (previousXp == -1) {
      stop();
      DiscordNotification.send("Xp could not be read.");
    }

    // Check the state of the course
    if (!isObstacleVisible()) {
      if (clickMarkOfGraceIfPresent()) {
        waitForObstacleToAppear();
      } else {
        recoverToResetTile();
      }
      return;
    }

    // Interact with the detected obstacle
    // Clicking continuously until the Red X animation is detected
    if (!MovingObject.clickMovingObjectByColourObjUntilRedClick(OBSTACLE_COLOUR, this)) {
      logger.error("Bot wasn't able to click the moving object within standard attempts.");
      stop();
      DiscordNotification.send(
          "Bot wasn't able to click the moving object within standard attempts.");
    }


    // Wait for the action to complete via XP update
    waitUntilXpChange(previousXp);

    // Humanizing sleep to mimic natural player behavior
    // And to prevent overloading moving object logic
    waitRandomMillis(650, 800);

    // 1% chance to take a break between 2 and 5 minutes after clicking an obstacle
    if (random.nextInt(100) < 1) {
      logger.info("Taking a break...");
      waitRandomMillis(120000, 300000);
    }
  }
```

## Further Reading
One should strive to design components in the UNIX philosophy. As Doug McIlroy said “Make each program do one thing well.” (Harvard.edu, 2024). For example, tightly coupling the detection of an obstacle to the action of clicking it would restrict the developer from adding further logic without creating mass code duplication or a god object. Adhering to single responsibility principle, which is a core aspect of clean code (Martin, 2008) would allow the developer to create scalable functions that would suit a behaviour tree and or decision model (the `cycle()`). A developer should apply object oriented principles in the spirit of the CUPID principle of composable (CUPID - for joyful code, 2026) to make the code more semantic, to be “intention revealing"; reducing cognitive load in a situation where scope can increase exponentially depending on the environment experienced by the deterministic finite state machine. Whilst considering the bot as a whole can give someone a good big picture, as Torvalds (2006) noted: “Bad programmers worry about the code. Good programmers worry about data structures and their relationships.” Therefore, one must focus on each of the state pipelines (pipelines being another core UNIX concept).

### Bibliography
_CUPID - for joyful code. (2026). CUPID Properties. [online] Available at: https://cupid.dev/properties/ [Accessed 19 Feb. 2026]._

_Martin, R.C., 2008. Clean code: a handbook of agile software craftsmanship. Upper Saddle River, NJ: Prentice Hall._

_Harvard.edu. (2024). Basics of the Unix Philosophy. [online] Available at: https://cscie2x.dce.harvard.edu/hw/ch01s06.html [Accessed 19 Feb. 2026]._

_Torvalds, L. (2006). Re: Licensing and the library version of git. [online] Lwn.net. Available at: https://lwn.net/Articles/193245/ [Accessed 21 Feb. 2026]_