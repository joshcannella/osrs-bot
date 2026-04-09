package scripts.edgevilleflycook;

import org.dreambot.api.methods.container.impl.Inventory;
import org.dreambot.api.methods.container.impl.equipment.Equipment;
import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.methods.skills.Skills;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import org.dreambot.api.utilities.Logger;
import scripts.edgevilleflycook.nodes.BankBranch;
import scripts.edgevilleflycook.nodes.CookBranch;
import scripts.edgevilleflycook.nodes.FishLeaf;
import scripts.shared.antiban.AntiBanNode;

import java.awt.*;

@ScriptManifest(name = "edgeville-flycook", author = "osrs-bot", version = 0.1,
                description = "Fly fishes trout/salmon at Edgeville river and cooks on nearby fire",
                category = Category.FISHING)
public class EdgevilleFlyFishCookScript extends TreeScript {

    @Override
    public void onStart() {
        // Check requirements
        if (!Inventory.contains("Fly fishing rod") && !Equipment.contains("Fly fishing rod")) {
            Logger.error("Fly fishing rod not found! Please equip or have in inventory.");
            stop();
            return;
        }
        if (!Inventory.contains("Feather")) {
            Logger.error("Feathers not found! Please have feathers in inventory.");
            stop();
            return;
        }

        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.FISHING, Skill.COOKING);

        addBranches(ab, new BankBranch(), new CookBranch(), new scripts.edgevilleflycook.nodes.leaves.DropBurntLeaf(), new FishLeaf());
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("Edgeville Fly Fisher & Cook", 25, 170);
        g.drawString("Fishing: " + Skills.getRealLevel(Skill.FISHING), 25, 185);
        g.drawString("Cooking: " + Skills.getRealLevel(Skill.COOKING), 25, 200);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 215);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 230);
    }
}
