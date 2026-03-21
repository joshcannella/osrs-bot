# Code Review Checklist

**Run every item against every script before presenting to the user.** This is not optional. Each item exists because it caused a real bug in a past script.

## Structure

- [ ] Script uses an `enum State` with a switch in `cycle()` — no implicit flow via boolean flags
- [ ] Each state is its own method — no monolithic methods that do walk + interact + walk back
- [ ] `cycle()` first line is `if (HumanBehavior.runPreCycleChecks(this)) return;`
- [ ] Every state transition is logged: `logger.info("State: {} → {}", old, new)`

## Stuck Detection

- [ ] `stuckCounter` only resets on **state transitions**, not after every action attempt
- [ ] `stuckCounter >= MAX_STUCK_CYCLES` check is at the top of `cycle()`
- [ ] Every `Walk.to()` return value is checked — `if (!Walk.to(...)) stuckCounter++`
- [ ] Every `ColourClick.getClickPoint()` null result increments `stuckCounter`

## Click Safety

- [ ] Every click uses full HumanBehavior pattern: `shouldSlowApproach`, `shouldHesitate`, `shouldMisclick`, `microJitter`
- [ ] No bare `controller().mouse().moveTo(loc, "medium")` + `leftClick()` without HumanBehavior

## UI Verification

- [ ] Bank open is **verified** (poll for expected item visible in game view), not just a blind delay
- [ ] Deposit is **verified** (check deposited items are gone from inventory before proceeding)
- [ ] Any interface interaction (cooking menu, smithing menu, etc.) is verified open before pressing space/keys

## Banking

- [ ] Tools/equipment are **never deposited** — deposit specific items, not deposit-all, unless the script withdraws everything it needs back
- [ ] If using `Bank.depositAll()`, the script must withdraw all required tools afterward and verify they're in inventory
- [ ] Use `Bank.depositAll()` + withdraw tools — do NOT left-click individual items to deposit (left-click deposits 1, not all)

## Inventory Detection

- [ ] Inventory full is detected via `Inventory.isFull()` (template) OR `Inventory.isFullByChat()` — ideally both as belt-and-suspenders
- [ ] Full-inventory check happens at the **top** of the gathering state (handles starting with full inventory)
- [ ] Full-inventory check also happens **after** the gathering action completes

## State Guards

- [ ] Cycle-level guards (e.g., "has required tool") skip states where the guard doesn't apply (e.g., skip net check during BANKING when net was just deposited)
- [ ] No boolean flags that get cleared before the action they trigger — use state enum transitions instead

## Shared Utilities

- [ ] No private methods that duplicate `Inventory.isFullByChat()`, `Inventory.findInGameView()`, `Inventory.clickItem()`, `Bank.depositAll()`, `Bank.close()`, `KeyPress.*`, `LevelUpDismisser.dismissIfPresent()`
- [ ] Run `osrs-bot lint` after writing — if a private method signature appears in 2+ scripts, extract it

## Loops

- [ ] Every `while` loop has `checkInterrupted()`
- [ ] Every `while` loop has `waitMillis()` to prevent hot-spinning (even if Idler is called — it can return instantly)
- [ ] Every `while` loop has a timeout/deadline

## Delays

- [ ] All delays use `HumanBehavior.adjustDelay(min, max)`, never hardcoded `waitMillis(1200)`
- [ ] Post-action delays are present (e.g., after clicking, after level-up dismiss, after bank close)

## Image Templates

- [ ] Every template path referenced in the script exists as a PNG in `ChromaScape/src/main/resources/images/user/`
- [ ] Verify with `file` command — must report PNG image data, not HTML or empty
