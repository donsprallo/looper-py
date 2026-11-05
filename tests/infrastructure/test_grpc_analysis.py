"""The profile, the findings and the signal graph through the gRPC adapter.

Against a scripted server in this process: what is checked is how the
contract's views become values of the domain, and how a graph built in the
domain goes out as the contract's request.
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import Dependency, ProFeatureLockedError, Signal, SignalGraph, SimulationRefusedError
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

APP_STEP = contract.ProfileEntryView(
    name="app_step",
    origin="firmware",
    calls=1000,
    self_nanoseconds=700,
    total_nanoseconds=900,
    source_path="src/app.c",
    line=127,
)
STEP = contract.ProfileEntryView(
    name="step", origin="device model", calls=1000, self_nanoseconds=200
)

A_VIOLATION = contract.ArchitectureFinding(
    key="violation:module:hal->module:app",
    kind="rule violation",
    severity=contract.TIER_CRITICAL,
    title="hal uses app",
    node_ids=["module:hal", "module:app"],
    edge_ids=["module:hal->module:app"],
    state="accepted",
    note="until the rework",
)


class AnalysisServicer(service.InspectorServicer):  # type: ignore[misc]
    """Answers the profile, the findings and the models, and keeps the graph it was sent."""

    def __init__(self) -> None:
        self.graph: contract.SignalGraphRequest | None = None
        self.graph_ack = contract.Ack()
        self.reads_the_code = True
        self.licensed = True
        self.models = contract.ModelList(
            models=[
                contract.ModelView(
                    name="DcMotor",
                    inputs=["voltage", "load"],
                    outputs=["speed", "current"],
                    parameters=[contract.ModelParameterView(name="supply", default_value=24.0)],
                    kind="state",
                    origin="project",
                )
            ]
        )

    def ObserveProfile(self, request: Any, context: Any) -> contract.ProfileView:
        firmware = contract.ProfileGroupView(
            label="firmware",
            children=[
                contract.ProfileGroupView(
                    label="src", children=[contract.ProfileGroupView(entry=APP_STEP)]
                )
            ],
        )
        model = contract.ProfileGroupView(
            label="device model", children=[contract.ProfileGroupView(entry=STEP)]
        )
        return contract.ProfileView(
            groups=[firmware, model],
            heaviest=[APP_STEP],
            measured_nanoseconds=900,
            is_profiling=True,
            note="2 functions",
        )

    def ObserveFindings(self, request: Any, context: Any) -> contract.FindingList:
        if not self.licensed:
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                "The Architect is part of looper Pro - no licence found.",
            )
        if not self.reads_the_code:
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION, "this server does not read the project's code"
            )
        return contract.FindingList(findings=[A_VIOLATION], complete=True, fixed=["cycle:x"])

    def ApplySignalGraph(self, request: Any, context: Any) -> contract.Ack:
        self.graph = request
        return self.graph_ack

    def ListModels(self, request: Any, context: Any) -> contract.ModelList:
        return self.models


@pytest.fixture
def servicer() -> AnalysisServicer:
    return AnalysisServicer()


@pytest.fixture
def inspector(servicer: AnalysisServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_every_function_of_the_tree_of_groups_is_in_the_profile(inspector: GrpcInspector) -> None:
    profile = inspector.read_profile()

    assert [one.name for one in profile.functions] == ["app_step", "step"]
    assert profile.is_profiling
    assert profile.measured_nanoseconds == 900
    app_step = profile.entry("app_step")
    assert app_step is not None
    assert (app_step.source_path, app_step.line, app_step.calls) == ("src/app.c", 127, 1000)


def test_a_finding_names_its_modules_and_dependencies_without_the_graph_ids(
    inspector: GrpcInspector,
) -> None:
    findings = inspector.read_findings()

    (finding,) = findings.findings
    assert findings.is_complete
    assert findings.fixed == ("cycle:x",)
    assert finding.severity == "critical"
    assert finding.modules == ("hal", "app")
    assert finding.dependencies == (Dependency("hal", "app"),)
    assert finding.is_accepted
    assert finding.note == "until the rework"


def test_a_server_that_does_not_read_the_code_refuses_the_findings(
    servicer: AnalysisServicer, inspector: GrpcInspector
) -> None:
    servicer.reads_the_code = False

    with pytest.raises(SimulationRefusedError, match="does not read the project's code"):
        inspector.read_findings()


def test_a_part_of_pro_without_a_licence_is_its_own_refusal(
    servicer: AnalysisServicer, inspector: GrpcInspector
) -> None:
    servicer.licensed = False

    with pytest.raises(ProFeatureLockedError, match="part of looper Pro"):
        inspector.read_findings()


def test_a_graph_goes_out_as_the_contract_carries_it(
    servicer: AnalysisServicer, inspector: GrpcInspector
) -> None:
    graph = (
        SignalGraph()
        .generator("load", Signal("sine", amplitude=0.1, frequency_hz=2.0))
        .channel("voltage", 5)
        .model("motor", "DcMotor", ["voltage", "load"], {"supply": 12.0}, interpreted=True)
        .drive(3, "motor", output=1)
        .probe("speed", "motor")
    )

    inspector.apply_signal_graph(graph)

    sent = servicer.graph
    assert sent is not None
    load, voltage, motor = sent.nodes
    assert (load.kind, load.signal.waveform, load.signal.frequency_hz) == ("generator", "sine", 2.0)
    assert (voltage.kind, voltage.source, voltage.HasField("signal")) == ("channel", 5, False)
    assert [(one.node, one.output) for one in motor.inputs] == [("voltage", 0), ("load", 0)]
    assert (motor.model, dict(motor.parameters), motor.interpreted) == (
        "DcMotor",
        {"supply": 12.0},
        True,
    )
    assert [(one.channel_id, one.node, one.output) for one in sent.targets] == [(3, "motor", 1)]
    assert [(one.name, one.node) for one in sent.probes] == [("speed", "motor")]


def test_a_graph_the_server_declines_is_a_refusal_with_its_text(
    servicer: AnalysisServicer, inspector: GrpcInspector
) -> None:
    servicer.graph_ack = contract.Ack(
        refusal=contract.REFUSAL_INVALID, refusal_text="MOTOR_VOLTAGE is an output"
    )

    with pytest.raises(SimulationRefusedError, match="is an output"):
        inspector.apply_signal_graph(SignalGraph().drive(5, "x"))


def test_models_come_back_with_their_ports_and_parameters(inspector: GrpcInspector) -> None:
    (motor,) = inspector.list_models()

    assert motor.inputs == ("voltage", "load")
    assert motor.output("current") == 1
    assert motor.parameters[0].default_value == 24.0
    assert (motor.kind, motor.origin) == ("state", "project")


def test_a_simulation_without_models_refuses_with_its_reason(
    servicer: AnalysisServicer, inspector: GrpcInspector
) -> None:
    servicer.models = contract.ModelList(unavailable_reason="started without a definition")

    with pytest.raises(SimulationRefusedError, match="without a definition"):
        inspector.list_models()
