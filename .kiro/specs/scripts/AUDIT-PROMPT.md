# Script Audit Prompt

<!-- Living document — add new checks as patterns evolve. -->
<!-- Paste this to osrs-scripter to trigger a full compliance review. -->
<!-- Replace <script-id> with the actual script ID (e.g., draynor-fisher). -->

## Usage

Copy everything below the line and paste it to `osrs-scripter`:

---

Audit the script `<script-id>`. Read all source files for this script, then check every item below. For each item, report PASS or FAIL with the specific file and line number. If FAIL, suggest the fix.

Also compare against other scripts in the repo for inconsistencies in logging format, naming conventions, and pattern usage.

### Tree Structure
- [ ] Extends TreeScript (or TaskScript/AbstractScript with justification)
- [ ] `isValid()` conditions are ordered correctly (highest priority first)
- [ ] Has a fallback leaf (always-valid action when nothing else matches)
- [ ] No state variables, state enums, or `getState()` — the tree IS the state
- [ ] Branches group related leaves logically
- [ ] `@ScriptManifest` present with correct category

### API Usage
- [ ] All method names exist in `references/api-reference.md` or domain files
- [ ] Parameter types are correct (no wrong overloads)
- [ ] Uses `interact()` not raw `Mouse.move()` + `Mouse.click()`
- [ ] Uses `useOn()` correctly for item-on-object/NPC interactions
- [ ] No hallucinated methods or classes

### Anti-Ban
- [ ] `AntiBanNode` added as first branch in `onStart()` / `addBranches()`
- [ ] `setSkillsToCheck()` called with relevant skills
- [ ] `shouldHesitate()` / `hesitate()` before important clicks
- [ ] `shouldMisclick()` / `misclick()` before primary interactions
- [ ] `reactionDelay()` after detecting action completion
- [ ] `humanDelay()` for all return values (never flat `return 600`)
- [ ] `shouldForceRightClick()` to vary interaction style
- [ ] `idleWatch()` or `hoverNextTarget()` during animation waits
- [ ] `glanceInventory()` occasionally after gaining items

### Edge Cases
- [ ] Supply depletion checked in leaves at runtime (not just `onStart()`)
- [ ] Null checks on all `.closest()` results
- [ ] Stuck detection (or reasonable fallback behavior)
- [ ] Bank full handling
- [ ] `return -1` with `Logger.error()` for unrecoverable states
- [ ] Level-up / dialog interruption handled

### Logging
- [ ] `Logger.log()` in every leaf/node `onLoop()`
- [ ] Consistent `[Prefix]` format (e.g., `[Fish]`, `[Bank]`, `[Cook]`)
- [ ] `Logger.error()` for failures and stop conditions
- [ ] No excessive logging (not every tick, only on state changes)

### Guards
- [ ] `Walking.shouldWalk()` before every `Walking.walk()` or `Bank.open()`
- [ ] `if (!Bank.isOpen())` before `Bank.open()` — no spam-opening
- [ ] Check return values before `Sleep.sleepUntil()`
- [ ] Lambda reset conditions in `Sleep.sleepUntil()` (not method references)
- [ ] `if (!Players.getLocal().isAnimating())` before interacting

### Return Values
- [ ] Never returns less than 600 (one game tick)
- [ ] Never returns a uniform value from every leaf
- [ ] Uses `AntiBanUtil.humanDelay()`, `reactionDelay()`, or `conditionSleep()`
- [ ] Idle/waiting states use longer delays than active states

### Deploy & Versioning
- [ ] No manually edited `@ScriptManifest` version numbers
- [ ] No manually edited `scripts.json` version entries

### Consistency with Other Scripts
- [ ] Logging prefix format matches other scripts
- [ ] File naming follows `{Name}Script.java`, `{Action}Leaf.java`, `{Action}Branch.java`
- [ ] Package naming follows `scripts.{scriptname}`
- [ ] Same anti-ban patterns used as other scripts in the repo

Report results as a table, then list all FAILs with suggested fixes.
