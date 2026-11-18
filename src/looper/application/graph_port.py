"""What the port answers about the applied signal graph.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. The probes' trace channels, the levels of the pins the graph
drives and every text about them are the server's.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.graph_state import SignalGraphState


class GraphInspector(ABC):
    """The applied signal graph, as the simulation reports it now."""

    @abstractmethod
    def read_signal_graph(self) -> SignalGraphState:
        """The probes, the pin targets and the comparators of the applied graph.

        An empty state when no graph is applied.
        """
