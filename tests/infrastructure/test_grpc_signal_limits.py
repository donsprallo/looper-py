"""Limit and Slew rate through gRPC (#8, looper-srv#34).

Against a scripted server in this process: how a limit's and a slew rate's
settings go out as the contract carries them, and how the server's view of
them -- what they give, and a limit's fault -- comes back.
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import SignalGraph
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector
from looper.infrastructure.translation import capabilities_of

FAULT = "The low limit 2 is above the high limit 1: it gives the low limit."


class LimitServicer(service.InspectorServicer):  # type: ignore[misc]
    """Keeps the graph it was sent and answers as a server that limits signals would."""

    def __init__(self) -> None:
        self.graph: contract.SignalGraphRequest | None = None

    def ApplySignalGraph(self, request: Any, context: Any) -> contract.Ack:
        self.graph = request
        return contract.Ack()

    def ObserveSignalGraph(self, request: Any, context: Any) -> contract.SignalGraphView:
        clamp = contract.SignalNodeView(
            node="clamp", summary_text="limit 2 … 1", value_text="2", value=2.0, fault_text=FAULT
        )
        ramp = contract.SignalNodeView(
            node="ramp", summary_text="slew ↑1 /ms ↓2 /ms", value_text="0.5", value=0.5
        )
        return contract.SignalGraphView(nodes=[clamp, ramp])


@pytest.fixture
def servicer() -> LimitServicer:
    return LimitServicer()


@pytest.fixture
def inspector(servicer: LimitServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def _sent(servicer: LimitServicer) -> contract.SignalGraphRequest:
    assert servicer.graph is not None
    return servicer.graph


def test_a_limit_and_a_slew_rate_go_out_field_for_field(
    servicer: LimitServicer, inspector: GrpcInspector
) -> None:
    graph = (
        SignalGraph()
        .limit("clamp", "sine", low=-1.0, high="ref")
        .slew_rate("ramp", "step", rise=1000.0, fall=2000.0)
    )

    inspector.apply_signal_graph(graph)

    clamp, ramp = _sent(servicer).nodes
    assert (clamp.kind, [one.node for one in clamp.inputs]) == ("limit", ["sine", "ref"])
    assert (clamp.limit.low, clamp.limit.low_linked, clamp.limit.high_linked) == (
        -1.0,
        False,
        True,
    )
    assert (ramp.kind, ramp.slew.rise, ramp.slew.fall) == ("slew_rate", 1000.0, 2000.0)
    assert not clamp.HasField("slew")
    assert not ramp.HasField("limit")


def test_the_other_nodes_leave_both_settings_unset(
    servicer: LimitServicer, inspector: GrpcInspector
) -> None:
    inspector.apply_signal_graph(SignalGraph().value("ref", 0.25))

    (ref,) = _sent(servicer).nodes
    assert not ref.HasField("limit")
    assert not ref.HasField("slew")


def test_a_limit_comes_back_with_what_it_gives_and_its_fault(inspector: GrpcInspector) -> None:
    state = inspector.read_signal_graph()

    clamp, ramp = state.node("clamp"), state.node("ramp")
    assert (clamp.value, clamp.value_text, clamp.fault_text) == (2.0, "2", FAULT)
    assert (ramp.value, ramp.fault_text) == (0.5, "")


def test_the_capability_is_named_signal_limits() -> None:
    assert capabilities_of([contract.CAPABILITY_SIGNAL_LIMITS]) == ("signal_limits",)
