package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.brutusfighter.BrutusConstants;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Branch: active when no food in inventory.
 * Handles depositing loot and withdrawing food.
 */
public class BankBranch extends Branch {

    public BankBranch() {
        addLeaves(new BankLeaf());
    }

    @Override
    public boolean isValid() {
        return !Inventory.contains(BrutusConstants.FOOD_NAMES);
    }

    private static class BankLeaf extends Leaf {

        @Override
        public boolean isValid() {
            return true;
        }

        @Override
        public int onLoop() {
            if (!Bank.isOpen()) {
                Logger.log("[Bank] Opening bank");
                if (Walking.shouldWalk()) Bank.open();
                return AntiBanUtil.humanDelay(600, 1200);
            }

            // Deposit all loot
            if (!Inventory.isEmpty()) {
                Logger.log("[Bank] Depositing loot");
                Bank.depositAllItems();
                Sleep.sleepUntil(Inventory::isEmpty, 3000);
                // F5: Bank full handling
                if (!Inventory.isEmpty()) {
                    Logger.error("[Bank] Bank appears full — stopping");
                    Bank.close();
                    return -1;
                }
                return AntiBanUtil.reactionDelay();
            }

            // Withdraw food — try best available
            for (String food : BrutusConstants.FOOD_NAMES) {
                if (Bank.contains(food)) {
                    Logger.log("[Bank] Withdrawing " + food);
                    if (Bank.withdraw(food, BrutusConstants.FOOD_COUNT)) {
                        Sleep.sleepUntil(() -> Inventory.contains(food), 3000);
                    }
                    Bank.close();
                    return AntiBanUtil.reactionDelay();
                }
            }

            // No food available — stop
            Logger.error("[Bank] No food in bank — stopping");
            Bank.close();
            return -1;
        }
    }
}
