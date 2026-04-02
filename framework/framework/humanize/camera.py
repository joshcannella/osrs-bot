"""
CameraController — random camera rotations via arrow key holds.

Simulates a real player periodically adjusting their camera angle.
Called during idle waits and between bot cycles.
"""

import random
import time

from framework.humanize.profile import HumanProfile


class CameraController:
    """Periodic camera rotation using arrow keys."""

    def __init__(self, profile: HumanProfile, keyboard, mouse=None):
        self._profile = profile
        self._keyboard = keyboard
        self._searching = False
        self._last_rotation = time.monotonic()
        self._next_interval = self._pick_interval()

    def set_searching(self, searching: bool) -> None:
        """Shorter rotation intervals when searching for something (e.g., ore respawn)."""
        self._searching = searching

    def maybe_rotate(self) -> None:
        """Check if it's time for a camera rotation. If so, perform one."""
        elapsed = time.monotonic() - self._last_rotation
        if elapsed < self._next_interval:
            return
        self._rotate()
        self._last_rotation = time.monotonic()
        self._next_interval = self._pick_interval()

    def _pick_interval(self) -> float:
        lo, hi = self._profile.camera_interval
        interval = random.uniform(lo, hi)
        if self._searching:
            interval *= self._profile.camera_searching_multiplier
        return interval

    def _rotate(self) -> None:
        """Perform a random camera rotation."""
        # Horizontal rotation (left/right) — always
        direction = random.choice(["left", "right"])
        duration_ms = random.randint(200, 1500)
        self._keyboard.hold_key(direction, duration_ms)

        # 15% chance of also adjusting pitch (up/down)
        if random.random() < 0.15:
            time.sleep(random.uniform(0.05, 0.2))
            pitch = random.choice(["up", "down"])
            pitch_ms = random.randint(100, 600)
            self._keyboard.hold_key(pitch, pitch_ms)
