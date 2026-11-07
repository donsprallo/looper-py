"""The things one can expect of a firmware's DMA channels (Pro).

Each is answered by the server's run findings about the channel, so that
no judgement the server makes -- what the guard caught, whether a transfer
fits its buffer by the debug information -- is made again here.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.checks.check import Check
from looper.domain.model import Observation, Outcome

#: What a check of a channel says when the firmware has no channel of that name.
NO_SUCH_CHANNEL = "no such DMA channel"
#: The findings each check expects away.
OVERRUN = ("DMA_OVERRUN",)
ACCESSED = ("DMA_READ_UNWRITTEN", "DMA_READ_UNANNOUNCED", "DMA_WRITE_CONFLICT")
LENGTH = ("DMA_LENGTH",)


def _against_findings(
    observed: Observation, channel: str, kinds: tuple[str, ...], expected: str
) -> Outcome:
    """Met when the server found none of the kinds about the channel."""
    found = [one for one in observed.dma.channels if one.name == channel]
    if not found:
        return Outcome(channel, expected, NO_SUCH_CHANNEL, met=False)
    dma_id = found[0].dma_id
    against = [one for one in observed.run_findings if one.dma_id == dma_id and one.kind in kinds]
    seen = "; ".join(one.title for one in against)
    return Outcome(channel, expected, seen or "none found", met=not against)


@dataclass(frozen=True)
class NoOverrun(Check):
    """The channel never wrote into a half whose ISR had not ended."""

    channel: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for the server's overrun finding about the channel."""
        return _against_findings(observed, self.channel, OVERRUN, "no overrun")


@dataclass(frozen=True)
class NotAccessedWhileRunning(Check):
    """The firmware never read or wrote the buffer where the channel still worked."""

    channel: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for what the server's guard caught about the channel."""
        return _against_findings(
            observed, self.channel, ACCESSED, "not accessed while the channel ran"
        )


@dataclass(frozen=True)
class LengthFits(Check):
    """Every transfer of the channel fit the variable it was given."""

    channel: str

    def evaluate(self, observed: Observation) -> Outcome:
        """Look for the server's length finding about the channel."""
        return _against_findings(observed, self.channel, LENGTH, "every transfer fits its buffer")
