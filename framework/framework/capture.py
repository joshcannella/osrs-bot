import numpy as np
import win32gui
import mss


def _find_runelite_canvas_hwnd() -> int:
    """
    Find the second SunAwtCanvas child window of the RuneLite main window.
    The first SunAwtCanvas is typically the toolbar/chrome; the second is the game viewport.
    Returns the HWND of the game canvas, or 0 if not found.
    """
    root_hwnd = win32gui.FindWindow(None, "RuneLite")
    if not root_hwnd:
        raise RuntimeError("RuneLite window not found. Is RuneLite running?")

    canvas_hwnds: list[int] = []

    def _enum_child(hwnd, _):
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "SunAwtCanvas":
            canvas_hwnds.append(hwnd)

    win32gui.EnumChildWindows(root_hwnd, _enum_child, None)

    if len(canvas_hwnds) < 2:
        raise RuntimeError(
            f"Expected at least 2 SunAwtCanvas windows, found {len(canvas_hwnds)}. "
            "Ensure RuneLite is fully loaded."
        )

    # Second SunAwtCanvas is the game viewport
    return canvas_hwnds[1]


class ScreenCapture:
    """
    Captures screenshots of the RuneLite game canvas.

    Coordinates returned/expected by this class are canvas-relative (origin at top-left
    of the game viewport), matching the coordinate space expected by KInput.
    """

    @staticmethod
    def find_runelite_canvas_hwnd() -> int:
        return _find_runelite_canvas_hwnd()

    def __init__(self, hwnd: int):
        self._hwnd = hwnd
        self._sct = mss.mss()

    def get_window_rect(self) -> tuple[int, int, int, int]:
        """Returns (x, y, width, height) in screen coordinates."""
        left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
        return left, top, right - left, bottom - top

    def capture_window(self) -> np.ndarray:
        """Capture the full game canvas. Returns a BGR numpy array."""
        x, y, w, h = self.get_window_rect()
        monitor = {"left": x, "top": y, "width": w, "height": h}
        sct_img = self._sct.grab(monitor)
        # mss returns BGRA; convert to BGR
        bgr = np.array(sct_img)[:, :, :3]
        return bgr

    def capture_zone(self, rect: tuple[int, int, int, int]) -> np.ndarray:
        """
        Capture a canvas-relative sub-region.
        rect = (canvas_x, canvas_y, width, height)
        """
        canvas_x, canvas_y, w, h = rect
        win_x, win_y, _, _ = self.get_window_rect()
        monitor = {
            "left": win_x + canvas_x,
            "top": win_y + canvas_y,
            "width": w,
            "height": h,
        }
        sct_img = self._sct.grab(monitor)
        return np.array(sct_img)[:, :, :3]

    def close(self):
        self._sct.close()
