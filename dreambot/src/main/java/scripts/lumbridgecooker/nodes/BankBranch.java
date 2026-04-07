package scripts.lumbridgecooker.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import scripts.lumbridgecooker.CookableFood;
import scripts.lumbridgecooker.LumbridgeCookerScript;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Valid when no raw food in inventory. Deposits cooked food, withdraws next raw food.
 */
public class BankBranch extends Branch {

    private static final Tile UPSTAIRS_BANK_TILE = new Tile(3208, 3220, 2);
    private static final Tile DOWNSTAIRS_BANK_TILE = new Tile(3208, 3220, 0);

    private final LumbridgeCookerScript script;

    public BankBranch(LumbridgeCookerScript script) {
        this.script = script;
        addLeaves(new DepositLeaf(), new WithdrawLeaf());
    }

    @Override
    public boolean isValid() {
        for (CookableFood food : script.getSelectedFoods()) {
            if (Inventory.contains(food.getRawName())) return false;
        }
        return true;
    }

    private Tile bankTile() {
        return script.useUpstairsBank() ? UPSTAIRS_BANK_TILE : DOWNSTAIRS_BANK_TILE;
    }

    private boolean onCorrectFloor() {
        return Players.getLocal().getZ() == bankTile().getZ();
    }

    /**
     * Deposit cooked food. Valid when inventory is not empty.
     */
    private class DepositLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return Inventory.fullSlotCount() > 0;
        }

        @Override
        public int onLoop() {
            if (!onCorrectFloor()) {
                Logger.log("[Bank] Walking to correct floor");
                if (Walking.shouldWalk()) Walking.walk(bankTile());
                return AntiBanUtil.humanDelay(600, 1200);
            }

            if (!Bank.isOpen()) {
                Logger.log("[Bank] Opening bank");
                if (Walking.shouldWalk()) Bank.open();
                return AntiBanUtil.humanDelay(600, 1200);
            }

            Logger.log("[Bank] Depositing all");
            if (Bank.depositAllItems()) {
                Sleep.sleepUntil(() -> Inventory.fullSlotCount() == 0, 3000);
            }
            return AntiBanUtil.reactionDelay();
        }
    }

    /**
     * Withdraw next raw food. Valid when inventory is empty.
     * Stops script if no selected raw food remains in bank.
     */
    private class WithdrawLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return Inventory.fullSlotCount() == 0;
        }

        @Override
        public int onLoop() {
            if (!onCorrectFloor()) {
                Logger.log("[Bank] Walking to correct floor");
                if (Walking.shouldWalk()) Walking.walk(bankTile());
                return AntiBanUtil.humanDelay(600, 1200);
            }

            if (!Bank.isOpen()) {
                Logger.log("[Bank] Opening bank");
                if (Walking.shouldWalk()) Bank.open();
                return AntiBanUtil.humanDelay(600, 1200);
            }

            // Find next raw food in bank
            for (CookableFood food : script.getSelectedFoods()) {
                if (Bank.contains(food.getRawName())) {
                    Logger.log("[Bank] Withdrawing " + food.getRawName());
                    if (Bank.withdrawAll(food.getRawName())) {
                        Sleep.sleepUntil(() -> Inventory.contains(food.getRawName()), 3000);
                    }
                    Bank.close();
                    return AntiBanUtil.reactionDelay();
                }
            }

            // No raw food left in bank
            Logger.log("[Bank] No more raw food - stopping");
            Bank.close();
            script.stop();
            return 600;
        }
    }
}
