package scripts.shared;

import org.dreambot.api.script.AbstractScript;

/**
 * Shared state container for TaskScript nodes. Pass to each node via constructor
 * so they can read/write shared data without static fields.
 *
 * Extend this class per-script to add script-specific fields.
 *
 * Usage:
 *   public class FishContext extends ScriptContext {
 *       public boolean inventoryFull = false;
 *       public FishContext(AbstractScript s) { super(s); }
 *   }
 *
 *   // In main script onStart():
 *   FishContext ctx = new FishContext(this);
 *   addNodes(new AntiBanNode(), new FishNode(ctx), new DropNode(ctx));
 *
 *   // In node constructor:
 *   public FishNode(FishContext ctx) { this.ctx = ctx; }
 */
public class ScriptContext {

    private final AbstractScript script;
    private int stuckCounter = 0;
    private static final int MAX_STUCK = 10;

    public ScriptContext(AbstractScript script) {
        this.script = script;
    }

    public AbstractScript getScript() { return script; }

    /** Call after a successful action to reset stuck counter. */
    public void resetStuck() { stuckCounter = 0; }

    /** Call after a failed/no-progress tick. Returns true if stuck limit reached. */
    public boolean incrementStuck() {
        stuckCounter++;
        return stuckCounter >= MAX_STUCK;
    }

    public int getStuckCounter() { return stuckCounter; }
}
