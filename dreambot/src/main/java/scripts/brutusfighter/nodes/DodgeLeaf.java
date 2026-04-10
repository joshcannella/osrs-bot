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
 * Dodge Brutus specials by moving to fixed north/south tiles.
 * Standing east of spawn prevents charge, but we still dodge it just in case.
 * After dodging, AttackLeaf handles repositioning back to FIGHT_TILE.
 */
public class DodgeLeaf extends Leaf {

    private long lastDodgeTime = 0;
    private boolean dodgeNorth = true; // alternate dodge direction

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
        // Pick north or south, alternate each time
        Tile dodgeTile = dodgeNorth ? BrutusConstants.DODGE_NORTH : BrutusConstants.DODGE_SOUTH;
        dodgeNorth = !dodgeNorth;

        Logger.log("[Dodge] Moving to " + (dodgeNorth ? "south" : "north") + " dodge tile");
        Walking.walkOnScreen(dodgeTile);
        lastDodgeTime = System.currentTimeMillis();

        return AntiBanUtil.humanDelay(600, 900);
    }
}
