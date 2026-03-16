package com.scriptgen.scripts;

import com.chromascape.api.DiscordNotification;
import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.Minimap;
import com.chromascape.utils.actions.MovingObject;
import com.chromascape.utils.actions.Idler;
import com.chromascape.utils.core.input.distribution.ClickDistribution;
import com.chromascape.utils.core.screen.colour.ColourObj;
import com.chromascape.utils.core.screen.topology.ChromaObj;
import com.chromascape.utils.core.screen.topology.ColourContours;
import com.scriptgen.behavior.HumanBehavior;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bytedeco.opencv.opencv_core.Scalar;

/**
 * Kills chickens at the Lumbridge chicken coop and loots feathers. Rotates attack styles
 * (Strength → Attack → Defence) based on levels gained.
 *
 * <p><b>RuneLite Setup:</b>
 * <ul>
 *   <li>NPC Indicators — highlight "Chicken" in cyan (HSV ~90, 254-255, 254-255)</li>
 *   <li>Ground Items — highlight "Feather" in purple (HSV ~140, 237-255, 205-255)</li>
 *   <li>XP bar set to permanent (required for XP-based kill detection)</li>
 *   <li>Windows Display Scaling: 100%</li>
 *   <li>RuneScape UI: "Fixed - Classic"</li>
 *   <li>Display Brightness: middle (50%)</li>
 *   <li>ChromaScape RuneLite Profile: activated</li>
 * </ul>
 */
public class ChickenKillerScript extends BaseScript {

  private static final Logger logger = LogManager.getLogger(ChickenKillerScript.class);

  // === Colour Definitions ===
  private static final ColourObj CHICKEN_COLOUR =
      new ColourObj("cyan", new Scalar(90, 254, 254, 0), new Scalar(91, 255, 255, 0));
  private static final ColourObj LOOT_COLOUR =
      new ColourObj("purple", new Scalar(139, 200, 200, 0), new Scalar(141, 255, 255, 0));

  // === Walker ===
  private static final Point COOP_CENTER = new Point(3235, 3295);

  // === Timeouts ===
  private static final int KILL_TIMEOUT_SECONDS = 15;
  private static final int CHICKEN_XP = 12; // 3 HP × 4 XP per damage
  private static final int MAX_COMBAT_FAILURES = 10;
  private static final int MAX_LOOT_ATTEMPTS = 2;
  private int combatFailures = 0;

  // === Attack Style Rotation ===
  private static final int LEVELS_PER_ROTATION_STR = 2;
  private static final int LEVELS_PER_ROTATION_ATT = 1;
  private static final int LEVELS_PER_ROTATION_DEF = 1;

  private enum AttackStyle { STRENGTH, ATTACK, DEFENCE }
  private AttackStyle currentStyle = AttackStyle.STRENGTH;
  private int levelsGainedThisRotation = 0;

  @Override
  protected void cycle() {
    HumanBehavior.updateTempoDrift();
    if (HumanBehavior.shouldTakeExtendedBreak()) {
      HumanBehavior.performBreak(this, true);
      return;
    }
    if (HumanBehavior.shouldTakeBreak()) {
      HumanBehavior.performBreak(this, false);
      return;
    }
    if (HumanBehavior.shouldFidgetCamera()) {
      HumanBehavior.performCameraFidget(this);
    }
    if (HumanBehavior.shouldIdleDrift()) {
      HumanBehavior.performIdleDrift(this);
    }

    dismissLevelUp();
    fight();
  }

  private void fight() {
    if (!isColourVisible(CHICKEN_COLOUR)) {
      logger.warn("No chicken found, failure {}/{}", combatFailures + 1, MAX_COMBAT_FAILURES);
      combatFailures++;
      if (combatFailures >= MAX_COMBAT_FAILURES) {
        logger.error("Failed to find chickens {} times, logging out.", MAX_COMBAT_FAILURES);
        DiscordNotification.send("Chicken Killer: can't find chickens, logging out.");
        stop();
        return;
      }
      recoverToCoop();
      return;
    }

    int previousXp;
    try {
      previousXp = Minimap.getXp(this);
    } catch (Exception e) {
      logger.warn("Could not read XP, retrying next cycle");
      return;
    }

    if (!MovingObject.clickMovingObjectByColourObjUntilRedClick(CHICKEN_COLOUR, this)) {
      logger.warn("Failed to red-click chicken");
      combatFailures++;
      return;
    }

    combatFailures = 0;
    logger.info("Attacked chicken, waiting for kill...");

    LocalDateTime deadline = LocalDateTime.now().plusSeconds(KILL_TIMEOUT_SECONDS);
    while (LocalDateTime.now().isBefore(deadline)) {
      try {
        int currentXp = Minimap.getXp(this);
        int delta = currentXp - previousXp;
        if (delta >= CHICKEN_XP && delta < 100) {
          logger.info("Kill confirmed via XP (+{})", delta);
          waitMillis(HumanBehavior.adjustDelay(600, 900));
          lootFeathers();
          checkStyleRotation();
          return;
        }
      } catch (Exception e) {
        // OCR misread — keep polling
      }
      waitMillis(300);
    }

    logger.info("Kill timeout — retrying");
  }

  /**
   * Attempts to loot feathers after a kill. Clicks loot colour up to MAX_LOOT_ATTEMPTS times,
   * verifying feather pickup via inventory template match. Bails quickly if nothing is picked up.
   */
  private void lootFeathers() {
    for (int attempt = 0; attempt < MAX_LOOT_ATTEMPTS; attempt++) {
      if (!isColourVisible(LOOT_COLOUR)) {
        return; // nothing visible, done
      }

      Point lootLoc = findGroundItemByColour(LOOT_COLOUR);
      if (lootLoc == null) {
        return;
      }

      controller().mouse().moveTo(lootLoc, "medium");
      controller().mouse().leftClick();

      // Wait for player to walk to item and pick it up
      Idler.waitUntilIdle(this, 10);

      // If loot colour is gone from ground, pickup succeeded
      if (!isColourVisible(LOOT_COLOUR)) {
        logger.info("Feathers looted.");
        return;
      }
    }

    logger.info("Loot attempts exhausted, moving on.");
  }

  // === Colour Utilities ===

  private boolean isColourVisible(ColourObj colour) {
    BufferedImage gameView = controller().zones().getGameView();
    List<ChromaObj> objs = ColourContours.getChromaObjsInColour(gameView, colour);
    boolean found = !objs.isEmpty();
    for (ChromaObj obj : objs) {
      obj.release();
    }
    return found;
  }

  private Point findGroundItemByColour(ColourObj colour) {
    BufferedImage gameView = controller().zones().getGameView();
    List<ChromaObj> objs = ColourContours.getChromaObjsInColour(gameView, colour);
    if (objs.isEmpty()) {
      return null;
    }
    try {
      ChromaObj smallest = objs.get(0);
      for (ChromaObj obj : objs) {
        if (obj.boundingBox().width * obj.boundingBox().height
            < smallest.boundingBox().width * smallest.boundingBox().height) {
          smallest = obj;
        }
      }
      Rectangle box = smallest.boundingBox();

      // If the contour is too large, it's likely merged tiles — pick a random quadrant
      if (box.width > 60 || box.height > 60) {
        int halfW = box.width / 2;
        int halfH = box.height / 2;
        int qx = ThreadLocalRandom.current().nextBoolean() ? box.x : box.x + halfW;
        int qy = ThreadLocalRandom.current().nextBoolean() ? box.y : box.y + halfH;
        box = new Rectangle(qx, qy, halfW, halfH);
      }

      return ClickDistribution.generateRandomPoint(box, 20.0);
    } catch (Exception e) {
      logger.warn("Failed to generate loot point: {}", e.getMessage());
      return null;
    } finally {
      for (ChromaObj obj : objs) {
        obj.release();
      }
    }
  }

  // === Recovery ===

  private void recoverToCoop() {
    try {
      logger.info("Walking back to chicken coop");
      controller().walker().pathTo(COOP_CENTER, false);
      waitMillis(HumanBehavior.adjustDelay(3000, 5000));
    } catch (IOException e) {
      logger.error("Walker error: {}", e.getMessage());
    } catch (InterruptedException e) {
      logger.error("Walker interrupted");
      stop();
    }
  }

  // === Attack Style Rotation ===

  private void checkStyleRotation() {
    int required = getRequiredLevels(currentStyle);
    if (levelsGainedThisRotation >= required) {
      rotateStyle();
    }
  }

  private int getRequiredLevels(AttackStyle style) {
    return switch (style) {
      case STRENGTH -> LEVELS_PER_ROTATION_STR;
      case ATTACK -> LEVELS_PER_ROTATION_ATT;
      case DEFENCE -> LEVELS_PER_ROTATION_DEF;
    };
  }

  private void rotateStyle() {
    AttackStyle previous = currentStyle;
    currentStyle = switch (currentStyle) {
      case STRENGTH -> AttackStyle.ATTACK;
      case ATTACK -> AttackStyle.DEFENCE;
      case DEFENCE -> AttackStyle.STRENGTH;
    };
    levelsGainedThisRotation = 0;
    logger.info("Rotating attack style: {} → {}", previous, currentStyle);
    switchAttackStyle(currentStyle);
  }

  private void switchAttackStyle(AttackStyle style) {
    Rectangle combatTab = controller().zones().getCtrlPanel().get("combatTab");
    controller().mouse().moveTo(ClickDistribution.generateRandomPoint(combatTab), "medium");
    controller().mouse().leftClick();
    waitMillis(HumanBehavior.adjustDelay(400, 600));

    Rectangle panel = controller().zones().getCtrlPanel().get("inventoryPanel");
    Rectangle styleBox = switch (style) {
      case ATTACK -> new Rectangle(panel.x, panel.y + 10, panel.width / 2 - 5, 45);
      case STRENGTH -> new Rectangle(panel.x + panel.width / 2 + 5, panel.y + 10,
          panel.width / 2 - 5, 45);
      case DEFENCE -> new Rectangle(panel.x + panel.width / 2 + 5, panel.y + 65,
          panel.width / 2 - 5, 45);
    };

    controller().mouse().moveTo(ClickDistribution.generateRandomPoint(styleBox), "medium");
    controller().mouse().leftClick();
    waitMillis(HumanBehavior.adjustDelay(300, 500));

    Rectangle invTab = controller().zones().getCtrlPanel().get("inventoryTab");
    controller().mouse().moveTo(ClickDistribution.generateRandomPoint(invTab), "medium");
    controller().mouse().leftClick();
    waitMillis(HumanBehavior.adjustDelay(200, 400));

    logger.info("Switched to {} style", style);
  }

  // === Level-Up Detection ===

  private void dismissLevelUp() {
    controller().keyboard().sendModifierKey(401, "space");
    waitMillis(HumanBehavior.adjustDelay(80, 120));
    controller().keyboard().sendModifierKey(402, "space");
    waitMillis(HumanBehavior.adjustDelay(100, 200));
  }

  public void onLevelUp() {
    levelsGainedThisRotation++;
    logger.info("Level gained! ({}/{} for {} rotation)", levelsGainedThisRotation,
        getRequiredLevels(currentStyle), currentStyle);
  }
}
