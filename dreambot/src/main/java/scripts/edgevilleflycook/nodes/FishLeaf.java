package scripts.edgevilleflycook.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.shared.antiban.AntiBanUtil;

public class FishLeaf extends Leaf {

    private static final Area FISH_AREA = new Area(3101, 3424, 3110, 3435);

    @Override
    public boolean isValid() {
        return !Inventory.isFull() && !Inventory.contains("Raw trout", "Raw salmon");
    }

    @Override
    public int onLoop() {
        if (Players.getLocal().isAnimating()) {
            return AntiBanUtil.humanDelay(600, 1200);
        }

        if (!Inventory.contains("Feather")) {
            Logger.error("[Fish] Out of feathers! Stopping.");
            return -1;
        }

        if (!FISH_AREA.contains(Players.getLocal())) {
            Logger.log("[Fish] Walking to Edgeville fishing spot");
            if (Walking.shouldWalk()) Walking.walk(FISH_AREA);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        NPC spot = NPCs.closest(n -> n != null
                && n.getName() != null
                && n.getName().equals("Rod Fishing spot")
                && n.hasAction("Lure"));

        if (spot == null) {
            Logger.log("[Fish] No Rod Fishing spot with 'Lure' action found");
            return AntiBanUtil.humanDelay(1000, 2000);
        }

        if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
        Logger.log("[Fish] Fly fishing at spot");
        if (spot.interact("Lure")) {
            Sleep.sleepUntil(() -> Players.getLocal().isAnimating(),
                    () -> Players.getLocal().isMoving(), 5000, 600);
        }

        return AntiBanUtil.humanDelay(600, 1200);
    }
}
