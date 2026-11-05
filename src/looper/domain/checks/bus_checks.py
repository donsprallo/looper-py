"""What one can expect of a bus."""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Exchange, Observation, Outcome


@dataclass(frozen=True)
class BusNothingRefused(Check):
    """Everything that crossed a bus was taken by something."""

    bus_id: int
    name: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Count what crossed the bus and what nothing took."""
        on_bus = observed.exchanges_on(self.bus_id)
        refused = [one for one in on_bus if one.was_refused]
        addresses = ", ".join(sorted({one.display_address for one in refused}))
        seen = f"{len(refused)} of {len(on_bus)} refused" + (f" at {addresses}" if refused else "")
        return Outcome(self.name, "nothing refused", seen, met=not refused)


@dataclass(frozen=True)
class BusCarriedAtLeast(Check):
    """A bus carried at least so many exchanges."""

    bus_id: int
    name: str
    count: int

    def evaluate(self, observed: Observation) -> Outcome:
        """Count what crossed the bus.

        What the recording lost is mentioned and not added: it may have been
        samples, and a lost sample must not make a bus check pass.
        """
        on_bus = observed.exchanges_on(self.bus_id)
        seen = f"{len(on_bus)}" + observed.exchange_loss_note
        return Outcome(
            self.name,
            f"at least {self.count} exchanges",
            seen,
            met=len(on_bus) >= self.count,
        )


@dataclass(frozen=True)
class MessageFilter:
    """Which exchanges on a bus a message expectation is about.

    Attributes:
        address: The CAN identifier, I2C address or chip select to match;
            ``None`` matches any.
        direction: ``outbound`` for what the firmware sent, ``inbound``
            for what reached it; ``None`` matches both.
        starts_with: Bytes the payload has to begin with.
    """

    address: int | None = None
    direction: str | None = None
    starts_with: bytes = b""

    def matches(self, exchange: Exchange) -> bool:
        """Whether one exchange is one of the messages meant."""
        if self.address is not None and exchange.address != self.address:
            return False
        if self.direction is not None and exchange.direction != self.direction:
            return False
        return exchange.payload.startswith(self.starts_with)

    def describe(self, name: str) -> str:
        """The subject of the outcome, as a reader would say it."""
        parts = [name]
        if self.address is not None:
            parts.append(f"id=0x{self.address:x}")
        if self.direction is not None:
            parts.append(self.direction)
        if self.starts_with:
            parts.append(f"starting {self.starts_with.hex(' ')}")
        return " ".join(parts)


def _messages(observed: Observation, bus_id: int, wanted: MessageFilter) -> list[Exchange]:
    return [one for one in observed.exchanges_on(bus_id) if wanted.matches(one)]


@dataclass(frozen=True)
class MessageCount(Check):
    """A bus carried between so many messages of one kind."""

    bus_id: int
    name: str
    wanted: MessageFilter
    at_least: int
    at_most: int | None = None

    def evaluate(self, observed: Observation) -> Outcome:
        """Count the messages the filter lets through."""
        count = len(_messages(observed, self.bus_id, self.wanted))
        if self.at_most is None:
            expected = f"at least {self.at_least} messages"
        elif self.at_most == 0:
            expected = "no message"
        else:
            expected = f"{self.at_least} to {self.at_most} messages"
        met = count >= self.at_least and (self.at_most is None or count <= self.at_most)
        seen = f"{count}" + observed.exchange_loss_note
        return Outcome(self.wanted.describe(self.name), expected, seen, met=met)


@dataclass(frozen=True)
class MessageRate(Check):
    """Messages of one kind crossed a bus at about a given rate."""

    bus_id: int
    name: str
    wanted: MessageFilter
    hertz: float
    tolerance: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Work the rate out of the messages and the time that passed."""
        subject = self.wanted.describe(self.name)
        expected = f"{self.hertz:g} Hz +/- {self.tolerance:.0%}"
        if observed.elapsed_seconds <= 0.0:
            return Outcome(subject, expected, "no time passed", met=False)
        measured = len(_messages(observed, self.bus_id, self.wanted)) / observed.elapsed_seconds
        met = abs(measured - self.hertz) <= self.hertz * self.tolerance
        return Outcome(
            subject, expected, f"{measured:.4g} Hz" + observed.exchange_loss_note, met=met
        )
