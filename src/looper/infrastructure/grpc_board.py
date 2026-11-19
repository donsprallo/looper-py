"""The board calls over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call, which turns the server's refusal into `SimulationRefusedError` with
the server's sentence.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.board_port import BoardInspector
from looper.domain.model.board import Board
from looper.domain.model.board_state import BoardState
from looper.infrastructure import board_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

#: The board of the image that runs; the server does not take another one yet.
RUNNING_IMAGE = contract.ImageScope()


class GrpcBoardCalls(BoardInspector):
    """The board and its live state, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    def read_board(self) -> Board:
        """The board as the server describes it."""
        return board_translation.board_of(self._call(self._stub.DescribeBoard, RUNNING_IMAGE))

    def read_board_state(self) -> BoardState:
        """The board's live state."""
        state = self._call(self._stub.ObserveBoard, RUNNING_IMAGE)
        return board_translation.board_state_of(state)
