"""
ZoneManager — hardcoded UI zone positions for RuneLite Fixed-Classic layout at 1920×1080.

WARNING: Zone positions are hardcoded for Fixed-Classic 1920×1080.
         Other resolutions/layouts will produce incorrect click targets.
         Run with --detect-zones to use template-matched detection (Phase 4).
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

_LAYOUT_WARNING = (
    "\n"
    "╔══════════════════════════════════════════════════════════════╗\n"
    "║  WARNING: Zone positions are hardcoded for Fixed-Classic    ║\n"
    "║           1920×1080 at 100%% display scaling.               ║\n"
    "║  Other resolutions/layouts will produce incorrect clicks.   ║\n"
    "║  Run with --detect-zones to use template-matched detection  ║\n"
    "║  (Phase 4).                                                 ║\n"
    "╚══════════════════════════════════════════════════════════════╝"
)

# ── Fixed-Classic 1920×1080 layout constants ────────────────────────────────
# All coordinates are relative to the RuneLite canvas (game viewport) origin.

# Inventory grid: top-left slot origin and spacing
_INV_ORIGIN_X = 562
_INV_ORIGIN_Y = 208
_INV_SLOT_W   = 36
_INV_SLOT_H   = 36
_INV_SPACING_X = 42
_INV_SPACING_Y = 46
_INV_COLS = 4
_INV_ROWS = 7

# Game view (main viewport area — excludes side panel)
_GAME_VIEW = (0, 0, 512, 334)   # (x, y, w, h)

# Minimap region approximate positions
_MINIMAP = {
    "minimap":   (572, 4,  152, 152),  # full minimap circle area
    "hp_orb":    (520, 44,  26,  26),
    "prayer_orb":(520, 84,  26,  26),
    "run_orb":   (520, 124, 26,  26),
    "spec_orb":  (520, 164, 26,  26),
}


class ZoneManager:
    """
    Provides canvas-relative bounding rectangles for UI zones.
    Phase 1: hardcoded for Fixed-Classic 1920×1080.
    """

    def __init__(self, capture=None):
        self._capture = capture  # ScreenCapture instance (unused in Phase 1)
        logger.warning(_LAYOUT_WARNING)

    def get_game_view_rect(self) -> tuple[int, int, int, int]:
        """Returns (x, y, w, h) of the main game viewport (canvas-relative)."""
        return _GAME_VIEW

    def get_game_view(self, full_canvas: np.ndarray) -> np.ndarray:
        """Crop the game view region from a full canvas BGR image."""
        x, y, w, h = _GAME_VIEW
        return full_canvas[y:y+h, x:x+w]

    def get_inventory_slots(self) -> list[tuple[int, int, int, int]]:
        """
        Returns 28 canvas-relative (x, y, w, h) rects for each inventory slot,
        in reading order (left→right, top→bottom).
        """
        slots = []
        for row in range(_INV_ROWS):
            for col in range(_INV_COLS):
                x = _INV_ORIGIN_X + col * _INV_SPACING_X
                y = _INV_ORIGIN_Y + row * _INV_SPACING_Y
                slots.append((x, y, _INV_SLOT_W, _INV_SLOT_H))
        return slots

    def get_inventory_slot_center(self, slot_index: int) -> tuple[int, int]:
        """Returns the center (x, y) of the given inventory slot (0–27)."""
        x, y, w, h = self.get_inventory_slots()[slot_index]
        return x + w // 2, y + h // 2

    def get_minimap_zones(self) -> dict[str, tuple[int, int, int, int]]:
        """Returns canvas-relative rects for minimap overlay zones."""
        return dict(_MINIMAP)
