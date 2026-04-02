"""
Drop pattern variation — selects inventory drop order based on HumanProfile.

Patterns:
- Zigzag (default): alternating columns top-to-bottom
- Column: drop column by column left-to-right
- Random: shuffled order

Also adds mid-drop pauses to simulate distraction.
"""

import random

from framework.humanize.profile import HumanProfile

# OSRS inventory: 4 columns x 7 rows = 28 slots (0-indexed)
_COLS = 4
_ROWS = 7


def zigzag_order() -> list[int]:
    """Alternating-column zigzag: col0 top-down, col1 top-down, etc."""
    order = []
    for row in range(_ROWS):
        for col in range(_COLS):
            order.append(row * _COLS + col)
    return order


def column_order() -> list[int]:
    """Column-by-column: all of col0 top-down, then col1, etc."""
    order = []
    for col in range(_COLS):
        for row in range(_ROWS):
            order.append(row * _COLS + col)
    return order


def random_order() -> list[int]:
    """Fully shuffled slot order."""
    order = list(range(_COLS * _ROWS))
    random.shuffle(order)
    return order


def select_pattern(profile: HumanProfile) -> list[int]:
    """Pick a drop pattern based on profile probabilities."""
    roll = random.random()
    if roll < profile.zigzag_probability:
        return zigzag_order()
    elif roll < profile.zigzag_probability + profile.column_probability:
        return column_order()
    else:
        return random_order()


def should_pause_mid_drop(profile: HumanProfile) -> bool:
    """Roll for a mid-drop pause (simulating distraction)."""
    return random.random() < profile.drop_pause_probability


def mid_drop_pause_ms() -> int:
    """Duration of a mid-drop pause (500ms - 3000ms)."""
    return random.randint(500, 3000)
