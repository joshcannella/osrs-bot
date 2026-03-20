package com.chromascape.scripts;

import com.chromascape.api.DiscordNotification;
import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.Minimap;
import com.chromascape.utils.actions.MovingObject;
import com.chromascape.utils.actions.custom.ColourClick;
import com.chromascape.utils.actions.custom.HumanBehavior;
import com.chromascape.utils.actions.custom.Inventory;
import com.chromascape.utils.actions.custom.Walk;
import com.chromascape.utils.core.screen.colour.ColourObj;
import com.chromascape.utils.domain.ocr.Ocr;
import java.awt.Point;
import java.awt.Rectangle;
import java.time.LocalDateTime;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bytedeco.opencv.opencv_core.Scalar;

/**
 * Kills goblins east of Lumbridge castle. Eats food when HP is low and recovers from death by
 * walking back from the Lumbridge respawn point.
 *
 * <p><b>Prerequisites:</b> Any melee weapon equipped, food in inventory.
 * <p><b>RuneLite Setup:</b> NPC Indicators — highlight Goblin in cyan. Ground Items — highlight
 * loot in purple (optional).
 * <p><b>Image Templates:</b> Trout.png (or whichever food you bring)
 */
public class LumbridgeGoblinScript extends BaseScript {

  private static final Logger logger = LogManager.getLogger(LumbridgeGoblinScript.class);

  // === Colour Definitions ===
  // Highlight goblins cyan via RuneLite NPC Indicators
  private static final ColourObj GOBLIN_COLOUR =
      new ColourObj("cyan", new Scalar(90, 254, 254, 0), new Scalar(91, 255, 255, 0));

  // === Food ===
  private static final String FOOD_IMAGE = "/images/user/Shrimps.png";
  private static final double FOOD_THRESHOLD = 0.07;
  private static final int EAT_AT_HP = 5;

  // === Chat ===
  // Red text in OSRS chat (HSV: hue ~0, high sat, high val)
  private static final ColourObj CHAT_RED =
      new ColourObj("red", new Scalar(0, 200, 200, 0), new Scalar(5, 255, 255, 0));
  // Black text for "I'm already under attack." / "Someone else is fighting that."
  private static final ColourObj CHAT_BLACK =
      new ColourObj("black", new Scalar(0, 0, 0, 0), new Scalar(0, 0, 0, 0));

  // === Combat ===
  private static final int GOBLIN_XP = 20; // 5 HP × 4 XP per damage
  private static final int KILL_TIMEOUT_SECONDS = 20;
  private static final int ENGAGE_TIMEOUT_MS = 2000;
  private static final int MAX_ENGAGE_ATTEMPTS = 3;

  // === Tiles ===
  // Goblin area east of Lumbridge castle, across the bridge
  private static final Point GOBLIN_AREA = new Point(3259, 3228);
  // Lumbridge respawn (death spawn point)
  private static final Point LUMBRIDGE_SPAWN = new Point(3222, 3218);

  // === Stuck Detection ===
  private static final int MAX_STUCK_CYCLES = 10;
  private int stuckCounter = 0;
  private boolean inCombat = false;

  @Override
  protected void cycle() {
    if (HumanBehavior.runPreCycleChecks(this)) return;

    // Check if we just left combat via chat message
    if (inCombat && isOutOfCombatChat()) {
      logger.info("Combat ended (chat: no longer in combat)");
      inCombat = false;
    }

    // Still in combat — wait for kill to finish
    if (inCombat) {
      waitMillis(300);
      return;
    }

    // Eat if HP is low
    if (shouldEat()) {
      if (!eatFood()) {
        logger.warn("Out of food, logging out.");
        DiscordNotification.send("Goblin Killer: out of food, logging out.");
        stop();
        return;
      }
      return;
    }

    // Check if goblins are visible — if not, we may have died or wandered off
    if (!ColourClick.isVisible(this, GOBLIN_COLOUR)) {
      stuckCounter++;
      logger.warn("No goblin found ({}/{})", stuckCounter, MAX_STUCK_CYCLES);
      if (stuckCounter >= MAX_STUCK_CYCLES) {
        logger.error("Stuck for {} cycles, logging out.", MAX_STUCK_CYCLES);
        DiscordNotification.send("Goblin Killer: stuck, logging out.");
        stop();
        return;
      }
      recoverToGoblins();
      return;
    }

    // Snapshot XP before engaging
    int previousXp;
    try {
      previousXp = Minimap.getXp(this);
    } catch (Exception e) {
      logger.warn("XP read failed, skipping cycle");
      return;
    }

    // Try to engage a goblin
    for (int attempt = 0; attempt < MAX_ENGAGE_ATTEMPTS; attempt++) {
      if (!MovingObject.clickMovingObjectByColourObjUntilRedClick(GOBLIN_COLOUR, this)) {
        logger.warn("Failed to red-click goblin (attempt {})", attempt + 1);
        continue;
      }
      if (waitForFirstHit(previousXp)) {
        stuckCounter = 0;
        inCombat = true;
        waitForKill(previousXp);
        return;
      }
      // Check if we're already fighting something
      String blackMsg = getLatestBlackChat();
      if (blackMsg.contains("alreadyunder")) {
        logger.info("Already in combat, waiting for kill");
        stuckCounter = 0;
        inCombat = true;
        waitForKill(previousXp);
        return;
      }
      if (blackMsg.contains("someoneelse")) {
        logger.info("Goblin taken by another player, trying next");
        continue;
      }
      logger.warn("Goblin unreachable (attempt {}), trying another", attempt + 1);
    }

    stuckCounter++;
  }

  // === Eating ===

  private boolean shouldEat() {
    try {
      int hp = Minimap.getHp(this);
      return hp != -1 && hp <= EAT_AT_HP;
    } catch (Exception e) {
      return false;
    }
  }

  private boolean eatFood() {
    if (!Inventory.hasItem(this, FOOD_IMAGE, FOOD_THRESHOLD)) {
      return false;
    }
    Inventory.clickItem(this, FOOD_IMAGE, FOOD_THRESHOLD, "fast");
    waitMillis(HumanBehavior.adjustDelay(1600, 2000));
    return true;
  }

  // === Combat ===

  private boolean waitForFirstHit(int previousXp) {
    LocalDateTime deadline = LocalDateTime.now().plusNanos(ENGAGE_TIMEOUT_MS * 1_000_000L);
    while (LocalDateTime.now().isBefore(deadline)) {
      try {
        if (Minimap.getXp(this) > previousXp) return true;
      } catch (Exception ignored) {}
      waitMillis(200);
    }
    return false;
  }

  private void waitForKill(int previousXp) {
    LocalDateTime deadline = LocalDateTime.now().plusSeconds(KILL_TIMEOUT_SECONDS);
    while (LocalDateTime.now().isBefore(deadline)) {
      // Eat mid-combat if needed
      if (shouldEat()) {
        eatFood();
      }
      // Check chat for combat end
      if (isOutOfCombatChat()) {
        logger.info("Kill confirmed (chat: no longer in combat)");
        inCombat = false;
        HumanBehavior.sleep(600, 900);
        return;
      }
      try {
        int delta = Minimap.getXp(this) - previousXp;
        if (delta >= GOBLIN_XP && delta < 100) {
          logger.info("Kill confirmed (+{} XP)", delta);
          inCombat = false;
          HumanBehavior.sleep(600, 900);
          return;
        }
      } catch (Exception ignored) {}
      waitMillis(300);
    }
    logger.info("Kill timeout — retrying");
    inCombat = false;
  }

  // === Recovery ===

  /**
   * Reads the latest chat message for red "no longer in combat" text.
   */
  private boolean isOutOfCombatChat() {
    Rectangle latestMsg = controller().zones().getChatTabs().get("Latest Message");
    if (latestMsg == null) return false;
    String text = Ocr.extractText(latestMsg, "Plain 12", CHAT_RED, true).toLowerCase();
    return text.contains("nolonger");
  }

  /**
   * Reads the latest chat message for black game text (e.g. "already under attack",
   * "someone else is fighting that").
   */
  private String getLatestBlackChat() {
    Rectangle latestMsg = controller().zones().getChatTabs().get("Latest Message");
    if (latestMsg == null) return "";
    return Ocr.extractText(latestMsg, "Plain 12", CHAT_BLACK, true).toLowerCase();
  }

  private void recoverToGoblins() {
    waitRandomMillis(600, 800);
    if (ColourClick.isVisible(this, GOBLIN_COLOUR)) return;

    logger.info("Walking back to goblin area");
    Walk.to(this, GOBLIN_AREA, "goblin area");
  }
}
