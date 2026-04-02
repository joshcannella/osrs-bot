"""
Controller — central coordinator that wires all framework modules together.

Discovers RuneLite's HWND and PID, initializes capture, input, detection,
zones, and actions. Provides convenience facades to scripts.
"""

import logging
import os

import win32gui
import win32process

from framework.capture import ScreenCapture
from framework.colors import ColorRegistry
from framework.detection.color import ColorDetector
from framework.input.keyboard import RemoteKeyboard
from framework.input.mouse import RemoteMouse
from framework.zones.zone_manager import ZoneManager
from framework.actions.dropper import ItemDropper
from framework.actions.idler import Idler

logger = logging.getLogger(__name__)

_LAYOUT_WARNING = (
    "\n╔══════════════════════════════════════════════════════════════╗\n"
    "║  WARNING: Zone positions are hardcoded for Fixed-Classic    ║\n"
    "║           1920×1080 at 100%% display scaling.               ║\n"
    "║  Other resolutions/layouts will produce incorrect clicks.   ║\n"
    "╚══════════════════════════════════════════════════════════════╝"
)


def _get_runelite_pid(hwnd: int) -> int:
    """Return the PID of the process owning the given HWND."""
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


class DetectionFacade:
    """Convenience wrapper exposing detection methods to scripts."""

    def __init__(self, capture: ScreenCapture, color_detector: ColorDetector,
                 registry: ColorRegistry, debug: bool = False,
                 debug_dir: str = "debug"):
        self._capture = capture
        self._detector = color_detector
        self._registry = registry
        self._debug = debug
        self._debug_dir = debug_dir
        self._frame_count = 0

    def get_random_point_in_color(
        self,
        color_name: str,
        max_attempts: int = 15,
        image=None,
    ) -> tuple[int, int] | None:
        """
        Find a random point inside the closest contour matching color_name.

        If image is None, captures a fresh canvas screenshot.
        In debug mode, saves an annotated image to debug/<frame>.png.
        """
        if image is None:
            image = self._capture.capture_window()

        color = self._registry.get_by_name(color_name)
        if color is None:
            logger.error("Unknown color name: %r. Available: %s",
                         color_name, self._registry.names())
            return None

        debug_path = None
        if self._debug:
            self._frame_count += 1
            debug_path = os.path.join(
                self._debug_dir, f"frame_{self._frame_count:04d}_{color_name}.png"
            )

        return self._detector.get_random_point_in_color(
            image, color,
            max_attempts=max_attempts,
            debug=self._debug,
            debug_save_path=debug_path,
        )


class ActionsFacade:
    """Convenience wrapper exposing action utilities to scripts."""

    def __init__(self, controller: "Controller"):
        self.dropper = ItemDropper(controller)
        self.idler = Idler(controller)


class Controller:
    """
    Central coordinator for all bot modules.

    Usage:
        ctrl = Controller(debug=True)
        ctrl.init()
        # ... use ctrl.mouse, ctrl.keyboard, ctrl.detection, ctrl.zones, ctrl.actions
        ctrl.shutdown()
    """

    capture: ScreenCapture
    mouse: RemoteMouse
    keyboard: RemoteKeyboard
    zones: ZoneManager
    detection: DetectionFacade
    actions: ActionsFacade
    colors: ColorRegistry

    def __init__(self, debug: bool = False, debug_dir: str = "debug"):
        self._debug = debug
        self._debug_dir = debug_dir
        self._initialized = False

    def init(self) -> None:
        """
        Discover RuneLite HWND/PID and wire all modules.
        Prints layout warning on every startup.
        """
        if self._initialized:
            return

        logger.info("Initializing controller (debug=%s)", self._debug)
        logger.warning(_LAYOUT_WARNING)

        # Screen capture
        canvas_hwnd = ScreenCapture.find_runelite_canvas_hwnd()
        self.capture = ScreenCapture(canvas_hwnd)
        logger.info("Canvas HWND: %d  rect: %s", canvas_hwnd, self.capture.get_window_rect())

        # RuneLite PID (from the top-level RuneLite window)
        root_hwnd = win32gui.FindWindow(None, "RuneLite")
        pid = _get_runelite_pid(root_hwnd)
        logger.info("RuneLite PID: %d", pid)

        # Input
        self.mouse = RemoteMouse(pid, debug=self._debug)
        self.keyboard = RemoteKeyboard(pid, debug=self._debug)

        # Color registry
        self.colors = ColorRegistry()

        # Detection
        color_detector = ColorDetector()
        self.detection = DetectionFacade(
            self.capture, color_detector, self.colors,
            debug=self._debug, debug_dir=self._debug_dir,
        )

        # Zones
        self.zones = ZoneManager(self.capture)

        # Actions
        self.actions = ActionsFacade(self)

        # Optional: game state plugin (shared memory IPC)
        self.game_state = None
        try:
            from framework.game_state.client import GameStateClient
            client = GameStateClient()
            if client.is_available():
                self.game_state = client
                logger.info("RuneLite plugin detected via shared memory")
            else:
                logger.info(
                    "RuneLite plugin not detected — color detection only "
                    "(enable 'State Export' plugin for structured game state)"
                )
        except ImportError:
            pass

        self._initialized = True
        logger.info("Controller initialized")

    def shutdown(self) -> None:
        if not self._initialized:
            return
        try:
            self.mouse.destroy()
        except Exception:
            pass
        try:
            self.capture.close()
        except Exception:
            pass
        self._initialized = False
        logger.info("Controller shut down")
