"""What the stream says of interrupts in a window, and what the server judged of the run (Pro)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InterruptMark:
    """One interrupt event of the window.

    Attributes:
        sim_us: When; a lock section's end.
        source_id: The source; 0 for the global lock.
        kind: pending, entered, left, lost, locked or storm.
        latency_us: An entry's latency.
        duration_us: An ISR's or a lock section's duration.
        by_race: Raised by the race mode (Pro).
    """

    sim_us: int
    source_id: int
    kind: str
    latency_us: int = 0
    duration_us: int = 0
    by_race: bool = False


@dataclass(frozen=True)
class RunFindingReading:
    """One finding of the run, in the server's words (Pro).

    Attributes:
        kind: IRQ_LOCK_TOO_LONG, IRQ_LOST, ...
        title: The line a person reads.
        severity: noticeable or critical.
        occurrences: How often it happened.
        check_text: The check that expects it away.
    """

    kind: str
    title: str
    severity: str = "critical"
    occurrences: int = 1
    check_text: str = ""
