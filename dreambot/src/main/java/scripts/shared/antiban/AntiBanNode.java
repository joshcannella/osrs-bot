package scripts.shared.antiban;

import org.dreambot.api.methods.interactive.Players;
import org.dreambot.api.methods.input.Camera;
import org.dreambot.api.methods.tabs.Tab;
import org.dreambot.api.methods.tabs.Tabs;
import org.dreambot.api.script.TaskNode;
import org.dreambot.api.utilities.Logger;

/**
 * High-priority anti-ban node. Fires probabilistically to perform
 * ambient human-like actions: camera rotation, tab switching, short pauses.
 * Register in onStart() of every TaskScript.
 */
public class AntiBanNode extends TaskNode {

    private long lastActionTime = System.currentTimeMillis();
    private static final long MIN_INTERVAL_MS = 15_000;

    @Override
    public int priority() {
        return 100;
    }

    @Override
    public boolean accept() {
        long elapsed = System.currentTimeMillis() - lastActionTime;
        if (elapsed < MIN_INTERVAL_MS) return false;
        return Math.random() < 0.08;
    }

    @Override
    public int execute() {
        lastActionTime = System.currentTimeMillis();
        int action = (int) (Math.random() * 4);
        switch (action) {
            case 0:
                Logger.log("[AntiBan] Rotating camera");
                Camera.rotateTo(Camera.getYaw() + (int) (Math.random() * 120 - 60), Camera.getPitch());
                break;
            case 1:
                Logger.log("[AntiBan] Checking stats tab");
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
