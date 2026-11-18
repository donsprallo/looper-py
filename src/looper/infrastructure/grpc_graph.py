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
from looper.domain.model.signal_starters import Starters
from looper.domain.model.signal_waves import TableFile
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.graph_state_translation import graph_state_of, starters_of
from looper.infrastructure.signal_translation import table_file_of

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

    def read_table(
        self, path: str, value_column: int, max_error: float, keep_every_point: bool, unit: str
    ) -> TableFile:
        """A table file, read and simplified by the server."""
        request = contract.TableRequest(
            path=path,
            value_column=value_column,
            max_error=max_error,
            keep_every_point=keep_every_point,
            unit=unit,
        )
        return table_file_of(self._call(self._stub.ReadTable, request))

    def list_starters(self) -> Starters:
        """The starters, with what each needs."""
        return starters_of(self._call(self._stub.ListStarters, EMPTY))
