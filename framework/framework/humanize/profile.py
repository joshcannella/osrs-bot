"""
HumanProfile — central configuration for the anti-detection humanization layer.

Captures one "player personality" so all subsystems produce coherent behavior.
All humanization is opt-in: pass a HumanProfile to BaseBot to enable it.
"""

from dataclasses import dataclass, field
import random


@dataclass
class HumanProfile:
    """Encapsulates a single human player's behavioral fingerprint."""

    name: str = "default"

    # ── Timing ──────────────────────────────────────────────────────────
    # Log-normal parameters for reaction time (median ~450ms with defaults)
    reaction_mu: float = 6.1
    reaction_sigma: float = 0.35
    # Gamma distribution for repetitive actions (typing, dropping)
    repetitive_shape: float = 4.0
    repetitive_scale: float = 15.0  # ms

    # ── Fatigue ─────────────────────────────────────────────────────────
    fatigue_rate: float = 1.0           # >1 = fatigues faster, <1 = slower
    fatigue_max: float = 0.4            # max degradation (0.4 = 40% slower at peak)
    fatigue_ramp_minutes: float = 120.0 # minutes to reach ~63% of max fatigue

    # ── Breaks ──────────────────────────────────────────────────────────
    micro_break_interval: tuple[float, float] = (180, 480)      # 3-8 min
    micro_break_duration: tuple[float, float] = (5, 30)          # 5-30s
    short_break_interval: tuple[float, float] = (1200, 3600)     # 20-60 min
    short_break_duration: tuple[float, float] = (120, 600)       # 2-10 min
    long_break_interval: tuple[float, float] = (7200, 14400)     # 2-4 hours
    long_break_duration: tuple[float, float] = (900, 3600)       # 15-60 min
    daily_session_limit: float = 6.0  # hours (0 = unlimited)

    # ── Camera ──────────────────────────────────────────────────────────
    camera_interval: tuple[float, float] = (30, 120)  # seconds between rotations
    camera_searching_multiplier: float = 0.4  # shorter interval when searching

    # ── Clicks ──────────────────────────────────────────────────────────
    click_hold_base: tuple[float, float] = (40, 90)    # ms press-release (skilling)
    click_hold_panic: tuple[float, float] = (20, 50)   # ms (combat/panic)
    misclick_probability: float = 0.02   # 2% chance per click
    double_click_probability: float = 0.01  # 1% chance

    # ── Idle behaviors ──────────────────────────────────────────────────
    idle_fidget_probability: float = 0.3
    idle_afk_probability: float = 0.15

    # ── Drop patterns ───────────────────────────────────────────────────
    zigzag_probability: float = 0.6
    column_probability: float = 0.25
    random_order_probability: float = 0.15
    drop_pause_probability: float = 0.1  # pause mid-drop

    # ── Tick discipline ─────────────────────────────────────────────────
    min_reaction_ticks: int = 1  # wait at least 1 game tick (600ms) before reacting

    @classmethod
    def random_variant(cls, base: "HumanProfile | None" = None) -> "HumanProfile":
        """Generate a slightly randomized variant of a base profile.

        Jitters all numeric fields by +/- 15% to create unique player fingerprints.
        """
        source = base or cls()
        jitter = 0.15

        def jit(val):
            if isinstance(val, float):
                return val * random.uniform(1 - jitter, 1 + jitter)
            if isinstance(val, int):
                return max(1, round(val * random.uniform(1 - jitter, 1 + jitter)))
            if isinstance(val, tuple) and len(val) == 2:
                return (
                    val[0] * random.uniform(1 - jitter, 1 + jitter),
                    val[1] * random.uniform(1 - jitter, 1 + jitter),
                )
            return val

        return cls(
            name=f"variant_{random.randint(1000, 9999)}",
            reaction_mu=jit(source.reaction_mu),
            reaction_sigma=jit(source.reaction_sigma),
            repetitive_shape=jit(source.repetitive_shape),
            repetitive_scale=jit(source.repetitive_scale),
            fatigue_rate=jit(source.fatigue_rate),
            fatigue_max=jit(source.fatigue_max),
            fatigue_ramp_minutes=jit(source.fatigue_ramp_minutes),
            micro_break_interval=jit(source.micro_break_interval),
            micro_break_duration=jit(source.micro_break_duration),
            short_break_interval=jit(source.short_break_interval),
            short_break_duration=jit(source.short_break_duration),
            long_break_interval=jit(source.long_break_interval),
            long_break_duration=jit(source.long_break_duration),
            daily_session_limit=jit(source.daily_session_limit),
            camera_interval=jit(source.camera_interval),
            camera_searching_multiplier=jit(source.camera_searching_multiplier),
            click_hold_base=jit(source.click_hold_base),
            click_hold_panic=jit(source.click_hold_panic),
            misclick_probability=max(0, min(0.1, jit(source.misclick_probability))),
            double_click_probability=max(0, min(0.05, jit(source.double_click_probability))),
            idle_fidget_probability=jit(source.idle_fidget_probability),
            idle_afk_probability=jit(source.idle_afk_probability),
            zigzag_probability=source.zigzag_probability,
            column_probability=source.column_probability,
            random_order_probability=source.random_order_probability,
            drop_pause_probability=jit(source.drop_pause_probability),
            min_reaction_ticks=source.min_reaction_ticks,
        )
