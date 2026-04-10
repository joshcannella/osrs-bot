package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.bank.Bank;
import org.dreambot.api.methods.dialogues.Dialogues;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;
import scripts.brutusfighter.BrutusConstants;
import scripts.brutusfighter.BrutusFighterScript;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Branch: active when no food in inventory.
 * Leaves the instance via the exit gate, then banks.
 */
public class BankBranch extends Branch {

    public BankBranch() {
        addLeaves(new LeaveInstanceLeaf(), new BankLeaf());
    }

    @Override
    public boolean isValid() {
        return !Inventory.contains(BrutusConstants.FOOD_NAMES);
    }

    /**
     * If still inside the instance (cow field area), leave via the exit gate.
     */
    private static class LeaveInstanceLeaf extends Leaf {

        private LeaveInstanceLeaf() {}

        @Override
        public boolean isValid() {
            BrutusFighterScript script = (BrutusFighterScript) getTree();
            return script.canLeaveInstance();
        }

        @Override
        public int onLoop() {
            BrutusFighterScript script = (BrutusFighterScript) getTree();

            if (Dialogues.inDialogue()) {
                if (Dialogues.areOptionsAvailable()) {
                    Logger.log("[Bank] Confirming leave instance");
                    Dialogues.chooseFirstOptionContaining("Yes");
                    Sleep.sleepUntil(() -> !Dialogues.inDialogue(), 3000);
                    script.setInInstance(false);
                } else if (Dialogues.canContinue()) {
                    Dialogues.continueDialogue();
                }
                return AntiBanUtil.humanDelay(600, 1200);
            }

            GameObject gate = GameObjects.closest(g -> g != null
                && "Gate".equals(g.getName()) && g.hasAction("Leave"));
            if (gate != null) {
                Logger.log("[Bank] Leaving instance via gate");
                if (gate.interact("Leave")) {
                    Sleep.sleepUntil(() -> Dialogues.inDialogue(),
                        () -> Players.getLocal().isMoving(), 8000, 600);
                }
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }
    }

    /**
     * Once outside the instance, bank normally.
     */
    private static class BankLeaf extends Leaf {

        @Override
        public boolean isValid() {
            BrutusFighterScript script = (BrutusFighterScript) getTree();
            return !script.isInInstance();
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
