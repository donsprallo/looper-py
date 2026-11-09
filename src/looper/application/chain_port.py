"""What the port answers about the chains of the signal graph and the Logic triggers.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.chain_blocks import ChainBlockState
from looper.domain.model.chain_runs import ChainExport, SequenceState
from looper.domain.model.dbc import DbcFile


class ChainInspector(ABC):
    """The chains, and a group's switch."""

    @abstractmethod
    def read_chains(self) -> tuple[ChainBlockState, ...]:
        """Every event block of the graph and of the Logic triggers, in the server's words."""

    @abstractmethod
    def switch_chain(self, group: str, enabled: bool) -> None:  # noqa: FBT001
        """Switch one group on or off; switching on starts it afresh.

        Raises:
            SimulationRefusedError: If there is no such group, or no room for it.
            ProFeatureLockedError: If it is switched on and holds a part of
                looper Pro the server's licence does not unlock; the server's
                sentence says which. Switching it off is never refused so.
        """

    @abstractmethod
    def read_sequences(self) -> tuple[SequenceState, ...]:
        """Every Sequence of the graph's chains, in the server's words."""

    @abstractmethod
    def export_chain(self, group: str, run_for_us: int) -> ChainExport:
        """One group's chain as a pytest, written by the server (looper Pro).

        Raises:
            ProFeatureLockedError: Without the licence.
            SimulationRefusedError: If there is no such group.
        """

    @abstractmethod
    def read_dbc(self, path: str) -> DbcFile:
        """A DBC file's CAN messages and signals, read by the server from its disk.

        A file that cannot be read is answered with its ``problem``, not refused.
        """
