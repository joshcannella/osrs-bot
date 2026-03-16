# Extending ChromaScape with Reusable Utilities

## Core Principle: Write It Once

When writing code for a script, **always ask: "Would another script need this?"** If the answer is yes — or even probably — put it in ChromaScape as a shared utility instead of a private method.

This is not optional cleanup. This is how you write code here. Private helper methods that duplicate framework-level functionality are bugs.

## The Rule

**If you are about to write a private method that performs a generic game interaction (pressing a key, checking inventory, clicking a colour, logging out, opening a bank, eating food), check the API reference first.** If a utility already exists, use it. If it doesn't exist and the method isn't script-specific, create the utility in ChromaScape before writing the script.

Script-specific logic (e.g., "drop one cooked shrimp", "check if we're on the right floor of a quest dungeon") stays as private methods in the script.

## Available Utilities

Check `.kiro/knowledge/chromascape-wiki/api-reference.md` for the full list. Key ones:

| Need | Utility | Example |
|------|---------|---------|
| Check/count/click inventory items | `Inventory` | `Inventory.hasItem(this, IMG, 0.07)` |
| Press space/escape/enter/char | `KeyPress` | `KeyPress.space(this)` |
| Log out | `Logout` | `Logout.perform(this)` |
| Dismiss level-up dialogs | `LevelUpDismisser` | `LevelUpDismisser.dismissIfPresent(this)` |
| Wait for player idle | `Idler` | `Idler.waitUntilIdle(this, 120)` |
| Drop all items | `ItemDropper` | `ItemDropper.dropAll(this)` |
| Read HP/Prayer/XP | `Minimap` | `Minimap.getHp(this)` |
| Click moving objects | `MovingObject` | `MovingObject.clickMovingObjectByColourObjUntilRedClick(colour, this)` |
| Read mouseover text | `MouseOver` | `MouseOver.getText(this)` |

## When to Create a New Utility

Create a new utility when:
1. You're writing a method that **two or more scripts need** (or one needs and it's clearly generic)
2. The method performs a **game interaction** — not script-specific decision logic
3. It would otherwise be **copy-pasted** across scripts

Do NOT create utilities for script-specific logic (quest dialog trees, specific state machine transitions).

## Where to Put It

`ChromaScape/src/main/java/com/chromascape/utils/actions/`

This is where `Idler`, `Inventory`, `ItemDropper`, `KeyPress`, `LevelUpDismisser`, `Logout`, `Minimap`, `MouseOver`, `MovingObject`, and `PointSelector` live.

## How to Write It

```java
package com.chromascape.utils.actions;

import com.chromascape.base.BaseScript;

public class UtilityName {
  private static final Logger logger = LogManager.getLogger(UtilityName.class);

  public static ReturnType methodName(BaseScript base) {
    // Access controller via base.controller()
    // Use BaseScript.waitMillis() / BaseScript.waitRandomMillis() for waits
    // Use BaseScript.checkInterrupted() in polling loops
    // Release ChromaObj Mats in finally blocks
    // Null-check all zone lookups and detection results
  }
}
```

Rules:
- Static methods only — no instance state
- `BaseScript base` as first parameter
- Always include a logger
- Null-safe zone lookups
- `checkInterrupted()` in any polling loop
- Release `ChromaObj` Mats in finally blocks

## How to Deploy

1. Create the file in `ChromaScape/src/main/java/com/chromascape/utils/actions/`
2. Compile: `cd ChromaScape && gradle compileJava`
3. Update scripts in scriptgen to import and use the new utility
4. Run `./scripts/sync-and-compile.sh`
5. **Update the API reference** at `.kiro/knowledge/chromascape-wiki/api-reference.md`

## Candidates for Future Extraction

| Pattern | Utility | Status |
|---------|---------|--------|
| Inventory check/count/click/find | `Inventory` | ✅ Done |
| Press space/escape/enter/char | `KeyPress` | ✅ Done |
| Log out | `Logout` | ✅ Done |
| Dismiss level-up dialogs | `LevelUpDismisser` | ✅ Done |
| Open bank + deposit + close | `Banking` | Not yet — duplicated in AlKharidGold, EdgevilleJewellery |
| Eat food when HP low | `Eating` | Not yet — pattern exists in api-reference |
| Check colour visibility + get click point | `ColourDetection` | Not yet — duplicated in DraynorFishCook, ChickenKiller |

## Checklist

Before committing a new ChromaScape utility:
- [ ] Compiles in ChromaScape (`gradle compileJava`)
- [ ] All scripts using it compile via `./scripts/sync-and-compile.sh`
- [ ] API reference updated with new class and method signatures
- [ ] Existing scripts refactored to use the new utility (no leftover private duplicates)
