"""Restarting the simulation over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from looper.application.restart_port import RestartInspector
from looper.domain.model import RestartStep
from looper.infrastructure import time_model_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

EMPTY = contract.Empty()


class GrpcRestartCalls(RestartInspector):
    """`RestartSimulation` and `ObserveRestart`, over the inspector's stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    def ask_restart(
        self,
        rebuild: bool,  # noqa: FBT001
        time_model: str | None,
        time_params: Mapping[str, float],
        from_definition: bool,  # noqa: FBT001
    ) -> RestartStep:
        """Ask for a restart; the answer comes before the connection drops."""
        request = time_model_translation.restart_request(
            rebuild, time_model, time_params, from_definition
        )
        return time_model_translation.restart_step_of(
            self._call(self._stub.RestartSimulation, request)
        )

    def observe_restart(self) -> RestartStep:
        """Where a restart stands."""
        return time_model_translation.restart_step_of(self._call(self._stub.ObserveRestart, EMPTY))
