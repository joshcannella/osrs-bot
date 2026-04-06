package scripts.shared.antiban;

import org.dreambot.api.utilities.Sleep;
import org.dreambot.api.methods.Calculations;

/**
 * Static utility methods for inline anti-ban within TaskNodes.
 * Use these instead of raw Calculations.random() for action delays.
 */
public final class AntiBanUtil {

    private AntiBanUtil() {}

    /** Randomized delay with occasional outliers for human-like timing. */
    public static int humanDelay(int baseMin, int baseMax) {
        if (Math.random() < 0.05) {
            return Calculations.random(baseMax, baseMax * 3);
        }
        return Calculations.random(baseMin, baseMax);
    }

    /** ~10% chance of returning true — use before actions for hesitation. */
    public static boolean shouldHesitate() {
        return Math.random() < 0.10;
    }

    /** Small random pause (200-800ms). Call when shouldHesitate() is true. */
    public static void hesitate() {
        Sleep.sleep(Calculations.random(200, 800));
    }

    /**
     * Context-aware sleep time. Returns appropriate delay based on what the bot is doing.
     * @param context "clicking", "waiting", or "idle"
     */
    public static int conditionSleep(String context) {
        switch (context) {
            case "clicking":
                return Calculations.random(100, 300);
            case "waiting":
                return Calculations.random(500, 1000);
            case "idle":
                return Calculations.random(2000, 5000);
            default:
                return Calculations.random(300, 600);
        }
    }
}
