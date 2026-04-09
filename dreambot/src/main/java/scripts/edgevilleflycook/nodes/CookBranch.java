package scripts.edgevilleflycook.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.methods.widget.helpers.ItemProcessing;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;
import org.dreambot.api.wrappers.items.Item;
import scripts.shared.antiban.AntiBanUtil;

public class CookBranch extends Branch {

    private static final Area FIRE_AREA = new Area(3104, 3432, 3106, 3434);

    @Override
    public boolean isValid() {
        return Inventory.isFull() && Inventory.contains("Raw trout", "Raw salmon");
    }

    public CookBranch() {
        addLeaves(new CookAllLeaf(), new UseOnFireLeaf());
    }

    /** Returns whichever raw fish is currently in inventory. */
    private static String currentRawFish() {
        if (Inventory.contains("Raw salmon")) return "Raw salmon";
        if (Inventory.contains("Raw trout")) return "Raw trout";
        return null;
    }

    private class CookAllLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return ItemProcessing.isOpen();
        }

        @Override
        public int onLoop() {
            String fish = currentRawFish();
            if (fish == null) return AntiBanUtil.reactionDelay();

            Logger.log("[Cook] Cooking all " + fish);
            if (ItemProcessing.makeAll(fish)) {
                // Sleep until THIS fish type is gone or we stop animating
                final String cooking = fish;
                Sleep.sleepUntil(() -> !Inventory.contains(cooking) || !Players.getLocal().isAnimating(),
                        () -> Players.getLocal().isAnimating(), 60_000, 600);
            }
            return AntiBanUtil.reactionDelay();
        }
    }

    private class UseOnFireLeaf extends Leaf {
        @Override
        public boolean isValid() {
            return !ItemProcessing.isOpen();
        }

        @Override
        public int onLoop() {
            if (Players.getLocal().isAnimating()) {
                return AntiBanUtil.humanDelay(600, 1200);
            }

            if (!FIRE_AREA.contains(Players.getLocal())) {
                Logger.log("[Cook] Walking to fire");
                if (Walking.shouldWalk()) Walking.walk(FIRE_AREA);
                return AntiBanUtil.humanDelay(600, 1200);
            }

            GameObject fire = GameObjects.closest(f -> f != null
                    && f.getName() != null
                    && f.getName().equals("Fire"));

            if (fire == null) {
                Logger.log("[Cook] No fire found in area");
                return AntiBanUtil.humanDelay(1000, 2000);
            }

            String rawFish = currentRawFish();
            if (rawFish == null) return AntiBanUtil.reactionDelay();

            Item rawItem = Inventory.get(rawFish);
            if (rawItem != null) {
                if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
                Logger.log("[Cook] Using " + rawFish + " on fire");
                rawItem.useOn(fire);
                Sleep.sleepUntil(ItemProcessing::isOpen,
                        () -> Players.getLocal().isMoving(), 5000, 600);
            }

            return AntiBanUtil.humanDelay(600, 1200);
        }
    }
}
