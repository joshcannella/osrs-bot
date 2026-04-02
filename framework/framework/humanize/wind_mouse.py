"""
WindMouse algorithm port — direct translation of ChromaScape WindMouse.java.

Original algorithm by BenLand100. "WindMouse2" implementation by holic.
Adapted for Python by StaticSweep.

Moved from framework/humanize.py into the humanize package.
"""

import math
import random
import time
from collections.abc import Callable


# Speed profiles: (mouseSpeed, mouseGravity, mouseWind)
_PROFILES = {
    "slow":   (20, 5.0, 1.0),
    "medium": (30, 4.5, 1.5),
    "fast":   (50, 6.0, 2.0),
}


class WindMouse:
    """
    Physics-based human-like mouse movement.

    Usage:
        wm = WindMouse()
        wm.move((x0, y0), (x1, y1), "medium", callback=lambda p: mouse.move_to(*p))
    """

    def move(
        self,
        start: tuple[int, int],
        target: tuple[int, int],
        speed_profile: str = "medium",
        callback: Callable[[tuple[int, int]], None] | None = None,
    ) -> None:
        profile = speed_profile.lower()
        speed, gravity, wind = _PROFILES.get(profile, _PROFILES["medium"])
        self._wind_mouse2(start, target, gravity, wind, speed, callback)

    def _wind_mouse2(self, start, target, gravity, wind, speed, callback):
        dist = math.hypot(target[0] - start[0], target[1] - start[1])
        intermediate = None
        if dist > 250 and random.randint(0, 1) == 1:
            intermediate = self._random_point(target, start)

        if intermediate is not None:
            self._wind_mouse_impl(
                start[0], start[1],
                intermediate[0], intermediate[1],
                gravity, wind, speed,
                random.randint(10, 25),
                callback,
            )
            time.sleep(random.randint(1, 150) / 1000.0)
            start = intermediate

        self._wind_mouse_impl(
            start[0], start[1],
            target[0], target[1],
            gravity, wind, speed,
            random.randint(10, 25),
            callback,
        )

    def _wind_mouse_impl(self, xs, ys, xe, ye, gravity, wind, speed, target_area, callback):
        sqrt2 = math.sqrt(2)
        sqrt3 = math.sqrt(3)
        sqrt5 = math.sqrt(5)

        t_dist = int(math.hypot(xe - xs, ye - ys))
        deadline = time.time() + 10.0  # 10-second timeout

        velo_x = velo_y = wind_x = wind_y = 0.0

        while True:
            dist = math.hypot(xs - xe, ys - ye)
            if dist < 3:
                break
            if time.time() > deadline:
                break

            wind_capped = min(wind, dist)

            d = round(round(t_dist * 0.3) / 7)
            d = max(5, min(20, d))

            if random.randint(0, 5) == 0:
                d = 2

            max_step = min(d, round(dist)) * 1.5

            if dist >= target_area:
                wind_range = int(round(wind_capped) * 2) + 1
                wind_x = (wind_x / sqrt3) + ((random.randrange(wind_range) - wind_capped) / sqrt5)
                wind_y = (wind_y / sqrt3) + ((random.randrange(wind_range) - wind_capped) / sqrt5)
            else:
                wind_x /= sqrt2
                wind_y /= sqrt2
                velo_x *= 0.64
                velo_y *= 0.64

            velo_x += wind_x + gravity * (xe - xs) / dist
            velo_y += wind_y + gravity * (ye - ys) / dist

            velo_mag = math.hypot(velo_x, velo_y)
            if velo_mag > max_step:
                max_step = max(2.0, max_step / 2)
                random_dist = max_step / 2 + random.randint(0, int(round(max_step) // 2) or 1)
                velo_x = (velo_x / velo_mag) * random_dist
                velo_y = (velo_y / velo_mag) * random_dist

            last_x = round(xs)
            last_y = round(ys)
            xs += velo_x
            ys += velo_y

            new_x = round(xs)
            new_y = round(ys)
            if (last_x != new_x or last_y != new_y) and callback is not None:
                callback((int(new_x), int(new_y)))

            # Sleep ~10-20ms targeting 60Hz
            w = random.randint(0, int(round(100.0 / speed))) * 12
            w = max(10, w)
            w = int(round(w * 0.9))
            time.sleep(w / 1000.0)

        # Bridge final <3 pixels
        final_x, final_y = round(xe), round(ye)
        if (round(xs) != final_x or round(ys) != final_y) and callback is not None:
            callback((int(final_x), int(final_y)))

    @staticmethod
    def _random_point(p1: tuple, p2: tuple) -> tuple[int, int]:
        def rand_between(a, b):
            if a == b:
                return float(a)
            return a + random.random() * (b - a)

        rx = int(rand_between(p1[0], p2[0]))
        ry = int(rand_between(p1[1], p2[1]))
        return rx, ry
