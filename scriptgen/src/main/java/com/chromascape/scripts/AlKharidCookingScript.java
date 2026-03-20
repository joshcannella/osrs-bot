package com.chromascape.scripts;

import com.chromascape.api.DiscordNotification;
import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.Idler;
import com.chromascape.utils.actions.PointSelector;
import com.chromascape.utils.actions.custom.Bank;
import com.chromascape.utils.actions.custom.ColourClick;
import com.chromascape.utils.actions.custom.HumanBehavior;
import com.chromascape.utils.actions.custom.Inventory;
import com.chromascape.utils.actions.custom.KeyPress;
import com.chromascape.utils.actions.custom.LevelUpDismisser;
import com.chromascape.utils.actions.custom.Logout;
import com.chromascape.utils.actions.custom.Walk;
import com.chromascape.utils.actions.custom.GameCenter;
import com.chromascape.utils.core.screen.colour.ColourObj;
import java.awt.Point;
import java.awt.image.BufferedImage;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bytedeco.opencv.opencv_core.Scalar;

/**
 * Cooks raw shrimp on the Al Kharid range, banks cooked/burnt shrimp, withdraws more raw shrimp,
 * and repeats. No quest requirements.
 *
 * <p><b>Prerequisites:</b> Raw shrimp in Al Kharid bank.
 * <p><b>RuneLite Setup:</b> Object Markers — range highlighted red, bank booth highlighted cyan.
 * <p><b>Start:</b> Near Al Kharid bank or range with raw shrimp in bank.
 */
public class AlKharidCookingScript extends BaseScript {

  private static final Logger logger = LogManager.getLogger(AlKharidCookingScript.class);

  // === Colours ===
  // Red wraps around HSV hue 0/180 — cover both ends
  private static final ColourObj RANGE_COLOUR_LOW =
      new ColourObj("red_low", new Scalar(0, 254, 254, 0), new Scalar(3, 255, 255, 0));
  private static final ColourObj RANGE_COLOUR_HIGH =
      new ColourObj("red_high", new Scalar(177, 254, 254, 0), new Scalar(180, 255, 255, 0));

  // === Images ===
  private static final String RAW_SHRIMP = "/images/user/Raw_shrimps.png";
  private static final String COOKED_SHRIMP = "/images/user/Shrimps.png";
  private static final String BURNT_SHRIMP = "/images/user/Burnt_shrimp.png";
  private static final double THRESHOLD = 0.07;

  // === Tiles ===
  private static final Point BANK_TILE = new Point(3269, 3167);
  private static final Point RANGE_DOOR_TILE = new Point(3275, 3180);
  private static final Point RANGE_TILE = new Point(3273, 3180);

  // === Stuck Detection ===
  private static final int MAX_STUCK_CYCLES = 10;
  private int stuckCounter = 0;

  @Override
  protected void cycle() {
    if (HumanBehavior.runPreCycleChecks(this)) return;

    if (stuckCounter >= MAX_STUCK_CYCLES) {
      logger.error("Stuck for {} cycles, logging out.", MAX_STUCK_CYCLES);
      DiscordNotification.send("AlKharidCooking: stuck, logging out.");
      Logout.perform(this);
      stop();
      return;
    }

    if (Inventory.hasItem(this, RAW_SHRIMP, THRESHOLD)) {
      cook();
    } else {
      bank();
    }
  }

  // === Cooking ===

  private void cook() {
    // Always walk to range area first
    if (!isRangeVisible()) {
      if (!Walk.to(this, RANGE_DOOR_TILE, "range door")) { stuckCounter++; return; }
      GameCenter.click(this);
      HumanBehavior.sleep(1500, 2500);
    }
    if (!Walk.to(this, RANGE_TILE, "range")) { stuckCounter++; return; }

    // Use raw shrimp on range
    Inventory.clickItem(this, RAW_SHRIMP, THRESHOLD, "medium");
    HumanBehavior.sleep(200, 400);

    Point rangeLoc = getRangeClickPoint();
    if (rangeLoc == null) {
      logger.warn("Range click point null");
      stuckCounter++;
      return;
    }
    controller().mouse().moveTo(rangeLoc, "medium");
    controller().mouse().leftClick();

    // Wait for cook dialog then press space to cook all
    HumanBehavior.sleep(2000, 3000);
    KeyPress.space(this);

    // Wait for cooking to finish
    Idler.waitUntilIdle(this, 90);

    // If raw shrimp remain, cooking was interrupted (likely level-up dialog).
    // Spam space to dismiss any dialogs, then return to re-cook.
    if (Inventory.hasItem(this, RAW_SHRIMP, THRESHOLD)) {
      logger.info("Cooking interrupted — dismissing dialogs");
      for (int i = 0; i < 4; i++) {
        KeyPress.space(this);
        HumanBehavior.sleep(800, 1200);
      }
      return;
    }

    stuckCounter = 0;
  }

  // === Banking ===

  private void bank() {
    // Always walk to bank first
    if (!Walk.to(this, BANK_TILE, "bank")) { stuckCounter++; return; }

    Bank.open(this, "Cyan");

    // Deposit cooked and burnt shrimp (left-click deposits all with bank qty set to All)
    Inventory.clickItem(this, COOKED_SHRIMP, THRESHOLD, "medium");
    HumanBehavior.sleep(300, 500);
    Inventory.clickItem(this, BURNT_SHRIMP, THRESHOLD, "medium");
    HumanBehavior.sleep(300, 500);

    // Withdraw raw shrimp by template matching it in the bank view
    BufferedImage gameView = controller().zones().getGameView();
    Point shrimpLoc = PointSelector.getRandomPointInImage(RAW_SHRIMP, gameView, THRESHOLD);
    if (shrimpLoc == null) {
      logger.error("No raw shrimp found in bank — out of supplies.");
      DiscordNotification.send("AlKharidCooking: no raw shrimp in bank.");
      Bank.close(this);
      Logout.perform(this);
      stop();
      return;
    }
    controller().mouse().moveTo(shrimpLoc, "medium");
    controller().mouse().leftClick();
    HumanBehavior.sleep(400, 600);

    Bank.close(this);

    // Verify withdrawal
    if (Inventory.hasItem(this, RAW_SHRIMP, THRESHOLD)) {
      stuckCounter = 0;
    } else {
      logger.warn("Withdrawal failed — raw shrimp not in inventory.");
      stuckCounter++;
    }
  }

  // === Utilities ===

  private boolean isRangeVisible() {
    return getRangeClickPoint() != null;
  }

  private Point getRangeClickPoint() {
    Point loc = ColourClick.getClickPoint(this, RANGE_COLOUR_LOW);
    if (loc != null) return loc;
    return ColourClick.getClickPoint(this, RANGE_COLOUR_HIGH);
  }
}
