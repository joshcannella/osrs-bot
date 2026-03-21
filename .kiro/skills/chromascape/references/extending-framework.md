# Extending ChromaScape with Reusable Utilities

## The Rule

If you're about to write a private method that performs a generic game interaction (pressing a key, checking inventory, clicking a colour, logging out, opening a bank, eating food), check the API reference first. If a utility exists, use it. If it doesn't and the method isn't script-specific, create the utility before writing the script.

Script-specific logic (e.g., "check if we're on the right floor") stays as private methods in the script.

## Where Utilities Live

`ChromaScape/src/main/java/com/chromascape/utils/actions/custom/`

Existing: Bank, ColourClick, GameCenter, HumanBehavior, Inventory, KeyPress, LevelUpDismisser, Logout, Walk

## How to Write One

```java
package com.chromascape.utils.actions.custom;

import com.chromascape.base.BaseScript;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class UtilityName {
    private static final Logger logger = LogManager.getLogger(UtilityName.class);

    public static ReturnType methodName(BaseScript base) {
        // Access controller via base.controller()
        // Use BaseScript.waitMillis() for waits
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

## When to Create vs Not

**Create** when: 2+ scripts need it, it's a generic game interaction, it would otherwise be copy-pasted.

**Don't create** for: script-specific decision logic, quest dialog trees, specific state transitions.

## Deploy Checklist

1. Create file in `utils/actions/custom/`
2. Compile: `osrs-bot build`
3. Update scripts to use the new utility
4. Update `references/api-reference.md` with new signatures
5. Run `osrs-bot lint` to verify no leftover private duplicates
