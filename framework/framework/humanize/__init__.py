"""
humanize — anti-detection humanization layer.

Re-exports WindMouse and wait_random_millis for backward compatibility.
When a TimingEngine is registered (via BaseBot with a HumanProfile),
wait_random_millis uses human-like log-normal distributions instead of
uniform random.
"""

import random
import threading
import time

from framework.humanize.wind_mouse import WindMouse

__all__ = ["WindMouse", "wait_random_millis", "set_timing_engine", "get_timing_engine"]

# Thread-local storage for the timing engine
_local = threading.local()


def set_timing_engine(engine) -> None:
    """Register a TimingEngine for the current thread.

    Called by BaseBot._init_humanization(). After this,
    wait_random_millis() uses the engine's distributions.
    """
    _local.timing_engine = engine


def get_timing_engine():
    """Get the current thread's TimingEngine, or None."""
    return getattr(_local, "timing_engine", None)


def wait_random_millis(min_ms: int, max_ms: int) -> None:
    """Sleep for a random duration between min_ms and max_ms milliseconds.

    If a TimingEngine is registered (humanization enabled), uses log-normal
    distribution with fatigue scaling. Otherwise falls back to uniform random.
    """
    engine = get_timing_engine()
    if engine is not None:
        engine.wait_random_millis(min_ms, max_ms)
    else:
        time.sleep(random.randint(min_ms, max_ms) / 1000.0)
