package scripts.draynorfisher.nodes;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Default leaf: walk to Draynor fishing spot and net fish.
 * Valid whenever inventory is not full (fallback action).
 */
public class FishLeaf extends Leaf {

    private static final Area FISH_AREA = new Area(3083, 3226, 3091, 3233);

    @Override
    public boolean isValid() {
        return !Inventory.isFull();
    }

    @Override
    public int onLoop() {
        if (Players.getLocal().isAnimating()) {
            return AntiBanUtil.humanDelay(600, 1200);
        }

        if (!FISH_AREA.contains(Players.getLocal())) {
            Logger.log("[Fish] Walking to fishing spot");
            if (Walking.shouldWalk()) Walking.walk(FISH_AREA);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        NPC spot = NPCs.closest(n -> n != null
                && "Fishing spot".equals(n.getName())
                && FISH_AREA.contains(n));
        if (spot != null) {
            if (AntiBanUtil.shouldHesitate()) AntiBanUtil.hesitate();
            Logger.log("[Fish] Net fishing");
            spot.interact("Small Net");
        }
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
