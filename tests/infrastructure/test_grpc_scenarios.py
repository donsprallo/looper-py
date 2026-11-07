"""Sequences, switched signals, faults, interrupts and resets through the gRPC adapter."""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import (
    Fault,
    FaultKind,
    Interrupt,
    ResetSeen,
    Sequence,
    SequenceProgress,
    SignalDo,
    SignalGraph,
    Start,
    Step,
    StepKind,
    SwitchSignal,
    step_port,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector
from looper.infrastructure.signal_graph_translation import signal_graph_request_of

STEPS = Sequence(
    (
        Step(StepKind.DO, "press"),
        Step(StepKind.WAIT, "settle", 1_000),
        Step(StepKind.WAIT_FOR, "lit", 200_000),
        Step(StepKind.DO, "release"),
        Step(StepKind.EXPECT_NONE, "quiet", 50_000),
    )
)


class ScenarioServicer(service.InspectorServicer):  # type: ignore[misc]
    """Lists one running Sequence and writes the test it is asked for."""

    def __init__(self) -> None:
        self.export: contract.PytestExportRequest | None = None

    def ObserveChains(self, request: Any, context: Any) -> contract.ChainList:
        return contract.ChainList(
            nodes=[contract.ChainNodeView(node_key="test", group_key="boost")],
            groups=[contract.ChainGroupView(group_key="boost", name="Boost test")],
            sequences=[
                contract.SequenceStateView(
                    node_key="test",
                    step_index=3,
                    step_count=5,
                    state=contract.SequenceStateView.RUNNING,
                    step_text="▸ step 3 of 5",
                )
            ],
        )

    def ExportChainAsPytest(self, request: Any, context: Any) -> contract.PytestExport:
        self.export = request
        return contract.PytestExport(file_name="test_boost_test.py", text="...", warnings=["w"])


@pytest.fixture
def servicer() -> ScenarioServicer:
    return ScenarioServicer()


@pytest.fixture
def inspector(servicer: ScenarioServicer) -> Iterator[GrpcInspector]:
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_a_sequence_s_steps_have_ports_in_step_order() -> None:
    ports = [step_port(STEPS, index) for index in (0, 2, 3, 4)]

    assert ports == [2, 1, 3, 2]
    with pytest.raises(IndexError, match="wait"):
        step_port(STEPS, 1)


def test_a_sequence_goes_out_with_its_steps() -> None:
    graph = SignalGraph().when("go", Start()).sequence("test", STEPS, after="go")

    request = signal_graph_request_of(graph)

    sequence = request.nodes[1].block.logic.sequence
    assert request.nodes[1].kind == "sequence"
    assert [step.kind for step in sequence.steps][:3] == [
        contract.SequenceStepRequest.DO,
        contract.SequenceStepRequest.WAIT,
        contract.SequenceStepRequest.WAIT_FOR,
    ]
    assert sequence.steps[2].label == "lit"
    assert sequence.steps[2].duration_us == 200_000


def test_switch_fault_interrupt_and_reset_go_out_as_their_actions() -> None:
    graph = (
        SignalGraph()
        .when("heard", Interrupt(7, on_entry=True))
        .when("again", ResetSeen(4))
        .switch_signal("ramp", SwitchSignal("setpoint", do=SignalDo.RAMP, to=3.0, over_us=2_000))
        .inject_fault("drop", Fault(FaultKind.DROP, bus_id=1, address=0x123, next=3))
        .raise_interrupt("raise", 7)
        .reset_firmware("reset", 5)
        .logic("first", "once", after="heard")
    )

    nodes = {node.key: node for node in signal_graph_request_of(graph).nodes}

    assert nodes["heard"].block.condition.interrupt.on_entry
    assert nodes["again"].block.condition.reset.cause == contract.RESET_CAUSE_PIN
    switch = nodes["ramp"].block.action.signal
    assert (switch.node, switch.action, switch.to) == (
        "setpoint",
        contract.SignalSwitchAction.RAMP,
        3.0,
    )
    fault = nodes["drop"].block.action.fault
    assert (fault.kind, fault.address, fault.next) == (contract.FaultAction.DROP, 0x123, 3)
    assert nodes["raise"].block.action.interrupt.source_id == 7
    assert nodes["reset"].block.action.reset.cause == contract.RESET_CAUSE_BROWN_OUT
    assert nodes["first"].block.logic.WhichOneof("kind") == "once"


def test_a_logic_block_needs_a_kind_without_settings() -> None:
    with pytest.raises(ValueError, match="delay"):
        SignalGraph().logic("late", "delay")


def test_a_sequence_is_read_with_its_group_s_name(inspector: GrpcInspector) -> None:
    (state,) = inspector.read_sequences()

    assert (state.key, state.group, state.group_name) == ("test", "boost", "Boost test")
    assert state.progress is SequenceProgress.RUNNING
    assert state.step_text == "▸ step 3 of 5"
    assert not state.ended


def test_an_export_names_the_group_and_its_time(
    inspector: GrpcInspector, servicer: ScenarioServicer
) -> None:
    written = inspector.export_chain("boost", 2_000_000)

    assert servicer.export is not None
    assert (servicer.export.group_key, servicer.export.run_for_us) == ("boost", 2_000_000)
    assert (written.file_name, written.warnings) == ("test_boost_test.py", ("w",))
