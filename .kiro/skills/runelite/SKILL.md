---
name: runelite
description: RuneLite open-source OSRS client guide covering architecture, built-in plugins, Plugin Hub, plugin development, configuration profiles, and Jagex's third-party client guidelines. Use when discussing RuneLite plugins, recommending plugin configurations for scripts, reasoning about what RuneLite can detect or overlay, understanding the plugin event system, or anything related to the RuneLite client — even if the user doesn't mention RuneLite by name.
---

# RuneLite

RuneLite is the dominant open-source client for Old School RuneScape. It extends the vanilla client with a plugin system that can overlay information, highlight objects, track XP/loot, swap menu entries, and much more. Jagex officially approves RuneLite.

## Architecture

RuneLite is a Java application (JDK 11) built with Gradle. It wraps the OSRS game applet and injects hooks via its API layer.

```
runelite/
├── runelite-api/        # Public API — events, interfaces, enums (what plugins use)
├── runelite-client/     # Client core + all built-in plugins
│   └── plugins/         # ~130 built-in plugins
└── runelite-mixins/     # Bytecode injection layer (hooks into game code)
```

Key concepts:
- **Plugins** extend `Plugin`, annotated with `@PluginDescriptor`. They subscribe to events, inject services, and register overlays.
- **Events** drive everything — `GameObjectSpawned`, `NpcSpawned`, `ChatMessage`, `GameTick`, `ItemContainerChanged`, etc. Plugins use `@Subscribe` to react.
- **Overlays** extend `Overlay` and draw on the game canvas (tile highlights, text, clickboxes).
- **Config** interfaces (extending `Config`) generate settings panels automatically. Settings persist between sessions.
- **Dependency injection** (Guice) — plugins `@Inject` services like `Client`, `ConfigManager`, `OverlayManager`, `ItemManager`.

## Var System (Game State)

RuneLite exposes the game's variable system for reading state:
- **VarPlayers (VarPs)**: 32-bit ints set by server, attached to player account. Older content.
- **VarBits**: Variable-size bits packed into VarPs. Newer content. More efficient.
- **VarClientInts/Strs**: Client-side only, used by client scripts (e.g., current chat input).

Plugins read vars to detect quest progress, interface states, equipment, prayer status, etc.

## Plugin Hub

The Plugin Hub is a curated marketplace where anyone can submit plugins. Plugins are reviewed by trusted RuneLite developers for compliance with Jagex's third-party client guidelines. ~300+ community plugins available.

Hub plugins:
- Built as standalone Gradle projects using the RuneLite API
- Reviewed before acceptance (no reflection, no JNI, no external code download)
- Must be written in Java (no Kotlin/Scala)
- Auto-update independently of client releases

## Profiles

RuneLite supports multiple configuration profiles — separate sets of plugin settings that can be switched instantly. Useful for different accounts or activities. Profiles can be cloud-synced via RuneLite.net account.

## Jagex Guidelines (What's Allowed)

Jagex maintains rules for third-party clients. Key restrictions:
- No boss helpers that trivialize encounters (Zulrah, Jad, Cerberus, Demonic Gorillas — all removed)
- No freeze timers on opponents
- No spellbook resizing
- No AFK agility aids
- No programmatic chat input (considered autotyping)
- No crowdsourcing player data
- Menu entry swapping is allowed for left-click and shift-click on NPCs/objects

For the full rejected features list, read `references/plugin-development.md`.

## Key Plugins for ChromaScape

These built-in plugins are critical for colour-based bot scripting:

| Plugin | Why It Matters |
|--------|---------------|
| NPC Indicators | Highlights NPCs in configurable colours (default cyan). ChromaScape detects these highlights. |
| Ground Items | Highlights ground loot by value tier with configurable colours. Essential for loot detection. |
| Object Markers | Shift+right-click to mark game objects with colour overlays. |
| Ground Markers | Mark tiles with colours. Used for navigation waypoints. |
| Idle Notifier | Detects when player goes idle. ChromaScape's `Idler.waitUntilIdle()` depends on this. |
| NPC Aggression Timer | Shows aggro timer and area boundaries. Useful for combat scripts. |
| Interface Styles | Controls gameframe style (2005/2006/2010). ChromaScape requires "Fixed - Classic" or "Resizable - Classic". |
| Menu Entry Swapper | Changes default left-click options. Affects what happens when ChromaScape clicks objects. |
| Camera | Zoom limits, vertical camera. Scripts may need specific zoom levels. |
| Tile Indicators | Highlights destination tile. Can interfere with colour detection if same colour as targets. |

## When to Load References

| Task | Reference |
|------|-----------|
| Need details on a specific plugin | `references/built-in-plugins.md` |
| Understanding plugin architecture, events, overlays, config | `references/plugin-development.md` |
| Setting up RuneLite for scripting, profiles, troubleshooting | `references/configuration.md` |
