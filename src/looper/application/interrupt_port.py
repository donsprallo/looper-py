"""What the port answers about the firmware's interrupts (free).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.interrupts import Interrupts


class InterruptInspector(ABC):
    """The interrupt sources and the lock."""

    @abstractmethod
    def read_interrupts(self) -> Interrupts:
        """Every source with what it did in this life, and the lock."""

    @abstractmethod
    def raise_interrupt(self, source_id: int, after_us: int = 0) -> None:
        """Make a source due, now or so long from now.

        Raises:
            SimulationRefusedError: If the server refuses it: no such source,
                the end of a transfer, or no table in the firmware yet.
        """
