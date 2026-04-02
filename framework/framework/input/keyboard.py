"""
RemoteKeyboard — injects Java AWT key events into the RuneLite JVM via KInputCtrl.dll.
"""

import time

from framework.input.mouse import _load_dll, _ts

# Java AWT KeyEvent IDs
KEY_TYPED   = 400
KEY_PRESSED = 401
KEY_RELEASED = 402

# Common virtual key codes (Java VK_ constants)
VK_SHIFT = 16
VK_CTRL  = 17
VK_ALT   = 18
VK_ENTER = 10
VK_ESCAPE = 27
VK_SPACE = 32
VK_F1    = 112
VK_F2    = 113
VK_F3    = 114
VK_F4    = 115
VK_F5    = 116
VK_F6    = 117
VK_F7    = 118
VK_F8    = 119
VK_F9    = 120
VK_F10   = 121
VK_F11   = 122
VK_F12   = 123

# Arrow keys (used for camera rotation)
VK_LEFT  = 37
VK_UP    = 38
VK_RIGHT = 39
VK_DOWN  = 40

_MODIFIER_VK = {
    "shift": VK_SHIFT,
    "ctrl":  VK_CTRL,
    "alt":   VK_ALT,
    "enter": VK_ENTER,
    "esc":   VK_ESCAPE,
    "space": VK_SPACE,
    "left":  VK_LEFT,
    "up":    VK_UP,
    "right": VK_RIGHT,
    "down":  VK_DOWN,
}


class RemoteKeyboard:
    """
    Injects keyboard events into a RuneLite process via KInputCtrl.dll.
    """

    def __init__(self, pid: int, debug: bool = False):
        self._pid = pid
        self._debug = debug

    def send_key_char(self, char: str) -> None:
        """Type a single printable character (KEY_TYPED event)."""
        if self._debug:
            return
        _load_dll().KInput_KeyEvent(
            self._pid, KEY_TYPED, _ts(), 0, 0, ord(char[0]), 0
        )

    def send_modifier_key(self, action: str, key: str) -> None:
        """
        Press or release a modifier key.

        action: "press" or "release"
        key: "shift", "ctrl", "alt", "enter", "esc", "space", or an integer VK code
        """
        if self._debug:
            return
        if isinstance(key, str):
            vk = _MODIFIER_VK.get(key.lower(), 0)
        else:
            vk = int(key)

        event_id = KEY_PRESSED if action.lower() == "press" else KEY_RELEASED
        _load_dll().KInput_KeyEvent(self._pid, event_id, _ts(), 0, vk, 0, 0)

    def hold_key(self, key: str | int, duration_ms: int) -> None:
        """Press a key, hold for duration_ms, then release.

        Useful for camera rotation via arrow keys.
        """
        self.send_modifier_key("press", key)
        time.sleep(duration_ms / 1000.0)
        self.send_modifier_key("release", key)

    def send_string(self, text: str, delay_ms: int = 50) -> None:
        """Type a string of characters with a small delay between each."""
        for ch in text:
            self.send_key_char(ch)
            time.sleep(delay_ms / 1000.0)
