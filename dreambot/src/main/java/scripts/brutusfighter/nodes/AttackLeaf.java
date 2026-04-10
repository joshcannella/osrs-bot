package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;
import scripts.brutusfighter.BrutusFighterScript;
import scripts.shared.antiban.AntiBanUtil;

public class AttackLeaf extends Leaf {

    private int stuckCount = 0;

    @Override
    public boolean isValid() {
        return Inventory.contains(BrutusConstants.FOOD_NAMES);
    }

    @Override
    public int onLoop() {
        if (stuckCount > 10) {
            Logger.error("[Attack] Stuck for too long — stopping");
            return -1;
        }

        BrutusFighterScript script = (BrutusFighterScript) getTree();

        // Not in instance — walk to gate and release
        if (!script.isInInstance()) {
            GameObject gate = GameObjects.closest(g -> g != null
                && "Gate".equals(g.getName()) && g.hasAction("Release"));
            if (gate == null) {
                Logger.log("[Attack] Walking to cow field gate");
                if (Walking.shouldWalk()) Walking.walk(BrutusConstants.GATE_TILE);
                return AntiBanUtil.humanDelay(600, 1200);
            }
            Logger.log("[Attack] Releasing gate to enter instance");
            gate.interact("Release");
            script.setInInstance(true);
            Sleep.sleep(10000);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // === In instance ===

        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);

        if (brutus == null || !brutus.exists()) {
            return AntiBanUtil.humanDelay(1000, 2000);
        }

        if (Players.getLocal().isInCombat() && brutus.isInteractedWith()) {
            stuckCount = 0;
            AntiBanUtil.idleWatch(AntiBanUtil.humanDelay(600, 1000));
            return AntiBanUtil.humanDelay(600, 1000);
        }

        if (Players.getLocal().isAnimating()) {
            return AntiBanUtil.humanDelay(600, 1000);
        }

        Logger.log("[Attack] Attacking Brutus");
        if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
        if (AntiBanUtil.shouldMisclick()) AntiBanUtil.misclick(brutus);
        if (brutus.interact("Attack")) {
            stuckCount = 0;
            Sleep.sleepUntil(() -> Players.getLocal().isInCombat(),
                () -> Players.getLocal().isMoving(), 5000, 600);
        } else {
            stuckCount++;
        }

        return AntiBanUtil.reactionDelay();
    }
}
