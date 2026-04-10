package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.combat.Combat;
import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.brutusfighter.BrutusConstants;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Eat food when HP drops below threshold.
 */
public class EatLeaf extends Leaf {

    @Override
    public boolean isValid() {
        return Combat.getHealthPercent() < BrutusConstants.EAT_HP_PERCENT
            && Inventory.contains(BrutusConstants.FOOD_NAMES);
    }

    @Override
    public int onLoop() {
        String food = null;
        for (String name : BrutusConstants.FOOD_NAMES) {
            if (Inventory.contains(name)) { food = name; break; }
        }
        if (food == null) return AntiBanUtil.humanDelay(600, 1200);

        Logger.log("[Brutus] Eating " + food + " (HP: " + Combat.getHealthPercent() + "%)");
        if (Inventory.interact(food, "Eat")) {
            Sleep.sleepUntil(() -> Combat.getHealthPercent() > BrutusConstants.EAT_HP_PERCENT, 2000);
        }
        return AntiBanUtil.reactionDelay();
    }
}
