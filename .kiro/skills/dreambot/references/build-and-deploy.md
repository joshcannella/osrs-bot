# Build & Deploy

## Gradle Setup

The build lives in `dreambot/build.gradle.kts`. It pulls the DreamBot client from their Maven repo:

```kotlin
repositories {
    maven { url = uri("https://maven.dreambot.org") }
}
dependencies {
    compileOnly("org.dreambot:client:4.0.0-SNAPSHOT")
}
```

`compileOnly` because DreamBot provides the client at runtime — it's not bundled in the jar.

Java 11 target for DreamBot compatibility.

## Single Jar, Multiple Scripts

All scripts compile into one jar. DreamBot scans the jar for classes with `@ScriptManifest` and lists each as a separate selectable script. No need for separate jars per script.

## Versioning

Two levels of versioning:

**Jar**: Uses datetime timestamp — `osrs-scripts-20260405-1135.jar`. Just a delivery container, not semantically versioned.

**Scripts**: Each script has independent major.minor tracked in `.kiro/scripts.json`:
- `osrs-bot deploy` auto-detects which scripts have changed source files and bumps their minor version
- `osrs-bot deploy --major-script <id>` bumps major for specific script(s)
- Version is written into `@ScriptManifest` annotation automatically
- DreamBot UI shows each script's version

## Deploy Flow (Linux → Windows)

### Full Deploy
```
osrs-bot deploy
  1. Detect which scripts have changed source files
  2. Auto-bump minor version for changed scripts (e.g., 0.1 → 0.2)
  3. Update @ScriptManifest version in Java source
  4. gradle jar → osrs-scripts-20260405-1135.jar
  5. Copy jar to ~/Dropbox/osrs-bot/builds/
  6. git add -A && git commit && git push
  7. Clear live feed (feedback addressed)
  8. Dropbox syncs jar to Windows automatically
```

### Quick Deploy (fast iteration)
```
osrs-bot deploy --quick
  1-5. Same as above
  6. Push only live feed + tracker (skip full git push)
  7. Keep live feed (still iterating)
```

### Windows: One-Shot
```
osrs-bot run
  1. Find latest jar in ~/Dropbox/osrs-bot/builds/
  2. Remove old jars from ~/DreamBot/Scripts/
  3. Copy new jar → shows old/new jar names
  4. Warn to stop script in DreamBot and refresh
```

### Windows: Watch Mode
```
osrs-bot run --watch
  Polls Dropbox every 5s, auto-copies new jars as they appear.
  Leave running in a terminal during testing sessions.
```

## Live Feed (Rapid Iteration)

During active testing, use the live feed instead of formal bugs:

```powershell
osrs-bot live <id> "message"                    # quick text
osrs-bot live <id> "message" -i screenshot.png  # with screenshot
osrs-bot live <id> "message" -l 10              # with last 10 log errors
osrs-bot push                                    # sync to git
```

On Linux, view with `osrs-bot inbox` or `osrs-bot live --tail`.

Full deploy clears the live feed. Quick deploy preserves it.

## Configurable Paths

`.osrs-bot.conf` in project root:
```ini
dropbox_dir=~/Dropbox/osrs-bot/builds
dreambot_scripts=~/DreamBot/Scripts
dreambot_logs=~/DreamBot/BotData/logs
```

Override with environment variables: `OSRS_BOT_DROPBOX`, `OSRS_BOT_DREAMBOT`, `OSRS_BOT_DREAMBOT_LOGS`.

## Rollback

Manual: copy an older timestamped jar from the Dropbox folder to `~/DreamBot/Scripts/`. All jars are preserved in Dropbox.

## Troubleshooting

- **Jar not appearing in DreamBot**: Click "Refresh" in the local scripts tab. Check that the jar is in `~/DreamBot/Scripts/`.
- **Compile error about missing class**: Run `gradle --refresh-dependencies` to update the DreamBot client snapshot.
- **Dropbox not syncing**: Check Dropbox desktop client is running. Verify the folder exists.
