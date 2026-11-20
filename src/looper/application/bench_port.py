"""What the port answers about a bench of devices with joined buses (Pro).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. A simulation answers; a project's code without one and a board
at a probe are refused with the server's sentence, the free download with
`ProFeatureLockedError` and its sentence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.bench import BenchState, JoinCandidates


class BenchInspector(ABC):
    """The bench this simulation is on, and joining or leaving one."""

    @abstractmethod
    def read_bench(self) -> BenchState:
        """The bench as this server sees it.

        Raises:
            SimulationRefusedError: If the server answers no bench here.
        """

    @abstractmethod
    def read_join_candidates(self, bus_id: int) -> JoinCandidates:
        """The other servers on this PC this device's bus could be joined with.

        Raises:
            SimulationRefusedError: If the server answers no bench here.
        """

    @abstractmethod
    def join_bus(self, bus_id: int, peer_instance_id: str, peer_bus_id: int) -> BenchState:
        """Join this device's bus with another server's; answers at once with phase JOINING.

        Raises:
            SimulationRefusedError: If the join cannot be carried out; the
                message is the server's sentence.
        """

    @abstractmethod
    def leave_bench(self) -> BenchState:
        """Leave the bench; answers at once with phase LEAVING.

        Raises:
            SimulationRefusedError: If this server is on no bench.
        """
