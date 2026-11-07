"""What the port answers about the chains of the signal graph and the Logic triggers.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.chain_blocks import ChainBlockState


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
        """
