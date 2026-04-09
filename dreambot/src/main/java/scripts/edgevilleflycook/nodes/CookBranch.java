package scripts.edgevilleflycook.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.methods.widget.helpers.ItemProcessing;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.GameObject;
import org.dreambot.api.wrappers.items.Item;
import scripts.shared.antiban.AntiBanUtil;

public class CookBranch extends Branch {

    private static final Area FIRE_AREA = new Area(3104, 3432, 3106, 3434);
    private boolean isCooking = false;

    @Override
    public boolean isValid() {
        boolean hasRaw = Inventory.contains("Raw trout", "Raw salmon");
        boolean inventoryWasFull = Inventory.isFull() || isCooking;
        
        // Reset cooking flag when no raw fish left
        if (!hasRaw) {
            isCooking = false;
        }
        
        return inventoryWasFull && hasRaw;
    }

    public CookBranch() {
        addLeaves(new CookAllLeaf(), new UseOnFireLeaf());
    }

    private class CookAllLeaf extends org.dreambot.api.script.frameworks.treebranch.Leaf {
        @Override
        public boolean isValid() {
            return ItemProcessing.isOpen();
        }

        @Override
        public int onLoop() {
            String fish = Inventory.contains("Raw salmon") ? "Raw salmon" : "Raw trout";
            Logger.log("[Cook] Cooking all " + fish);
            
            if (ItemProcessing.makeAll(fish)) {
                isCooking = true;
                Sleep.sleepUntil(() -> !Inventory.contains("Raw trout", "Raw salmon") || !Players.getLocal().isAnimating(),
                        () -> Players.getLocal().isAnimating(), 60_000, 600);
            }
            return AntiBanUtil.reactionDelay();
        }
    }

    private class UseOnFireLeaf extends org.dreambot.api.script.frameworks.treebranch.Leaf {
        @Override
        public boolean isValid() {
            return Inventory.contains("Raw trout", "Raw salmon") 
                   && !ItemProcessing.isOpen() 
                   && !isCooking;
        }

        @Override
        public int onLoop() {
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
            
            String rawFish = Inventory.contains("Raw salmon") ? "Raw salmon" : "Raw trout";
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
