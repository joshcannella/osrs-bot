package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Map;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;

/**
 * Dodge Brutus specials by sidestepping 2 tiles north or south.
 * Charge (*growls*): 3-tick window.
 * Slam (*snorts*): 4-tick window, 3 slams.
 */
public class DodgeLeaf extends Leaf {

    private long lastDodgeTime = 0;

    @Override
    public boolean isValid() {
        if (System.currentTimeMillis() - lastDodgeTime < 3000) return false;
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return false;
        String overhead = brutus.getOverhead();
        if (overhead == null) return false;
        return overhead.contains("growl") || overhead.contains("snort");
    }

    @Override
    public int onLoop() {
        Tile myTile = Players.getLocal().getTile();
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        Logger.log("[Dodge] Player at " + myTile);

        int dy = 1;
        if (brutus != null) {
            dy = myTile.getY() >= brutus.getTile().getY() ? 1 : -1;
        }

        final Tile target = myTile.translate(0, dy * 2);
        Logger.log("[Dodge] Sidestepping to " + target);

        if (Map.isTileOnScreen(target)) {
            Map.interact(target, "Walk here");
        } else {
            Walking.clickTileOnMinimap(target);
        }

        Sleep.sleepUntil(() -> Players.getLocal().getTile().distance(target) < 1, 1200);
        lastDodgeTime = System.currentTimeMillis();
        return 600;
    }
}
