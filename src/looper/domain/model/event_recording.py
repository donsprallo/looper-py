"""Which interrupt and DMA events the simulation records.

A source at bus speed makes more events than anybody reads, so the server
records nothing of a source or a DMA channel unless it is named, in
looper.toml or by a client. Each is named with a mode: ``"off"`` (only its
findings), ``"summary"`` (an ISR as one event; a channel without its halves)
or ``"detailed"`` (pending, entered and left; a channel's halves too). The
name ``"*"`` stands for every one not named. The counts of
`Simulation.interrupts` and `Simulation.dma` are complete whatever is
recorded.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

#: The modes a source or channel is recorded in.
MODES = ("off", "summary", "detailed")
#: The name that stands for every source or channel not named.
EVERY_OTHER = "*"


@dataclass(frozen=True)
class EventRecording:
    """What to record: each source and channel by its name in contract.toml, and the rings.

    Attributes:
        interrupts: A source's name (or ``"*"``) and its mode.
        dma: A channel's name (or ``"*"``) and its mode.
        interrupt_ring: Events the interrupt ring holds; 0 keeps it.
        dma_ring: Events the DMA ring holds; 0 keeps it.
        at_least: Raise the named ones to at least their mode and keep the
            rest, in place of replacing what is recorded.
    """

    interrupts: Mapping[str, str] = field(default_factory=dict)
    dma: Mapping[str, str] = field(default_factory=dict)
    interrupt_ring: int = 0
    dma_ring: int = 0
    at_least: bool = False

    def __post_init__(self) -> None:
        """Refuse a mode that is not one of the three, before the server is asked."""
        for name, mode in [*self.interrupts.items(), *self.dma.items()]:
            if mode not in MODES:
                message = f"{name}: '{mode}' is no mode; the modes are off, summary and detailed"
                raise ValueError(message)
