package scripts.brutusfighter;

import org.dreambot.api.methods.map.Area;
import org.dreambot.api.methods.map.Tile;

/**
 * Shared constants for the Brutus fighter script.
 */
public final class BrutusConstants {

    private BrutusConstants() {}

    // NPC
    public static final String BRUTUS_NAME = "Brutus";

    // Location
    public static final Area COW_FIELD = new Area(3250, 3270, 3275, 3310);
    public static final Tile FIGHT_TILE = new Tile(3266, 3297, 0); // east of spawn — prevents charge

    // Overhead text for special attacks
    public static final String CHARGE_OVERHEAD = "*growls*";
    public static final String SLAM_OVERHEAD = "*snorts*";

    // Food
    public static final String[] FOOD_NAMES = {"Lobster", "Salmon", "Trout"};
    public static final int FOOD_COUNT = 20;
    public static final int EAT_HP_PERCENT = 50;

    // Loot
    public static final String[] LOOT_NAMES = {
        "Raw t-bone steak", "Mooleta", "Cow slippers", "Bottomless milk bucket (empty)",
        "Clue scroll (beginner)", "Clue scroll (easy)",
        "Iron full helm", "Iron platebody", "Iron platelegs", "Iron plateskirt",
        "Iron arrow", "Air rune", "Mind rune", "Chaos rune",
        "Cowhide", "Oak logs", "Logs", "Coins"
    };
    public static final String BULL_BONES = "Bull bones";

    // Cowbell
    public static final String COWBELL_AMULET = "Cowbell amulet";
}
