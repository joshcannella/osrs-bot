"""
BaseBot — base class for all OSRS automation scripts.

Override cycle() with your bot logic. Call run() to start the loop.
Ctrl+C triggers clean shutdown.

Example (no humanization):
    class MyBot(BaseBot):
        def cycle(self):
            point = self.controller.detection.get_random_point_in_color("Cyan")
            if point:
                self.controller.mouse.move_to_wind(*point)
                self.controller.mouse.left_click()
            self.wait_random_millis(600, 1200)

Example (with humanization — one parameter):
    class MyBot(BaseBot):
        def __init__(self, debug=False):
            super().__init__(debug=debug, profile=HumanProfile())

    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        args = parser.parse_args()
        MyBot(debug=args.debug).run()
"""

import logging
import threading
import time

from framework.controller import Controller
from framework.humanize import wait_random_millis as _wait_random_millis

logger = logging.getLogger(__name__)


class BaseBot:
    """
    Base class for all bot scripts.

    Subclass this and override `cycle()`. The `run()` method calls `cycle()`
    in a loop until `stop()` is called or a KeyboardInterrupt is received.

    Args:
        debug:     Enable debug mode. Screenshots are saved; clicks are no-ops.
        debug_dir: Directory for debug screenshots (default: "debug").
        profile:   Optional HumanProfile for anti-detection humanization.
                   Pass HumanProfile() to enable breaks, fatigue, camera
                   movement, varied timing, and idle behaviors.
    """

    def __init__(self, debug: bool = False, debug_dir: str = "debug", profile=None):
        self._debug = debug
        self._debug_dir = debug_dir
        self._profile = profile
        self._running = False
        self._stop_event = threading.Event()
        self.controller = Controller(debug=debug, debug_dir=debug_dir)

        # Humanization subsystems (initialized in run() after controller.init())
        self._fatigue = None
        self._timing = None
        self._camera = None
        self._break_manager = None
        self._idle_engine = None
        self._click_variation = None

    # ── Override in subclass ────────────────────────────────────────────────

    def cycle(self) -> None:
        """Main bot logic. Called repeatedly by run(). Override this."""
        raise NotImplementedError("Subclass must implement cycle()")

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def run(self) -> None:
        """
        Initialize the controller and loop cycle() until stopped.
        Handles KeyboardInterrupt cleanly.
        """
        if self._debug:
            logger.info(
                "DEBUG MODE: screenshots will be saved to '%s', clicks are no-ops",
                self._debug_dir,
            )

        try:
            self.controller.init()
            self._running = True
            self._stop_event.clear()

            if self._profile:
                self._init_humanization()

            logger.info("Bot started (debug=%s). Press Ctrl+C to stop.", self._debug)

            while not self._stop_event.is_set():
                # Break check (before each cycle)
                if self._break_manager:
                    if not self._break_manager.check_and_take_break(self._stop_event):
                        logger.info("Session limit reached — stopping bot")
                        break

                # Camera rotation check
                if self._camera:
                    self._camera.maybe_rotate()

                try:
                    self.cycle()
                except StopIteration:
                    logger.info("Bot requested stop via StopIteration")
                    break
                except Exception as exc:
                    logger.exception("Unhandled exception in cycle(): %s", exc)
                    break

        except KeyboardInterrupt:
            logger.info("Ctrl+C received — stopping bot")
        finally:
            self._running = False
            self.controller.shutdown()
            logger.info("Bot stopped")

    def _init_humanization(self) -> None:
        """Wire up all humanization subsystems from the profile."""
        from framework.humanize import set_timing_engine
        from framework.humanize.breaks import BreakManager
        from framework.humanize.camera import CameraController
        from framework.humanize.click import ClickVariation
        from framework.humanize.fatigue import FatigueModel
        from framework.humanize.idle_behavior import IdleBehaviorEngine
        from framework.humanize.timing import TimingEngine

        p = self._profile
        self._fatigue = FatigueModel(p.fatigue_rate, p.fatigue_max, p.fatigue_ramp_minutes)
        self._timing = TimingEngine(p, self._fatigue)
        set_timing_engine(self._timing)

        self._camera = CameraController(p, self.controller.keyboard, self.controller.mouse)
        self._break_manager = BreakManager(p, self._fatigue, self.controller)
        self._click_variation = ClickVariation(p, self._timing, self._fatigue)
        self._idle_engine = IdleBehaviorEngine(
            p, self.controller.mouse, self.controller.keyboard, self._camera
        )

        # Wire idle engine into the idler action
        if hasattr(self.controller, 'actions') and hasattr(self.controller.actions, 'idler'):
            self.controller.actions.idler.set_idle_engine(self._idle_engine)

        logger.info("Humanization enabled: profile='%s'", p.name)

    def start_in_thread(self) -> threading.Thread:
        """Run the bot in a background thread. Returns the thread."""
        t = threading.Thread(target=self.run, daemon=True, name="BotThread")
        t.start()
        return t

    def stop(self) -> None:
        """Signal the bot to stop after the current cycle completes."""
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Convenience ─────────────────────────────────────────────────────────

    def wait_random_millis(self, min_ms: int, max_ms: int) -> None:
        """Sleep for a random duration between min_ms and max_ms milliseconds."""
        _wait_random_millis(min_ms, max_ms)
