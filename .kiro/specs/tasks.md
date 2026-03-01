# Tasks: AI-Powered ChromaScape Script Generator

## Task 1: Scaffold the `scriptgen` Project
**Implements**: NFR-5, Design §Project Layout, §Build Configuration
**Files**: `scriptgen/build.gradle.kts`, `scriptgen/settings.gradle.kts`, `settings.gradle.kts` (root)

- [x] Create `scriptgen/settings.gradle.kts` with `rootProject.name = "scriptgen"` and `includeBuild("../ChromaScape")`
- [x] Create `scriptgen/build.gradle.kts` with:
  - Java 17 toolchain
  - `implementation("com.chromascape:chromascape")` composite dependency
  - Transitive deps used directly: javacv-platform, commons-math3, log4j2
- [x] Create directory structure: `scriptgen/src/main/java/com/scriptgen/behavior/` and `scriptgen/src/main/java/com/scriptgen/scripts/`
- [x] Verify `cd scriptgen && gradle compileJava` succeeds

## Task 2: Create HumanBehavior Utility Class
**Implements**: FR-5 (all sub-requirements), Design §3
**File**: `scriptgen/src/main/java/com/scriptgen/behavior/HumanBehavior.java`

- [x] Fatigue tracking: `SESSION_START`, elapsed time calculation, fatigue multiplier (1.0 → 1.25 cap, +0.05/hr)
- [x] Tempo system: `tempoMultiplier` (0.85–1.15 random at class load), `updateTempoDrift()` shifting ±0.05 every 10-20 min
- [x] `adjustDelay(long baseMin, long baseMax)` — applies tempo + fatigue to delay ranges, returns adjusted value
- [x] `shouldMisclick()` — base 3% + fatigue scaling (+0.5%/30min, cap 8%)
- [x] `performMisclick(BaseScript script, Point intended)` — offset 15-60px via Gaussian, pause 300-800ms
- [x] `shouldIdleDrift()` / `shouldLongDrift()` — 2% short (2-8s), 0.3% long (15-45s)
- [x] `performIdleDrift(BaseScript script)` — stationary wait, optionally drift mouse to game view center first
- [x] `shouldHesitate()` — 7% chance, `performHesitation()` waits 200-600ms
- [x] `shouldSlowApproach()` — 3% chance, returns true to signal `"slow"` speed
- [x] `shouldTakeBreak()` / `shouldTakeExtendedBreak()` — 1% / 0.1% per call
- [x] `performBreak(BaseScript script, boolean extended)` — 1-5min or 5-15min wait, resets fatigue partially on extended
- [x] `shouldFidgetCamera()` — 3% chance
- [x] `performCameraFidget(BaseScript script)` — middle-click press, small drag, middle-click release
- [x] All probability constants as `public static final double` at class top
- [x] Javadoc on class and every public method
- [x] Use `ThreadLocalRandom`, `BaseScript.waitMillis()` / `waitRandomMillis()`, `checkInterrupted()` before long waits
- [x] Verify compiles: `cd scriptgen && gradle compileJava`

## Task 3: Create Script Generator Agent Configuration
**Implements**: Design §1, §Agent Configuration
**Files**: `.kiro/agents/script-generator.json`, `.kiro/agents/script-generator.md`

- [x] Create `script-generator.json` with tools, allowedTools, resources pointing to ChromaScape source and scriptgen behavior class, agentSpawn hook
- [x] Create `script-generator.md` system prompt encoding:
  - Full ChromaScape API surface reference (BaseScript lifecycle, Controller accessors, all utils/actions classes, all utils/core classes)
  - Script template skeleton (per Design §4) — note package is `com.scriptgen.scripts`, imports from both `com.chromascape` and `com.scriptgen.behavior`
  - Human behavior integration pattern (per Design §3.2)
  - Research phase instructions: how to query OSRS Wiki Bucket API, MediaWiki API, Prices API
  - Validation checklist (per Design §5) — compile command is `cd scriptgen && ../gradlew compileJava`
  - Output format: Java file in scriptgen/ + setup instructions
  - Iterative refinement rules: modify existing script on follow-up, don't regenerate
  - HSV bounds rules, image path conventions, error handling patterns

## Task 4: Implement Research Phase in Agent Prompt
**Implements**: FR-2, Design §2
**File**: `.kiro/agents/script-generator.md` (section within the prompt)

- [x] Document the research workflow the agent must follow before generating code:
  1. Parse user intent into structured fields (skill, method, location, strategy, stop conditions)
  2. Construct and execute Bucket API queries for item/NPC/object resolution
  3. Query MediaWiki API for location details, quest requirements, skill prerequisites
  4. Query Prices API `/mapping` for item metadata when needed
  5. Document all resolved IDs, coordinates, and requirements as context
- [x] Include example queries for common scenarios (mining, fishing, woodcutting, cooking, agility)
- [x] Specify that the agent must cite wiki URLs for any data it uses
- [x] Specify fallback: if Bucket API doesn't have the data, use MediaWiki page parse

## Task 5: Implement Script Generation Templates in Agent Prompt
**Implements**: FR-3, FR-4, Design §4
**File**: `.kiro/agents/script-generator.md` (section within the prompt)

- [x] Encode the script skeleton template with all required sections:
  - Package `com.scriptgen.scripts`, imports from `com.chromascape.*` and `com.scriptgen.behavior.*`
  - Class Javadoc with prerequisites, RuneLite setup, inventory layout
  - Image template constants, ColourObj definitions
  - Human behavior tuning constants (overrides for HumanBehavior defaults)
  - Script-specific constants (timeouts, tiles, slot indices)
  - `cycle()` with HumanBehavior integration points
  - Private helper methods with Javadoc
- [x] Document patterns for common script types:
  - **Gather & Drop**: click resource → idle → check inventory → drop
  - **Gather & Bank**: click resource → idle → check inventory → walk to bank → deposit → walk back
  - **Process**: withdraw materials → close bank → use item on item → wait → bank product
  - **Agility**: detect obstacle → click → wait XP change → check mark of grace → loop
  - **Combat**: detect NPC → click → wait idle → loot → eat food if low HP
- [x] Document setup instructions format for each pattern type
- [x] Include the HumanBehavior weaving pattern showing where checks go in each script type

## Task 6: Implement Validation Phase in Agent Prompt
**Implements**: FR-7, Design §5
**File**: `.kiro/agents/script-generator.md` (section within the prompt)

- [x] Define the validation checklist the agent must execute after generating a script:
  1. Run `cd scriptgen && ../gradlew compileJava` and check for errors
  2. If compile fails, read error output, fix the generated file, re-validate
  3. Grep ChromaScape source to confirm every imported class exists
  4. Verify all `ColourObj` constructor args: H 0-180, S 0-255, V 0-255
  5. Verify all image paths start with `/images/user/`
  6. Verify `checkInterrupted()` present in any `while` loop
  7. Verify walker `pathTo()` calls wrapped in try/catch (IOException, InterruptedException)
  8. Verify all `PointSelector` / `TemplateMatching` results have null checks before use
  9. Verify `stop()` called on unrecoverable errors
- [x] Define max 3 fix-and-retry cycles before asking the user for help
- [x] Agent must report validation results to the user (pass/fail with details)

## Task 7: Integration Test — Generate a Sample Script End-to-End
**Implements**: All FRs, full pipeline validation

- [x] Use the script-generator agent to process: "mine iron ore at Al Kharid mine and drop when inventory is full"
- [x] Verify the agent:
  1. Queries Wiki for iron ore item ID, pickaxe requirements
  2. Generates `scriptgen/src/main/java/com/scriptgen/scripts/AlKharidIronMiningScript.java`
  3. Script extends `com.chromascape.base.BaseScript`, imports `com.scriptgen.behavior.HumanBehavior`
  4. Integrates HumanBehavior calls (misclicks, idle drifts, hesitation, breaks, camera fidgets)
  5. Includes fatigue-adjusted delays via `HumanBehavior.adjustDelay()`
  6. Includes setup instructions (image templates, RuneLite colour config, inventory layout)
  7. Passes `cd scriptgen && gradle compileJava`
- [x] Verify the generated script has all human behavior tuning constants at the top
- [x] Verify Javadoc is present on class and all methods

## Task 8: Iterative Refinement Test
**Implements**: FR-6

- [x] Send follow-up: "add banking at Al Kharid bank instead of dropping"
- [x] Verify the agent modifies the existing script (not regenerates from scratch)
- [x] Verify walker pathTo() added with proper try/catch
- [x] Verify bank interaction logic added (click bank, deposit, return)
- [x] Verify script still compiles in scriptgen project
- [ ] Send follow-up: "make it more passive" — verify human behavior constants adjusted (higher idle/break rates, lower tempo)
