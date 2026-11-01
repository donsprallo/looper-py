"""What one can expect of an analog channel."""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import NOTHING_RECORDED, Check
from looper.domain.model import Observation, Outcome

MICROSECONDS_PER_SECOND = 1_000_000


@dataclass(frozen=True)
class ChannelStaysBetween(Check):
    """A channel never leaves a range."""

    channel_id: int
    name: str
    low: float
    high: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Compare every recorded sample of the channel against the range."""
        values = [sample.value for sample in observed.samples_of(self.channel_id)]
        expected = f"every sample within {self.low:g} .. {self.high:g}"
        if not values:
            return Outcome(self.name, expected, NOTHING_RECORDED, met=False)
        seen = (
            f"{min(values):g} .. {max(values):g} over {len(values)} samples"
            + observed.sample_loss_note
        )
        return Outcome(
            self.name, expected, seen, met=min(values) >= self.low and max(values) <= self.high
        )


@dataclass(frozen=True)
class ChannelReaches(Check):
    """A channel arrives at a value, and does so in time."""

    channel_id: int
    name: str
    value: float
    tolerance: float
    within_seconds: float

    def evaluate(self, observed: Observation) -> Outcome:
        """Find the first sample within tolerance, and say how long it took."""
        samples = observed.samples_of(self.channel_id)
        expected = f"{self.value:g} +/- {self.tolerance:g} within {self.within_seconds:g} s"
        if not samples:
            return Outcome(self.name, expected, NOTHING_RECORDED, met=False)
        start = samples[0].sim_us
        arrived = [sample for sample in samples if abs(sample.value - self.value) <= self.tolerance]
        if not arrived:
            closest = min(samples, key=lambda one: abs(one.value - self.value))
            return Outcome(self.name, expected, f"never closer than {closest.value:g}", met=False)
        took = (arrived[0].sim_us - start) / MICROSECONDS_PER_SECOND
        return Outcome(
            self.name, expected, f"reached after {took:.4g} s", met=took <= self.within_seconds
        )
