package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.item.GroundItems;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.NPC;
import org.dreambot.api.wrappers.items.GroundItem;
import scripts.brutusfighter.BrutusConstants;
import scripts.brutusfighter.BrutusFighterScript;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Loot drops after Brutus dies. Bury bull bones on the spot.
 * Only valid when inside the instance and Brutus is dead.
 */
public class LootLeaf extends Leaf {

    @Override
    public boolean isValid() {
        BrutusFighterScript script = (BrutusFighterScript) getTree();
        if (!script.isInInstance()) return false;

        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus != null && brutus.exists()) return false;
        return hasLoot() || hasBullBones();
    }

    @Override
    public int onLoop() {
        GroundItem bones = GroundItems.closest(BrutusConstants.BULL_BONES);
        if (bones != null) {
            Logger.log("[Loot] Burying bull bones");
            if (bones.interact("Bury")) {
                Sleep.sleepUntil(() -> GroundItems.closest(BrutusConstants.BULL_BONES) == null, 3000);
            }
            return AntiBanUtil.reactionDelay();
        }

        if (Inventory.isFull()) {
            Logger.log("[Loot] Inventory full, skipping remaining loot");
            return AntiBanUtil.humanDelay(600, 1200);
        }

        GroundItem loot = GroundItems.closest(BrutusConstants.LOOT_NAMES);
        if (loot != null) {
            Logger.log("[Loot] Looting " + loot.getName());
            if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
            if (AntiBanUtil.shouldForceRightClick()) {
                loot.interactForceRight("Take");
            } else {
                loot.interact("Take");
            }
            String name = loot.getName();
            Sleep.sleepUntil(() -> GroundItems.closest(name) == null || Inventory.contains(name), 3000);
            if (Math.random() < 0.15) AntiBanUtil.glanceInventory();
            return AntiBanUtil.reactionDelay();
        }

        return AntiBanUtil.humanDelay(600, 1200);
    }

    private boolean hasLoot() {
        return GroundItems.closest(BrutusConstants.LOOT_NAMES) != null;
    }

    private boolean hasBullBones() {
        return GroundItems.closest(BrutusConstants.BULL_BONES) != null;
    }
}
