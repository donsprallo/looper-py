"""Moving generators, selects, sample and hold, tables, starters and pin delays, through gRPC.

Against a scripted server in this process: how the new fields go out as the
contract carries them, and how the server's answers come back as values of
the domain (#5, looper-srv#29, #30).
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import Polarity, SampleMode, Signal, SignalGraph
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector

DELAY_TEXT = "BUTTON_MODE↑ → MCP_2↑ 7.50 ms, 4 delays"


class LogicServicer(service.InspectorServicer):  # type: ignore[misc]
    """Keeps what it was sent and answers as a server with signal logic would."""

    def __init__(self) -> None:
        self.graph: contract.SignalGraphRequest | None = None
        self.signal: contract.SignalRequest | None = None
        self.measured: contract.PinMeasureRequest | None = None
        self.table: contract.TableRequest | None = None

    def ApplySignalGraph(self, request: Any, context: Any) -> contract.Ack:
        self.graph = request
        return contract.Ack()

    def ApplySignal(self, request: Any, context: Any) -> contract.Ack:
        self.signal = request
        return contract.Ack()

    def ObserveSignalGraph(self, request: Any, context: Any) -> contract.SignalGraphView:
        select = contract.SignalNodeView(
            node="sel", summary_text="select ≥ 0.5 → when 1", value_text="3.3", value=3.3
        )
        select.passing_port = "when 1"
        hold = contract.SignalNodeView(
            node="sh", summary_text="on rising trigger", samples=4, sampled_us=17_500
        )
        return contract.SignalGraphView(nodes=[select, hold])

    def MeasurePin(self, request: Any, context: Any) -> contract.PinMeasurement:
        self.measured = request
        measured = contract.PinMeasurement(pin_id=request.pin_id, delays=4, delay_text=DELAY_TEXT)
        if request.HasField("reference_pin_id"):
            measured.reference_pin_id = request.reference_pin_id
            measured.delay_min_us, measured.delay_max_us = 7_500, 7_500
        return measured

    def ReadTable(self, request: Any, context: Any) -> contract.TableView:
        self.table = request
        return contract.TableView(
            path=request.path,
            summary_text="3 points · 0 to 2 s · 0 to 4",
            columns=["time", "volts"],
            rows=3,
            times=[0.0, 1.0, 2.0],
            values=[0.0, 4.0, 0.0],
            preview_times=[0.0, 2.0],
            hash="0123456789abcdef",
        )

    def ListStarters(self, request: Any, context: Any) -> contract.StarterList:
        needs = contract.StarterNeeds(input_pins=1, output_pins=1, models=["Triac"])
        dimmer = contract.StarterView(
            name="phase_angle_dimmer",
            display_name="Phase-angle dimmer",
            search_words=["dimmer"],
            graph_text='{"looper_graph": 1}',
            needs=needs,
            needs_text="an input pin, an output pin and the model Triac",
            is_available=True,
        )
        return contract.StarterList(starters=[dimmer])


@pytest.fixture
def servicer() -> LogicServicer:
    return LogicServicer()


@pytest.fixture
def inspector(servicer: LogicServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def _sent(servicer: LogicServicer) -> contract.SignalGraphRequest:
    assert servicer.graph is not None
    return servicer.graph


def test_a_linked_pulse_goes_out_with_its_levels_its_duty_and_its_link(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    graph = SignalGraph().generator(
        "gate", Signal("pulse", 1.65, 1.65, 50.0, duty=0.25), frequency="ramp"
    )

    inspector.apply_signal_graph(graph)

    (gate,) = _sent(servicer).nodes
    assert (gate.signal.low, gate.signal.high, gate.signal.duty) == (0.0, 3.3, 0.25)
    assert list(gate.linked_fields) == ["frequency_hz"]
    assert [one.node for one in gate.inputs] == ["ramp"]


def test_a_sine_leaves_its_duty_unset(servicer: LogicServicer, inspector: GrpcInspector) -> None:
    inspector.apply_signal_graph(SignalGraph().generator("mains", Signal("sine", 325.0)))

    (mains,) = _sent(servicer).nodes
    assert not mains.signal.HasField("duty")
    assert list(mains.linked_fields) == []


def test_a_sweep_and_a_table_go_out_field_for_field_on_an_analog_input(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    sweep = Signal("sweep", 1.0, sweep_from_hz=10.0, sweep_to_hz=1e3, sweep_spacing="logarithmic")

    inspector.apply_signal(3, sweep)
    assert servicer.signal is not None
    sent = servicer.signal.signal
    assert (sent.sweep_from_hz, sent.sweep_to_hz, sent.sweep_spacing) == (10.0, 1e3, "logarithmic")

    inspector.apply_signal(3, Signal.table([(0.0, 1.0), (1.0, 2.0)], end="hold"))
    sent = servicer.signal.signal
    assert (list(sent.table_times), list(sent.table_values)) == ([0.0, 1.0], [1.0, 2.0])
    assert (sent.amplitude, sent.table_end) == (1.0, "hold")


def test_a_select_a_sample_and_hold_and_a_pin_that_holds_pulses_go_out(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    graph = (
        SignalGraph()
        .pin("gate", 4, hold_pulses=True)
        .select("sel", "gate", "hi", "lo")
        .sample_hold("sh", "mains", "gate", mode=SampleMode.FALLING, initial=-2.0)
    )

    inspector.apply_signal_graph(graph)

    gate, select, hold = _sent(servicer).nodes
    assert (gate.kind, gate.source, gate.hold_pulses) == ("pin", 4, True)
    assert (select.kind, [one.node for one in select.inputs]) == ("select", ["gate", "hi", "lo"])
    assert (hold.kind, hold.sample.mode, hold.sample.initial) == ("sample_hold", "falling", -2.0)
    assert not select.HasField("sample")


def test_a_select_and_a_sample_and_hold_come_back_with_what_they_give(
    inspector: GrpcInspector,
) -> None:
    state = inspector.read_signal_graph()

    select, hold = state.node("sel"), state.node("sh")
    assert (select.passing_port, select.value, select.value_text) == ("when 1", 3.3, "3.3")
    assert (hold.value, hold.samples, hold.sampled_us) == (None, 4, 17_500)


def test_a_pin_delay_asks_for_its_reference_and_edges_and_reads_the_delay(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    measured = inspector.measure_pin_delay(102, 4, 0, 50_000, (Polarity.FALL, Polarity.ANY))

    asked = servicer.measured
    assert asked is not None
    assert (asked.reference_pin_id, asked.reference_edge, asked.edge) == (
        4,
        contract.EDGE_FALL,
        contract.EDGE_ANY,
    )
    assert (measured.reference_pin_id, measured.delays, measured.delay_min_us) == (4, 4, 7_500)
    assert measured.delay_text == DELAY_TEXT


def test_a_plain_pin_measurement_names_no_reference(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    measured = inspector.measure_pin(102, 0, 50_000)

    assert servicer.measured is not None
    assert not servicer.measured.HasField("reference_pin_id")
    assert (measured.reference_pin_id, measured.delays) == (None, 0)


def test_a_table_file_is_read_by_the_server(
    servicer: LogicServicer, inspector: GrpcInspector
) -> None:
    read = inspector.read_table("dip.csv", 1, 0.5, False, "V")

    assert servicer.table is not None
    assert (servicer.table.value_column, servicer.table.max_error, servicer.table.unit) == (
        1,
        0.5,
        "V",
    )
    assert (read.times, read.values, read.columns) == (
        (0.0, 1.0, 2.0),
        (0.0, 4.0, 0.0),
        ("time", "volts"),
    )
    assert read.signal(amplitude=2.0).table_values == (0.0, 4.0, 0.0)


def test_the_starters_come_with_what_they_need(inspector: GrpcInspector) -> None:
    starters = inspector.list_starters()

    dimmer = starters.named("phase_angle_dimmer")
    assert (dimmer.display_name, dimmer.is_available) == ("Phase-angle dimmer", True)
    assert (dimmer.needs.input_pins, dimmer.needs.models) == (1, ("Triac",))
    assert dimmer.needs_text == "an input pin, an output pin and the model Triac"
