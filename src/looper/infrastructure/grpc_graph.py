"""The calls about the applied signal graph over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from looper.application.graph_port import GraphInspector
from looper.domain.model import SignalGraphState
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.graph_state_translation import graph_state_of

EMPTY = contract.Empty()


class GrpcGraphCalls(GraphInspector):
    """The applied signal graph, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    def read_signal_graph(self) -> SignalGraphState:
        """The probes, the pin targets and the comparators of the applied graph."""
        return graph_state_of(self._call(self._stub.ObserveSignalGraph, EMPTY))
