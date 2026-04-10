# Script Handoff Format

<!-- Living document — update sections as the workflow evolves. -->
<!-- The osrs-expert agent produces this at the end of a research session. -->
<!-- The osrs-scripter agent consumes it as authoritative input for requirements + code. -->

When research is complete, the expert should produce a single message in this format:

---

## SCRIPT HANDOFF

### Name & ID
- **Name**: [Human-readable name]
- **ID**: [kebab-case-id]

### Goal
[One-line description of what the script does]

### Skill / Activity
- **Skill**: [e.g., Fishing, Cooking, Woodcutting]
- **Method**: [e.g., Fly fishing, Power mining, Cooking on range]

### Location
- **Area**: [e.g., Edgeville river, south side]
- **Nearest bank**: [e.g., Edgeville bank, ~15 tiles north]
- **Landmarks**: [anything useful for orientation]

### Items Required
| Item | Purpose | Obtain From |
|------|---------|-------------|
| | | |

### NPC / Object Interactions
<!-- Exact names and right-click actions — wiki-verified. These are what the script will target. -->
| Target | Type | Action | Notes |
|--------|------|--------|-------|
| | NPC/Object | | |

### State Flow
<!-- Game-level steps, not code. Describe what a human player does. -->
1. [e.g., Fish at river until inventory full]
2. [e.g., Walk to bank, deposit all except rod and feathers]
3. [e.g., Return to fishing spot, repeat]

### Prerequisites
- [Quest requirements, if any]
- [Minimum skill levels]
- [Unlocks needed]

### Edge Cases
<!-- Things that can go wrong, discovered during research -->
- [e.g., Fishing spots move — need to re-find closest spot]
- [e.g., Feathers deplete — must stop when out]
- [e.g., Level-up dialog interrupts fishing]
- [e.g., Other players competing for spots]

### Stop Conditions
- [e.g., Reach level 40 Fishing]
- [e.g., Out of feathers]
- [e.g., Bank is full]

### Banking Strategy
- **Deposit**: [what to deposit]
- **Keep**: [what stays in inventory]
- **Method**: [e.g., depositAllExcept rod + feathers]

### Special Notes
- [Anything unusual about this activity]
- [Tips from research that affect implementation]

---

### Scripter Compliance Reminder
Before deploying, the scripter must verify:
- [ ] Tree structure: correct isValid() ordering, fallback leaf, no state variables
- [ ] API usage: methods verified against api-reference.md
- [ ] Anti-ban: AntiBanNode + all inline AntiBanUtil calls
- [ ] Edge cases: supply depletion in leaves, null checks, stuck detection
- [ ] Logging: Logger in every leaf with consistent [Prefix] format
- [ ] Guards: shouldWalk(), bank open checks, return value checks before sleep
- [ ] Return values: never < 600, never uniform, always AntiBanUtil delays
- [ ] Deploy: use `osrs-bot deploy` — never manually edit versions
