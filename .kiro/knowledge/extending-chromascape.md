# Extending ChromaScape with Reusable Utilities

## When to Extend ChromaScape

Create a new utility in ChromaScape (not scriptgen) when:
1. **Two or more scripts** need the same functionality (or one script needs it and it's clearly generic)
2. The functionality is **framework-level** — it interacts with the game client, UI zones, OCR, or input systems
3. It would otherwise be **copy-pasted** as a private method across scripts

Do NOT extend ChromaScape for script-specific logic (e.g., a particular quest's dialog tree).

## Where to Put It

Reusable utilities go in `ChromaScape/src/main/java/com/chromascape/utils/actions/`. This is where `Idler`, `ItemDropper`, `LevelUpDismisser`, `Minimap`, `MouseOver`, `MovingObject`, and `PointSelector` already live.

The pattern: stateless static methods that take a `BaseScript` parameter for controller access.

## How to Write It

Follow the existing conventions in the `actions` package:

```java
package com.chromascape.utils.actions;

import com.chromascape.base.BaseScript;
// ... other imports

/**
 * [What it does and when to use it.]
 *
 * <p><b>Usage:</b> {@code UtilityName.methodName(this)}
 */
public class UtilityName {

  private static final Logger logger = LogManager.getLogger(UtilityName.class);

  /**
   * @param base the active {@link BaseScript} instance, usually passed as {@code this}
   * @return [what it returns]
   */
  public static ReturnType methodName(BaseScript base) {
    // Access controller via base.controller()
    // Use BaseScript.waitMillis() for static waits
    // Use BaseScript.checkInterrupted() in loops
  }
}
```

Key rules:
- **Static methods only** — no instance state, no constructors
- **BaseScript parameter** — always the first parameter, named `base`
- **Logger** — always include one
- **Null-safe** — check zone lookups and detection results for null
- **Release ChromaObj Mats** — always in a finally block
- **checkInterrupted()** — call in any polling loop

## How to Deploy It

Unlike scripts (which go in scriptgen first), utilities go directly into ChromaScape:

1. Create the file in `ChromaScape/src/main/java/com/chromascape/utils/actions/`
2. Compile: `cd ChromaScape && gradle compileJava`
3. Update scripts in scriptgen to import and use the new utility
4. Run `./scripts/sync-and-compile.sh` to sync scripts and verify everything compiles together
5. Update the API reference at `.kiro/knowledge/chromascape-wiki/api-reference.md` with the new class and method signatures

## How to Update the API Reference

After creating a new utility, append its documentation to `.kiro/knowledge/chromascape-wiki/api-reference.md` following the existing format:

```markdown
## UtilityName (com.chromascape.utils.actions.UtilityName)
\```java
static ReturnType methodName(BaseScript base)
\```
```

This ensures future script generation sessions know the utility exists.

## Refactoring Existing Scripts

When extracting a utility from existing scripts:

1. Identify the duplicated pattern across scripts
2. Create the utility in ChromaScape
3. Compile ChromaScape to verify
4. Update each script in scriptgen to use the utility (add import, replace private method)
5. Run `./scripts/sync-and-compile.sh`
6. Remove the old private methods from scripts

## Examples of Good Candidates for Extraction

| Pattern | Utility | Status |
|---------|---------|--------|
| Dismiss level-up dialogs | `LevelUpDismisser` | ✅ Done |
| Press space / escape / enter | Could be in a `KeyPress` utility | Not yet |
| Open bank + deposit + close | Could be a `Banking` utility | Not yet |
| Eat food when HP low | Could be an `Eating` utility | Not yet |
| Logout safely | Could be a `Logout` utility | Not yet |
| Check if inventory is full | Could be in an `Inventory` utility | Not yet |

## Checklist

Before committing a new ChromaScape utility:
- [ ] Compiles in ChromaScape (`gradle compileJava`)
- [ ] All scripts using it compile via `./scripts/sync-and-compile.sh`
- [ ] API reference updated
- [ ] Lessons learned updated (if the extraction revealed a bug or pattern)
