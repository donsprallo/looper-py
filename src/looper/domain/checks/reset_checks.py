"""The things one can expect of a firmware's resets and of its flash.

A reset in a test window is either the point of the test -- the watchdog
caught the hang -- or the bug. So a test says which: that it happened, of
which cause and how often, or that the firmware did not reset in a loop.
The flash is expected to be written by its rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome


def _times(count: int) -> str:
    return "once" if count == 1 else f"{count} times"


@dataclass(frozen=True)
class ResetHappened(Check):
    """The firmware was reset, of a cause if one is given, as often as given.

    Attributes:
        cause: ``watchdog``, ``software``, ``pin``, ...; empty for any.
        times: How often exactly; 0 for at least once.
    """

    cause: str = ""
    times: int = 0

    def evaluate(self, observed: Observation) -> Outcome:
        """Count the resets of the window."""
        resets = [one for one in observed.resets if not self.cause or one.cause == self.cause]
        subject = f"{self.cause} reset" if self.cause else "a reset"
        expected = _times(self.times) if self.times else "at least once"
        seen = ", ".join(f"{one.cause} at {one.sim_us / 1e6:.6f} s" for one in observed.resets)
        met = len(resets) == self.times if self.times else bool(resets)
        return Outcome(subject, expected, seen or "no reset", met=met)


@dataclass(frozen=True)
class NoResetLoop(Check):
    """The firmware did not reset in a loop: the server found none."""

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for the server's finding."""
        seen = observed.loop_finding or f"{len(observed.resets)} resets, no loop"
        return Outcome("the resets", "no reset loop", seen, met=not observed.loop_finding)


@dataclass(frozen=True)
class NoFlashViolation(Check):
    """Every flash write kept the flash's rules: no bit went from 0 to 1 without an erase."""

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for a violation among the window's flash operations."""
        broken = [one for one in observed.flash_marks if one.kind == "violation"]
        seen = ", ".join(f"at 0x{one.offset:x} ({one.partition or 'outside'})" for one in broken)
        return Outcome("the flash", "no write against its rules", seen or "none", met=not broken)
