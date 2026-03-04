# Bug Report: Script progresses through steps without verifying completion

## Script ID
`restless-ghost`

## What happened
The script transitioned from TALK_AERECK to TALK_URHNEY without verifying that the first dialog was completed. When it reached TALK_URHNEY, it clicked but did not actually interact with the NPC. The script then proceeded to enter dialog options (3 then 1) when no dialog window was open, and moved to the next step even though the quest was never started.

## Expected behavior
The script should verify that each step completed successfully before moving to the next step:
1. After clicking Aereck, verify the dialog window opened
2. After entering dialog options, verify the quest started (check quest journal or quest state)
3. After clicking Urhney, verify the dialog window opened before sending keyboard inputs
4. Each step should have a validation mechanism to confirm success

## When it failed
- Started in the church (Lumbridge)
- Step: TALK_AERECK appeared to complete without verification
- Step: TALK_URHNEY clicked but did not engage NPC
- Script sent keyboard inputs (3, 1) with no dialog window open
- Progressed to next step despite quest not being started

## Steps to reproduce
1. Starting conditions: Inside Lumbridge church, quest not started
2. Launch RestlessGhostScript
3. Script immediately goes to TALK_AERECK
4. Script transitions to TALK_URHNEY without verifying dialog completion
5. Script sends keyboard inputs to non-existent dialog

## Terminal output
```
23:27:34.892 [Thread-5] INFO  com.chromascape.scripts.RestlessGhostScript - Step: TALK_AERECK
23:27:35.009 [Thread-5] INFO  com.chromascape.utils.domain.walker.Walker - Synchronously clicking once at 3243, 3210
23:27:55.096 [Thread-5] INFO  com.chromascape.scripts.RestlessGhostScript - Step: TALK_URHNEY
23:27:55.222 [Thread-5] INFO  com.chromascape.utils.domain.walker.Walker - Synchronously clicking once at 3238, 3210
23:27:56.004 [Thread-5] INFO  com.chromascape.utils.domain.walker.Walker - Precomputing next click at 3237, 3202
23:28:01.949 [Thread-5] ERROR com.chromascape.utils.domain.walker.Walker - Veered off path, recalculating...
```

Full log available in: `.kiro/specs/scripts/dev/restless-ghost/runtime.log`

## Root Cause Analysis
The script lacks validation between steps. It assumes:
- Clicks always succeed in opening dialogs
- Dialog options are always accepted
- Quest state changes happen immediately

## Proposed Solution
Add validation methods:
1. `waitForDialog()` - Poll for dialog window after NPC click (timeout 5-10s)
2. `waitForDialogClose()` - Verify dialog closed after keyboard input
3. `verifyQuestStarted()` - Check quest journal or quest state via OCR
4. Add retry logic if validation fails (max 3 attempts)
5. Throw exception if step cannot be verified after retries

## Screenshots (if applicable)
N/A - issue is behavioral, not visual

## Environment
- World: Unknown
- Camera zoom: Default
- RuneLite plugins active: Standard ChromaScape profile
