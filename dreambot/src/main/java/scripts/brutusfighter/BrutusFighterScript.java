package scripts.brutusfighter;

import org.dreambot.api.methods.combat.Combat;
import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import org.dreambot.api.utilities.Logger;
import scripts.brutusfighter.nodes.*;
import scripts.shared.antiban.AntiBanNode;

import java.awt.*;

@ScriptManifest(name = "brutus-fighter", author = "osrs-bot", version = 0.23,
                description = "Fights Brutus cow boss - dodges specials, eats, loots, banks",
                category = Category.COMBAT)
public class BrutusFighterScript extends TreeScript {

    private int killCount = 0;
    private boolean inInstance = false;
    private long instanceEntryTime = 0;

    @Override
    public void onStart() {
        Logger.log("[Brutus] Starting Brutus Fighter");

        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.ATTACK, Skill.STRENGTH, Skill.DEFENCE, Skill.HITPOINTS);
        ab.setTriggerRate(0.02);     // 2% — rarely fire during active combat
        ab.setMinInterval(45_000);   // 45s minimum between ambient actions

        addBranches(
            ab,
            new DialogueLeaf(),
            new DodgeLeaf(),
            new EatLeaf(),
            new BankBranch(),
            new LootLeaf(),
            new RingCowbellLeaf(),
            new AttackLeaf()
        );
    }

    public void incrementKills() { killCount++; }
    public boolean isInInstance() { return inInstance; }
    public void setInInstance(boolean in) {
        this.inInstance = in;
        if (in) this.instanceEntryTime = System.currentTimeMillis();
    }
    public boolean canLeaveInstance() {
        return inInstance && (System.currentTimeMillis() - instanceEntryTime) > 15000;
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("Brutus Fighter", 25, 170);
        g.drawString("Kills: " + killCount, 25, 185);
        g.drawString("HP: " + Combat.getHealthPercent() + "%", 25, 200);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 215);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 230);
    }
}
