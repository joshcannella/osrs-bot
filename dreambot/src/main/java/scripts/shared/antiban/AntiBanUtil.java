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
     * Click a nearby entity by mistake, pause, then click the intended one.
     * No-ops if no nearby distraction found.
     */
    public static void misclick(Entity intended) {
        if (intended == null) return;
        Entity distraction = findDistraction(intended);
        if (distraction == null) return;
        Logger.log("[AntiBan] Misclick on " + distraction.getName());
        Mouse.move(distraction);
        Sleep.sleep(Calculations.random(80, 200));
        Mouse.click();
        Sleep.sleep(Calculations.random(300, 800));
        Logger.log("[AntiBan] Correcting to " + intended.getName());
        intended.interact();
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
     * Small random micro-movements while "watching" an action.
     * Call instead of Sleep.sleep() during animation waits.
     *
     * @param durationMs total drift duration
     */
    public static void driftMouse(int durationMs) {
        long end = System.currentTimeMillis() + durationMs;
        while (System.currentTimeMillis() < end) {
            if (!Mouse.isMouseInScreen()) break;
            Point pos = Mouse.getPosition();
            int dx = Calculations.random(-4, 5);
            int dy = Calculations.random(-4, 5);
            int nx = Math.max(0, Math.min(760, pos.x + dx));
            int ny = Math.max(0, Math.min(500, pos.y + dy));
            Mouse.hop(nx, ny);
            Sleep.sleep(Calculations.random(150, 400));
        }
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
     * Right-click an entity, "read" the menu, then dismiss.
     * If entity is null, finds a nearby one.
     */
    public static void rightClickCancel(Entity target) {
        if (target == null) {
            target = GameObjects.closest(o -> o.getName() != null
                    && !"null".equals(o.getName()) && o.distance() < 8);
        }
        if (target == null) return;
        Logger.log("[AntiBan] Right-click cancel on " + target.getName());
        Mouse.move(target);
        Sleep.sleep(Calculations.random(50, 150));
        Mouse.click(true); // right-click
        Sleep.sleep(Calculations.random(400, 1200));
        // Dismiss by clicking away
        Mouse.move(new Point(
                Calculations.random(10, 750),
                Calculations.random(10, 490)));
        Sleep.sleep(Calculations.random(50, 150));
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
