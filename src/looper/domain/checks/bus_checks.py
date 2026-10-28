"""What one can expect of a bus."""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome


@dataclass(frozen=True)
class BusNothingRefused(Check):
    """Everything that crossed a bus was taken by something."""

    bus_id: int
    name: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Count what crossed the bus and what nothing took."""
        on_bus = observed.exchanges_on(self.bus_id)
        refused = [one for one in on_bus if one.was_refused]
        addresses = ", ".join(sorted({one.address for one in refused}))
        seen = f"{len(refused)} of {len(on_bus)} refused" + (f" at {addresses}" if refused else "")
        return Outcome(self.name, "nothing refused", seen, met=not refused)


@dataclass(frozen=True)
class BusCarriedAtLeast(Check):
    """A bus carried at least so many exchanges."""

    bus_id: int
    name: str
    count: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Count what crossed the bus, including what the recording lost."""
        on_bus = observed.exchanges_on(self.bus_id)
        seen = f"{len(on_bus)}" + observed.exchange_loss_note
        return Outcome(
            self.name,
            f"at least {self.count} exchanges",
            seen,
            met=len(on_bus) + observed.lost_exchanges >= self.count,
        )
