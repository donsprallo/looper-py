"""Groups of signal blocks, labels, switches and the views of what runs, through gRPC (#6).

Against a scripted server in this process: how the new fields go out as the
contract carries them, how a switch of several parts goes out as one
request, and how the server's answers and refusals come back (looper-srv#31,
#32).
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import (
    BlockLiveness,
    GroupDo,
    SignalGraph,
    SimulationRefusedError,
)
from looper.domain.model import GraphPartSwitch
from looper.domain.model.graph_switches import SwitchTime
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

TWO_WRITERS = "SPEED would have two writers on: Plant and Ideal. Switch both in one request."


class GroupsServicer(service.InspectorServicer):  # type: ignore[misc]
    """Keeps what it was sent and answers as a server that switches groups would."""

    def __init__(self) -> None:
        self.graph: contract.SignalGraphRequest | None = None
        self.switches: list[contract.GraphPartsSwitch] = []
        self.refusal = ""

    def ApplySignalGraph(self, request: Any, context: Any) -> contract.Ack:
        self.graph = request
        return contract.Ack()

    def SwitchGraphParts(self, request: Any, context: Any) -> contract.Ack:
        self.switches.append(request)
        if self.refusal:
            return contract.Ack(refusal=contract.REFUSAL_INVALID, refusal_text=self.refusal)
        return contract.Ack()

    def ObserveSignalGraph(self, request: Any, context: Any) -> contract.SignalGraphView:
        off = contract.SignalNodeStateView(
            node="ideal_out",
            state=contract.SignalNodeStateView.SWITCHED_OFF,
            state_text="Off – Ideal plant is off.",
        )
        label = contract.SignalLabelView(
            name="SPEED", writer_node="plant_out", is_live=True, value=1500.0
        )
        label.writer_nodes.extend(["plant_out", "ideal_out"])
        label.state_text = "now 1500 · set by Plant"
        capacity = contract.SignalCapacityView(nodes_used=5, nodes_max=128, text="signal nodes 5")
        value = contract.GraphValueView(
            node="nominal", value=1450.0, state_text="group Ideal plant is off"
        )
        probe = contract.ProbeView(name="SPEED", channel_id=900, node="speed", is_live=False)
        return contract.SignalGraphView(
            node_states=[off], labels=[label], capacity=capacity, values=[value], probes=[probe]
        )

    def ObserveChains(self, request: Any, context: Any) -> contract.ChainList:
        group = contract.ChainGroupView(
            group_key="plant",
            name="Plant",
            enabled=False,
            signal_blocks=2,
            switched_by_text='chain "Faults" at 0.020000 s',
            switched_at_us=20_000,
            off_text="2 blocks off · SPEED gives its fallback 0",
        )
        return contract.ChainList(groups=[group])

    def ReadEvents(self, request: Any, context: Any) -> contract.EventBatch:
        fired = contract.Event(event_seq=41, sim_us=20_000, chain=contract.ChainFire())
        switched = contract.Event(
            event_seq=41,
            sim_us=20_000,
            graph_switch=contract.GraphSwitchEvent(
                group_key="plant", enabled=False, by_text='chain "Faults"'
            ),
        )
        return contract.EventBatch(events=[fired, switched], next_event_seq=42)


@pytest.fixture
def servicer() -> GroupsServicer:
    return GroupsServicer()


@pytest.fixture
def inspector(servicer: GroupsServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def _sent(servicer: GroupsServicer) -> contract.SignalGraphRequest:
    assert servicer.graph is not None
    return servicer.graph


def test_groups_labels_signs_and_switched_off_blocks_go_out_field_for_field(
    servicer: GroupsServicer, inspector: GrpcInspector
) -> None:
    graph = (
        SignalGraph()
        .group("plant", "Plant")
        .label("SPEED", fallback=0.0)
        .label("LOAD")
        .value("measured", 1500.0, group="plant")
        .title("measured", "Sensor A")
        .set_signal("plant_out", "SPEED", source="measured", group="plant")
        .read_signal("speed", "SPEED")
        .sum("error", ("speed", 1), ("measured", -1))
        .switched_off("error")
        .switch_group("cut", "plant", do=GroupDo.ON)
    )

    inspector.apply_signal_graph(graph)

    sent = _sent(servicer)
    measured, out, speed, error, cut = sent.nodes
    assert (measured.group_key, measured.title) == ("plant", "Sensor A")
    assert (out.kind, out.label, [one.node for one in out.inputs]) == (
        "set_signal",
        "SPEED",
        ["measured"],
    )
    assert (speed.kind, speed.label, speed.group_key) == ("read_signal", "SPEED", "")
    assert (error.kind, list(error.negated_inputs), error.switched_off) == (
        "sum",
        [False, True],
        True,
    )
    assert (cut.kind, cut.block.action.group.group_key) == ("switch_group", "plant")
    assert cut.block.action.group.action == contract.GroupSwitchAction.ON
    speed_label, load_label = sent.labels
    assert (speed_label.name, speed_label.HasField("fallback"), speed_label.fallback) == (
        "SPEED",
        True,
        0.0,
    )
    assert (load_label.name, load_label.HasField("fallback")) == ("LOAD", False)


def test_groups_and_blocks_are_switched_in_one_request_at_a_time(
    servicer: GroupsServicer, inspector: GrpcInspector
) -> None:
    parts = (
        GraphPartSwitch(group_key="plant", enabled=False),
        GraphPartSwitch(group_key="ideal", enabled=True),
        GraphPartSwitch(node_key="lowpass", enabled=True),
    )

    inspector.switch_graph_parts(parts, SwitchTime(at_us=3_000_000))
    inspector.switch_graph_parts(parts[:1], SwitchTime())

    timed, now = servicer.switches
    assert [(one.WhichOneof("part"), one.enabled) for one in timed.parts] == [
        ("group_key", False),
        ("group_key", True),
        ("node_key", True),
    ]
    assert (timed.when.WhichOneof("at"), timed.when.at_us) == ("at_us", 3_000_000)
    assert not now.HasField("when")


def test_a_refused_switch_raises_the_server_s_sentence(
    servicer: GroupsServicer, inspector: GrpcInspector
) -> None:
    servicer.refusal = TWO_WRITERS

    with pytest.raises(SimulationRefusedError) as refused:
        inspector.switch_graph_parts((GraphPartSwitch(group_key="ideal"),), SwitchTime())

    assert str(refused.value) == TWO_WRITERS


def test_what_runs_comes_back_as_node_states_labels_capacity_and_values(
    inspector: GrpcInspector,
) -> None:
    state = inspector.read_signal_graph()

    off = state.node_state("ideal_out")
    assert (off.state, off.is_live, off.state_text) == (
        BlockLiveness.SWITCHED_OFF,
        False,
        "Off – Ideal plant is off.",
    )
    assert state.node_state("speed").is_live
    speed = state.label("SPEED")
    assert (speed.writer_node, speed.value, speed.fallback) == ("plant_out", 1500.0, None)
    assert speed.writer_nodes == ("plant_out", "ideal_out")
    assert (state.capacity.nodes_used, state.capacity.text) == (5, "signal nodes 5")
    assert state.value("nominal").state_text == "group Ideal plant is off"
    assert not state.probes[0].is_live
    with pytest.raises(KeyError, match="no label 'LOAD'"):
        state.label("LOAD")


def test_a_group_says_who_switched_it_and_what_its_being_off_does(
    inspector: GrpcInspector,
) -> None:
    (plant,) = inspector.read_chain_groups()

    assert (plant.key, plant.enabled, plant.signal_blocks) == ("plant", False, 2)
    assert (plant.switched_by_text, plant.switched_at_us) == (
        'chain "Faults" at 0.020000 s',
        20_000,
    )
    assert plant.off_text.startswith("2 blocks off")


def test_a_switch_in_the_stream_keeps_the_number_of_the_record_before_it(
    inspector: GrpcInspector,
) -> None:
    page = inspector.read_events(epoch=1, from_event_seq=41)

    (switched,) = page.graph_switches
    assert (switched.sim_us, switched.event_seq, switched.group_key) == (20_000, 41, "plant")
    assert (switched.enabled, switched.by_text) == (False, 'chain "Faults"')
