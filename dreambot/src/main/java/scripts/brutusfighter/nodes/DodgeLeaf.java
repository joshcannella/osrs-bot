package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Highest combat priority: detect Brutus overhead text and dodge.
 * *growls* = charge (walk 3 tiles perpendicular)
 * *snorts* = slam (walk 3 tiles diagonally away)
 */
public class DodgeLeaf extends Leaf {

    @Override
    public boolean isValid() {
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return false;
        String overhead = brutus.getOverhead();
        return BrutusConstants.CHARGE_OVERHEAD.equals(overhead)
            || BrutusConstants.SLAM_OVERHEAD.equals(overhead);
    }

    @Override
    public int onLoop() {
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return AntiBanUtil.humanDelay(600, 1200);

        Tile myTile = Players.getLocal().getTile();
        Tile brutusTile = brutus.getTile();

        // Move 3 tiles away — prefer diagonal/perpendicular to Brutus
        int dx = myTile.getX() - brutusTile.getX();
        int dy = myTile.getY() - brutusTile.getY();

        // Default: move south-east (away and diagonal)
        int moveX = dx >= 0 ? 3 : -3;
        int moveY = dy >= 0 ? 3 : -3;

        Tile dodgeTile = myTile.translate(moveX, moveY);
        Logger.log("[Brutus] Dodging special! Moving to " + dodgeTile);
        Walking.walkExact(dodgeTile);

        return AntiBanUtil.humanDelay(600, 900);
    }
}
