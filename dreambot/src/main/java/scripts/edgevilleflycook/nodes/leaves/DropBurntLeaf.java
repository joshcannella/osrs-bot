package scripts.edgevilleflycook.nodes.leaves;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.shared.antiban.AntiBanUtil;

public class DropBurntLeaf extends Leaf {

    @Override
    public boolean isValid() {
        // Only drop burnt fish when we have no raw fish left (cooking is done)
        return Inventory.contains("Burnt fish") && !Inventory.contains("Raw trout", "Raw salmon");
    }

    @Override
    public int onLoop() {
        Logger.log("[Drop] Dropping burnt fish");
        if (Inventory.dropAll("Burnt fish")) {
            Sleep.sleepUntil(() -> !Inventory.contains("Burnt fish"), 2000);
        }
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
