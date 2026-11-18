"""Comparators, input pins the graph drives and probes on their own clock, through gRPC.

Against a scripted server in this process: how the builder's new parts go
out as the contract carries them, and how the applied graph, the pins and
the models come back as values of the domain (looper-srv#28).
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import NodeOutput, Signal, SignalGraph, SignalNodeKind, SimulationRefusedError
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

OVERRIDDEN = (
    "BUTTON_MODE is driven by the signal graph, which comes first: "
    "this drive does nothing while the graph drives it."
)

ZERO_CROSS = contract.PinTargetView(
    pin_id=4,
    pin_name="BUTTON_MODE",
    node="zc",
    high=True,
    value_text="high",
    edges=6,
    resolution_text="exact to 1 µs",
    check_text="Planned ahead to the microsecond.",
    level_text="High from 0.5, low below. Active low in the firmware.",
)


class EdgesServicer(service.InspectorServicer):  # type: ignore[misc]
    """Keeps the graph it was sent and answers with a zero-cross detector applied."""

    def __init__(self) -> None:
        self.graph: contract.SignalGraphRequest | None = None
        self.overridden_text = ""

    def ApplySignalGraph(self, request: Any, context: Any) -> contract.Ack:
        self.graph = request
        return contract.Ack()

    def ObserveSignalGraph(self, request: Any, context: Any) -> contract.SignalGraphView:
        comparator = contract.SignalNodeView(
            node="zc",
            summary_text="rises above 0 · hysteresis 0.1",
            value_text="high",
            hover_lines=["switches high above 0, low below −0.1"],
        )
        probe = contract.ProbeView(name="size", channel_id=0x8001, node="size")
        return contract.SignalGraphView(
            probes=[probe], pin_targets=[ZERO_CROSS], nodes=[comparator]
        )

    def ObserveSimulation(self, request: Any, context: Any) -> contract.SimulationView:
        pin = contract.PinView(
            pin_id=4,
            name="BUTTON_MODE",
            level="high",
            is_drivable=True,
            is_driven_by_graph=True,
            set_by_text="signal graph",
        )
        return contract.SimulationView(pins=[pin])

    def DrivePin(self, request: Any, context: Any) -> contract.PinDriven:
        return contract.PinDriven(
            ack=contract.Ack(), high=False, overridden_text=self.overridden_text
        )

    def ListModels(self, request: Any, context: Any) -> contract.ModelList:
        load = contract.ModelParameterView(
            name="load_ohms", default_value=529.0, description="The load's resistance."
        )
        triac = contract.ModelView(
            name="Triac", parameters=[load], group="Power switches", keywords=["dimmer", "tri"]
        )
        return contract.ModelList(models=[triac])


@pytest.fixture
def servicer() -> EdgesServicer:
    return EdgesServicer()


@pytest.fixture
def inspector(servicer: EdgesServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_a_zero_cross_detector_goes_out_as_the_contract_carries_it(
    servicer: EdgesServicer, inspector: GrpcInspector
) -> None:
    graph = (
        SignalGraph()
        .generator("mains", Signal("sine", amplitude=325.0, frequency_hz=50.0))
        .operation("size", SignalNodeKind.ABS, "mains")
        .compare("zc", "size", level=15.0, hysteresis=2.0, below=True, check_us=20)
        .drive_pin(4, "zc")
        .probe("size", "size", sample_us=1_000)
    )

    inspector.apply_signal_graph(graph)

    sent = servicer.graph
    assert sent is not None
    mains, size, zc = sent.nodes
    assert (size.kind, [one.node for one in size.inputs]) == ("abs", ["mains"])
    assert (zc.kind, [one.node for one in zc.inputs]) == ("compare", ["size"])
    assert (zc.compare.level, zc.compare.hysteresis, zc.compare.below) == (15.0, 2.0, True)
    assert (zc.compare.linked, zc.compare.check_us) == (False, 20)
    assert not mains.HasField("compare")
    assert [(one.pin_id, one.node, one.output) for one in sent.pin_targets] == [(4, "zc", 0)]
    assert [(one.name, one.sample_us) for one in sent.probes] == [("size", 1_000)]


def test_a_linked_threshold_is_the_comparator_s_second_input(
    servicer: EdgesServicer, inspector: GrpcInspector
) -> None:
    graph = SignalGraph().compare("zc", "size", threshold=NodeOutput("ref", 1))

    inspector.apply_signal_graph(graph)

    assert servicer.graph is not None
    (zc,) = servicer.graph.nodes
    assert [(one.node, one.output) for one in zc.inputs] == [("size", 0), ("ref", 1)]
    assert zc.compare.linked


def test_the_applied_graph_comes_back_with_its_probes_pin_targets_and_comparators(
    inspector: GrpcInspector,
) -> None:
    state = inspector.read_signal_graph()

    assert [(one.name, one.channel_id) for one in state.probes] == [("size", 0x8001)]
    target = state.pin_target(4)
    assert (target.pin_name, target.node, target.high, target.edges) == (
        "BUTTON_MODE",
        "zc",
        True,
        6,
    )
    assert target.resolution_text == "exact to 1 µs"
    assert target.level_text.startswith("High from 0.5")
    assert state.node("zc").summary_text == "rises above 0 · hysteresis 0.1"
    assert state.node("zc").hover_lines == ("switches high above 0, low below −0.1",)


def test_a_pin_says_the_graph_drives_it(inspector: GrpcInspector) -> None:
    (pin,) = inspector.read_pins()

    assert pin.is_driven_by_graph
    assert pin.set_by_text == "signal graph"


def test_a_toggle_the_graph_overrides_is_refused_with_the_server_s_sentence(
    servicer: EdgesServicer, inspector: GrpcInspector
) -> None:
    servicer.overridden_text = OVERRIDDEN

    with pytest.raises(SimulationRefusedError, match="driven by the signal graph"):
        inspector.toggle_pin(4)


def test_a_model_comes_with_its_group_its_keywords_and_what_a_parameter_does(
    inspector: GrpcInspector,
) -> None:
    (triac,) = inspector.list_models()

    assert (triac.group, triac.keywords) == ("Power switches", ("dimmer", "tri"))
    assert triac.parameters[0].description == "The load's resistance."
