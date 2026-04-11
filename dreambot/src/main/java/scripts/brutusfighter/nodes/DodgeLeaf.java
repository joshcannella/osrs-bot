package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Map;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;

/**
 * Dodge Brutus specials by moving diagonally away from him.
 * Charge (*growls*): 3-tick (1.8s) dodge window.
 * Slam (*snorts*): 4-tick (2.4s) dodge window, slams 3 times.
 * We dodge diagonally (away + sideways) and wait for the full attack to finish
 * before the tree hands control back to AttackLeaf for repositioning.
 */
public class DodgeLeaf extends Leaf {

    private long lastDodgeTime = 0;
    private static final long CHARGE_WAIT = 2400; // 4 ticks — safe margin over 3-tick window
    private static final long SLAM_WAIT   = 5400; // 9 ticks — 3 slams at ~3 ticks each

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
        Logger.log("[Dodge] Player at " + myTile);

        // Dodge diagonally: move away from Brutus on both axes.
        // East of Brutus → go further east (+1 x) and north or south on y.
        int dx = 0;
        int dy;
        if (brutus != null) {
            Tile bTile = brutus.getTile();
            // Move away on X axis
            dx = myTile.getX() >= bTile.getX() ? 1 : -1;
            // Move away on Y axis — pick direction away from Brutus
            dy = myTile.getY() >= bTile.getY() ? 1 : -1;
        } else {
            dy = Math.random() < 0.5 ? 1 : -1;
        }

        Tile dodgeTile = myTile.translate(dx, dy);
        Logger.log("[Dodge] Dodging to " + dodgeTile);

        if (Map.isTileOnScreen(dodgeTile)) {
            Map.interact(dodgeTile, "Walk here");
        } else {
            Walking.clickTileOnMinimap(dodgeTile);
        }
        lastDodgeTime = System.currentTimeMillis();

        // Wait for the attack to fully resolve before returning control
        long wait = isSlamAttack ? SLAM_WAIT : CHARGE_WAIT;
        return (int) wait;
    }
}
