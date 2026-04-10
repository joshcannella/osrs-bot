package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.equipment.Equipment;
import org.dreambot.api.methods.container.impl.equipment.EquipmentSlot;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;
import scripts.brutusfighter.BrutusFighterScript;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Fallback leaf: attack Brutus or wait for respawn.
 * Walks to fight position (east of spawn) if not in cow field.
 */
public class AttackLeaf extends Leaf {

    @Override
    public boolean isValid() {
        return Inventory.contains(BrutusConstants.FOOD_NAMES);
    }

    @Override
    public int onLoop() {
        // Walk to cow field if not there
        if (!BrutusConstants.COW_FIELD.contains(Players.getLocal())) {
            // Try cowbell teleport first
            if (Equipment.slotContains(EquipmentSlot.AMULET, BrutusConstants.COWBELL_AMULET)) {
                Logger.log("[Brutus] Teleporting to cow field");
                Equipment.interact(EquipmentSlot.AMULET, "Teleport");
                Sleep.sleepUntil(() -> BrutusConstants.COW_FIELD.contains(Players.getLocal()),
                    () -> Players.getLocal().isMoving(), 8000, 600);
                return AntiBanUtil.humanDelay(600, 1200);
            }
            Logger.log("[Brutus] Walking to cow field");
            if (Walking.shouldWalk()) Walking.walk(BrutusConstants.FIGHT_TILE);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);

        // Brutus not spawned — wait for respawn
        if (brutus == null || !brutus.exists()) {
            return AntiBanUtil.humanDelay(1000, 2000);
        }

        // Already in combat with Brutus
        if (Players.getLocal().isInCombat() && brutus.isInteractedWith()) {
            return AntiBanUtil.humanDelay(600, 1000);
        }

        // Walk to fight position (east of spawn) if far
        if (Players.getLocal().getTile().distance(BrutusConstants.FIGHT_TILE) > 5) {
            if (Walking.shouldWalk()) Walking.walk(BrutusConstants.FIGHT_TILE);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // Attack Brutus
        if (brutus.hasAction("Attack")) {
            Logger.log("[Brutus] Attacking Brutus");
            if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
            if (AntiBanUtil.shouldMisclick()) AntiBanUtil.misclick(brutus);
            if (brutus.interact("Attack")) {
                Sleep.sleepUntil(() -> Players.getLocal().isInCombat(),
                    () -> Players.getLocal().isMoving(), 5000, 600);
            }
        } else if (brutus.hasAction("Release")) {
            Logger.log("[Brutus] Releasing Brutus");
            brutus.interact("Release");
            Sleep.sleepUntil(() -> {
                NPC b = NPCs.closest(BrutusConstants.BRUTUS_NAME);
                return b != null && b.hasAction("Attack");
            }, 5000);
        }

        return AntiBanUtil.reactionDelay();
    }
}
