"""What the port answers about restarting the simulation, and on which time model.

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. A restart begins the simulation again from 0 s; the connection
drops meanwhile and comes back with the new one.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from looper.domain.model import RestartStep


class RestartInspector(ABC):
    """Restarting the simulation, and where a restart stands."""

    @abstractmethod
    def ask_restart(
        self,
        rebuild: bool,  # noqa: FBT001
        time_model: str | None,
        time_params: Mapping[str, float],
        from_definition: bool,  # noqa: FBT001
    ) -> RestartStep:
        """Ask for a restart, and return at once with where it stands.

        Args:
            rebuild: Build first; the old simulation runs on meanwhile.
            time_model: The model to restart on; None keeps the one running.
            time_params: Its parameters; one left out takes its default.
            from_definition: Restart on what looper.toml chooses instead.
        """

    @abstractmethod
    def observe_restart(self) -> RestartStep:
        """Where a restart stands, and what the last one did."""
