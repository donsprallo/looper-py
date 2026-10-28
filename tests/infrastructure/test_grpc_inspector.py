"""The gRPC adapter against a real server in this process.

The server answers from a script rather than from a simulation, so what is
checked is the adapter's half: the calls it makes, how the messages become
values of the domain, and how a failure becomes one of the port's two.
"""

from __future__ import annotations

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import pytest

from looper import Signal, SimulationRefusedError, SimulationUnreachableError, TimeMode
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector


class ScriptedServicer(service.InspectorServicer):  # type: ignore[misc]
    """Answers a handful of calls and remembers what it was asked."""

    def __init__(self) -> None:
        self.asked: list[str] = []
        self.signal: contract.SignalRequest | None = None

    def Describe(self, request: Any, context: Any) -> contract.Description:
        return contract.Description(
            contract_version=contract.CONTRACT_VERSION_CURRENT,
            firmware_name="blinky",
            time_mode="virtual",
            definition_path="/projects/blinky/looper.toml",
        )

    def ReadRecordings(self, request: Any, context: Any) -> contract.Recordings:
        self.asked.append(f"recordings after {request.after_sample}")
        sample = contract.SampleView(channel_id=1, seconds=0.5, value=2.0, sequence=7)
        return contract.Recordings(
            trace=contract.TraceView(samples=[sample], next_sequence=8),
            bus_trace=contract.BusTraceView(next_sequence=0),
        )

    def ObserveTimings(self, request: Any, context: Any) -> contract.TimingReportView:
        return contract.TimingReportView(
            entries=[
                contract.CallTimingView(function="adapter_gpio_write", calls=4, origin="adapter"),
                contract.CallTimingView(function="app_run", calls=9, origin="firmware"),
            ]
        )

    def ObserveMemory(self, request: Any, context: Any) -> contract.MemoryView:
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, "the build cannot be read")

    def AdvanceTime(self, request: Any, context: Any) -> contract.Empty:
        context.abort(grpc.StatusCode.UNAVAILABLE, "the simulation closed the channel")

    def ApplySignal(self, request: Any, context: Any) -> contract.Empty:
        self.signal = request
        return contract.Empty()


@pytest.fixture
def servicer() -> ScriptedServicer:
    return ScriptedServicer()


@pytest.fixture
def inspector(servicer: ScriptedServicer) -> Iterator[GrpcInspector]:
    """An adapter connected to the scripted server on a free port."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    service.add_InspectorServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    connected = GrpcInspector(f"127.0.0.1:{port}")
    yield connected
    connected.close()
    server.stop(None)


def test_the_description_becomes_values_of_the_domain(inspector: GrpcInspector) -> None:
    described = inspector.describe()

    assert described.time_mode is TimeMode.VIRTUAL
    assert described.definition_path == "/projects/blinky/looper.toml"


def test_the_recordings_are_asked_for_from_the_given_position(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    page = inspector.read_recordings(after_sample=7, after_exchange=0)

    assert servicer.asked == ["recordings after 7"]
    assert page.samples[0].value == 2.0
    assert page.next_sample == 8


def test_only_the_adapter_functions_count_as_calls(inspector: GrpcInspector) -> None:
    """The server ranks the profiled firmware functions beside them."""
    assert [one.function for one in inspector.read_timings()] == ["adapter_gpio_write"]


def test_a_refusal_keeps_its_reason(inspector: GrpcInspector) -> None:
    with pytest.raises(SimulationRefusedError, match="build cannot be read"):
        inspector.read_memory()


def test_anything_else_is_a_simulation_that_cannot_be_read(inspector: GrpcInspector) -> None:
    with pytest.raises(SimulationUnreachableError, match="closed the channel"):
        inspector.advance(1_000)


def test_a_signal_is_sent_as_the_contract_carries_it(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    inspector.apply_signal(10, Signal(waveform="sine", amplitude=5.0, frequency_hz=2.0))

    assert servicer.signal is not None
    assert servicer.signal.channel_id == 10
    assert servicer.signal.signal.waveform == "sine"


def test_an_address_nothing_answers_at_is_unreachable() -> None:
    with pytest.raises(SimulationUnreachableError, match="no inspector server"):
        GrpcInspector("127.0.0.1:9", timeout_seconds=0.2)
