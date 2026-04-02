"""
BreakManager — three-tier break scheduling with session limits.

Micro breaks:  3-8 min apart, 5-30s duration (idle)
Short breaks:  20-60 min apart, 2-10 min duration (may logout)
Long breaks:   2-4 hours apart, 15-60 min duration (always logout)

Checked before each cycle() call by BaseBot. Scripts are unaware of breaks.
"""

import logging
import random
import time

from framework.humanize.fatigue import FatigueModel
from framework.humanize.profile import HumanProfile

logger = logging.getLogger(__name__)


class BreakManager:
    """Schedules and executes breaks based on a HumanProfile."""

    def __init__(self, profile: HumanProfile, fatigue: FatigueModel, controller):
        self._profile = profile
        self._fatigue = fatigue
        self._ctrl = controller
        self._session_start = time.monotonic()

        # Schedule next break times
        self._next_micro = self._schedule(profile.micro_break_interval)
        self._next_short = self._schedule(profile.short_break_interval)
        self._next_long = self._schedule(profile.long_break_interval)

    def _schedule(self, interval: tuple[float, float]) -> float:
        """Return a monotonic timestamp for the next break."""
        return time.monotonic() + random.uniform(*interval)

    def check_and_take_break(self, stop_event) -> bool:
        """Check if a break is due and take it. Returns False if session limit reached.

        Called by BaseBot before each cycle(). Sleeps in 1s increments so
        stop_event can interrupt.
        """
        now = time.monotonic()
        session_hours = (now - self._session_start) / 3600.0
        limit = self._profile.daily_session_limit

        if limit > 0 and session_hours >= limit:
            logger.info("Daily session limit reached (%.1f hours) — stopping", session_hours)
            return False

        # Check breaks in order of priority (long > short > micro)
        if now >= self._next_long:
            self._take_break("long", self._profile.long_break_duration, stop_event)
            self._fatigue.reset()
            self._next_long = self._schedule(self._profile.long_break_interval)
            # Reset shorter break timers too
            self._next_short = self._schedule(self._profile.short_break_interval)
            self._next_micro = self._schedule(self._profile.micro_break_interval)
        elif now >= self._next_short:
            self._take_break("short", self._profile.short_break_duration, stop_event)
            self._fatigue.partial_reset(0.5)
            self._next_short = self._schedule(self._profile.short_break_interval)
            self._next_micro = self._schedule(self._profile.micro_break_interval)
        elif now >= self._next_micro:
            self._take_break("micro", self._profile.micro_break_duration, stop_event)
            self._fatigue.partial_reset(0.1)
            self._next_micro = self._schedule(self._profile.micro_break_interval)

        return True

    def _take_break(self, tier: str, duration_range: tuple[float, float], stop_event) -> None:
        """Execute a break of the given tier."""
        duration = random.uniform(*duration_range)
        logger.info("Taking %s break (%.0fs)", tier, duration)

        # Pick break behavior based on tier
        if tier == "long":
            self._break_logout(duration, stop_event)
        elif tier == "short":
            behavior = random.choice(["logout", "idle", "mouse_drift"])
            if behavior == "logout":
                self._break_logout(duration, stop_event)
            elif behavior == "mouse_drift":
                self._break_mouse_drift(stop_event)
                self._interruptible_sleep(duration * 0.9, stop_event)
            else:
                self._interruptible_sleep(duration, stop_event)
        else:
            # Micro: just idle or small mouse drift
            if random.random() < 0.3:
                self._break_mouse_drift(stop_event)
            self._interruptible_sleep(duration, stop_event)

        logger.info("%s break finished", tier.capitalize())

    def _break_logout(self, duration: float, stop_event) -> None:
        """Log out, wait, log back in."""
        # Press the logout button (fixed position in classic layout)
        # Tab to logout panel: click the door icon at the bottom-right of the interface
        logger.info("Logging out for break")
        # Send Escape to open the logout panel in most contexts
        self._ctrl.keyboard.send_modifier_key("press", "esc")
        time.sleep(0.1)
        self._ctrl.keyboard.send_modifier_key("release", "esc")
        time.sleep(random.uniform(0.5, 1.5))
        # Sleep for the break duration
        self._interruptible_sleep(duration, stop_event)
        # After break, the script's cycle() will handle re-login if needed

    def _break_mouse_drift(self, stop_event) -> None:
        """Move mouse to edge of screen."""
        try:
            edge_x = random.choice([0, 760])  # canvas edges
            edge_y = random.randint(0, 500)
            self._ctrl.mouse.move_to_wind(edge_x, edge_y, speed="slow")
        except Exception:
            pass

    def _interruptible_sleep(self, seconds: float, stop_event) -> None:
        """Sleep in 1s chunks, checking stop_event."""
        slept = 0.0
        while slept < seconds:
            if stop_event.is_set():
                return
            chunk = min(1.0, seconds - slept)
            time.sleep(chunk)
            slept += chunk
