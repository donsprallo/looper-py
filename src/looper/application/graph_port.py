"""What the port answers about the applied signal graph.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. The probes' trace channels, the levels of the pins the graph
drives and every text about them are the server's, and so are the table
files read for a generator and the starters a graph can begin with.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.graph_state import SignalGraphState
from looper.domain.model.signal_starters import Starters
from looper.domain.model.signal_waves import TableFile


class GraphInspector(ABC):
    """The applied signal graph, as the simulation reports it now."""

    @abstractmethod
    def read_signal_graph(self) -> SignalGraphState:
        """The probes, the pin targets and the comparators of the applied graph.

        An empty state when no graph is applied.
        """

    @abstractmethod
    def read_table(
        self, path: str, value_column: int, max_error: float, keep_every_point: bool, unit: str
    ) -> TableFile:
        """A CSV or PWL file on the server's disk, read and simplified for a Table generator.

        A file that cannot be played comes back with its ``problem_text``.
        """

    @abstractmethod
    def list_starters(self) -> Starters:
        """The starters a graph can begin with, and whether this firmware has what each needs."""
