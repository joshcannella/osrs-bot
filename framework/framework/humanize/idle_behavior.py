"""
IdleBehaviorEngine — simulates idle human behavior during waits.

During waits (mining, fishing, woodcutting), a real player doesn't sit
perfectly still. They fidget the mouse, hover over inventory, occasionally
go briefly AFK, or rotate the camera.
"""

import random
import time

from framework.humanize.profile import HumanProfile


class IdleBehaviorEngine:
    """Generates idle behaviors during wait periods."""

    def __init__(self, profile: HumanProfile, mouse, keyboard, camera=None):
        self._profile = profile
        self._mouse = mouse
        self._keyboard = keyboard
        self._camera = camera

    def perform_idle_action(self) -> None:
        """Randomly perform one idle behavior based on profile probabilities."""
        roll = random.random()
        total = 0.0

        # Brief AFK (no input at all)
        total += self._profile.idle_afk_probability
        if roll < total:
            self._brief_afk()
            return

        # Mouse fidget
        total += self._profile.idle_fidget_probability
        if roll < total:
            self._mouse_fidget()
            return

        # Camera rotation (if available)
        if self._camera is not None:
            total += 0.2
            if roll < total:
                self._camera._rotate()
                return

        # Default: small pause
        time.sleep(random.uniform(1.0, 3.0))

    def _brief_afk(self) -> None:
        """No input for 3-15 seconds."""
        time.sleep(random.uniform(3.0, 15.0))

    def _mouse_fidget(self) -> None:
        """Small random mouse movement ±30px from current position."""
        try:
            pos = self._mouse.get_position()
            if pos is None:
                return
            x, y = pos
            dx = random.randint(-30, 30)
            dy = random.randint(-30, 30)
            self._mouse.move_to(x + dx, y + dy)
        except Exception:
            pass

    def idle_loop(self, duration_seconds: float, stop_event=None) -> None:
        """Run idle behaviors for a duration, interruptible by stop_event.

        Used during waits where the bot is idle (e.g., waiting for ore).
        Performs random idle actions with 1-5 second gaps.
        """
        end_time = time.monotonic() + duration_seconds
        while time.monotonic() < end_time:
            if stop_event is not None and stop_event.is_set():
                return

            # Random chance to do something vs just wait
            if random.random() < 0.4:
                self.perform_idle_action()

            # Gap between actions
            gap = random.uniform(1.0, 5.0)
            remaining = end_time - time.monotonic()
            sleep_time = min(gap, max(0, remaining))
            if sleep_time > 0:
                # Sleep in 1s increments for stop_event responsiveness
                slept = 0.0
                while slept < sleep_time:
                    if stop_event is not None and stop_event.is_set():
                        return
                    chunk = min(1.0, sleep_time - slept)
                    time.sleep(chunk)
                    slept += chunk
