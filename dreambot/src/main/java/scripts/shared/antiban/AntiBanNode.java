package scripts.shared.antiban;

import org.dreambot.api.input.Mouse;
import org.dreambot.api.methods.Calculations;
import org.dreambot.api.methods.input.Camera;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.item.GroundItems;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.methods.skills.Skills;
import org.dreambot.api.methods.tabs.Tab;
import org.dreambot.api.methods.tabs.Tabs;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.Entity;

/**
 * Anti-ban leaf node with 12 weighted ambient actions and progressive fatigue.
 * Add as first branch in any TreeScript.
 *
 * 7 node-owned actions (camera, mouse, tabs, entities, idle) plus
 * 5 delegated to AntiBanUtil (inventory glance, right-click cancel,
 * run energy, chat glance, world map).
 *
 * Usage:
 *   AntiBanNode ab = new AntiBanNode();
 *   ab.setSkillsToCheck(Skill.FISHING, Skill.COOKING);
 *   addBranches(ab, ...otherBranches);
 */
public class AntiBanNode extends Leaf {

    private long lastActionTime = System.currentTimeMillis();
    private long lastIdleTime = System.currentTimeMillis();
    private final long startTime = System.currentTimeMillis();

    private long minIntervalMs = 15_000;
    private double triggerRate = 0.08;
    private Skill[] skillsToCheck = {Skill.HITPOINTS};
    private int maxRuntimeMinutes = 480;

    // Weighted action table — weights are relative, total = 100
    private static final int W_CAMERA       = 25;
    private static final int W_MOUSE_OFF    = 18;
    private static final int W_CHECK_SKILL  = 12;
    private static final int W_CHECK_TAB    =  8;
    private static final int W_HOVER        =  8;
    private static final int W_IDLE         =  8;
    private static final int W_EXAMINE      =  6;
    private static final int W_GLANCE_INV   =  5;
    private static final int W_RC_CANCEL    =  3;
    private static final int W_RUN_CHECK    =  3;
    private static final int W_CHAT         =  2;
    private static final int W_WORLD_MAP    =  2;
    private static final int TOTAL = W_CAMERA + W_MOUSE_OFF + W_CHECK_SKILL
            + W_CHECK_TAB + W_HOVER + W_IDLE + W_EXAMINE + W_GLANCE_INV
            + W_RC_CANCEL + W_RUN_CHECK + W_CHAT + W_WORLD_MAP;

    // ── Configuration ────────────────────────────────────────────────

    public void setSkillsToCheck(Skill... skills) { this.skillsToCheck = skills; }
    public void setMinInterval(long ms) { this.minIntervalMs = ms; }
    public void setTriggerRate(double rate) { this.triggerRate = rate; }
    public void setMaxRuntimeMinutes(int mins) { this.maxRuntimeMinutes = mins; }

    // ── Leaf interface ───────────────────────────────────────────────

    @Override
    public boolean isValid() {
        if (System.currentTimeMillis() - lastActionTime < minIntervalMs) return false;
        return Math.random() < triggerRate;
    }

    @Override
    public int onLoop() {
        lastActionTime = System.currentTimeMillis();

        // Periodically adjust mouse speed for fatigue
        AntiBanUtil.adjustMouseSpeed(startTime, maxRuntimeMinutes);

        int roll = Calculations.random(0, TOTAL);
        int c = 0;

        // Node-owned actions
        c += W_CAMERA;      if (roll < c) return doCamera();
        c += W_MOUSE_OFF;   if (roll < c) return doMouseOff();
        c += W_CHECK_SKILL; if (roll < c) return doCheckSkill();
        c += W_CHECK_TAB;   if (roll < c) return doCheckTab();
        c += W_HOVER;       if (roll < c) return doHover();
        c += W_IDLE;        if (roll < c) return doIdle();
        c += W_EXAMINE;     if (roll < c) return doExamine();

        // Delegated to AntiBanUtil
        c += W_GLANCE_INV;  if (roll < c) return doGlanceInventory();
        c += W_RC_CANCEL;   if (roll < c) return doRightClickCancel();
        c += W_RUN_CHECK;   if (roll < c) return doRunCheck();
        c += W_CHAT;        if (roll < c) return doGlanceChat();
        return doWorldMap();
    }

    // ── Node-owned actions ───────────────────────────────────────────

    private int doCamera() {
        Tile t = Players.getLocal().getTile();
        Area nearby = new Area(t.getX() - 12, t.getY() - 12, t.getX() + 12, t.getY() + 12);
        Logger.log("[AntiBan] Camera rotate");
        Camera.rotateToTile(nearby.getRandomTile());
        return fatigue(300, 800);
    }

    private int doMouseOff() {
        if (!Mouse.isMouseInScreen()) return fatigue(100, 300);
        Logger.log("[AntiBan] Mouse off-screen");
        Mouse.moveOutsideScreen();
        return fatigue(3000, 8000);
    }

    private int doCheckSkill() {
        Skill skill = skillsToCheck[Calculations.random(0, skillsToCheck.length)];
        Logger.log("[AntiBan] Check " + skill.getName()
                + " Lv" + Skills.getRealLevel(skill));
        Tabs.open(Tab.SKILLS);
        Sleep.sleep(fatigue(800, 2000));
        Tabs.open(Tab.INVENTORY);
        return fatigue(200, 600);
    }

    private int doCheckTab() {
        Tab[] tabs = {Tab.QUEST, Tab.EQUIPMENT, Tab.PRAYER, Tab.COMBAT, Tab.FRIENDS};
        Tab tab = tabs[Calculations.random(0, tabs.length)];
        Logger.log("[AntiBan] Check " + tab);
        Tabs.open(tab);
        Sleep.sleep(fatigue(600, 2000));
        Tabs.open(Tab.INVENTORY);
        return fatigue(200, 600);
    }

    private int doHover() {
        Entity e = findNearby();
        if (e == null) return fatigue(100, 300);
        Logger.log("[AntiBan] Hover " + e.getName());
        Mouse.move(e);
        return fatigue(300, 1200);
    }

    private int doExamine() {
        Entity e = findNearby();
        if (e == null) return fatigue(100, 300);
        Logger.log("[AntiBan] Examine " + e.getName());
        if (e.hasAction("Examine")) {
            e.interact("Examine");
        } else {
            Mouse.move(e);
        }
        return fatigue(500, 2000);
    }

    private int doIdle() {
        long now = System.currentTimeMillis();
        // Extended idle only every 5+ minutes
        if (now - lastIdleTime >= 300_000 && Math.random() < 0.3) {
            lastIdleTime = now;
            int sec = Calculations.random(8, 25);
            Logger.log("[AntiBan] Extended idle " + sec + "s");
            if (Math.random() < 0.7) Mouse.moveOutsideScreen();
            return sec * 1000;
        }
        Logger.log("[AntiBan] Short idle");
        return fatigue(1500, 4000);
    }

    // ── Delegated to AntiBanUtil ─────────────────────────────────────

    private int doGlanceInventory() {
        AntiBanUtil.glanceInventory();
        return fatigue(200, 600);
    }

    private int doRightClickCancel() {
        AntiBanUtil.rightClickCancel(findNearby());
        return fatigue(300, 800);
    }

    private int doRunCheck() {
        AntiBanUtil.checkRunEnergy();
        return fatigue(200, 500);
    }

    private int doGlanceChat() {
        AntiBanUtil.glanceChat();
        return fatigue(200, 600);
    }

    private int doWorldMap() {
        AntiBanUtil.checkWorldMap();
        return fatigue(300, 800);
    }

    // ── Helpers ───────────────────────────────────────────────────────

    private Entity findNearby() {
        int pick = Calculations.random(0, 3);
        if (pick == 0) {
            return GameObjects.closest(o -> o.getName() != null
                    && !"null".equals(o.getName()) && o.distance() < 8);
        } else if (pick == 1) {
            return NPCs.closest(n -> n.getName() != null
                    && !"null".equals(n.getName()) && n.distance() < 10);
        }
        return GroundItems.closest(i -> i.getName() != null
                && !"null".equals(i.getName()) && i.distance() < 8);
    }

    /**
     * Delay that increases as the script runs longer (fatigue).
     * Early session: near baseMin. After maxRuntimeMinutes: ~2x baseMax.
     * 5% chance of outlier (up to 3x).
     */
    private int fatigue(int baseMin, int baseMax) {
        return AntiBanUtil.fatigueDelay(startTime, baseMin, baseMax, maxRuntimeMinutes);
    }
}
