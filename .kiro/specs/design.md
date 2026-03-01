# Design: AI-Powered ChromaScape Script Generator

## Architecture Overview

The system is a separate Gradle project (`scriptgen`) that depends on ChromaScape as a library. It is driven by a Kiro agent that orchestrates research, code generation, and validation. ChromaScape is never modified — it is consumed via Gradle composite build.

```
User (natural language)
  → Script Generator Agent (orchestrator)
    → Research Phase (osrs-expert + Wiki APIs)
    → Planning Phase (script structure decision)
    → Generation Phase (Java code into scriptgen/)
    → Validation Phase (compile check + API audit)
  → Output: .java file in scriptgen/ + setup instructions
```

## Project Layout

```
osrs-bot/                              (repo root)
├── ChromaScape/                       (READ-ONLY — external project)
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   └── src/main/java/com/chromascape/
│       ├── base/BaseScript.java
│       ├── controller/Controller.java
│       ├── utils/actions/             (Idler, ItemDropper, PointSelector, etc.)
│       ├── utils/core/                (input, screen, state, statistics)
│       └── utils/domain/              (ocr, walker, zones)
├── scriptgen/                         (NEW — our project)
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   └── src/main/java/com/scriptgen/
│       ├── behavior/
│       │   └── HumanBehavior.java
│       └── scripts/
│           └── (generated scripts go here)
├── settings.gradle.kts                (root — composite build)
└── .kiro/
    ├── agents/
    │   ├── script-generator.json
    │   └── script-generator.md
    └── specs/
```

## Build Configuration

### `scriptgen/settings.gradle.kts`
Composite build — scriptgen references ChromaScape directly so it works standalone without a root project:
```kotlin
rootProject.name = "scriptgen"
includeBuild("../ChromaScape")
```

### `scriptgen/build.gradle.kts`
References ChromaScape as a composite build dependency. This gives scriptgen compile-time access to all ChromaScape classes without modifying ChromaScape:
```kotlin
plugins {
    java
}

group = "com.scriptgen"
version = "0.1.0"

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(17))
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // ChromaScape as composite build dependency
    implementation("com.chromascape:chromascape")

    // Transitive deps we use directly
    implementation("org.bytedeco:javacv-platform:1.5.11")
    implementation("org.apache.commons:commons-math3:3.6.1")
    implementation("org.apache.logging.log4j:log4j-api:2.24.3")
    implementation("org.apache.logging.log4j:log4j-core:2.24.3")
}
```

This means generated scripts `import com.chromascape.base.BaseScript` etc. and compile against ChromaScape's classes, but all new source lives in `scriptgen/`.

## Component Design

### 1. Script Generator Agent

A Kiro agent (`script-generator`) that orchestrates the full pipeline. Configured in `.kiro/agents/script-generator.json`.

The agent's system prompt encodes:
- The full ChromaScape API surface (derived from reading the actual codebase)
- Script structure templates
- Human behavior system rules
- Validation checklist

### 2. Research Module (Prompt-Driven)

A phase within the agent's reasoning. When the user provides a task description, the agent:

1. Parses the intent (skill, method, location, inventory strategy)
2. Constructs OSRS Wiki Bucket API queries to resolve:
   - Item data: `bucket('infobox_item').select('item_id','item_name').where('item_name','Iron ore').run()`
   - NPC/object data for interaction targets
   - Skill requirements from quest/activity pages
3. Calls the Wiki APIs via `execute_bash` (curl) or the web tool
4. Stores resolved data as context for the generation phase

### 3. Human Behavior System Design

The human behavior logic lives in `scriptgen/src/main/java/com/scriptgen/behavior/HumanBehavior.java`. It imports ChromaScape's `BaseScript`, `ClickDistribution`, and mouse utilities but is entirely owned by the scriptgen project.

#### 3.1 HumanBehavior Utility Class

```
com.scriptgen.behavior.HumanBehavior
```

Responsibilities:
- Centralized random decision-making for all human-like behaviors
- Fatigue state tracking (runtime, escalating probabilities)
- Tempo profile management (session multiplier + drift)

Key state:
```java
private static final long SESSION_START = System.currentTimeMillis();
private static double tempoMultiplier;        // 0.85–1.15, set at class load
private static long lastTempoDriftTime;       // tracks drift interval
private static long lastBreakTime;            // for fatigue reset after breaks
```

Key methods:
```java
// Core decision methods — each returns true/false based on probability + fatigue
static boolean shouldMisclick()
static boolean shouldIdleDrift()
static boolean shouldLongDrift()
static boolean shouldHesitate()
static boolean shouldSlowApproach()
static boolean shouldTakeBreak()
static boolean shouldTakeExtendedBreak()
static boolean shouldFidgetCamera()

// Action methods
static void performMisclick(BaseScript script, Point intended)
static void performIdleDrift(BaseScript script)
static void performHesitation()
static void performBreak(BaseScript script)
static void performCameraFidget(BaseScript script)

// Tempo
static long adjustDelay(long baseMin, long baseMax)
static void updateTempoDrift()

// Fatigue
static double getFatigueMultiplier()
```

#### 3.2 Integration Pattern in Generated Scripts

Generated scripts in `com.scriptgen.scripts` import both ChromaScape APIs and `HumanBehavior`:

```java
package com.scriptgen.scripts;

import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.*;
import com.scriptgen.behavior.HumanBehavior;
// ...

public class ExampleScript extends BaseScript {

    @Override
    protected void cycle() {
        HumanBehavior.updateTempoDrift();

        if (HumanBehavior.shouldTakeExtendedBreak()) {
            HumanBehavior.performBreak(this);
            return;
        }
        if (HumanBehavior.shouldTakeBreak()) {
            HumanBehavior.performBreak(this);
            return;
        }
        if (HumanBehavior.shouldFidgetCamera()) {
            HumanBehavior.performCameraFidget(this);
        }
        if (HumanBehavior.shouldIdleDrift()) {
            HumanBehavior.performIdleDrift(this);
        }

        clickTarget();
        waitRandomMillis(HumanBehavior.adjustDelay(800, 1000));
        Idler.waitUntilIdle(this, 20);
    }

    private void clickTarget() {
        Point clickLoc = /* resolve target */;

        String speed = HumanBehavior.shouldSlowApproach() ? "slow" : "medium";
        controller().mouse().moveTo(clickLoc, speed);

        if (HumanBehavior.shouldHesitate()) {
            HumanBehavior.performHesitation();
        }
        if (HumanBehavior.shouldMisclick()) {
            HumanBehavior.performMisclick(this, clickLoc);
            controller().mouse().moveTo(clickLoc, "medium");
        }

        controller().mouse().microJitter();
        controller().mouse().leftClick();
    }
}
```

#### 3.3 Fatigue Model State Machine

```
FRESH (0-30 min)     → base probabilities, tempoMultiplier near 1.0
NORMAL (30-90 min)   → +2.5% delay, +1% misclick, +0.5% idle drift
TIRED (90-180 min)   → +10% delay, +3% misclick, +1.5% idle drift
FATIGUED (180+ min)  → +25% delay (cap), +4% misclick (cap), +2% idle drift
  ↓ (extended break resets to NORMAL)
```

### 4. Script Template Structure

Every generated script follows this skeleton:

```java
package com.scriptgen.scripts;

import com.chromascape.base.BaseScript;
import com.chromascape.utils.actions.*;
import com.chromascape.utils.core.screen.colour.ColourObj;
import com.chromascape.utils.core.screen.topology.*;
import com.chromascape.utils.core.screen.window.ScreenManager;
import com.chromascape.utils.core.input.distribution.ClickDistribution;
import com.scriptgen.behavior.HumanBehavior;
// ...

/**
 * [Description of what the script does]
 *
 * <p>Prerequisites: [skills, quests, items]
 * <p>RuneLite Setup: [required plugin configurations]
 * <p>Inventory Layout: [required slot positions if any]
 */
public class [Name]Script extends BaseScript {

    private static final Logger logger = LogManager.getLogger([Name]Script.class);

    // === Image Templates ===
    private static final String ITEM_IMAGE = "/images/user/Item_name.png";

    // === Colour Definitions ===
    private static final ColourObj TARGET_COLOUR = new ColourObj(
        "target", new Scalar(H_MIN, S_MIN, V_MIN, 0), new Scalar(H_MAX, S_MAX, V_MAX, 0));

    // === Human Behavior Tuning ===
    private static final double MISCLICK_BASE_RATE = 0.03;
    private static final double IDLE_DRIFT_RATE = 0.02;
    private static final double BREAK_RATE = 0.01;
    private static final double HESITATION_RATE = 0.07;

    // === Script Constants ===
    private static final int IDLE_TIMEOUT = 20;
    private static final Point RESET_TILE = new Point(x, y);

    @Override
    protected void cycle() {
        // Human behavior checks woven into task logic
    }

    // Private helper methods with Javadoc
}
```

### 5. Validation Phase

After generating the script, the agent performs:

1. **Compile test**: Run `cd scriptgen && ./gradlew compileJava` to catch syntax/type errors
2. **API surface check**: Grep ChromaScape source to confirm every referenced class and method exists
3. **HSV bounds check**: Verify all `ColourObj` scalars are within H:0-180, S:0-255, V:0-255
4. **Image path check**: Confirm paths start with `/images/user/`
5. **Pattern check**: Ensure `checkInterrupted()` exists in loops, walker calls are try/caught, null checks on click locations

### 6. Output Artifacts

For each generation request, the system produces:

1. **`[Name]Script.java`** — placed in `scriptgen/src/main/java/com/scriptgen/scripts/`
2. **`HumanBehavior.java`** — placed in `scriptgen/src/main/java/com/scriptgen/behavior/` (generated once, reused)
3. **Setup instructions** — printed to chat, covering:
   - Image templates to capture (with cropping guidance)
   - RuneLite plugin settings
   - Inventory layout diagram
   - Prerequisites checklist

## Data Flow

```
1. User: "fish lobsters at Catherby and bank them"
2. Agent parses: skill=Fishing, method=lobster, location=Catherby, strategy=bank
3. Agent queries Wiki:
   - bucket('infobox_item').select('item_id').where('item_name','Raw lobster').run()
   - bucket('infobox_item').select('item_id').where('item_name','Lobster pot').run()
   - MediaWiki API for Catherby fishing spot coordinates
4. Agent resolves: itemId=377, toolId=301, bankLocation=Catherby bank
5. Agent generates scriptgen/src/.../CatherbyLobsterScript.java with:
   - cycle(): click spot → wait idle → check inventory → bank or continue
   - HumanBehavior integration at each decision point
   - Walker pathTo() for bank runs
6. Agent validates: cd scriptgen && ./gradlew compileJava passes
7. Agent outputs: file + setup instructions
```

## Agent Configuration

```json
{
  "name": "script-generator",
  "description": "Generates production-ready ChromaScape scripts from natural language",
  "prompt": "file:///.kiro/agents/script-generator.md",
  "tools": ["fs_read", "fs_write", "execute_bash", "grep", "glob", "code"],
  "allowedTools": ["fs_read", "grep", "glob", "code"],
  "resources": [
    "file://ChromaScape/src/main/java/com/chromascape/base/BaseScript.java",
    "file://ChromaScape/src/main/java/com/chromascape/controller/Controller.java",
    "file://ChromaScape/src/main/java/com/chromascape/scripts/*.java",
    "file://ChromaScape/src/main/java/com/chromascape/utils/actions/*.java",
    "file://scriptgen/src/main/java/com/scriptgen/behavior/HumanBehavior.java"
  ],
  "hooks": {
    "agentSpawn": [{
      "command": "find ChromaScape/src/main/java -name '*.java' | head -50 && echo '---' && find scriptgen/src/main/java -name '*.java' 2>/dev/null",
      "description": "Index available classes in both projects"
    }]
  }
}
```
