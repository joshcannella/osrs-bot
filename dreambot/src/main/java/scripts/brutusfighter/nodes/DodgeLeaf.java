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
 * Dodge Brutus specials by sidestepping 1 tile north or south.
 * Charge (*growls*): 3-tick window — step north/south, wait for charge to pass.
 * Slam (*snorts*): 4-tick window, 3 slams — step away, wait for all slams to finish.
 */
public class DodgeLeaf extends Leaf {

    private long lastDodgeTime = 0;
    private boolean isSlamAttack = false;

    @Override
    public boolean isValid() {
        if (System.currentTimeMillis() - lastDodgeTime < 3000) return false;
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return false;
        String overhead = brutus.getOverhead();
        if (overhead == null) return false;
        if (overhead.contains("growl") || overhead.contains("snort")) {
            isSlamAttack = overhead.contains("snort");
            Logger.log("[Dodge] Brutus overhead: '" + overhead + "'");
            return true;
        }
        return false;
    }

    @Override
    public int onLoop() {
        Tile myTile = Players.getLocal().getTile();
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        Logger.log("[Dodge] Player at " + myTile + " attack=" + (isSlamAttack ? "slam" : "charge"));

        // Sidestep 1 tile north or south — pick direction away from Brutus Y
        int dy = 1;
        if (brutus != null) {
            dy = myTile.getY() >= brutus.getTile().getY() ? 1 : -1;
        }

        Tile dodgeTile = myTile.translate(0, dy);
        Logger.log("[Dodge] Sidestepping to " + dodgeTile);

        if (Map.isTileOnScreen(dodgeTile)) {
            Map.interact(dodgeTile, "Walk here");
        } else {
            Walking.clickTileOnMinimap(dodgeTile);
        }

        // Wait until we've moved
        Sleep.sleepUntil(() -> Players.getLocal().getTile().distance(dodgeTile) < 1, 1200);

        lastDodgeTime = System.currentTimeMillis();

        // Short return so the tree re-evaluates quickly — EatLeaf can fire if needed.
        // The 3s cooldown in isValid() prevents re-dodging the same attack.
        return 600;
    }
}
