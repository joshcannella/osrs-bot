# State Export Plugin — Setup

A RuneLite plugin that exports game state to a memory-mapped file for the osrs-bot Python framework.

## How It Works

The plugin writes a 64KB memory-mapped file at `%USERPROFILE%/.runelite/osrsbot_state.dat` every game tick (~600ms). The Python framework reads this file directly from memory — no network ports, no HTTP server.

## Building

```bash
cd plugin
./gradlew jar
```

The JAR will be at `plugin/build/libs/osrsbot-plugin-0.1.0.jar`.

## Installing

### Option 1: External Plugin Loader (recommended)

1. Install the [External Plugin Loader](https://github.com/AterAnimAvis/runelite-external-plugins-loader) RuneLite plugin
2. Copy `osrsbot-plugin-0.1.0.jar` into `%USERPROFILE%/.runelite/externalmanager/`
3. Restart RuneLite
4. Enable "State Export" in the plugin panel (wrench icon)

### Option 2: RuneLite `--developer-mode`

1. Launch RuneLite with `--developer-mode`
2. Place the JAR in `%USERPROFILE%/.runelite/plugins/`
3. Enable "State Export" in the plugin panel

## Verifying

With RuneLite open and logged in:

1. Check the file exists:
   ```bash
   ls -la "$USERPROFILE/.runelite/osrsbot_state.dat"
   # Should be 65536 bytes (64KB)
   ```

2. Verify from Python:
   ```bash
   python -c "from framework.game_state.client import GameStateClient; c = GameStateClient(); print('available:', c.is_available()); print(c.get_player())"
   ```

## Data Available

| Field | Contents |
|-------|----------|
| `player` | `{x, y, plane, hp, prayer, run_energy, animation_id, canvas_x, canvas_y}` |
| `inventory` | `[{slot, item_id, quantity}, ...]` (28 slots) |
| `npcs` | `[{id, name, canvas_x, canvas_y, hp_ratio, animation_id, is_interacting}, ...]` |
| `objects` | `[{id, name, canvas_x, canvas_y}, ...]` |
| `stats` | `{skill_name: {level, boosted, xp}, ...}` |
| `ground_items` | `[{item_id, quantity, canvas_x, canvas_y}, ...]` |

All positions are **canvas coordinates** (pixels relative to the game viewport top-left), not world tile coordinates. Off-screen entities are omitted.

## Notes

- No network ports are opened — communication is via shared memory (mmap)
- The `.dat` file is created on plugin startup. It persists after shutdown (Windows cannot delete memory-mapped files until GC runs) but is inert — the sequence counters are zeroed to signal "not running"
- All data uses standard `java.nio` classes already loaded by RuneLite
- If the plugin isn't running, the Python framework degrades gracefully to color detection only
