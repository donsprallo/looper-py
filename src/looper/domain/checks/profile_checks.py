"""The things one can expect of where the firmware spends its time.

A profile measured on the host does not say how long anything takes on
the target. What carries over is the ranking: the function that is
heaviest here is, in a build of the same code, very likely heaviest there.
So the check is about the order, never about nanoseconds.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import FIRMWARE_ORIGIN, Observation, Outcome

NOT_PROFILED = "the build is not woven for profiling"
NOTHING_MEASURED = "nothing of it was measured"


@dataclass(frozen=True)
class HeaviestFunctionIs(Check):
    """One function spent more time in itself than any other of its origin.

    Attributes:
        function: The function expected at the top.
        origin: The part of the simulation ranked, ``firmware`` unless a
            test is about the device model or a library; the device model's
            own step would otherwise often win.
    """

    function: str
    origin: str = FIRMWARE_ORIGIN

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare the heaviest measured function against the one expected."""
        subject = f"the {self.origin} profile"
        expected = f"{self.function} the heaviest"
        if not observed.profile.is_profiling:
            return Outcome(subject, expected, NOT_PROFILED, met=False)
        heaviest = observed.profile.heaviest(self.origin)
        if heaviest is None:
            return Outcome(subject, expected, NOTHING_MEASURED, met=False)
        seen = f"{heaviest.name} the heaviest, {heaviest.self_nanoseconds} ns in itself"
        return Outcome(subject, expected, seen, met=heaviest.name == self.function)
