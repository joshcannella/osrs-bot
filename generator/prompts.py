"""
System prompt construction for the script generator.

Assembled fresh on every generation call. Includes:
1. Full Python framework API reference
2. One complete worked example (mining bot)
3. Coordinate system note
4. Available color names
5. Code rules
6. Live lessons from lessons-learned.md (capped at 30 + [critical])
"""

import json
import os
import re

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_LESSONS_PATH = os.path.join(_ROOT, "knowledge", "script-generation-lessons-learned.md")
_LESSONS_ARCHIVE_PATH = os.path.join(_ROOT, "knowledge", "lessons-archive.md")
_COLORS_PATH = os.path.join(_ROOT, "framework", "framework", "colors", "colors.json")


# ── Framework API Reference ──────────────────────────────────────────────────

_FRAMEWORK_API_REFERENCE = """\
# Python Framework API Reference

## BaseBot (framework.bot)
```python
class BaseBot:
    controller: Controller
    def cycle(self) -> None          # override with your bot logic
    def run(self) -> None            # main loop: init → cycle() until stop()
    def stop(self) -> None           # signal clean shutdown
    def wait_random_millis(self, min_ms: int, max_ms: int) -> None

    # Humanization: pass profile=HumanProfile() to enable anti-detection
    def __init__(self, debug=False, debug_dir="debug", profile=None): ...
```

## Controller (framework.controller)
```python
class Controller:
    capture: ScreenCapture           # screen capture
    mouse: RemoteMouse               # KInput remote mouse
    keyboard: RemoteKeyboard         # KInput remote keyboard
    zones: ZoneManager               # UI zone positions (inventory slots, game view, minimap)
    detection: DetectionFacade       # color detection helpers
    actions: ActionsFacade           # dropper, idler
    colors: ColorRegistry            # HSV color definitions
    game_state: GameStateClient | None  # RuneLite plugin bridge (None if plugin not running)
```

## ScreenCapture (framework.capture)
```python
class ScreenCapture:
    def capture_window(self) -> np.ndarray          # full canvas BGR image
    def capture_zone(self, rect) -> np.ndarray      # canvas-relative sub-region
    def get_window_rect(self) -> tuple[int,int,int,int]  # (x, y, w, h) screen coords
```

## RemoteMouse (framework.input.mouse)
```python
class RemoteMouse:
    def move_to(self, x: int, y: int) -> None       # instant move (canvas-relative)
    def move_to_wind(self, x: int, y: int, speed: str = "medium") -> None  # WindMouse humanized
    def left_click(self) -> None
    def right_click(self) -> None
    @property
    def pos(self) -> tuple[int, int]
```

## RemoteKeyboard (framework.input.keyboard)
```python
class RemoteKeyboard:
    def send_key_char(self, char: str) -> None               # type a character
    def send_modifier_key(self, action: str, key: str) -> None  # "press"/"release", "shift"/"ctrl"/etc.
    def send_string(self, text: str, delay_ms: int = 50) -> None
    def hold_key(self, key: str | int, duration_ms: int) -> None  # press, hold, release
```

## DetectionFacade (framework.controller)
```python
class DetectionFacade:
    def get_random_point_in_color(
        self, color_name: str, max_attempts: int = 15, image: np.ndarray | None = None
    ) -> tuple[int, int] | None
    # Returns canvas-relative (x, y) of a random point inside the closest
    # contour matching the named color. Returns None if nothing found.
    # If image is None, captures a fresh canvas screenshot.
```

## ZoneManager (framework.zones.zone_manager)
```python
class ZoneManager:
    def get_game_view_rect(self) -> tuple[int,int,int,int]   # (x, y, w, h)
    def get_game_view(self, full_canvas: np.ndarray) -> np.ndarray
    def get_inventory_slots(self) -> list[tuple[int,int,int,int]]  # 28 rects
    def get_inventory_slot_center(self, slot_index: int) -> tuple[int, int]
    def get_minimap_zones(self) -> dict[str, tuple[int,int,int,int]]
```

## ActionsFacade (framework.controller)
```python
class ActionsFacade:
    dropper: ItemDropper    # dropper.drop_all(exclude=[])
    idler: Idler            # idler.wait_until_idle(timeout_seconds=20)
```

## GameStateClient (framework.game_state.client) — available when RuneLite plugin is running
```python
class GameStateClient:
    def is_available(self) -> bool
    def get_player(self) -> dict | None        # {x, y, hp, prayer, run_energy, animation_id, canvas_x, canvas_y}
    def get_inventory(self) -> list[dict]      # [{slot, item_id, quantity}, ...]
    def get_npcs(self) -> list[dict]           # [{id, name, canvas_x, canvas_y, hp_ratio}, ...]
    def get_stats(self) -> dict | None         # {skill_name: {level, boosted, xp}, ...}
    def get_ground_items(self) -> list[dict]
```

## HumanProfile (framework.humanize.profile)
```python
from framework.humanize.profile import HumanProfile

# Default profile — enables all anti-detection features
profile = HumanProfile()

# Randomized variant — unique fingerprint per session
profile = HumanProfile.random_variant()
```

## Utilities
```python
from framework.humanize import wait_random_millis
# wait_random_millis(min_ms, max_ms) — or use self.wait_random_millis() from BaseBot
# When HumanProfile is active, uses log-normal distribution + fatigue scaling automatically
```
"""


# ── Example Script ───────────────────────────────────────────────────────────

_EXAMPLE_SCRIPT = """\
# Complete Example: Iron Mining Bot

```python
# WARNING: Do not run on accounts less than 24 hours old with no quest completions.
import argparse
import logging
from framework.bot import BaseBot
from framework.humanize.profile import HumanProfile

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(name)s %(message)s")
logger = logging.getLogger("iron_miner")

ROCK_COLOR = "Cyan"
STUCK_LIMIT = 5

class IronMiner(BaseBot):
    def __init__(self, debug=False):
        profile = None if debug else HumanProfile()
        super().__init__(debug=debug, debug_dir="debug/iron_miner", profile=profile)
        self._state = "MINING"
        self._stuck = 0

    def cycle(self):
        if self._state == "MINING":
            self._mine()
        elif self._state == "DROPPING":
            self._drop()

    def _mine(self):
        canvas = self.controller.capture.capture_window()
        game_view = self.controller.zones.get_game_view(canvas)

        point = self.controller.detection.get_random_point_in_color(
            ROCK_COLOR, max_attempts=15, image=game_view
        )

        if point is None:
            self._stuck += 1
            logger.warning("No rock found (%d/%d)", self._stuck, STUCK_LIMIT)
            if self._stuck >= STUCK_LIMIT:
                logger.error("Stuck — stopping")
                raise StopIteration
            self.wait_random_millis(1000, 2000)
            return

        self._stuck = 0

        # Convert game_view coords to canvas coords
        gx, gy, _, _ = self.controller.zones.get_game_view_rect()
        self.controller.mouse.move_to_wind(point[0] + gx, point[1] + gy, "medium")
        self.controller.mouse.left_click()
        self.wait_random_millis(800, 1200)
        self.controller.actions.idler.wait_until_idle()

        # Check inventory
        if self.controller.game_state and self.controller.game_state.is_available():
            inv = self.controller.game_state.get_inventory()
            filled = sum(1 for s in inv if s.get("item_id", -1) != -1)
            if filled >= 28:
                self._state = "DROPPING"
        else:
            self._state = "DROPPING"  # Phase 1 fallback: always drop

    def _drop(self):
        self.controller.actions.dropper.drop_all()
        self.wait_random_millis(400, 800)
        self._state = "MINING"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    IronMiner(debug=args.debug).run()
```
"""


# ── Code Rules ───────────────────────────────────────────────────────────────

_CODE_RULES = """\
# Code Rules (Mandatory)

1. **Null-check all detection results.** `get_random_point_in_color()` can return None.
   Always handle the None case (log, retry, or stop).

2. **Always use `wait_random_millis()` between actions.** Never use fixed `time.sleep()`.
   Bot timing must vary to look human.

3. **State machine pattern.** Use a `self._state` string to track what the bot is doing.
   Each state maps to a method. Log state transitions.

4. **Log at decision points.** Every significant action (click, state change, detection
   result) must be logged at INFO or DEBUG level.

5. **Stuck detection with shutdown.** Track a counter that increments when a cycle makes
   no progress and resets on success. After a threshold (e.g., 5-10 cycles),
   `raise StopIteration` to cleanly shut down.

6. **Never hardcode sleep values.** Use `self.wait_random_millis(min_ms, max_ms)` with
   appropriate ranges.

7. **Convert game_view coordinates to canvas coordinates.** When you detect a point in
   a cropped game_view image, add the game_view origin offset before passing to mouse:
   ```python
   gx, gy, _, _ = self.controller.zones.get_game_view_rect()
   canvas_x = point[0] + gx
   canvas_y = point[1] + gy
   ```

8. **Never assume inventory slot positions.** Use `game_state.get_inventory()` to check
   contents by item_id, or scan all 28 slots.

9. **Support --debug flag.** Accept `debug` parameter in __init__ and pass to BaseBot.

10. **Use the game state plugin when available.** Check `self.controller.game_state` is
    not None before calling its methods. Provide a fallback for when the plugin isn't running.

# Anti-Detection Rules (Mandatory)

11. **Always use `HumanProfile()` in production scripts.** Pass `profile=HumanProfile()`
    to BaseBot in __init__. Only omit for `--debug` mode. This enables breaks, fatigue,
    camera movement, varied timing, and idle behaviors automatically.

12. **Never act on the exact game tick a state change occurs.** Always wait at least 1
    game tick (600ms) plus a perception delay before responding to ore depletion, inventory
    change, or NPC movement. Tick-perfect scripts get banned.

13. **Variety over efficiency.** It's better to be 80% efficient with varied behavior than
    100% efficient with robotic precision. The framework handles this automatically via
    HumanProfile, but scripts should not fight it (e.g., don't retry immediately after a
    break or add extra sleeps that stack with humanization delays).

14. **Never run on fresh accounts.** Add this comment at the top of every generated script:
    `# WARNING: Do not run on accounts less than 24 hours old with no quest completions.`

# Coordinate System
All coordinates passed to RemoteMouse are canvas-relative (0,0 = top-left of the
RuneLite game viewport). Screen coordinates are never used directly.
"""


# ── Lessons Loading ──────────────────────────────────────────────────────────

def _load_recent_lessons(max_count: int = 30) -> str:
    """
    Load lessons from lessons-learned.md.
    Returns the last `max_count` lessons plus any tagged [critical].
    """
    if not os.path.exists(_LESSONS_PATH):
        return "(No lessons recorded yet.)"

    with open(_LESSONS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into individual lessons by the "---" separator
    sections = re.split(r"\n---\n", content)

    # First section is the title, skip it
    if sections and sections[0].strip().startswith("# "):
        sections = sections[1:]

    # Separate critical from non-critical
    critical = []
    regular = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if "[critical]" in section.lower():
            critical.append(section)
        else:
            regular.append(section)

    # Take the most recent `max_count` regular lessons
    recent = regular[-max_count:]

    # Combine critical (always included) + recent
    all_lessons = critical + recent
    if not all_lessons:
        return "(No lessons recorded yet.)"

    return "\n\n---\n\n".join(all_lessons)


def _load_color_names() -> str:
    if not os.path.exists(_COLORS_PATH):
        return "(colors.json not found)"
    with open(_COLORS_PATH, "r") as f:
        colors = json.load(f)
    return ", ".join(c["name"] for c in colors)


# ── Public API ───────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    """
    Assemble the full system prompt for script generation.
    Called fresh on every generation request.
    """
    color_names = _load_color_names()
    lessons = _load_recent_lessons(max_count=30)

    return (
        _FRAMEWORK_API_REFERENCE
        + "\n\n"
        + _EXAMPLE_SCRIPT
        + "\n\n"
        + _CODE_RULES
        + "\n\n"
        + f"# Available Color Names\n{color_names}\n\n"
        + f"# Lessons Learned From Previous Scripts\n{lessons}\n"
    )
