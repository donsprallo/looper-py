"""The board part of the scripted inspector: a fixed picture and state, or a refusal."""

from __future__ import annotations

from looper.application.ports import SimulationRefusedError
from looper.domain.model.board import (
    Board,
    BoardEdge,
    BoardEdgeKind,
    BoardNode,
    BoardNodeKind,
)
from looper.domain.model.board_state import BoardNodeState, BoardState, BoardTapState

#: A board of one MCU, one input pin driven by a comparator, and SPI1 with an AS8510 at CS 0.
BOARD = Board(
    title="blinky",
    nodes=(
        BoardNode("mcu", BoardNodeKind.MCU, "MCU"),
        BoardNode(
            "pin:ZC",
            BoardNodeKind.PIN,
            "ZC",
            parent_key="mcu",
            is_input=True,
            driven_by_text="Comparator",
            driven_by_node_key="zero_cross",
            reference_text="◁ Comparator",
        ),
        BoardNode("bus:SPI1", BoardNodeKind.BUS, "SPI1", parent_key="mcu", bus_kind="spi"),
        BoardNode("device:SPI1:0", BoardNodeKind.DEVICE, "AS8510", hand_wired=True),
    ),
    edges=(BoardEdge("device:SPI1:0", "bus:SPI1", BoardEdgeKind.ON_BUS, text="CS 0"),),
    revision=2,
    revision_text="ZC is driven by Comparator now.",
)
STATE = BoardState(
    revision=2,
    sim_us=600_000,
    nodes=(
        BoardNodeState("pin:ZC", state_text="high", value=1.0),
        BoardNodeState("bus:SPI1", state_text="6 exchanges", exchanges=6, last_us=500_000),
    ),
    taps=(BoardTapState("device:SPI1:0", "bus:SPI1", exchanges=6, unanswered=1),),
)


class ScriptedBoard:
    """Answers the board questions from a fixed picture, or refuses with a sentence."""

    def __init__(self) -> None:
        self.board = BOARD
        self.board_state = STATE
        self.board_refusal = ""

    def read_board(self) -> Board:
        self._refuse_if_asked()
        return self.board

    def read_board_state(self) -> BoardState:
        self._refuse_if_asked()
        return self.board_state

    def _refuse_if_asked(self) -> None:
        if self.board_refusal:
            raise SimulationRefusedError(self.board_refusal)
