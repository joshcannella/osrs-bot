# Built-in Plugins Reference

RuneLite ships with ~130 built-in plugins. This reference covers every plugin, grouped by category. Plugins marked with ⭐ are especially relevant to ChromaScape scripting.

## Table of Contents
- [Highlighting & Markers](#highlighting--markers)
- [Combat & PvM](#combat--pvm)
- [Skilling](#skilling)
- [Bank & Inventory](#bank--inventory)
- [Chat & Social](#chat--social)
- [UI & Display](#ui--display)
- [Notifications & Tracking](#notifications--tracking)
- [Navigation & World](#navigation--world)
- [Minigames](#minigames)
- [Miscellaneous](#miscellaneous)

---

## Highlighting & Markers

### ⭐ NPC Indicators
Highlights tagged NPCs with configurable colour and style.
- **Highlight styles**: Off, Tile (1x1 under NPC), Hull (outline around body, default)
- **NPCs to Highlight**: Comma-separated names, supports wildcards (`TzHaar*`, `*impling`)
- **Colour**: Default cyan, configurable per-NPC
- **Options**: Draw names above NPC, draw on minimap
- **ChromaScape**: This is how scripts detect NPCs — highlight in a distinct colour, then use `PointSelector.getRandomPointInColour()`.

### ⭐ Ground Items
Highlights ground items with value-tiered colours and GE/HA price display.
- **Value tiers**: Low, Medium, High, Insane — each with configurable colour and price threshold
- **Per-item colours**: Shift+right-click to set custom colour for specific items
- **Highlighted/Hidden lists**: Comma-separated item names, supports quantity filters (`item<5`, `item>5`)
- **Highlight modes**: Tile highlight, text overlay, or both
- **Ownership filter**: All / Takeable / Drops (your loot only)
- **Despawn timer**: Green (visible to others countdown), Yellow (despawn countdown)
- **Lootbeams**: Configurable for highlighted items or by value tier
- **Collapse menu**: Groups identical ground items in right-click menu
- **ChromaScape**: Essential for loot detection. Configure distinct colours per tier, detect with `ColourContours`.

### ⭐ Object Markers
Mark game objects with colour overlays. Shift+right-click → "Mark" to toggle.
- Persists between sessions
- **ChromaScape**: Mark bank booths, furnaces, anvils, etc. for colour detection.

### ⭐ Ground Markers
Mark tiles with configurable colours. Shift+right-click → "Mark tile".
- **Options**: Border width, fill opacity, minimap display, labels, per-tile colours
- **Import/Export**: Right-click World Map orb. JSON format with regionId, regionX/Y, z, color
- **Cloud sync**: Via RuneLite.net account
- **ChromaScape**: Mark navigation waypoints, safe tiles, reset positions.

### ⭐ Tile Indicators
Highlights the tile you're moving to (destination tile).
- Configurable colour
- **ChromaScape**: Can interfere with colour detection if same colour as targets. Disable or use a non-conflicting colour.

### Screen Markers
Draw persistent rectangles on the client window.
- Create via sidebar panel, snap to UI widgets or draw freehand
- Configurable border colour, fill colour, transparency, thickness
- Move with Alt+drag
- **Use cases**: Mark inventory slots, spell positions, agility obstacles

### Player Indicators
Highlights other players by type (friends, clan, team, non-clan).
- Configurable colours per category
- Draw on minimap option

### Entity Hider
Hide other players, NPCs, projectiles, or pets from rendering.
- Options: Hide others, hide friends, hide clan, hide local player, hide NPCs, hide pets, hide projectiles, hide dead NPCs

---

## Combat & PvM

### ⭐ NPC Aggression Timer
Shows how long until NPCs become unaggressive (10-minute timer).
- **Area lines**: Displays the boundary you must leave to reset aggro
- **NPC names**: Filter which NPCs trigger the timer (supports wildcards)
- **Always active**: Show timer regardless of nearby NPCs
- **Crab note**: Rock/sand/ammonite crabs — enter the NPC's rock form name (e.g., `fossil rock`)
- **ChromaScape**: Useful for combat scripts that need aggro reset logic.

### Opponent Information
Shows opponent's HP bar and hit counter above their model.

### Attack Styles
Warns when using an undesired attack style (e.g., training Defence accidentally).
- Configurable warnings per style
- Can hide the attack style interface

### Special Attack Counter
Tracks special attack damage dealt by you and your party.

### Boss Timers
Shows respawn timers for bosses after kills.

### Cannon
Shows cannon placement tile and remaining cannonball count.

### Slayer
Tracks slayer task progress with infobox showing remaining kills.

---

## Skilling

### Agility
Highlights agility course obstacles and shows lap counter.
- Marks of grace highlighting
- Obstacle highlighting with configurable colour

### Mining
Shows mining spot status and respawn timers.

### Woodcutting
Shows tree respawn timers and session stats.

### Fishing
Shows fishing spot types and movement indicators.
- Aerial fishing helper
- Minnow movement indicator

### Cooking
Shows cooking success/fail rates and burn chance.

### Runecraft
Highlights Abyss rifts and shows pouch degradation.

### Hunter
Shows trap status (set, caught, fallen).

### Motherlode Mine
Shows sack count, pay-dirt on ground, and vein timers.

### Blast Furnace
Shows bar dispenser status, conveyor belt, and coffer amount.

### Blast Mine
Shows dynamite placement and collection status.

### Herbiboar
Tracks herbiboar trail and shows start/end locations.

### Smelting
Shows smelting progress.

---

## Bank & Inventory

### ⭐ Bank
Enhanced bank features.
- **Bank value**: Shows total GE/HA value in bank title
- **Keyboard bankpin**: Use keyboard for PIN entry
- **Advanced search**: `qty > 10`, `ha > 5k`, `ge > 1m`, `ha per > 1m` (per-item)
- **Disable left-click**: Prevents accidental clicks on bank inventory/equipment buttons

### Bank Tags
Tag bank items for fast searching and organization.
- **Tag tabs**: Visual tabs in bank sidebar for quick access to tagged items
- **Drag to tag**: Drag items onto tab to tag them
- **Variant tagging**: Shift+drag to tag all variants (potion doses, degraded items)
- **Search**: `tag:name` for tag-only search

### Inventory Grid
Shows grid lines in inventory.

### Inventory Tags
Colour-code inventory items with configurable tag groups.

### Inventory Viewer
Shows inventory contents in an overlay outside the inventory tab.

### Item Charges
Tracks remaining charges on items (teleport jewellery, degradable equipment, etc.).

### Item Identification
Shows abbreviated names on items (e.g., herb identification).

### Item Prices
Shows GE price when examining items.

### Item Stats
Shows equipment stat changes when hovering over items.

### Rune Pouch
Shows rune pouch contents as an overlay.

---

## Chat & Social

### Chat Commands
Type commands in chat for quick lookups:
- `!lvl <skill>` — show skill level
- `!kc <boss>` — show boss kill count
- `!pb <activity>` — show personal best
- `!clues <tier>` — show clue completions
- `!qp` — show quest points
- `!gc` — show collection log count

### Chat Filter
Filter chat messages by regex or keyword. Supports filtering by type (public, private, clan).

### Chat Colour
Customize chat text colours by message type.

### Chat Notifications
Highlight messages containing specific words. Supports regex.

### Chat Timestamps
Add timestamps to chat messages.

### Chat History
Preserves chat history when hopping worlds or logging out.

### Chat Channels
Shows clan/friends chat rank icons.

### Friend List
Shows world numbers next to online friends.

### Friend Notes
Add notes to friends list entries.

---

## UI & Display

### ⭐ Interface Styles
Changes the gameframe appearance.
- **Gameframe options**: 2005, 2006, 2010
- **Stack bottom bar**: Always stack interface tiles in resizable mode
- **HD health bars**: RuneScape HD-style health bars
- **HD menu**: HD-style right-click menu
- **Menu alpha**: Transparency for right-click menu (0-255)
- **ChromaScape**: Requires "Fixed - Classic" or "Resizable - Classic" gameframe.

### ⭐ Camera
Controls zoom and camera behaviour.
- **Inner/Outer zoom limits**: Expand zoom range
- **Vertical camera**: Allow higher camera angles
- **Zoom speed**: Configurable
- **Right-click moves camera**: Remaps right-click to middle-mouse when no menu options
- **Compass options**: Adds Look South/East/West to compass right-click
- **Invert yaw/pitch**: Reverse camera movement directions
- **ChromaScape**: Scripts may need specific zoom levels for consistent detection.

### ⭐ Stretched Mode
Scales the game view to fill the window.
- **Integer scaling**: Whole number scale factor (sharper)
- **Keep aspect ratio**: Maintains proportions
- **Resizable scaling %**: Magnification amount
- **ChromaScape**: Affects pixel coordinates. Scripts should be calibrated for a specific scaling setting.

### GPU
Hardware-accelerated rendering with extended draw distance.
- Draw distance up to 90 tiles (vs 25 vanilla)
- Anti-aliasing, anisotropic filtering
- UI scaling mode (affects stretched mode sharpness)

### Low Detail
Reduces visual detail for performance (removes roofs, ground decorations, etc.).

### FPS Control
Limits FPS to reduce CPU/GPU usage. Separate limits for focused and unfocused client.

### Skybox
Adds a coloured skybox background.

### Animation Smoothing
Smooths NPC and player animations between game ticks.

### Custom Cursor
Replace the default cursor with a custom image (`~/.runelite/cursor.png`).

---

## Notifications & Tracking

### ⭐ Idle Notifier
Detects when the player goes idle or HP/prayer drops below threshold.
- **Idle animation**: Stopped skilling (mining, fletching, etc.)
- **Idle interaction**: Stopped interacting with NPC (combat, fishing)
- **Idle movement**: Character stopped moving
- **Idle logout**: No client interaction for too long
- **6-hour logout**: Approaching forced logout
- **HP/Prayer/Energy thresholds**: Configurable notification points
- **Special attack energy**: Notify when spec regenerates to threshold
- **Notification delay**: How long idle before triggering (don't set too low)
- **ChromaScape**: `Idler.waitUntilIdle()` depends on this plugin being enabled.

### XP Tracker
Tracks XP gains per skill with rates, time to level, and actions remaining.
- Sidebar panel with per-skill breakdown
- Overlay showing XP/hr and actions left

### XP Globes
Shows floating XP orbs near the minimap when gaining XP.

### XP Drop
Configures XP drop appearance (colour by prayer, group skills).

### XP Updater
Automatically updates hiscores after gaining XP.

### Loot Tracker
Tracks all loot drops in a sidebar panel.
- Groups by source (NPC, clue tier, activity)
- Shows individual and total value
- Chat message on kill with loot value
- Cloud sync via RuneLite.net account (90-day retention per source)
- **ChromaScape**: Useful for verifying script loot rates during testing.

### Boosts Information
Shows current stat boosts/drains with timers until they expire.

### Time Tracking
Tracks farming patches, birdhouses, and other timed activities.

### Daily Task Indicator
Reminds about daily activities (battlestaves, herb boxes, etc.).

### HiScore
Look up player stats from the sidebar.

### Skill Calculator
Calculate XP needed and items/actions required for target levels.

---

## Navigation & World

### ⭐ Menu Entry Swapper
Changes default left-click and shift-click options on objects, NPCs, and items.
- **Object swaps**: Shift+right-click → "Swap" to set custom left-click (e.g., "Bank" instead of "Talk-to")
- **Item swaps**: Shift+right-click inventory items to set left/shift-click options
- **NPC swaps**: Bank, Trade, Travel, Assignment, Exchange, Pay, etc.
- **UI swaps**: Bank deposit/withdrawal shift-click behaviour, GE collect options, shop buy/sell
- **ChromaScape**: Affects what action occurs when the bot clicks. Ensure swaps match script expectations.

### World Map
Enhanced world map with teleport locations, quest markers, and transportation routes.

### World Hopper
Quick world hopping from sidebar or right-click menu. Shows player counts.

### Minimap
Minimap customization (hide minimap, show player dot colour).

### Fairy Rings
Shows fairy ring codes and favourites.

### Clue Scroll
Solves clue scroll steps with map markers, puzzle solutions, and answers.

### Quest List
Shows quest completion status with filtering.

### Diary Requirements
Shows achievement diary requirements and completion status.

---

## Minigames

### Barbarian Assault
Shows role-specific information during BA.

### Barrows Brothers
Shows which brothers are killed and tunnel location.

### Chambers of Xeric
Scouting, point tracking, and raid layout display.

### Corporeal Beast
Shows damage counter and spec tracking.

### Mage Training Arena
Shows room-specific helpers for all four MTA rooms.

### Nightmare Zone
Shows power-up spawns and absorption/overload timers.

### Pest Control
Shows portal shield status and activity bar.

### Pyramid Plunder
Shows room timers and sarcophagus/urn status.

### Tears of Guthix
Shows stream movement timing.

### Tithe Farm
Shows plant status and watering timers.

### Wintertodt
Shows brazier status, damage timer, and points.

### Zalcano
Shows damage counter and shield status.

---

## Miscellaneous

### RuneLite (core settings)
Client-level settings: window size, always-on-top, sidebar toggle, overlay fonts, infobox size, drag hotkey.

### Login Screen
Custom login screen background (`~/.runelite/login.png`).

### Screenshot
Auto-screenshot on level ups, boss kills, loot drops, deaths, duels, pets, collection log.

### Discord
Shows OSRS activity in Discord Rich Presence.

### Twitch
Integration with Twitch chat for streamers.

### Examine
Shows GE/HA price when examining items.

### Poison
Shows poison/venom status and damage timer.

### Prayer
Shows prayer drain rate and time remaining.

### Status Bars
Shows HP/prayer bars near the game view.

### Regeneration Meter
Shows HP regeneration timer on the HP orb.

### Run Energy
Shows stamina potion timer and run energy recovery rate.

### Report Button
Shows login time on the report button.

### Logout Timer
Shows time until automatic logout.

### Random Events
Notifies and highlights your random events.

### Notes
In-client notepad accessible from sidebar.

### Info Panel
Shows RuneLite version, account info, and useful links.

### Emojis
Type emoji codes in chat (e.g., `:)` renders as emoji). Supports ~50 emojis.

### Key Remapping
Remap F-keys and other keys. Enables number keys for dialogue options.

### Anti-Drag
Requires holding Shift to drag items in inventory (prevents accidental drags).

### Mouse Tooltips
Shows tooltip text when hovering over interface elements.

### Spellbook
Filters and highlights spells. Shows rune requirements.

### Kingdom of Miscellania
Tracks kingdom approval and coffers.

### Kourend Library
Tracks book locations in the Arceuus library.

### Player-owned House
Shows room/furniture information in POH.

### Metronome
Plays a tick sound every game tick (0.6s). Useful for tick manipulation.

### Team
Shows team cape numbers on other players.

### Virtual Levels
Shows virtual levels above 99 (up to 126).

### Wiki
Adds "Lookup" option to right-click menu, opens OSRS Wiki page.

### Ammo
Shows remaining ammo count.

### Combat Level
Shows combat level next to player name.

### Default World
Sets a preferred world to log into.

### DPS Counter
Tracks damage per second in multi-combat.

### Grand Exchange
Shows GE offer status and notifications.

### Instance Map
Shows dungeon instance map.

### Implings
Highlights implings in the world with configurable colours.

### Party
Party system for sharing HP, prayer, spec, and location with friends.

### Mouse Over
Shows mouseover text information (item names, NPC names, object names).
