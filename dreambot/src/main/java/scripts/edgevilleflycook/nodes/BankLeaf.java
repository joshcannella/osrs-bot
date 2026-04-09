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
        boolean hasCooked = Inventory.contains("Trout", "Salmon");
        boolean hasRaw = Inventory.contains("Raw trout", "Raw salmon");
        boolean hasBurnt = Inventory.contains("Burnt fish");

        return hasCooked && !hasRaw && !hasBurnt;
    }

    @Override
    public int onLoop() {
        if (!Bank.isOpen()) {
            Logger.log("[Bank] Opening bank");
            if (Walking.shouldWalk()) Bank.open();
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // Deposit one type per loop tick
        if (Inventory.contains("Trout")) {
            Logger.log("[Bank] Depositing trout");
            if (Bank.depositAll("Trout")) {
                Sleep.sleepUntil(() -> !Inventory.contains("Trout"), 2000);
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        if (Inventory.contains("Salmon")) {
            Logger.log("[Bank] Depositing salmon");
            if (Bank.depositAll("Salmon")) {
                Sleep.sleepUntil(() -> !Inventory.contains("Salmon"), 2000);
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        Logger.log("[Bank] Closing bank");
        Bank.close();
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
