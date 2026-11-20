"""The bench calls over gRPC, mixed into `GrpcInspector`.

A mixin rather than more methods on `GrpcInspector`, so that both files
stay readable; it uses the inspector's stub and its one way of making a
call, which turns the server's refusal into `SimulationRefusedError` and the
free download's `PERMISSION_DENIED` into `ProFeatureLockedError`, each with
the server's sentence.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import Any

from looper.application.bench_port import BenchInspector
from looper.domain.model.bench import BenchState, JoinCandidates
from looper.infrastructure import bench_translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service

EMPTY = contract.Empty()
#: How long a look at the bench may take. The servers of a bench tell each other
#: what changed through files; a look that does not come back in this time is a
#: server that no longer answers, not a slow one.
READ_TIMEOUT_SECONDS = 10.0


class GrpcBenchCalls(BenchInspector):
    """`ObserveBench`, `DescribeJoinCandidates`, `JoinBus` and `LeaveBench`, over the stub."""

    _stub: service.InspectorStub

    @staticmethod
    def _call(method: Callable[[Any], Any], request: Any) -> Any:
        raise NotImplementedError

    def read_bench(self) -> BenchState:
        """The bench as the server sees it."""
        observe = partial(self._stub.ObserveBench, timeout=READ_TIMEOUT_SECONDS)
        return bench_translation.bench_state_of(self._call(observe, EMPTY))

    def read_join_candidates(self, bus_id: int) -> JoinCandidates:
        """The other servers on this PC, joinable or not."""
        request = contract.JoinCandidatesRequest(bus_id=bus_id)
        describe = partial(self._stub.DescribeJoinCandidates, timeout=READ_TIMEOUT_SECONDS)
        listing = self._call(describe, request)
        return bench_translation.join_candidates_of(listing)

    def join_bus(self, bus_id: int, peer_instance_id: str, peer_bus_id: int) -> BenchState:
        """Ask for the join; the server answers before both restart."""
        request = contract.JoinRequest(
            bus_id=bus_id, peer_instance_id=peer_instance_id, peer_bus_id=peer_bus_id
        )
        return bench_translation.bench_state_of(self._call(self._stub.JoinBus, request))

    def leave_bench(self) -> BenchState:
        """Ask to leave; the server answers before the devices restart alone."""
        return bench_translation.bench_state_of(self._call(self._stub.LeaveBench, EMPTY))
