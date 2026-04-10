package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.equipment.Equipment;
import org.dreambot.api.methods.container.impl.equipment.EquipmentSlot;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.item.GroundItems;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Ring the cowbell amulet after a kill for faster respawn (13 ticks vs 36).
 * Valid when Brutus is dead, no loot remaining, and cowbell is equipped.
 */
public class RingCowbellLeaf extends Leaf {

    private boolean rangThisKill = false;
    private long lastKillTime = 0;

    @Override
    public boolean isValid() {
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        boolean brutusDead = brutus == null || !brutus.exists();

        // Reset flag when Brutus is alive
        if (!brutusDead) {
            rangThisKill = false;
            return false;
        }

        // Don't ring if we already rang this kill, or if there's still loot
        if (rangThisKill) return false;
        if (GroundItems.closest(BrutusConstants.LOOT_NAMES) != null) return false;
        if (GroundItems.closest(BrutusConstants.BULL_BONES) != null) return false;

        return Equipment.slotContains(EquipmentSlot.AMULET, BrutusConstants.COWBELL_AMULET);
    }

    @Override
    public int onLoop() {
        Logger.log("[Brutus] Ringing cowbell for fast respawn");
        Equipment.interact(EquipmentSlot.AMULET, "Ring");
        rangThisKill = true;
        lastKillTime = System.currentTimeMillis();
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
