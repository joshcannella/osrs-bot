package scripts.edgevilleflycook.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.shared.antiban.AntiBanUtil;

public class BankLeaf extends Leaf {

    @Override
    public boolean isValid() {
        boolean hasRaw = Inventory.contains("Raw trout", "Raw salmon");
        boolean hasBurnt = Inventory.contains("Burnt fish");

        return !hasRaw && !hasBurnt && Inventory.contains("Trout", "Salmon");
    }

    @Override
    public int onLoop() {
        if (!Bank.isOpen()) {
            Logger.log("[Bank] Opening bank");
            if (Walking.shouldWalk()) Bank.open();
            return AntiBanUtil.humanDelay(600, 1200);
        }

        Logger.log("[Bank] Depositing all except rod and feathers");
        if (Bank.depositAllExcept("Fly fishing rod", "Feather")) {
            Sleep.sleepUntil(() -> !Inventory.contains("Trout", "Salmon"), 2000);
        }

        Logger.log("[Bank] Closing bank");
        Bank.close();
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
