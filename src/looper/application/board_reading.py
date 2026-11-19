"""Reading the device as a block diagram, and its live state.

A mixin of `Simulation`, so that both files stay readable. The picture is
the server's -- it joins looper.toml, component.toml and contract.toml with
what the board code registered, and says per port what in the signal graph
drives and reads it -- so this only asks. Where the server shows no board,
in a project's code without a simulation for one, its sentence is the
refusal's message.
"""

from __future__ import annotations

from looper.application.ports import Inspector
from looper.domain.model.board import Board
from looper.domain.model.board_state import BoardState


class BoardReading:
    """The board of the running image and its live state."""

    _inspector: Inspector

    def board(self) -> Board:
        """The device as a block diagram: the MCU, ports, buses with their taps, devices.

        ``board.port("ZC").driven_by_text`` names what drives a pin in the
        applied signal graph; ``board.bus("SPI1").tap("AS8510").text`` is
        where a chip hangs, ``CS 0``. Read it again when a `board_state`
        names another `revision`.

        Raises:
            SimulationRefusedError: If the server shows no board here; the
                message is the server's sentence.
        """
        return self._inspector.read_board()

    def board_state(self) -> BoardState:
        """The board's live state now: pin levels and values, exchanges per tap and per bus.

        ``state.tap("device:SPI1:0").exchanges`` counts a chip's exchanges,
        ``state.rail("SPI1").last_us`` says when its bus last carried one.

        Raises:
            SimulationRefusedError: If the server shows no board here; the
                message is the server's sentence.
        """
        return self._inspector.read_board_state()
