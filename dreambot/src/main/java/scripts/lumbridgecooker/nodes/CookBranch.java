package scripts.lumbridgecooker.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.methods.widget.helpers.ItemProcessing;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;
import org.dreambot.api.wrappers.items.Item;
import scripts.lumbridgecooker.CookableFood;
import scripts.lumbridgecooker.LumbridgeCookerScript;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Valid when inventory contains any selected raw food.
 * Two leaves: use food on range, then cook all when widget opens.
 */
public class CookBranch extends Branch {

    private final LumbridgeCookerScript script;

    public CookBranch(LumbridgeCookerScript script) {
        this.script = script;
        addLeaves(new CookAllLeaf(), new UseOnRangeLeaf());
    }

    @Override
    public boolean isValid() {
        return hasRawFood();
    }

    private boolean hasRawFood() {
        for (CookableFood food : script.getSelectedFoods()) {
            if (Inventory.contains(food.getRawName())) return true;
        }
        return false;
    }

    /** Find the first selected food currently in inventory (raw). */
    private CookableFood currentFood() {
        for (CookableFood food : script.getSelectedFoods()) {
            if (Inventory.contains(food.getRawName())) return food;
        }
        return null;
    }

    /**
     * Valid when ItemProcessing widget is open. Clicks "Cook All".
     */
    private class CookAllLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return ItemProcessing.isOpen();
        }

        @Override
        public int onLoop() {
            CookableFood food = currentFood();
            if (food == null) return AntiBanUtil.reactionDelay();

            Logger.log("[Cook] Cooking all " + food.getRawName());
            if (ItemProcessing.makeAll(food.getRawName())) {
                Sleep.sleepUntil(() -> !hasRawFood() || !Players.getLocal().isAnimating(),
                        () -> Players.getLocal().isAnimating(), 60_000, 600);
            }
            return AntiBanUtil.reactionDelay();
        }
    }

    /**
     * Valid when we have raw food and the cooking widget is NOT open.
     * Uses raw food on the Cooking range.
     */
    private class UseOnRangeLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return !ItemProcessing.isOpen();
        }

        @Override
        public int onLoop() {
            if (Players.getLocal().isAnimating()) {
                return AntiBanUtil.humanDelay(600, 1200);
            }

            GameObject range = GameObjects.closest("Cooking range");
            if (range == null) {
                Logger.log("[Cook] Walking to range");
                if (Walking.shouldWalk()) Walking.walk(3211, 3215, 0);
                return AntiBanUtil.humanDelay(600, 1200);
            }

            CookableFood food = currentFood();
            if (food == null) return AntiBanUtil.humanDelay(600, 1200);

            Item rawItem = Inventory.get(food.getRawName());
            if (rawItem != null) {
                if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
                Logger.log("[Cook] Using " + food.getRawName() + " on range");
                rawItem.useOn(range);
                Sleep.sleepUntil(ItemProcessing::isOpen,
                        () -> Players.getLocal().isMoving(), 5000, 600);
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }
    }
}
