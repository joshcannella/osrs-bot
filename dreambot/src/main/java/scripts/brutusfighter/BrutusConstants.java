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
    public static final Tile FIGHT_TILE = new Tile(13472, 2424, 0);
    public static final Tile DODGE_NORTH = new Tile(13472, 2426, 0);
    public static final Tile DODGE_SOUTH = new Tile(13472, 2422, 0);
    public static final Tile GATE_TILE = new Tile(3263, 3297, 0); // near the pen gate

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
        "Air rune", "Mind rune", "Chaos rune", "Coins"
    };
    public static final String BULL_BONES = "Bull bones";

    // Cowbell
    public static final String COWBELL_AMULET = "Cowbell amulet";
}
