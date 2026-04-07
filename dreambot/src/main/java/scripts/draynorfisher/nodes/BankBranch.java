package scripts.draynorfisher.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Branch: active when inventory is full.
 * Single leaf handles bank open + deposit (Bank.open() walks for you).
 */
public class BankBranch extends Branch {

    public BankBranch() {
        addLeaves(new DepositLeaf());
    }

    @Override
    public boolean isValid() {
        return Inventory.isFull();
    }

    private static class DepositLeaf extends Leaf {

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

            if (Bank.depositAllItems()) {
                Logger.log("[Bank] Deposited fish");
                Sleep.sleepUntil(() -> !Inventory.isFull(), 3000);
            }

            // Stop if bank is full and we still have a full inventory
            if (Inventory.isFull()) {
                Logger.log("[Bank] Bank appears full - stopping script");
                Bank.close();
                getTree().stop();
            }

            return AntiBanUtil.reactionDelay();
        }
    }
}
