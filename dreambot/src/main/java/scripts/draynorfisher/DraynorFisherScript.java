package scripts.draynorfisher;

import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import scripts.draynorfisher.nodes.BankBranch;
import scripts.draynorfisher.nodes.FishLeaf;
import scripts.shared.antiban.AntiBanNode;

import java.awt.*;

@ScriptManifest(name = "draynor-fisher", author = "osrs-bot", version = 0.1,
                description = "F2P net fishing at Draynor Village - banks shrimps/anchovies",
                category = Category.FISHING)
public class DraynorFisherScript extends TreeScript {

    @Override
    public void onStart() {
        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.FISHING);

        addBranches(ab, new BankBranch(), new FishLeaf());
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("Draynor Fisher", 25, 170);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 185);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 200);
    }
}
