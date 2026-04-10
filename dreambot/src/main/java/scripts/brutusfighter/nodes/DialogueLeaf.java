package scripts.brutusfighter.nodes;

import org.dreambot.api.methods.dialogues.Dialogues;
import org.dreambot.api.script.frameworks.treebranch.Leaf;
import org.dreambot.api.utilities.Logger;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Handles dialogue interrupts (level-up, release confirmation, etc.).
 */
public class DialogueLeaf extends Leaf {

    @Override
    public boolean isValid() {
        return Dialogues.inDialogue();
    }

    @Override
    public int onLoop() {
        if (Dialogues.canContinue()) {
            Logger.log("[Brutus] Continuing dialogue");
            Dialogues.continueDialogue();
        } else if (Dialogues.areOptionsAvailable()) {
            Logger.log("[Brutus] Choosing Yes option");
            Dialogues.chooseFirstOptionContaining("Yes");
        }
        return AntiBanUtil.humanDelay(600, 1200);
    }
}
