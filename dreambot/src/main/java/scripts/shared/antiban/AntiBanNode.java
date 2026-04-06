package scripts.shared.antiban;

import org.dreambot.api.methods.input.Camera;
import org.dreambot.api.methods.tabs.Tab;
import org.dreambot.api.methods.tabs.Tabs;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;

/**
 * Anti-ban leaf node for TreeScript. Add to any branch.
 * Fires probabilistically (~8% of ticks, min 15s apart).
 * Actions: camera rotation, tab switching, short pauses.
 *
 * Also works standalone — call isValid() + onLoop() from AbstractScript/TaskScript.
 */
public class AntiBanNode extends Leaf {

    private long lastActionTime = System.currentTimeMillis();
    private static final long MIN_INTERVAL_MS = 15_000;

    @Override
    public boolean isValid() {
        long elapsed = System.currentTimeMillis() - lastActionTime;
        if (elapsed < MIN_INTERVAL_MS) return false;
        return Math.random() < 0.08;
    }

    @Override
    public int onLoop() {
        lastActionTime = System.currentTimeMillis();
        int action = (int) (Math.random() * 4);
        switch (action) {
            case 0:
                Logger.log("[AntiBan] Rotating camera");
                Camera.rotateTo(Camera.getYaw() + (int) (Math.random() * 120 - 60), Camera.getPitch());
                break;
            case 1:
                Logger.log("[AntiBan] Checking skills tab");
                Tabs.open(Tab.SKILLS);
                AntiBanUtil.hesitate();
                Tabs.open(Tab.INVENTORY);
                break;
            case 2:
                Logger.log("[AntiBan] Short idle pause");
                break;
            case 3:
                Logger.log("[AntiBan] Checking quest tab");
                Tabs.open(Tab.QUEST);
                AntiBanUtil.hesitate();
                Tabs.open(Tab.INVENTORY);
                break;
        }
        return AntiBanUtil.humanDelay(800, 2500);
    }
}
