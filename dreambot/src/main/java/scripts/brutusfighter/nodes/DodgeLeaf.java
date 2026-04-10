package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.map.Map;
import org.dreambot.api.methods.map.Tile;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.methods.walking.impl.Walking;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.NPC;
import scripts.brutusfighter.BrutusConstants;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Dodge Brutus specials by moving to fixed north/south tiles.
 * Standing east of spawn prevents charge, but we still dodge it just in case.
 * After dodging, AttackLeaf handles repositioning back to FIGHT_TILE.
 */
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
        // Log player position for debugging instance coords
        Tile myTile = Players.getLocal().getTile();
        NPC brutus = NPCs.closest(BrutusConstants.BRUTUS_NAME);
        Logger.log("[Dodge] Player at " + myTile);

        // Dodge north or south — pick direction away from nearest fence
        // If player is north of Brutus, dodge south (away from north fence)
        // If player is south of Brutus, dodge north (away from south fence)
        int dy;
        if (brutus != null) {
            dy = myTile.getY() > brutus.getTile().getY() ? -2 : 2;
        } else {
            dy = Math.random() < 0.5 ? 2 : -2;
        }
        Tile dodgeTile = myTile.translate(0, dy);

        Logger.log("[Dodge] Dodging to " + dodgeTile + " onScreen=" + Map.isTileOnScreen(dodgeTile) + " onMap=" + Map.isTileOnMap(dodgeTile));
        if (Map.isTileOnScreen(dodgeTile)) {
            Map.interact(dodgeTile, "Walk here");
        } else if (Map.isTileOnMap(dodgeTile)) {
            Walking.clickTileOnMinimap(dodgeTile);
        } else {
            // Last resort — just click minimap with relative tile
            Walking.clickTileOnMinimap(dodgeTile);
        }
        lastDodgeTime = System.currentTimeMillis();

        return AntiBanUtil.humanDelay(600, 900);
    }
}
