"""The firmware's interrupt sources and the lock, as the server reports them (free).

Times are simulated microseconds; every text is the server's.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class InterruptSource:
    """One interrupt source and what it did in this life.

    Attributes:
        source_id: Its number, which a raise names.
        name: Its name in contract.toml, ``EXTI0``.
        kind_text: What makes it due, ``timer, every 1 ms``.
        handler: The firmware's function that handles it; empty without one.
        is_raisable: Whether a test may raise it.
        state_text: ``idle``, ``pending``, ``running`` or ``disabled``.
    """

    source_id: int
    name: str
    kind_text: str = ""
    handler: str = ""
    priority: int = 0
    enabled: bool = False
    pending: bool = False
    raised: int = 0
    handled: int = 0
    lost: int = 0
    latency_max_us: int = 0
    latency_mean_us: int = 0
    duration_max_us: int = 0
    duration_mean_us: int = 0
    period_us: int = 0
    is_raisable: bool = False
    state_text: str = ""


@dataclass(frozen=True)
class InterruptLock:
    """The global lock in this life.

    Attributes:
        disabled_now: Whether interrupts are masked now.
        sections: How often it was taken and given back.
        longest_us: Its longest section.
        total_us: Every section together.
    """

    disabled_now: bool = False
    sections: int = 0
    longest_us: int = 0
    total_us: int = 0


@dataclass(frozen=True)
class Interrupts:
    """Every source, the lock, and what the numbers mean.

    Attributes:
        installed: Whether the firmware called an interrupt role yet, so
            that the counts are live.
        note: The server's word on the time model, or why nothing is there.
    """

    sources: tuple[InterruptSource, ...] = field(default_factory=tuple)
    lock: InterruptLock = field(default_factory=InterruptLock)
    installed: bool = False
    note: str = ""

    def source(self, name: str) -> InterruptSource:
        """The source of a name.

        Raises:
            KeyError: If there is none.
        """
        for source in self.sources:
            if source.name == name:
                return source
        raise KeyError(f"there is no interrupt source called {name}")
