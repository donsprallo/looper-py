"""Everything the checks are allowed to look at, taken once per run.

Gathered in one place and handed to every check, so that twenty
expectations cost one reading of each recording rather than twenty --
and so that all twenty are looking at the same window rather than at
twenty slightly different ones.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from looper.domain.model.boot import BootChain, PartitionHeader
from looper.domain.model.marks import FlashMark, ResetMark
from looper.domain.model.profile import Profile
from looper.domain.model.readings import CallTiming, Exchange, MemoryUsage, Sample


def _loss_note(lost: int) -> str:
    """Say that the recording overflowed, when it did."""
    return f", and {lost} events the recording could not keep" if lost > 0 else ""


@dataclass(frozen=True)
class Observation:
    """Everything the checks are allowed to look at, taken once per run.

    Attributes:
        samples: The analog samples recorded over the window.
        exchanges: What crossed the buses over the window.
        timings: What the adapter boundary was asked, since it was reset.
        elapsed_seconds: Simulated time the window covered.
        lost_events: Events the recording could not keep. A fast channel
            fills a ring faster than any client empties it, and a check
            that pretended otherwise would quietly measure the ring. The
            server does not say whether they were samples or exchanges.
        memory: The heap and the stack, which say nothing at all in a
            build that is not watching them.
        profile: Where the time went over the window; read only when an
            expectation is about it, since ranking it costs the server a while.
        resets: The resets of the window.
        flash_marks: The flash operations of the window.
        loop_finding: The server's reset loop finding at the window's end, or empty.
        headers: What each partition holds at the window's end (Pro); read
            only when an expectation is about it.
        boot_chains: The run's boot chains at the window's end (Pro); read
            only when an expectation is about them.
    """

    samples: tuple[Sample, ...]
    exchanges: tuple[Exchange, ...]
    timings: tuple[CallTiming, ...]
    elapsed_seconds: float
    lost_events: int = 0
    memory: MemoryUsage = field(default_factory=MemoryUsage)
    profile: Profile = field(default_factory=Profile)
    resets: tuple[ResetMark, ...] = ()
    flash_marks: tuple[FlashMark, ...] = ()
    loop_finding: str = ""
    headers: dict[str, PartitionHeader] = field(default_factory=dict)
    boot_chains: tuple[BootChain, ...] = ()

    @property
    def sample_loss_note(self) -> str:
        """What to add to an observation when events were discarded."""
        return _loss_note(self.lost_events)

    @property
    def exchange_loss_note(self) -> str:
        """What to add to an observation when events were discarded."""
        return _loss_note(self.lost_events)

    def samples_of(self, channel_id: int) -> tuple[Sample, ...]:
        """The samples of one channel, oldest first."""
        return tuple(sample for sample in self.samples if sample.channel_id == channel_id)

    def exchanges_on(self, bus_id: int) -> tuple[Exchange, ...]:
        """The exchanges on one bus, oldest first."""
        return tuple(exchange for exchange in self.exchanges if exchange.bus_id == bus_id)

    def timing_of(self, function: str) -> CallTiming | None:
        """The calls of one function, or None when it was never called."""
        for timing in self.timings:
            if timing.function == function:
                return timing
        return None
