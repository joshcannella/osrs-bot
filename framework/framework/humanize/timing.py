"""
TimingEngine — human-like timing distributions with fatigue scaling.

Replaces uniform random.randint with log-normal and gamma distributions
that better model real human reaction times and repetitive action intervals.
"""

import math
import random
import time

from framework.humanize.fatigue import FatigueModel
from framework.humanize.profile import HumanProfile


class TimingEngine:
    """Generates human-like delays based on a HumanProfile and FatigueModel."""

    def __init__(self, profile: HumanProfile, fatigue: FatigueModel):
        self._profile = profile
        self._fatigue = fatigue

    @property
    def fatigue(self) -> FatigueModel:
        return self._fatigue

    def wait_random_millis(self, min_ms: int, max_ms: int) -> None:
        """Sleep for a human-like duration between min_ms and max_ms.

        Uses a truncated log-normal distribution centered between min/max,
        scaled by the current fatigue multiplier.
        """
        if min_ms >= max_ms:
            time.sleep(min_ms / 1000.0)
            return

        # Log-normal centered at midpoint
        mid = (min_ms + max_ms) / 2.0
        mu = math.log(mid)
        sigma = 0.25  # moderate spread

        delay = random.lognormvariate(mu, sigma)
        # Truncate to [min_ms, max_ms * 1.3] — allow slight overshoot
        delay = max(min_ms, min(max_ms * 1.3, delay))
        # Apply fatigue
        delay *= self._fatigue.multiplier

        time.sleep(delay / 1000.0)

    def reaction_delay(self, expected: bool = True) -> None:
        """Simulate human perception + reaction time.

        expected=True: player is anticipating the event (e.g., waiting for ore)
        expected=False: unexpected event (e.g., random event, PK)

        Never produces delays shorter than min_reaction_ticks * 600ms.
        """
        p = self._profile
        mu = p.reaction_mu
        sigma = p.reaction_sigma

        if not expected:
            # Unexpected events: slower reaction, wider spread
            mu += 0.4
            sigma += 0.15

        delay_ms = random.lognormvariate(mu, sigma)
        # Clamp to reasonable range: 200ms - 4000ms
        delay_ms = max(200, min(4000, delay_ms))
        # Apply fatigue
        delay_ms *= self._fatigue.multiplier
        # Enforce tick discipline
        min_delay = p.min_reaction_ticks * 600.0
        delay_ms = max(min_delay, delay_ms)

        time.sleep(delay_ms / 1000.0)

    def repetitive_delay(self, base_ms: float = 60.0) -> None:
        """Delay for repetitive actions (typing, dropping inventory slots).

        Uses gamma distribution — peaked with a tail, models the rhythm
        of repeated keystrokes/clicks.
        """
        p = self._profile
        delay = random.gammavariate(p.repetitive_shape, p.repetitive_scale)
        delay = max(20, delay + base_ms)  # at least 20ms + base
        delay *= self._fatigue.multiplier
        time.sleep(delay / 1000.0)

    def click_hold_ms(self, context: str = "skill") -> int:
        """Generate a press-release duration for a mouse click.

        context: "skill" (default), "panic" (combat/flee), "drop" (inventory dropping)
        Returns milliseconds (not a sleep — caller handles timing).
        """
        p = self._profile
        if context == "panic":
            lo, hi = p.click_hold_panic
        else:
            lo, hi = p.click_hold_base

        # Gamma-distributed hold time centered in range
        mid = (lo + hi) / 2.0
        shape = 3.0
        scale = mid / shape
        hold = random.gammavariate(shape, scale)
        hold = max(lo * 0.8, min(hi * 1.3, hold))
        hold *= self._fatigue.multiplier
        return max(10, int(hold))
