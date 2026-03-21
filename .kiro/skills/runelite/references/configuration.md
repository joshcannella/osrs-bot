# RuneLite Configuration

## Table of Contents
- [Client Settings](#client-settings)
- [Profiles](#profiles)
- [ChromaScape Setup](#chromascape-setup)
- [File Locations](#file-locations)
- [Troubleshooting](#troubleshooting)

---

## Client Settings

### Window Settings
- **Game size**: Resize client window
- **Lock window size**: Prevent accidental resizing
- **Remember client position**: Saves position/size between sessions
- **Always on top**: Client stays in front of other windows
- **Custom window chrome**: RuneLite-styled title bar and borders
- **Window opacity**: Adjustable transparency

### Overlay Settings
- **Dynamic overlay font**: Font for in-game overlays (player names, ground items)
- **Tooltip font**: Font for hover tooltips
- **Interface font**: Font for interface overlays (opponent info, clue scrolls)
- **Infobox size**: Pixel size of infoboxes
- **Overlay colour**: Background colour of infoboxes and overlays
- **Drag hotkey**: Key to drag overlays (default: Alt)

### Moving Overlays
Hold Alt and drag overlays/infoboxes to reposition. Blue squares show snap positions. Alt+right-click to reset position.

### Custom Assets
Place in `~/.runelite/`:
- `cursor.png` — custom cursor
- `fonts/<name>.ttf` — custom fonts
- `notification.wav` — default notification sound
- `notifications/<name>.wav` — named notification sounds
- `login.png` — custom login screen (765×503 recommended)

---

## Profiles

Profiles are separate sets of plugin settings that can be switched instantly.

### Managing Profiles
- Access via Configuration panel → Profiles tab
- **Create**: New profile button
- **Rename**: Click arrow → rename button
- **Duplicate**: Clone existing profile
- **Export**: Copy settings to clipboard/file
- **Delete**: Remove profile (optionally keep settings)
- **Reorder**: Drag profiles to rearrange
- **Default per account**: Assign a profile to a specific RuneScape account
- **Cloud sync**: Enable per-profile via RuneLite.net account

### Startup Profile
- Default: loads most recently active profile
- Override: pass `--profile=<name>` to launcher
- Legacy `--session`/`--config` users: use import feature to convert to profiles

### Storage
- Settings stored in `~/.runelite/profiles2/`
- Each profile is a separate settings file
- Cloud-synced profiles update across machines

---

## ChromaScape Setup

These RuneLite settings are required for ChromaScape scripts to work correctly:

### Display
- **Windows Display Scaling**: 100% (Settings → Display → Scale)
- **Interface Styles**: "Fixed - Classic" or "Resizable - Classic" gameframe
- **Brightness**: Middle position (50%) in OSRS display settings
- **Stretched Mode**: If enabled, calibrate scripts for the specific scaling %

### Required Plugins
| Plugin | Setting | Why |
|--------|---------|-----|
| Idle Notifier | Idle Animation + Idle Interaction ON | `Idler.waitUntilIdle()` depends on it |
| NPC Indicators | Hull highlight, distinct colour | Colour detection for NPCs |
| Ground Items | Tile highlight ON, distinct tier colours | Loot detection |
| Interface Styles | Fixed/Resizable Classic | Zone mapping assumes this layout |

### Recommended Plugins
| Plugin | Setting | Why |
|--------|---------|-----|
| Object Markers | Mark relevant objects | Colour detection for banks, furnaces, etc. |
| Ground Markers | Mark key tiles | Navigation waypoints |
| NPC Aggression Timer | Enable for combat areas | Aggro reset timing |
| Camera | Set consistent zoom | Stable detection coordinates |
| Menu Entry Swapper | Match script expectations | Ensure left-click does the right action |

### ChromaScape Profile
Create a dedicated RuneLite profile for ChromaScape with all the above settings. Switch to it before running scripts.

### XP Bar
Set to permanent display (not fading) if scripts use `Minimap.getXp()` for progress tracking.

### Potential Conflicts
- **Tile Indicators**: Destination tile highlight can interfere with colour detection if same colour as targets. Disable or use non-conflicting colour.
- **Entity Hider**: Don't hide NPCs/objects the script needs to detect.
- **Ground Items**: Ensure highlight colours don't overlap with NPC indicator colours.
- **GPU plugin**: Extended draw distance can affect what's visible. Scripts calibrated for standard draw distance may behave differently.

---

## File Locations

| Platform | Path |
|----------|------|
| Windows | `%userprofile%\.runelite\` |
| macOS | `~/.runelite/` |
| Linux | `~/.runelite/` |

### Directory Contents
```
~/.runelite/
├── profiles2/          # Profile settings files
├── logs/               # Client logs
├── screenshots/        # Auto-screenshots
├── fonts/              # Custom fonts
├── notifications/      # Custom notification sounds
├── cursor.png          # Custom cursor
├── login.png           # Custom login screen
└── notification.wav    # Default notification sound
```

---

## Troubleshooting

### Safe Mode
Disables all Plugin Hub plugins and GPU. Useful for isolating issues.
- Windows: Run "RuneLite (safe mode)" shortcut
- macOS: `/Applications/RuneLite.app/Contents/MacOS/RuneLite --safe-mode`
- With Jagex account: Use "RuneLite (configure)" shortcut → check "Safe mode"

### Common Issues
- **Plugin Hub not loading**: Only works on release builds, check `https://repo.runelite.net` access
- **Hub plugin broken**: Report to plugin developer (click ? button next to plugin in Hub)
- **Client won't start**: Delete `%TEMP%/cache-165`, or run Gradle `:cleanAll`
- **White/black screen**: Try disabling GPU plugin via safe mode
- **Settings missing**: Check you're on the correct profile
- **Loot tracker empty**: Data requires RuneLite.net login for persistence, 90-day retention per source
