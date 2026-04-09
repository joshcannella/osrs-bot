package scripts.edgevilleflycook.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.shared.antiban.AntiBanUtil;

public class BankBranch extends Leaf {

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
            if (Walking.shouldWalk()) {
                Bank.open();
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        if (Inventory.contains("Trout", "Salmon")) {
            Logger.log("[Bank] Depositing cooked fish");
            if (Bank.depositAll("Trout")) {
                Sleep.sleepUntil(() -> !Inventory.contains("Trout"), 2000);
            }
            if (Bank.depositAll("Salmon")) {
                Sleep.sleepUntil(() -> !Inventory.contains("Salmon"), 2000);
            }
        }

        if (Bank.isOpen() && Inventory.isEmpty()) {
            Logger.log("[Bank] Closing bank");
            Bank.close();
        }

        return AntiBanUtil.humanDelay(600, 1200);
    }
}
