package scripts.shared.antiban;

import org.dreambot.api.input.Mouse;
import org.dreambot.api.methods.Calculations;
import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.item.GroundItems;
import org.dreambot.api.methods.tabs.Tab;
import org.dreambot.api.methods.tabs.Tabs;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.Entity;
import org.dreambot.api.wrappers.items.Item;

import java.awt.*;

/**
 * Static humanization utilities. Two usage patterns:
 *
 * 1. Called by AntiBanNode for ambient actions (tab glances, run checks, etc.)
 * 2. Called inline by script nodes during normal gameplay (reaction delays,
 *    hover-next, misclicks, mouse drift, inventory glances).
 *
 * All methods are safe to call at any time — they no-op gracefully when
 * preconditions aren't met (e.g., hoverNextTarget when entity is off-screen).
 */
public final class AntiBanUtil {

    private AntiBanUtil() {}

    // ── Existing methods (kept) ──────────────────────────────────────

    /** Randomized delay with 5% outlier chance (up to 3x). */
    public static int humanDelay(int baseMin, int baseMax) {
        if (Math.random() < 0.05) {
            return Calculations.random(baseMax, baseMax * 3);
        }
        return Calculations.random(baseMin, baseMax);
    }

    /** ~10% chance — use before actions for hesitation. */
    public static boolean shouldHesitate() {
        return Math.random() < 0.10;
    }

    /** Small random pause (200-800ms). */
    public static void hesitate() {
        Sleep.sleep(Calculations.random(200, 800));
    }

    /** Context-aware sleep: "clicking" 100-300, "waiting" 500-1000, "idle" 2000-5000. */
    public static int conditionSleep(String context) {
        switch (context) {
            case "clicking": return Calculations.random(100, 300);
            case "waiting":  return Calculations.random(500, 1000);
            case "idle":     return Calculations.random(2000, 5000);
            default:         return Calculations.random(300, 600);
        }
    }

    // ── Fatigue ──────────────────────────────────────────────────────

    /**
     * Delay that scales with session duration. Use from script nodes
     * that track their own start time.
     *
     * @param startTime System.currentTimeMillis() when script started
     * @param baseMin   minimum delay at session start
     * @param baseMax   maximum delay at session start
     * @param maxMins   minutes until fatigue reaches 2x (default 480)
     */
    public static int fatigueDelay(long startTime, int baseMin, int baseMax, int maxMins) {
        double mins = (System.currentTimeMillis() - startTime) / 60_000.0;
        double f = Math.min(mins / maxMins, 1.0);
        int min = baseMin + (int) (baseMin * f);
        int max = baseMax + (int) (baseMax * f);
        if (Math.random() < 0.05) return Calculations.random(max, max * 3);
        return Calculations.random(min, max);
    }

    public static int fatigueDelay(long startTime, int baseMin, int baseMax) {
        return fatigueDelay(startTime, baseMin, baseMax, 480);
    }

    /**
     * Adjust DreamBot's mouse speed based on session fatigue.
     * Call periodically (e.g., from AntiBanNode). Early session: 80-95.
     * Late session: 55-75. Simulates a tired player moving the mouse slower.
     *
     * @param startTime script start time
     * @param maxMins   fatigue curve duration
     */
    public static void adjustMouseSpeed(long startTime, int maxMins) {
        double mins = (System.currentTimeMillis() - startTime) / 60_000.0;
        double f = Math.min(mins / maxMins, 1.0);
        int fast = Calculations.random(80, 95);
        int slow = Calculations.random(55, 75);
        int speed = fast - (int) ((fast - slow) * f);
        Mouse.getMouseSettings().setSpeed(speed);
    }

    // ── Reaction time (#3) ───────────────────────────────────────────

    /**
     * Human-like reaction delay after an event (action complete, inventory full, etc.).
     * Gaussian-centered ~400-800ms, 5% chance of 2-3s "wasn't paying attention" spike.
     */
    public static int reactionDelay() {
        if (Math.random() < 0.05) {
            return Calculations.random(2000, 3500);
        }
        // Approximate gaussian: average of two randoms clusters toward center
        int a = Calculations.random(300, 900);
        int b = Calculations.random(300, 900);
        return (a + b) / 2;
    }

    // ── Hover next target (#2) ───────────────────────────────────────

    /**
     * Move mouse to the next target while waiting for current action.
     * No-ops if entity is null or off-screen.
     */
    public static void hoverNextTarget(Entity next) {
        if (next == null || !next.isOnScreen()) return;
        Logger.log("[AntiBan] Hover next target: " + next.getName());
        Mouse.move(next);
    }

    // ── Misclick recovery (#1) ───────────────────────────────────────

    /** ~3% chance of misclicking. */
    public static boolean shouldMisclick() {
        return Math.random() < 0.03;
    }

    /**
     * Click a nearby entity by mistake, pause, then interact with the intended one.
     * Uses DreamBot's interact() for natural click behavior.
     */
    public static void misclick(Entity intended) {
        if (intended == null) return;
        Entity distraction = findDistraction(intended);
        if (distraction == null) return;
        Logger.log("[AntiBan] Misclick on " + distraction.getName());
        distraction.interact();
        Sleep.sleep(Calculations.random(300, 800));
        Logger.log("[AntiBan] Correcting to " + intended.getName());
    }

    private static Entity findDistraction(Entity intended) {
        // Find a nearby entity that isn't the intended target
        Entity e = GameObjects.closest(o -> o.getName() != null
                && !"null".equals(o.getName())
                && o.distance() < 6
                && !o.equals(intended));
        if (e != null) return e;
        return NPCs.closest(n -> n.getName() != null
                && !"null".equals(n.getName())
                && n.distance() < 6
                && !n.equals(intended));
    }

    // ── Mouse drift (#4) ─────────────────────────────────────────────

    /**
     * Pause while "watching" an action, optionally hovering the next target.
     * Does NOT add mouse micro-drift — DreamBot's mouse algorithm already
     * produces natural movement. Adding jitter creates detectable double-randomization.
     *
     * @param durationMs total wait duration
     * @param nextTarget optional entity to hover while waiting (null to just wait)
     */
    public static void idleWatch(int durationMs, Entity nextTarget) {
        if (nextTarget != null && nextTarget.isOnScreen()) {
            Sleep.sleep(Calculations.random(durationMs / 3, durationMs / 2));
            hoverNextTarget(nextTarget);
            Sleep.sleep(Calculations.random(durationMs / 4, durationMs / 2));
        } else {
            Sleep.sleep(durationMs);
        }
    }

    public static void idleWatch(int durationMs) {
        idleWatch(durationMs, null);
    }

    // ── Inventory glance (#5) ────────────────────────────────────────

    /**
     * Briefly hover over a random occupied inventory slot.
     * Call after picking up loot or completing a craft.
     */
    public static void glanceInventory() {
        int full = Inventory.fullSlotCount();
        if (full == 0) return;
        // Pick a random occupied slot
        int target = Calculations.random(0, 28);
        int attempts = 0;
        while (Inventory.isSlotEmpty(target) && attempts < 10) {
            target = Calculations.random(0, 28);
            attempts++;
        }
        if (Inventory.isSlotEmpty(target)) return;

        if (Tabs.getOpen() != Tab.INVENTORY) Tabs.open(Tab.INVENTORY);
        Logger.log("[AntiBan] Glance inventory slot " + target);
        Rectangle bounds = Inventory.slotBounds(target);
        if (bounds != null) {
            Mouse.move(new Point(
                    (int) bounds.getCenterX() + Calculations.random(-5, 6),
                    (int) bounds.getCenterY() + Calculations.random(-5, 6)));
        }
        Sleep.sleep(Calculations.random(300, 800));
    }

    // ── Right-click cancel (#6) ──────────────────────────────────────

    /** ~2% chance. */
    public static boolean shouldRightClickCancel() {
        return Math.random() < 0.02;
    }

    /**
     * Right-click an entity, "read" the menu, then dismiss by clicking away.
     * Uses DreamBot's hover() for natural mouse movement.
     */
    public static void rightClickCancel(Entity target) {
        if (target == null) {
            target = GameObjects.closest(o -> o.getName() != null
                    && !"null".equals(o.getName()) && o.distance() < 8);
        }
        if (target == null) return;
        Logger.log("[AntiBan] Right-click cancel on " + target.getName());
        target.interact(target.getName(), true, true); // force right-click menu
        Sleep.sleep(Calculations.random(400, 1200));
        // Dismiss menu — clicking anywhere closes it
        Mouse.click();
    }

    // ── Run energy check (#7) ────────────────────────────────────────

    /**
     * Check run energy and toggle if appropriate.
     * Low energy (<30%): toggle off. High energy (>50%) and off: toggle on.
     * Sometimes just glances at the orb without toggling.
     */
    public static void checkRunEnergy() {
        int energy = Walking.getRunEnergy();
        boolean running = Walking.isRunEnabled();
        Logger.log("[AntiBan] Check run energy: " + energy + "% (running=" + running + ")");

        if (!running && energy > 50) {
            Walking.toggleRun();
        } else if (running && energy < 30) {
            Walking.toggleRun();
        }
        // Either way, pause as if we looked at it
        Sleep.sleep(Calculations.random(200, 600));
    }

    // ── Minimap variation (#8) ───────────────────────────────────────

    /** ~20% chance — scripts use this to vary walk method. */
    public static boolean shouldUseMinimap() {
        return Math.random() < 0.20;
    }

    // ── Interaction variation ────────────────────────────────────────

    /**
     * ~15% chance of forcing right-click interaction instead of left-click.
     * Use before interact() calls to vary how the bot clicks things.
     *
     * Usage:
     *   if (AntiBanUtil.shouldForceRightClick()) {
     *       target.interactForceRight("Chop down");
     *   } else {
     *       target.interact("Chop down");
     *   }
     */
    public static boolean shouldForceRightClick() {
        return Math.random() < 0.15;
    }

    // ── Break scheduler ──────────────────────────────────────────────

    private static long lastBreakTime = System.currentTimeMillis();
    private static final long MIN_BREAK_INTERVAL = 20 * 60_000; // 20 minutes minimum

    /**
     * Check if it's time for an extended AFK break (1-5 minutes).
     * Call from AntiBanNode or script loop. Returns 0 if no break needed,
     * otherwise returns the break duration in ms (already sleeps internally).
     *
     * Triggers roughly every 20-40 minutes with ~30% chance when eligible.
     */
    public static int maybeBreak() {
        long now = System.currentTimeMillis();
        long elapsed = now - lastBreakTime;
        long threshold = MIN_BREAK_INTERVAL + Calculations.random(0, 20 * 60_000);

        if (elapsed < threshold || Math.random() > 0.30) return 0;

        lastBreakTime = now;
        int breakSec = Calculations.random(60, 300); // 1-5 minutes
        Logger.log("[AntiBan] Taking break: " + breakSec + "s");

        // Move mouse off screen like a real AFK player
        if (Mouse.isMouseInScreen()) Mouse.moveOutsideScreen();
        Sleep.sleep(breakSec * 1000);

        Logger.log("[AntiBan] Break over, resuming");
        return breakSec * 1000;
    }

    // ── Chat glance (#9) ─────────────────────────────────────────────

    /**
     * Briefly switch to a different game tab to simulate reading chat/clan.
     * Uses Clan or Friends tab as proxy since there's no direct chat tab API.
     */
    public static void glanceChat() {
        Tab[] chatTabs = {Tab.CLAN, Tab.FRIENDS};
        Tab tab = chatTabs[Calculations.random(0, chatTabs.length)];
        Tab prev = Tabs.getOpen();
        Logger.log("[AntiBan] Glance chat (" + tab + ")");
        Tabs.open(tab);
        Sleep.sleep(Calculations.random(600, 2000));
        if (prev != null) Tabs.open(prev);
    }

    // ── World map check (#10) ────────────────────────────────────────

    /**
     * Very briefly open the world map via keyboard shortcut, then close.
     * Uses the 'M' key which is the default world map keybind.
     */
    public static void checkWorldMap() {
        Logger.log("[AntiBan] Check world map");
        org.dreambot.api.input.Keyboard.type("m", false);
        Sleep.sleep(Calculations.random(1000, 3000));
        org.dreambot.api.input.Keyboard.pressEsc();
        Sleep.sleep(Calculations.random(200, 500));
    }
}
