"""
ClickVariation — adds human-like imperfections to clicks.

Applies fatigue-based position jitter, misclicks, and double-clicks
based on HumanProfile probabilities.
"""

import random
import time

from framework.humanize.fatigue import FatigueModel
from framework.humanize.profile import HumanProfile
from framework.humanize.timing import TimingEngine


class ClickVariation:
    """Wraps click actions with human-like imperfections."""

    def __init__(self, profile: HumanProfile, timing: TimingEngine, fatigue: FatigueModel):
        self._profile = profile
        self._timing = timing
        self._fatigue = fatigue

    def jitter_position(self, x: int, y: int) -> tuple[int, int]:
        """Apply fatigue-based gaussian jitter to a click position."""
        penalty = self._fatigue.accuracy_penalty()
        if penalty < 0.5:
            return x, y
        jx = int(random.gauss(0, penalty))
        jy = int(random.gauss(0, penalty))
        return x + jx, y + jy

    def should_misclick(self) -> bool:
        """Roll for a misclick based on profile probability."""
        return random.random() < self._profile.misclick_probability

    def should_double_click(self) -> bool:
        """Roll for an accidental double-click."""
        return random.random() < self._profile.double_click_probability

    def misclick_offset(self) -> tuple[int, int]:
        """Generate an offset for a misclick (wrong spot, not far off)."""
        dx = random.randint(-30, 30)
        dy = random.randint(-30, 30)
        # Ensure it's at least a few pixels off
        if abs(dx) < 5:
            dx = 5 * (1 if dx >= 0 else -1)
        if abs(dy) < 5:
            dy = 5 * (1 if dy >= 0 else -1)
        return dx, dy

    def misclick_recovery_ms(self) -> int:
        """How long to pause after realizing a misclick (300-800ms)."""
        return random.randint(300, 800)

    def double_click_gap_ms(self) -> int:
        """Gap between accidental double-click presses (50-150ms)."""
        return random.randint(50, 150)

    def hold_ms(self, context: str = "skill") -> int:
        """Get press-release duration for a click."""
        return self._timing.click_hold_ms(context)
