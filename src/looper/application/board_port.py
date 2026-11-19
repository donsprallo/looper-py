"""What the port answers about the device as a block diagram (free).

Apart from the rest of the port so that both stay readable; `Inspector`
inherits it. The picture and its live state are the server's: a simulation
answers, a project's code without one and a board at a probe are refused
with the server's sentence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model.board import Board
from looper.domain.model.board_state import BoardState


class BoardInspector(ABC):
    """The board of the running image, and its live state."""

    @abstractmethod
    def read_board(self) -> Board:
        """The MCU, its ports, the buses and the chips on them, and the wires between.

        Raises:
            SimulationRefusedError: If the server shows no board here; the
                message is its sentence.
        """

    @abstractmethod
    def read_board_state(self) -> BoardState:
        """Pin levels, analog values, the exchanges per tap and per bus, now.

        Raises:
            SimulationRefusedError: If the server shows no board here; the
                message is its sentence.
        """
