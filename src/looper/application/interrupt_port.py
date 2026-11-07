"""What the port answers about the firmware's interrupts and DMA channels (free).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.dma import DmaChannels
from looper.domain.model.interrupt_facts import RunFindingReading
from looper.domain.model.interrupts import Interrupts
from looper.domain.model.race import RaceCoverage


class InterruptInspector(ABC):
    """The interrupt sources, the lock, and the DMA channels."""

    @abstractmethod
    def read_interrupts(self) -> Interrupts:
        """Every source with what it did in this life, and the lock."""

    @abstractmethod
    def read_run_findings(self) -> tuple[RunFindingReading, ...]:
        """The server's findings of the run.

        Raises:
            ProFeatureLockedError: Without a licence for run findings.
        """

    @abstractmethod
    def raise_interrupt(self, source_id: int, after_us: int = 0) -> None:
        """Make a source due, now or so long from now.

        Raises:
            SimulationRefusedError: If the server refuses it: no such source,
                the end of a transfer, or no table in the firmware yet.
        """

    @abstractmethod
    def read_dma(self) -> DmaChannels:
        """Every DMA channel with where it stands and what it moved in this life."""

    @abstractmethod
    def set_race(self, on: bool, source_id: int) -> RaceCoverage:  # noqa: FBT001
        """Raise a source at each interruption point in turn, or stop (Pro).

        Raises:
            ProFeatureLockedError: Without a licence for run findings.
        """

    @abstractmethod
    def read_race(self) -> RaceCoverage:
        """What the race mode did since it was switched on (Pro).

        Raises:
            ProFeatureLockedError: Without a licence for run findings.
        """
