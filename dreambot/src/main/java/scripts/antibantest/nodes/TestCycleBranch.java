package scripts.antibantest.nodes;

import org.dreambot.api.methods.interactive.GameObjects;
import org.dreambot.api.methods.interactive.NPCs;
import org.dreambot.api.script.frameworks.treebranch.Branch;
import org.dreambot.api.utilities.Logger;
import org.dreambot.api.wrappers.interactive.Entity;
import scripts.shared.antiban.AntiBanUtil;

/**
 * Cycles through each AntiBanUtil method, testing one per loop.
 * Logs results so you can verify each feature works.
 */
public class TestCycleBranch extends Branch {

    private int testIndex = 0;
    private final long startTime = System.currentTimeMillis();
    private static final int NUM_TESTS = 12;

    public TestCycleBranch() {
        addLeaves(new TestLeaf());
    }

    @Override
    public boolean isValid() {
        return true; // always valid — this is the only action branch
    }

    /**
     * Single leaf that runs the current test based on testIndex.
     */
    public class TestLeaf extends org.dreambot.api.script.frameworks.treebranch.Leaf {

        @Override
        public boolean isValid() {
            return true;
        }

        @Override
        public int onLoop() {
            int test = testIndex % NUM_TESTS;
            testIndex++;

            Logger.log("═══════════════════════════════════════");
            Logger.log("[Test " + test + "/" + NUM_TESTS + "] " + testName(test));
            Logger.log("═══════════════════════════════════════");

            switch (test) {
                case 0: return testHumanDelay();
                case 1: return testFatigueDelay();
                case 2: return testReactionDelay();
                case 3: return testHesitate();
                case 4: return testMisclick();
                case 5: return testIdleWatch();
                case 6: return testHoverNextTarget();
                case 7: return testGlanceInventory();
                case 8: return testRightClickCancel();
                case 9: return testCheckRunEnergy();
                case 10: return testGlanceChat();
                case 11: return testInteractionVariation();
                default: return AntiBanUtil.humanDelay(600, 1200);
            }
        }

        private String testName(int i) {
            switch (i) {
                case 0: return "humanDelay()";
                case 1: return "fatigueDelay()";
                case 2: return "reactionDelay()";
                case 3: return "shouldHesitate() + hesitate()";
                case 4: return "shouldMisclick() + misclick()";
                case 5: return "idleWatch()";
                case 6: return "hoverNextTarget()";
                case 7: return "glanceInventory()";
                case 8: return "rightClickCancel()";
                case 9: return "checkRunEnergy()";
                case 10: return "glanceChat()";
                case 11: return "shouldForceRightClick()";
                default: return "unknown";
            }
        }

        // ── Individual tests ─────────────────────────────────────────

        private int testHumanDelay() {
            int d1 = AntiBanUtil.humanDelay(500, 1000);
            int d2 = AntiBanUtil.humanDelay(500, 1000);
            int d3 = AntiBanUtil.humanDelay(500, 1000);
            Logger.log("  humanDelay(500,1000) = " + d1 + ", " + d2 + ", " + d3);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testFatigueDelay() {
            int d1 = AntiBanUtil.fatigueDelay(startTime, 500, 1000);
            int d2 = AntiBanUtil.fatigueDelay(startTime, 500, 1000, 60); // 1hr curve
            long fakeOld = startTime - (240 * 60_000L); // simulate 4hrs in
            int d3 = AntiBanUtil.fatigueDelay(fakeOld, 500, 1000);
            Logger.log("  fatigueDelay now=" + d1 + ", 1hr-curve=" + d2 + ", 4hrs-in=" + d3);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testReactionDelay() {
            int d1 = AntiBanUtil.reactionDelay();
            int d2 = AntiBanUtil.reactionDelay();
            int d3 = AntiBanUtil.reactionDelay();
            Logger.log("  reactionDelay() = " + d1 + ", " + d2 + ", " + d3);
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testHesitate() {
            boolean h1 = AntiBanUtil.shouldHesitate();
            boolean h2 = AntiBanUtil.shouldHesitate();
            boolean h3 = AntiBanUtil.shouldHesitate();
            Logger.log("  shouldHesitate() = " + h1 + ", " + h2 + ", " + h3);
            if (h1 || h2 || h3) {
                Logger.log("  Executing hesitate()...");
                AntiBanUtil.hesitate();
                Logger.log("  hesitate() done");
            } else {
                Logger.log("  No hesitation triggered (expected ~10% rate)");
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testMisclick() {
            boolean m = AntiBanUtil.shouldMisclick();
            Logger.log("  shouldMisclick() = " + m + " (expected ~3% rate)");
            Entity target = findAnyEntity();
            if (target != null) {
                Logger.log("  Found target: " + target.getName());
                // Force a misclick for testing regardless of shouldMisclick result
                AntiBanUtil.misclick(target);
                Logger.log("  misclick() executed — check that it clicked wrong then paused");
            } else {
                Logger.log("  No nearby entity to test misclick on");
            }
            return AntiBanUtil.humanDelay(1500, 3000);
        }

        private int testIdleWatch() {
            Entity next = findAnyEntity();
            Logger.log("  idleWatch(2000) with next=" + (next != null ? next.getName() : "null"));
            AntiBanUtil.idleWatch(2000, next);
            Logger.log("  idleWatch() done");
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testHoverNextTarget() {
            Entity next = findAnyEntity();
            if (next != null) {
                Logger.log("  hoverNextTarget(" + next.getName() + ")");
                AntiBanUtil.hoverNextTarget(next);
            } else {
                Logger.log("  No entity to hover");
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testGlanceInventory() {
            Logger.log("  glanceInventory()...");
            AntiBanUtil.glanceInventory();
            Logger.log("  glanceInventory() done");
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testRightClickCancel() {
            Entity target = findAnyEntity();
            Logger.log("  rightClickCancel(" + (target != null ? target.getName() : "null") + ")");
            AntiBanUtil.rightClickCancel(target);
            Logger.log("  rightClickCancel() done");
            return AntiBanUtil.humanDelay(1500, 3000);
        }

        private int testCheckRunEnergy() {
            Logger.log("  checkRunEnergy()...");
            AntiBanUtil.checkRunEnergy();
            Logger.log("  checkRunEnergy() done");
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testGlanceChat() {
            Logger.log("  glanceChat()...");
            AntiBanUtil.glanceChat();
            Logger.log("  glanceChat() done");
            return AntiBanUtil.humanDelay(600, 1200);
        }

        private int testInteractionVariation() {
            boolean r1 = AntiBanUtil.shouldForceRightClick();
            boolean r2 = AntiBanUtil.shouldForceRightClick();
            boolean r3 = AntiBanUtil.shouldForceRightClick();
            boolean m1 = AntiBanUtil.shouldUseMinimap();
            boolean m2 = AntiBanUtil.shouldUseMinimap();
            Logger.log("  shouldForceRightClick() = " + r1 + ", " + r2 + ", " + r3 + " (expected ~15%)");
            Logger.log("  shouldUseMinimap() = " + m1 + ", " + m2 + " (expected ~20%)");

            Entity target = findAnyEntity();
            if (target != null && r1) {
                Logger.log("  Testing interactForceRight on " + target.getName());
                target.interactForceRight("Examine");
            }
            return AntiBanUtil.humanDelay(600, 1200);
        }

        // ── Helper ───────────────────────────────────────────────────

        private Entity findAnyEntity() {
            Entity e = GameObjects.closest(o -> o.getName() != null
                    && !"null".equals(o.getName()) && o.distance() < 10);
            if (e != null) return e;
            return NPCs.closest(n -> n.getName() != null
                    && !"null".equals(n.getName()) && n.distance() < 10);
        }
    }
}
