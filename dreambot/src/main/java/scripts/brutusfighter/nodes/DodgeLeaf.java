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

public class DodgeLeaf extends Leaf {

    @Override
    public boolean isValid() {
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return false;
        String overhead = brutus.getOverhead();
        if (overhead != null && !overhead.isEmpty()) {
            Logger.log("[Dodge] Brutus overhead: '" + overhead + "'");
        }
        return overhead != null
            && (overhead.contains("growl") || overhead.contains("snort"));
    }

    @Override
    public int onLoop() {
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        if (brutus == null) return AntiBanUtil.humanDelay(600, 1200);

        Tile myTile = Players.getLocal().getTile();
        Tile brutusTile = brutus.getTile();

        int dx = myTile.getX() - brutusTile.getX();
        int dy = myTile.getY() - brutusTile.getY();

        int moveX = dx >= 0 ? 2 : -2;
        int moveY = dy >= 0 ? 2 : -2;

        Tile dodgeTile = myTile.translate(moveX, moveY);
        Logger.log("[Dodge] Dodging special! Moving to " + dodgeTile);
        Walking.walkOnScreen(dodgeTile);

        return AntiBanUtil.humanDelay(600, 900);
    }
}
