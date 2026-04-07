package scripts.draynorfisher;

import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.methods.skills.Skills;
import org.dreambot.api.methods.tabs.Tabs;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import org.dreambot.api.utilities.Logger;
import scripts.draynorfisher.nodes.BankBranch;
import scripts.draynorfisher.nodes.FishLeaf;
import scripts.shared.antiban.AntiBanNode;

import java.awt.*;

@ScriptManifest(name = "draynor-fisher", author = "osrs-bot", version = 0.1,
                description = "F2P net fishing at Draynor Village - banks shrimps/anchovies",
                category = Category.FISHING)
public class DraynorFisherScript extends TreeScript {

    private static final int TARGET_LEVEL = 20;

    @Override
    public void onStart() {
        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.FISHING);

        addBranches(ab, new BankBranch(), new FishLeaf());
    }

    @Override
    public int onLoop() {
        if (Skills.getRealLevel(Skill.FISHING) >= TARGET_LEVEL) {
            Logger.log("[Fisher] Reached level " + TARGET_LEVEL + " - logging out");
            Tabs.logout();
            stop();
            return 600;
        }
        return super.onLoop();
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("Draynor Fisher (target: Lv" + TARGET_LEVEL + ")", 25, 170);
        g.drawString("Fishing: " + Skills.getRealLevel(Skill.FISHING), 25, 185);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 200);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 215);
    }
}
