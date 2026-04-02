"""
FatigueModel — exponential approach curve simulating player tiredness over time.

multiplier = 1.0 + max_factor * (1 - e^(-rate * elapsed / ramp))

Fresh session: multiplier = 1.0 (no effect)
After ramp minutes: multiplier ≈ 1.0 + max_factor * 0.63
Fully fatigued: multiplier → 1.0 + max_factor
"""

import math
import time


class FatigueModel:
    """Tracks accumulated fatigue and produces timing/accuracy multipliers."""

    def __init__(
        self,
        rate: float = 1.0,
        max_factor: float = 0.4,
        ramp_minutes: float = 120.0,
    ):
        self._rate = rate
        self._max_factor = max_factor
        self._ramp_seconds = ramp_minutes * 60.0
        self._start = time.monotonic()

    @property
    def elapsed_minutes(self) -> float:
        return (time.monotonic() - self._start) / 60.0

    @property
    def multiplier(self) -> float:
        """Current timing multiplier (1.0 = fresh, up to 1.0 + max_factor)."""
        elapsed = time.monotonic() - self._start
        if self._ramp_seconds <= 0:
            return 1.0
        exponent = -self._rate * elapsed / self._ramp_seconds
        return 1.0 + self._max_factor * (1.0 - math.exp(exponent))

    def accuracy_penalty(self) -> float:
        """Extra pixel jitter due to fatigue (0.0 fresh, up to ~4px fatigued)."""
        # Scale 0-4px based on how close multiplier is to max
        fraction = (self.multiplier - 1.0) / self._max_factor if self._max_factor > 0 else 0
        return fraction * 4.0

    def reset(self) -> None:
        """Full reset — as if starting a fresh session (after long break)."""
        self._start = time.monotonic()

    def partial_reset(self, fraction: float = 0.5) -> None:
        """Partial reset — shift start time forward to reduce accumulated fatigue.

        fraction=0.5 means halve the accumulated fatigue (short break).
        fraction=0.1 means reduce fatigue by 10% (micro break).
        """
        elapsed = time.monotonic() - self._start
        reduced = elapsed * (1.0 - fraction)
        self._start = time.monotonic() - reduced
