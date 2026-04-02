"""
ItemDropper — shift-click drop with pattern variation.

Supports zigzag (default), column, and random drop orders via the
humanize.drop_patterns module when a HumanProfile is active.
"""

import logging
import random
import time

from framework.humanize import get_timing_engine

logger = logging.getLogger(__name__)

# Zigzag drop order: processes rows in pairs (0-1, 2-3, 4-5) then final row
def _zigzag_indices() -> list[int]:
    indices = []
    for row_group in range(3):      # row groups: 0-1, 2-3, 4-5
        base = row_group * 8        # 0, 8, 16
        for col in range(4):
            indices.append(base + col)      # top of pair
            indices.append(base + col + 4)  # bottom of pair
    indices.extend([24, 25, 26, 27])        # last row
    return indices

_ZIGZAG_ORDER = _zigzag_indices()


class ItemDropper:
    """
    Drops inventory items using shift-click with varied patterns.

    When a HumanProfile is active (TimingEngine registered), uses
    drop_patterns.select_pattern() for order and repetitive_delay()
    for inter-slot timing. Otherwise falls back to zigzag with uniform delay.
    """

    def __init__(self, controller):
        self._ctrl = controller

    def drop_all(self, exclude: list[int] | None = None) -> None:
        """
        Shift-click drop all 28 inventory slots.

        exclude: list of slot indices (0–27) to skip.
        """
        exclude_set = set(exclude or [])
        slots = self._ctrl.zones.get_inventory_slots()

        # Select drop pattern
        engine = get_timing_engine()
        if engine is not None:
            from framework.humanize.drop_patterns import select_pattern, should_pause_mid_drop, mid_drop_pause_ms
            order = select_pattern(engine._profile)
        else:
            order = _ZIGZAG_ORDER

        logger.info("Starting drop — %d slots to drop", 28 - len(exclude_set))

        self._ctrl.keyboard.send_modifier_key("press", "shift")
        time.sleep(random.uniform(0.10, 0.25))

        try:
            for i, idx in enumerate(order):
                if idx in exclude_set:
                    continue
                if idx >= len(slots):
                    continue

                x, y, w, h = slots[idx]
                cx = x + w // 2 + random.randint(-4, 4)
                cy = y + h // 2 + random.randint(-4, 4)

                self._ctrl.mouse.move_to_wind(cx, cy, speed="fast")
                self._ctrl.mouse.left_click()

                # Inter-slot delay
                if engine is not None:
                    engine.repetitive_delay(base_ms=40.0)
                    # Mid-drop pause check
                    if should_pause_mid_drop(engine._profile):
                        pause = mid_drop_pause_ms()
                        logger.debug("Mid-drop pause: %dms", pause)
                        time.sleep(pause / 1000.0)
                else:
                    time.sleep(random.uniform(0.04, 0.09))

        finally:
            time.sleep(random.uniform(0.10, 0.20))
            self._ctrl.keyboard.send_modifier_key("release", "shift")

        logger.info("Drop complete")
