"""
RemoteMouse — injects Java AWT mouse events into the RuneLite JVM via KInputCtrl.dll.

All coordinates are canvas-relative (0,0 = top-left of the RuneLite game viewport),
matching the coordinate space of mss captures. From Kinput.java Javadoc:
  "This operates in client relative co-ordinates, not screen relative co-ordinates."
"""

import ctypes
import os
import random
import time

# Mouse event IDs (Java AWT MouseEvent)
MOUSE_PRESS   = 501
MOUSE_RELEASE = 502
MOUSE_MOVE    = 503
MOUSE_ENTER   = 504

# Mouse button codes (Java AWT: left=1, middle=2, right=3, none=0)
BTN_NONE   = 0
BTN_LEFT   = 1
BTN_MIDDLE = 2
BTN_RIGHT  = 3

# Focus event IDs
FOCUS_GAINED = 1004

_dll = None


def _load_dll():
    global _dll
    if _dll is not None:
        return _dll

    dll_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../ChromaScape/build/dist/KInputCtrl.dll")
    )
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"KInputCtrl.dll not found at: {dll_path}")

    _dll = ctypes.CDLL(dll_path)

    # KInput_Create(pid: int) -> bool
    _dll.KInput_Create.restype = ctypes.c_bool
    _dll.KInput_Create.argtypes = [ctypes.c_int]

    # KInput_Delete(pid: int) -> bool
    _dll.KInput_Delete.restype = ctypes.c_bool
    _dll.KInput_Delete.argtypes = [ctypes.c_int]

    # KInput_FocusEvent(pid: int, eventID: int) -> bool
    _dll.KInput_FocusEvent.restype = ctypes.c_bool
    _dll.KInput_FocusEvent.argtypes = [ctypes.c_int, ctypes.c_int]

    # KInput_MouseEvent(pid, eventID, when, modifiers, x, y, clickCount, popupTrigger, button) -> bool
    _dll.KInput_MouseEvent.restype = ctypes.c_bool
    _dll.KInput_MouseEvent.argtypes = [
        ctypes.c_int,       # pid
        ctypes.c_int,       # eventID
        ctypes.c_longlong,  # when (timestamp ms)
        ctypes.c_int,       # modifiers
        ctypes.c_int,       # x
        ctypes.c_int,       # y
        ctypes.c_int,       # clickCount
        ctypes.c_bool,      # popupTrigger
        ctypes.c_int,       # button
    ]

    # KInput_KeyEvent(pid, eventID, when, modifiers, keyCode, keyChar, keyLocation) -> bool
    _dll.KInput_KeyEvent.restype = ctypes.c_bool
    _dll.KInput_KeyEvent.argtypes = [
        ctypes.c_int,       # pid
        ctypes.c_int,       # eventID
        ctypes.c_longlong,  # when
        ctypes.c_int,       # modifiers
        ctypes.c_int,       # keyCode
        ctypes.c_short,     # keyChar
        ctypes.c_int,       # keyLocation
    ]

    return _dll


def _ts() -> int:
    return int(time.time() * 1000)


class RemoteMouse:
    """
    Injects mouse events into a RuneLite process via KInputCtrl.dll.

    Coordinates are canvas-relative (0,0 = top-left of the game viewport).
    In debug mode, left_click() and right_click() are no-ops.
    """

    def __init__(self, pid: int, debug: bool = False):
        self._pid = pid
        self._debug = debug
        self._pos: tuple[int, int] = (0, 0)
        if not debug:
            dll = _load_dll()
            if not dll.KInput_Create(pid):
                raise RuntimeError(f"KInput_Create failed for PID {pid}")

    def _focus(self):
        _load_dll().KInput_FocusEvent(self._pid, FOCUS_GAINED)

    def move_to(self, x: int, y: int) -> None:
        """Move cursor to canvas-relative (x, y)."""
        if not self._debug:
            dll = _load_dll()
            self._focus()
            dll.KInput_MouseEvent(self._pid, MOUSE_ENTER, _ts(), 0, x, y, 0, False, BTN_NONE)
            dll.KInput_MouseEvent(self._pid, MOUSE_MOVE,  _ts(), 0, x, y, 0, False, BTN_NONE)
        self._pos = (x, y)

    def left_click(self, hold_ms: int | None = None) -> None:
        """Left-click at the current cursor position.

        hold_ms: override press-release duration in milliseconds.
                 If None, uses uniform 40-90ms (original behavior).
        """
        if self._debug:
            return
        x, y = self._pos
        dll = _load_dll()
        self._focus()
        dll.KInput_MouseEvent(self._pid, MOUSE_PRESS,   _ts(), 1, x, y, 1, False, BTN_LEFT)
        if hold_ms is not None:
            time.sleep(hold_ms / 1000.0)
        else:
            time.sleep(random.uniform(0.04, 0.09))
        dll.KInput_MouseEvent(self._pid, MOUSE_RELEASE, _ts(), 1, x, y, 1, False, BTN_LEFT)

    def right_click(self, hold_ms: int | None = None) -> None:
        """Right-click at the current cursor position.

        hold_ms: override press-release duration in milliseconds.
                 If None, uses uniform 40-90ms (original behavior).
        """
        if self._debug:
            return
        x, y = self._pos
        dll = _load_dll()
        self._focus()
        dll.KInput_MouseEvent(self._pid, MOUSE_PRESS,   _ts(), 1, x, y, 1, False, BTN_RIGHT)
        if hold_ms is not None:
            time.sleep(hold_ms / 1000.0)
        else:
            time.sleep(random.uniform(0.04, 0.09))
        dll.KInput_MouseEvent(self._pid, MOUSE_RELEASE, _ts(), 1, x, y, 1, False, BTN_RIGHT)

    def move_to_wind(self, x: int, y: int, speed: str = "medium") -> None:
        """Move using WindMouse humanization."""
        from framework.humanize import WindMouse
        WindMouse().move(self._pos, (x, y), speed, callback=lambda p: self.move_to(*p))

    def get_position(self) -> tuple[int, int]:
        """Return the current cursor position."""
        return self._pos

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    def destroy(self):
        if not self._debug:
            _load_dll().KInput_Delete(self._pid)
