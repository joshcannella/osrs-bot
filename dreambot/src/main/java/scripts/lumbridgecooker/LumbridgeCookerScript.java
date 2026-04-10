package scripts.lumbridgecooker;

import org.dreambot.api.methods.skills.Skill;
import org.dreambot.api.script.Category;
import org.dreambot.api.script.ScriptManifest;
import org.dreambot.api.script.frameworks.treebranch.TreeScript;
import org.dreambot.api.utilities.Logger;
import scripts.lumbridgecooker.nodes.BankBranch;
import scripts.lumbridgecooker.nodes.CookBranch;
import scripts.shared.antiban.AntiBanNode;

import javax.swing.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

@ScriptManifest(name = "lumbridge-cooker", author = "osrs-bot", version = 0.2,
                description = "Cooks food at Lumbridge castle range and banks",
                category = Category.COOKING)
public class LumbridgeCookerScript extends TreeScript {

    private List<CookableFood> selectedFoods = new ArrayList<>();
    private boolean useUpstairsBank = true;

    public List<CookableFood> getSelectedFoods() { return selectedFoods; }
    public boolean useUpstairsBank() { return useUpstairsBank; }

    @Override
    public void onStart() {
        if (!showGui()) {
            Logger.log("No food selected or GUI cancelled - stopping");
            stop();
            return;
        }

        Logger.log("Cooking: " + selectedFoods);
        Logger.log("Bank: " + (useUpstairsBank ? "upstairs" : "downstairs"));

        AntiBanNode ab = new AntiBanNode();
        ab.setSkillsToCheck(Skill.COOKING);

        addBranches(ab, new CookBranch(this), new BankBranch(this));
    }

    @Override
    public void onPaint(Graphics2D g) {
        g.setColor(Color.WHITE);
        g.drawString("Lumbridge Cooker", 25, 170);
        g.drawString("Branch: " + getCurrentBranchName(), 25, 185);
        g.drawString("Leaf: " + getCurrentLeafName(), 25, 200);
    }

    private boolean showGui() {
        AtomicBoolean started = new AtomicBoolean(false);

        try {
            SwingUtilities.invokeAndWait(() -> {
                JDialog dialog = new JDialog();
                dialog.setTitle("Lumbridge Cooker");
                dialog.setModal(true);
                dialog.setLayout(new BorderLayout(10, 10));

                // Food checkboxes
                JPanel foodPanel = new JPanel(new GridLayout(0, 2, 5, 5));
                foodPanel.setBorder(BorderFactory.createTitledBorder("Select Food"));
                JCheckBox[] boxes = new JCheckBox[CookableFood.values().length];
                for (int i = 0; i < CookableFood.values().length; i++) {
                    CookableFood food = CookableFood.values()[i];
                    boxes[i] = new JCheckBox(food.getRawName());
                    foodPanel.add(boxes[i]);
                }

                // Bank location
                JPanel bankPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
                bankPanel.setBorder(BorderFactory.createTitledBorder("Bank Location"));
                JRadioButton upstairs = new JRadioButton("Upstairs (2nd floor)", true);
                JRadioButton downstairs = new JRadioButton("Downstairs (ground floor)");
                ButtonGroup bg = new ButtonGroup();
                bg.add(upstairs);
                bg.add(downstairs);
                bankPanel.add(upstairs);
                bankPanel.add(downstairs);

                // Start button
                JButton startBtn = new JButton("Start");
                startBtn.addActionListener(e -> {
                    for (int i = 0; i < boxes.length; i++) {
                        if (boxes[i].isSelected()) {
                            selectedFoods.add(CookableFood.values()[i]);
                        }
                    }
                    useUpstairsBank = upstairs.isSelected();
                    started.set(!selectedFoods.isEmpty());
                    dialog.dispose();
                });

                dialog.add(foodPanel, BorderLayout.CENTER);
                dialog.add(bankPanel, BorderLayout.NORTH);
                dialog.add(startBtn, BorderLayout.SOUTH);
                dialog.pack();
                dialog.setLocationRelativeTo(null);
                dialog.setVisible(true);
            });
        } catch (Exception e) {
            Logger.error("GUI error: " + e.getMessage());
        }

        return started.get();
    }
}
