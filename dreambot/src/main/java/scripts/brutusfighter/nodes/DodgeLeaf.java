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

    private long lastDodgeTime = 0;

    @Override
    public boolean isValid() {
        if (System.currentTimeMillis() - lastDodgeTime < 3000) return false;
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

        String overhead = brutus.getOverhead();
        Tile myTile = Players.getLocal().getTile();

        Tile dodgeTile;
        if (overhead != null && overhead.contains("growl")) {
            // Charge — dodge north or south (perpendicular)
            int dy = myTile.getY() >= brutus.getTile().getY() ? 2 : -2;
            dodgeTile = myTile.translate(0, dy);
            Logger.log("[Dodge] Charge! Sidestepping to " + dodgeTile);
        } else {
            // Slam — dodge 1 tile diagonally
            int dx = myTile.getX() >= brutus.getTile().getX() ? 1 : -1;
            int dy = myTile.getY() >= brutus.getTile().getY() ? 1 : -1;
            dodgeTile = myTile.translate(dx, dy);
            Logger.log("[Dodge] Slam! Moving diagonally to " + dodgeTile);
        }

        Walking.walkOnScreen(dodgeTile);
        lastDodgeTime = System.currentTimeMillis();

        return AntiBanUtil.humanDelay(600, 900);
    }
}
