"""
Idler — waits until the player is idle (animation finished).

PHASE 1 STUB: sleeps a fixed 15 seconds with a loud warning.
Scripts requiring accurate idle detection (fishing, combat, skilling) will
behave incorrectly with this stub. The mining drop script works because it
doesn't need precise idle timing.

Phase 4 will replace this with OCR-based detection of the RuneLite
Idle Notifier chat message.
"""

import logging
import time

logger = logging.getLogger(__name__)

_STUB_WARNING = (
    "STUB: idler sleeping fixed 15s — fishing/combat/skilling scripts will "
    "behave incorrectly until Phase 4 OCR idle detection is implemented."
)


def wait_until_idle(controller=None, timeout_seconds: int = 20) -> None:
    """
    STUB: Wait for the player to become idle.

    Phase 1 implementation: fixed 15-second sleep.
    """
    logger.warning(_STUB_WARNING)
    time.sleep(15.0)


class Idler:
    def __init__(self, controller):
        self._ctrl = controller
        self._idle_engine = None

    def set_idle_engine(self, engine) -> None:
        """Register an IdleBehaviorEngine for human-like idle behavior."""
        self._idle_engine = engine

    def wait_until_idle(self, timeout_seconds: int = 20, stop_event=None) -> None:
        """Wait for the player to become idle.

        If an idle engine is registered, performs human-like idle behaviors
        (fidgets, camera rotations, brief AFK) during the wait.
        """
        if self._idle_engine is not None:
            self._idle_engine.idle_loop(min(timeout_seconds, 15.0), stop_event)
        else:
            wait_until_idle(self._ctrl, timeout_seconds)
