"""
Demo Mining Bot — Python port of AlKharidIronMiningScript.java.

Mines iron ore at Al Kharid using Cyan-highlighted rocks (RuneLite Object Markers),
waits for idle (Phase 1: 15s stub), then drops the full inventory.

Usage:
    python scripts/demo_mining_bot.py            # live run
    python scripts/demo_mining_bot.py --debug    # dry-run + annotated screenshots in debug/

RuneLite Setup:
    Object Markers plugin → mark iron ore rocks with Cyan (#00FFFF)
    Idle Notifier → enabled (for Phase 4 OCR idle detection)

Prerequisites:
    Level 15 Mining, any pickaxe equipped, all 28 inventory slots free.
    RuneLite in Fixed - Classic layout, 1920×1080, 100% display scaling.
"""

import argparse
import logging
import sys
import os

# Allow running from the repo root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "framework"))

from framework.bot import BaseBot
from framework.humanize.profile import HumanProfile

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("demo_mining_bot")

# ── Constants ────────────────────────────────────────────────────────────────

ROCK_COLOR     = "Cyan"   # RuneLite Object Marker highlight color
IDLE_TIMEOUT   = 20       # seconds (Phase 1 stub ignores this)
STUCK_LIMIT    = 5        # consecutive cycles without finding a rock → stop

# ── Bot implementation ───────────────────────────────────────────────────────

class DemoMiningBot(BaseBot):
    """
    State machine:
      MINING  → click ore rock → wait idle → check inventory
      DROPPING → drop all ore → return to MINING
    """

    def __init__(self, debug: bool = False):
        profile = None if debug else HumanProfile()
        super().__init__(debug=debug, debug_dir="debug/demo_mining", profile=profile)
        self._state = "MINING"
        self._stuck_count = 0

    def cycle(self) -> None:
        if self._state == "MINING":
            self._do_mining()
        elif self._state == "DROPPING":
            self._do_dropping()

    def _do_mining(self) -> None:
        # Capture game view
        canvas = self.controller.capture.capture_window()
        game_view = self.controller.zones.get_game_view(canvas)

        # Find a cyan rock
        point = self.controller.detection.get_random_point_in_color(
            ROCK_COLOR, max_attempts=15, image=game_view
        )

        if point is None:
            self._stuck_count += 1
            logger.warning(
                "No %s rock found (stuck count: %d/%d)",
                ROCK_COLOR, self._stuck_count, STUCK_LIMIT,
            )
            if self._stuck_count >= STUCK_LIMIT:
                logger.error("No rock found for %d consecutive cycles — stopping", STUCK_LIMIT)
                raise StopIteration
            self.wait_random_millis(1000, 2000)
            return

        self._stuck_count = 0

        # Adjust point from game_view-relative to canvas-relative
        gx, gy, _, _ = self.controller.zones.get_game_view_rect()
        canvas_x = point[0] + gx
        canvas_y = point[1] + gy

        logger.info("Clicking rock at canvas (%d, %d)", canvas_x, canvas_y)
        self.controller.mouse.move_to_wind(canvas_x, canvas_y, speed="medium")
        self.controller.mouse.left_click()

        self.wait_random_millis(800, 1200)

        # Wait for mining animation to finish
        self.controller.actions.idler.wait_until_idle(timeout_seconds=IDLE_TIMEOUT)

        # Check if inventory is full (28 items)
        if self._is_inventory_full():
            logger.info("Inventory full — switching to DROPPING state")
            self._state = "DROPPING"

    def _do_dropping(self) -> None:
        logger.info("Dropping all inventory items")
        self.controller.actions.dropper.drop_all()
        self.wait_random_millis(400, 800)
        self._state = "MINING"
        logger.info("Inventory dropped — returning to MINING state")

    def _is_inventory_full(self) -> bool:
        """
        Phase 1: check via game state plugin if available, otherwise assume
        inventory fills after ~28 mining cycles (not implemented here — scripts
        that need this must use the plugin, Phase 2).

        For Phase 1 demo: always drops after each idle, to keep the loop simple.
        """
        if self.controller.game_state is not None:
            inv = self.controller.game_state.get_inventory()
            filled = sum(1 for slot in inv if slot.get("item_id", -1) != -1)
            logger.debug("Inventory slots filled: %d/28", filled)
            return filled >= 28

        # Phase 1 fallback: drop every N cycles (crude but functional for demo)
        # Scripts should upgrade to Phase 2 plugin for accurate inventory checks.
        return True  # always drop after each rock click


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Demo Mining Bot")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode: save annotated screenshots, no-op clicks",
    )
    args = parser.parse_args()

    bot = DemoMiningBot(debug=args.debug)
    bot.run()


if __name__ == "__main__":
    main()
