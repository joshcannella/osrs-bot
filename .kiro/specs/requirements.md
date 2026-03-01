# Requirements: AI-Powered ChromaScape Script Generator

## Overview

A separate project (`scriptgen`) that takes natural language descriptions of OSRS tasks and produces production-ready Java scripts targeting the ChromaScape API. ChromaScape is treated as an external dependency — this project never modifies ChromaScape source. The system leverages the osrs-expert agent for game knowledge, the OSRS Wiki APIs for data verification, and ChromaScape's layered architecture (BaseScript, Controller, utils) to generate correct, idiomatic automation scripts.

## Project Structure Constraint

- ChromaScape lives at `ChromaScape/` and is **read-only** — treated as a library dependency
- All generated code lives in a new sibling project (`scriptgen/`) that references ChromaScape via Gradle composite build or project dependency
- The `scriptgen` project contains: generated scripts, the HumanBehavior utility, and any supporting code

## Functional Requirements

### FR-1: Natural Language Input Parsing
The system shall accept a plain-English description of an OSRS task (e.g., "mine iron ore at Al Kharid and drop when inventory is full") and extract:
- The target skill/activity
- The specific method or item involved
- The location
- Inventory management strategy (drop, bank, process)
- Any stop conditions or break logic

### FR-2: Game Data Research & Verification
Before generating code, the system shall:
- Query the OSRS Wiki Bucket API to resolve item IDs, NPC IDs, and object IDs referenced in the task
- Verify skill/quest prerequisites for the requested activity
- Identify required items (tools, bait, runes, etc.) and their IDs
- Determine relevant colour signatures for RuneLite highlights (the user must configure these in RuneLite; the system documents which colours to set)
- Look up any relevant tile coordinates for walker-based navigation

### FR-3: Script Generation
The system shall generate a Java class that:
- Extends `com.chromascape.base.BaseScript` and overrides `cycle()`
- Uses the correct ChromaScape API patterns:
  - `controller().zones().getGameView()` for screen capture
  - `PointSelector.getRandomPointInColour()` / `getRandomPointByColourObj()` for colour-based clicking
  - `PointSelector.getRandomPointInImage()` for template-matching clicks
  - `TemplateMatching.match()` for inventory/UI checks
  - `controller().mouse().moveTo(point, speed)` + `leftClick()` / `rightClick()` for input
  - `controller().mouse().microJitter()` for pre-click hand tremor
  - `controller().keyboard().sendModifierKey()` for key presses
  - `controller().walker().pathTo(point, boolean)` for navigation
  - `Ocr.extractText()` for reading on-screen text
  - `MouseOver.getText()` for reading mouseover tooltip text
  - `Idler.waitUntilIdle()` for idle detection
  - `ItemDropper.dropAll()` with appropriate patterns and exclusions
  - `ColourObj` for custom HSV colour definitions
  - `ColourContours.getChromaObjsInColour()` for colour presence checks
  - `Minimap.getXp()` for XP tracking
  - `ClickDistribution.generateRandomPoint()` for humanized slot clicks
  - `ScreenManager.captureZone()` for sub-region captures
- Implements a state-machine or sequential flow appropriate to the task complexity
- Includes human-like behavior patterns (see FR-5)
- Has proper error handling: null checks on click locations, OCR failures, walker exceptions
- Places image path constants as `private static final String` fields referencing `/images/user/`
- Includes full Javadoc on the class and all methods

### FR-4: Setup Instructions Output
Alongside the generated script, the system shall produce:
- A list of required image templates the user must capture (with guidance on cropping)
- RuneLite plugin configuration instructions (which highlights/colours to enable)
- Required inventory layout (if the script depends on specific slot positions)
- Any quest/skill prerequisites the user must meet

### FR-5: Human-Like Behavior System
All generated scripts must include a configurable human behavior layer that simulates realistic player imperfections:

#### FR-5.1: Misclicks
- Occasional misclicks at a configurable probability (default ~2-4% per click action)
- Misclick offset: click lands 15-60px away from the intended target, biased by `ClickDistribution` Gaussian spread
- After a misclick, the script must pause briefly (300-800ms) as if the player noticed the error, then re-attempt the correct click
- Misclick probability should increase slightly during long sessions (fatigue simulation) — e.g., +0.5% per 30 minutes of runtime, capped at 8%

#### FR-5.2: Idle Drifts (AFK Moments)
- Random micro-AFK pauses where the player "zones out" — configurable probability (default ~1-3% per cycle)
- Duration: short drifts (2-8 seconds) at higher frequency, long drifts (15-45 seconds) at lower frequency (~0.3% per cycle)
- During an idle drift, the mouse should remain stationary (no movement, no clicks)
- Optionally move the mouse to a neutral area (e.g., center of game view or off the inventory) before idling, simulating the player looking away

#### FR-5.3: Mouse Hesitation
- Before certain clicks (configurable, default ~5-10% of clicks), the mouse should pause for 200-600ms after arriving at the target but before clicking — simulating the player visually confirming the target
- Occasional slow approach: ~3% of movements use `"slow"` speed profile regardless of the configured default, simulating distracted or cautious movement

#### FR-5.4: Variable Action Cadence
- Instead of fixed `waitRandomMillis(min, max)` ranges, the system shall generate per-session cadence profiles:
  - A base tempo multiplier (0.85–1.15) randomized at script start, shifting all delays
  - Intra-session tempo drift: the multiplier shifts by ±0.05 every 10-20 minutes
- This prevents the script from having a detectable fixed rhythm across sessions

#### FR-5.5: Attention Breaks
- Periodic longer breaks simulating the player checking their phone, getting a drink, etc.
- Default: ~1% chance per cycle of a 1-5 minute break
- Rare extended AFK: ~0.1% chance per cycle of a 5-15 minute break
- During breaks, the mouse may drift to a random safe position or remain still

#### FR-5.6: Camera Fidgeting
- Occasional middle-click camera rotations (~2-5% of cycles) using `controller().mouse().middleClick()` with small drag movements
- Simulates the player adjusting their view out of habit, not necessity

#### FR-5.7: Inventory Interaction Variance
- When dropping items, occasionally skip a slot and come back to it (simulating visual scanning)
- When banking, occasionally pause between withdraw actions (100-400ms extra)
- Vary the drop pattern between runs (ZIGZAG vs column-based) if `ItemDropper` supports it

#### FR-5.8: Fatigue Model
- Track cumulative runtime within the script
- As runtime increases, gradually:
  - Increase average delay multiplier (+5% per hour, capped at +25%)
  - Increase misclick probability (per FR-5.1)
  - Increase idle drift frequency (per FR-5.2)
- These values reset if the script takes an extended break (FR-5.5)

### FR-6: Iterative Refinement
The system shall support follow-up commands to modify a generated script:
- "Add banking instead of dropping"
- "Use a different colour for the fishing spot"
- "Add a logout timer after 2 hours"
- "Handle the random event popup"
- "Make it more aggressive / more passive" (adjusts human behavior parameters)

The system modifies the existing script rather than regenerating from scratch.

### FR-7: Script Validation (Static)
Before delivering the final script, the system shall:
- Verify all referenced ChromaScape classes/methods exist in the ChromaScape source
- Ensure the script compiles via `./gradlew compileJava` in the scriptgen project
- Check that image paths follow the `/images/user/` convention
- Validate that `ColourObj` HSV ranges are within valid bounds (H: 0-180, S: 0-255, V: 0-255)

## Non-Functional Requirements

### NFR-1: Framework Fidelity
Generated scripts must use only APIs that exist in the ChromaScape codebase. The system must not hallucinate methods or classes. The source of truth is the actual code under `ChromaScape/src/main/java/com/chromascape/`.

### NFR-2: Safety
- Scripts must include `stop()` calls on unrecoverable errors (null click locations, failed OCR reads)
- Scripts must handle `InterruptedException` properly via `ScriptStoppedException`
- Walker calls must be wrapped in try/catch for `IOException` and `InterruptedException`
- `checkInterrupted()` must be called in any long-running loop

### NFR-3: Data Accuracy
All game data (item IDs, coordinates, requirements) must be verified against the OSRS Wiki APIs. The system must not rely on memorized values — it must query and cite the wiki.

### NFR-4: Configurability
Human behavior parameters (misclick rate, idle frequency, break probability, fatigue scaling) should be exposed as `private static final` constants at the top of the generated script so users can tune them without modifying logic.

### NFR-5: Separation of Concerns
ChromaScape is never modified. All new code (HumanBehavior utility, generated scripts, build config) lives in the `scriptgen` project. ChromaScape is consumed as a compile dependency only.

## Out of Scope
- Runtime testing against a live OSRS client
- Automatic image template capture
- RuneLite plugin modification
- Account management or login automation
- Anti-ban evasion beyond humanized input patterns already in ChromaScape
- Modifications to the ChromaScape project itself
