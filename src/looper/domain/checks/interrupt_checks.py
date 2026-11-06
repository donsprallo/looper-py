"""The things one can expect of a firmware's interrupts (Pro).

Most are counted on the window's interrupt events, which are facts the
runtime records: how late each ISR started, what was lost, how long the
lock was held. What the server judges against looper.toml -- the lock's
limit there -- and every other finding come from its run findings, so
that no judgement the server makes is made again here.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome
from looper.domain.model.interrupt_facts import InterruptMark

#: What a check of a source says when the firmware has no source of that name.
NO_SUCH_SOURCE = "no such interrupt source"


def _source_id(observed: Observation, name: str) -> int | None:
    found = [one for one in observed.interrupts.sources if one.name == name]
    return found[0].source_id if found else None


def _marks(observed: Observation, source_id: int, kind: str) -> list[InterruptMark]:
    return [
        mark
        for mark in observed.interrupt_marks
        if mark.source_id == source_id and mark.kind == kind and not mark.by_race
    ]


@dataclass(frozen=True)
class LatencyBelow(Check):
    """Every ISR of a source started less than a limit after its source fell due."""

    source: str
    limit_us: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Find the longest latency of the window."""
        expected = f"latency below {self.limit_us} us"
        source_id = _source_id(observed, self.source)
        if source_id is None:
            return Outcome(self.source, expected, NO_SUCH_SOURCE, met=False)
        latencies = [mark.latency_us for mark in _marks(observed, source_id, "entered")]
        longest = max(latencies, default=0)
        seen = f"at most {longest} us over {len(latencies)} ISRs"
        return Outcome(self.source, expected, seen, met=longest < self.limit_us)


@dataclass(frozen=True)
class NeverLost(Check):
    """No interrupt of a source was lost in the window."""

    source: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Count the losses."""
        source_id = _source_id(observed, self.source)
        if source_id is None:
            return Outcome(self.source, "none lost", NO_SUCH_SOURCE, met=False)
        lost = len(_marks(observed, source_id, "lost"))
        return Outcome(self.source, "none lost", f"{lost} lost", met=lost == 0)


@dataclass(frozen=True)
class HandledAtLeast(Check):
    """A source's ISR ran at least so often in the window."""

    source: str
    times: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Count the ISRs that began."""
        expected = f"handled at least {self.times} times"
        source_id = _source_id(observed, self.source)
        if source_id is None:
            return Outcome(self.source, expected, NO_SUCH_SOURCE, met=False)
        handled = len(_marks(observed, source_id, "entered"))
        return Outcome(self.source, expected, f"{handled} times", met=handled >= self.times)


@dataclass(frozen=True)
class ShorterThanPeriod(Check):
    """A timer's ISR always ended within its period: the server found nothing else."""

    source: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for the server's finding about this source."""
        too_long = [
            one
            for one in observed.run_findings
            if one.kind == "IRQ_LONGER_THAN_PERIOD" and one.title.startswith(f"{self.source}'s")
        ]
        seen = too_long[0].title if too_long else "always within it"
        return Outcome(self.source, "ISR shorter than its period", seen, met=not too_long)


@dataclass(frozen=True)
class LockedAtMost(Check):
    """Interrupts were never masked longer than a limit; without one, than looper.toml's."""

    limit_us: int = 0

    def evaluate(self, observed: Observation) -> Outcome:
        """Find the longest lock of the window, or the server's finding about it."""
        if self.limit_us == 0:
            return _against_the_project(observed)
        locks = [mark.duration_us for mark in observed.interrupt_marks if mark.kind == "locked"]
        longest = max(locks, default=0)
        expected = f"masked at most {self.limit_us} us"
        return Outcome("the interrupts", expected, f"{longest} us", met=longest <= self.limit_us)


def _against_the_project(observed: Observation) -> Outcome:
    too_long = [one for one in observed.run_findings if one.kind == "IRQ_LOCK_TOO_LONG"]
    seen = too_long[0].title if too_long else "within the limit"
    expected = "masked no longer than [interrupts] max_disabled"
    return Outcome("the interrupts", expected, seen, met=not too_long)


@dataclass(frozen=True)
class NoRunFindings(Check):
    """The server found nothing in the run, of the kinds given or of any."""

    kinds: tuple[str, ...] = ()

    def evaluate(self, observed: Observation) -> Outcome:
        """List what the server found."""
        found = [one for one in observed.run_findings if not self.kinds or one.kind in self.kinds]
        seen = "; ".join(one.title for one in found)
        return Outcome("the run", "no findings", seen or "none", met=not found)
