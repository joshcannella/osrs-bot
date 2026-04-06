package scripts.antibantest;

import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import scripts.antibantest.nodes.TestCycleBranch;
import scripts.shared.antiban.AntiBanNode;

import java.awt.*;

/**
 * Test script that exercises every AntiBan feature.
 *
 * Cycles through AntiBanUtil methods one at a time, logging results.
 * AntiBanNode runs as first branch for ambient action testing.
 *
 * Stand anywhere in-game and start — no requirements.
 */
@ScriptManifest(name = "antiban-test", author = "osrs-bot", version = 0.1,
                description = "Tests all anti-ban functionality", category = Category.MISC)
public class AntiBanTestScript extends TreeScript {

    @Override
    public void onStart() {
        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.HITPOINTS, Skill.ATTACK, Skill.STRENGTH);
        ab.setMinInterval(10_000);   // faster triggering for testing
        ab.setTriggerRate(0.15);     // higher rate for testing

        addBranches(ab, new TestCycleBranch());
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("AntiBan Test Script", 25, 170);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 185);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 200);
    }
}
