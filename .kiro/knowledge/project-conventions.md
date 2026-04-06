# Project Conventions

## Package Structure

```
scripts/
├── shared/              # Shared utilities — antiban, ScriptContext
│   ├── antiban/
│   └── ScriptContext.java
└── {scriptname}/        # One package per script
    ├── {Name}Script.java
    ├── {Name}Context.java   # (TaskScript only)
    └── nodes/               # (TaskScript only)
```

## Naming

- Script entry points: `{Name}Script.java` (e.g., `FisherScript.java`)
- Script context: `{Name}Context.java` (e.g., `FisherContext.java`)
- Task nodes: `{Action}Node.java` (e.g., `FishNode.java`, `BankNode.java`)
- Script IDs: kebab-case (e.g., `draynor-fishing`)
- Package names: script ID without hyphens (e.g., `scripts.draynorfishing`)

## One Jar, Multiple Scripts

All scripts compile into a single `osrs-scripts-{timestamp}.jar`. DreamBot discovers each `@ScriptManifest` class and lists them separately.

## Versioning

- Jar uses datetime timestamp: `osrs-scripts-20260405-1135.jar`
- Each script has independent major.minor tracked in `.kiro/scripts.json`
- `osrs-bot deploy` auto-bumps minor for changed scripts, updates `@ScriptManifest`
- `osrs-bot deploy --major-script <id>` bumps major for specific script(s)

## Framework Choice

- **TaskScript** (default): 3+ states, banking, walking, multiple actions
- **AbstractScript**: ≤2 states, no banking, trivial logic

## Anti-Ban

Every TaskScript registers `AntiBanNode` in `onStart()`. All nodes use `AntiBanUtil` for delays.

## Feedback Loop

- `osrs-bot live <id> "msg"` for quick feedback during testing
- `osrs-bot push` to sync feedback to git
- `osrs-bot inbox` to see all unresolved bugs, notes, and live messages
- `osrs-bot deploy --quick` for fast iteration (build + Dropbox, skip full push)
- `osrs-bot run --watch` on Windows to auto-copy new jars
- Full `osrs-bot deploy` clears the live feed
