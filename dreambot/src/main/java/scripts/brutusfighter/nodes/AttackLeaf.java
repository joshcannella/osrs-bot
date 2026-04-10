package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.equipment.Equipment;
import org.dreambot.api.methods.container.impl.equipment.EquipmentSlot;
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

/**
 * Fallback leaf: attack Brutus or wait for respawn.
 * Walks to fight position (east of spawn) if not in cow field.
 * Releases gate to enter instance on first visit.
 */
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

        // Not in instance — need to get there and release gate
        if (!script.isInInstance()) {
            // Teleport to cow field if not there
            if (!BrutusConstants.COW_FIELD.contains(Players.getLocal())) {
                if (Equipment.slotContains(EquipmentSlot.AMULET, BrutusConstants.COWBELL_AMULET)) {
                    Logger.log("[Attack] Teleporting to cow field");
                    Equipment.interact(EquipmentSlot.AMULET, "Teleport");
                    Sleep.sleepUntil(() -> BrutusConstants.COW_FIELD.contains(Players.getLocal()),
                        () -> Players.getLocal().isMoving(), 8000, 600);
                    return AntiBanUtil.humanDelay(600, 1200);
                }
                Logger.log("[Attack] Walking to cow field");
                if (Walking.shouldWalk()) Walking.walk(BrutusConstants.FIGHT_TILE);
                return AntiBanUtil.humanDelay(600, 1200);
            }

            // At cow field — release gate
            GameObject gate = GameObjects.closest(g -> g != null
                && "Gate".equals(g.getName()) && g.hasAction("Release"));
            if (gate != null) {
                Logger.log("[Attack] Releasing gate to enter instance");
                if (gate.interact("Release")) {
                    stuckCount = 0;
                    // Wait for cutscene + Brutus to appear
                    Logger.log("[Attack] Waiting for cutscene and Brutus spawn...");
                    Sleep.sleepUntil(() -> {
                        NPC b = NPCs.closest(BrutusConstants.BRUTUS_NAME);
                        return b != null && b.canAttack();
                    }, 30000);
                    script.setInInstance(true);
                } else {
                    stuckCount++;
                }
            } else {
                stuckCount++;
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // === In instance from here ===

        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);

        // Waiting for respawn
        if (brutus == null || !brutus.exists()) {
            Logger.log("[Attack] Waiting for Brutus respawn");
            return AntiBanUtil.humanDelay(1000, 2000);
        }

        // Already in combat
        if (Players.getLocal().isInCombat() && brutus.isInteractedWith()) {
            stuckCount = 0;
            AntiBanUtil.idleWatch(AntiBanUtil.humanDelay(600, 1000));
            return AntiBanUtil.humanDelay(600, 1000);
        }

        // Don't interact while animating
        if (Players.getLocal().isAnimating()) {
            return AntiBanUtil.humanDelay(600, 1000);
        }

        // Walk to fight position (east of spawn) if far
        if (Players.getLocal().getTile().distance(BrutusConstants.FIGHT_TILE) > 5) {
            if (Walking.shouldWalk()) Walking.walk(BrutusConstants.FIGHT_TILE);
            stuckCount++;
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // Attack Brutus
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
