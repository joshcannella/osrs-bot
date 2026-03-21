# Plugin Development

How RuneLite plugins work internally. This is for understanding what's possible, not a step-by-step dev tutorial.

## Table of Contents
- [Plugin Architecture](#plugin-architecture)
- [Event System](#event-system)
- [Overlays](#overlays)
- [Configuration](#configuration)
- [Dependency Injection](#dependency-injection)
- [Var System Internals](#var-system-internals)
- [Client Scripts](#client-scripts)
- [Plugin Hub Submission](#plugin-hub-submission)
- [Rejected Features & Guidelines](#rejected-features--guidelines)
- [Developer Tools](#developer-tools)

---

## Plugin Architecture

Every plugin has these components:

### Plugin Class
```java
@PluginDescriptor(name = "My Plugin", description = "Does things", tags = {"tag1", "tag2"})
public class MyPlugin extends Plugin {
    @Inject private Client client;
    @Inject private MyConfig config;
    @Inject private OverlayManager overlayManager;

    @Override protected void startUp() { overlayManager.add(myOverlay); }
    @Override protected void shutDown() { overlayManager.remove(myOverlay); }

    @Subscribe
    public void onGameTick(GameTick event) { /* runs every 0.6s */ }

    @Provides MyConfig getConfig(ConfigManager cm) { return cm.getConfig(MyConfig.class); }
}
```

### Config Interface
```java
@ConfigGroup("myplugin")
public interface MyConfig extends Config {
    @ConfigItem(keyName = "highlight", name = "Highlight NPCs", description = "Toggle NPC highlighting")
    default boolean highlight() { return true; }

    @ConfigItem(keyName = "color", name = "Highlight Color", description = "Color for highlights")
    default Color highlightColor() { return Color.CYAN; }
}
```

Return type determines the UI widget: `boolean` → checkbox, `Color` → colour picker, `String` → text field, `int` → number field, `enum` → dropdown.

### Overlay
```java
public class MyOverlay extends Overlay {
    @Override public Dimension render(Graphics2D graphics) {
        // Draw on game canvas: tile highlights, text, clickboxes
        return null;
    }
}
```

Overlay types:
- `Overlay` — draw anywhere on the game canvas
- `OverlayPanel` — text box overlay (like attack styles info)
- `WidgetItemOverlay` — draw on inventory/bank items

---

## Event System

Plugins react to game events via `@Subscribe` methods. Key events:

### Game State
| Event | When |
|-------|------|
| `GameTick` | Every 0.6s game tick |
| `GameStateChanged` | Login, logout, loading, hopping |
| `ClientTick` | Every client frame (faster than game tick) |

### Spawning/Despawning
| Event | When |
|-------|------|
| `NpcSpawned` / `NpcDespawned` | NPC appears/disappears |
| `GameObjectSpawned` / `GameObjectDespawned` | Game object changes |
| `GroundObjectSpawned` / `GroundObjectDespawned` | Ground decoration changes |
| `WallObjectSpawned` / `WallObjectDespawned` | Wall object changes |
| `DecorativeObjectSpawned` / `DecorativeObjectDespawned` | Decorative object changes |
| `ItemSpawned` / `ItemDespawned` | Ground item appears/disappears |
| `ProjectileMoved` | Projectile in flight |

### Player Actions
| Event | When |
|-------|------|
| `ChatMessage` | Any chat message received |
| `MenuOptionClicked` | Player clicks a menu option |
| `ItemContainerChanged` | Inventory, bank, or equipment changes |
| `StatChanged` | Skill XP or level changes |
| `AnimationChanged` | Player/NPC animation changes |
| `InteractingChanged` | Player starts/stops interacting with entity |
| `HitsplatApplied` | Damage splat appears |

### Vars
| Event | When |
|-------|------|
| `VarbitChanged` | Any varbit value changes |
| `ScriptCallbackEvent` | Client script triggers a RuneLite callback |

### UI
| Event | When |
|-------|------|
| `WidgetLoaded` | Interface widget becomes visible |
| `WidgetClosed` | Interface widget closes |
| `MenuEntryAdded` | Right-click menu entry added (for swapping/modifying) |

---

## Overlays

### Drawing on Tiles
```java
Polygon tilePoly = Perspective.getCanvasTilePoly(client, localPoint);
OverlayUtil.renderPolygon(graphics, tilePoly, color);
```

### Drawing on Objects/NPCs
```java
Shape clickbox = npc.getConvexHull();
OverlayUtil.renderHoverableArea(graphics, clickbox, mousePosition, fillColor, borderColor, borderWidth);
```

### Text Overlays
```java
OverlayUtil.renderTextLocation(graphics, textLocation, text, color);
```

### Infoboxes
Persistent small icons with text, shown in a row (e.g., slayer task count, cannon balls).
```java
infoBoxManager.addInfoBox(new MyInfoBox(image, plugin, text, tooltip));
```

---

## Configuration

### ConfigManager
Programmatic access to settings (beyond the Config interface):
```java
@Inject ConfigManager configManager;
configManager.setConfiguration("group", "key", value);
String val = configManager.getConfiguration("group", "key");
```

### Config Sections
Group related settings:
```java
@ConfigSection(name = "Colors", description = "Color settings", position = 0)
String colorSection = "colors";

@ConfigItem(keyName = "npcColor", name = "NPC Color", section = colorSection, ...)
```

### Config Persistence
- Settings stored in `~/.runelite/profiles2/` (per profile)
- Cloud sync available via RuneLite.net account
- Profiles switchable at runtime

---

## Dependency Injection

RuneLite uses Google Guice. Plugins can inject:

| Service | Purpose |
|---------|---------|
| `Client` | Game client API — access to game state, players, NPCs, objects, vars |
| `ClientThread` | Run code on the client thread (required for some API calls) |
| `ConfigManager` | Read/write plugin settings |
| `OverlayManager` | Register/unregister overlays |
| `InfoBoxManager` | Add/remove infoboxes |
| `ItemManager` | Item images, prices, compositions |
| `SpriteManager` | Game sprites |
| `ChatMessageManager` | Send chat messages |
| `KeyManager` | Register hotkeys |
| `MenuManager` | Add custom menu entries |
| `WorldService` | World list and player counts |

---

## Var System Internals

### VarPlayers (VarPs)
- 32-bit integers, server-set, per-account
- Older content uses these directly
- Read: `client.getVarpValue(varpIndex)`

### VarBits
- Variable-size bit fields packed into VarPs
- Each VarBit has: parent VarP index, LSB position, MSB position
- Read: `client.getVarbitValue(varbitId)`
- More efficient, used by newer content

### VarBit Extraction (how it works internally)
```java
int value = getVarp(varbit.getIndex());
int lsb = varbit.getLeastSignificantBit();
int msb = varbit.getMostSignificantBit();
int mask = (1 << ((msb - lsb) + 1)) - 1;
return (value >> lsb) & mask;
```

### VarClients
- Client-side only (not server-synced)
- `VarClientInt` / `VarClientStr`
- Used by client scripts for UI state (e.g., chat input text)

### Finding Vars
Use the Var Inspector in DevTools — it logs all var changes in real-time. Do an action in-game and watch what changes.

---

## Client Scripts

Jagex uses client scripts (cs2) for building interfaces and handling input. RuneLite can:
- **Read** decompiled scripts from the cache
- **Override** scripts by placing modified `rs2asm` in `runelite-client/src/main/scripts`
- **Insert callbacks** via `runelite_callback` instruction, which posts `ScriptCallbackEvent` to the event bus

Decompiled scripts available at: https://github.com/runelite/cs2-scripts

---

## Plugin Hub Submission

### Requirements
- Standalone Gradle project using RuneLite API
- Java only (no Kotlin/Scala)
- No reflection, JNI, external code download, or subprocess execution
- Reviewed by trusted RuneLite developers before acceptance
- Must comply with Jagex third-party client guidelines

### Forbidden Behaviours
- Java reflection
- JNI (Java Native Interface)
- External program execution
- Runtime code download
- Exposing player information over HTTP
- Crowdsourcing player data
- Programmatic chat input (autotyping)
- Storing account credentials directly
- Adult/sexual content
- Simulating game content

**Rule of thumb**: If reviewers can't read every line of source code your plugin executes, it won't be accepted.

---

## Rejected Features & Guidelines

Features Jagex has requested removal of or RuneLite won't implement:

### Removed by Jagex
- AoE plugin (area-of-effect indicators)
- Zulrah helper (rotation/phase overlay)
- Demonic Gorilla plugin (attack style prediction)
- Fight Cave / Jad plugin (prayer switching helper)
- Cerberus plugin (ghost order prediction)
- Volcanic Mine helper
- Inventory pane background removal (trivializes click-intensive skilling)

### Won't Implement
- Boss helpers that trivialize encounters
- Opponent freeze timers
- Spellbook resizing
- AFK agility aids
- Level-based PvP indicators
- Camera presets (yaw/pitch/position)
- Touchscreen/controller plugins (triggers macro detection)
- ID-based plugins (user-provided IDs cause moderation issues)
- Twitch/BTTV/FFZ emote plugins (licensing issues)

### Menu Entry Swapping Rules
- Left-click and shift-click swaps on NPCs/objects: **allowed**
- Conditional menu entry removing: **not allowed** (too powerful for hiding attack options)

---

## Developer Tools

Enable with `--developer-mode` program argument and `-ea` VM argument.

### Available Tools
- **Var Inspector**: Logs all var changes in real-time
- **Widget Inspector**: Browse all visible widgets and their properties
- **Item/NPC/Object Inspector**: Look up IDs and properties
- **Tile Inspector**: Show what's on a specific tile

### External Resources
- [API Javadoc](https://static.runelite.net/runelite-api/apidocs/)
- [Client Javadoc](https://static.runelite.net/runelite-client/apidocs/)
- [Cache Viewer](https://abextm.github.io/cache2/#/viewer) — browse game cache data
- [World Map Coordinates](https://mejrs.github.io/osrs) — find world positions
- [MOID](https://chisel.weirdgloop.org/moid/) — item/NPC/object ID database
- [CS2 Scripts](https://github.com/runelite/cs2-scripts/) — decompiled client scripts
