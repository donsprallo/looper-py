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

from looper import (
    BusMessage,
    ClockMode,
    ContractMismatchError,
    Signal,
    SimulationRefusedError,
    SimulationUnreachableError,
)
from looper.infrastructure import grpc_inspector
from looper.infrastructure.contract import looper_inspector_pb2 as contract
from looper.infrastructure.contract import looper_inspector_pb2_grpc as service
from looper.infrastructure.grpc_inspector import GrpcInspector
from looper.starting import connect

A_VARIABLE = contract.VariableView(
    variable_id=7,
    path="config.gain",
    name="gain",
    encoding="uint",
    byte_width=1,
    runtime_address=0x2000,
    is_writable=True,
    display_type="uint 1 B",
    display_address="0x2000",
)

A_WATCH = contract.WatchView(
    channel_id=100,
    path="config.gain",
    name="gain",
    encoding="uint",
    byte_width=1,
    runtime_address=0x2000,
    is_writable=True,
    value=3.0,
    display_value="3",
    range_text="uint8, 0 to 255",
)


REFUSED_BY_THE_CLOCK = contract.Ack(
    refusal=contract.REFUSAL_INVALID,
    refusal_text="the clock runs in real time and cannot be advanced",
)


class ScriptedServicer(service.InspectorServicer):  # type: ignore[misc]
    """Answers a handful of calls and remembers what it was asked."""

    def __init__(self) -> None:
        self.asked: list[str] = []
        self.signal: contract.SignalRequest | None = None
        self.bus_request: contract.BusMessageRequest | None = None
        self.written: contract.VariableWrite | None = None
        self.catalogue = contract.VariableCatalogue(variables=[A_VARIABLE])
        self.run_ack = contract.Ack()
        self.runs_still_under_way = 0
        self.reply_ack = contract.Ack()
        self.exchange = contract.Exchange(
            bus_id=5,
            start_us=240_000,
            end_us=250_000,
            direction=contract.DIRECTION_INBOUND,
            address_value=0x123,
            payload=b"\x01\x02\x03\x04",
            payload_length=4,
            accepted=False,
        )
        self.lost = [contract.Lost(from_event_seq=3, to_event_seq=5)]

    def Describe(self, request: Any, context: Any) -> contract.Description:
        return contract.Description(
            contract_version=contract.CONTRACT_VERSION_CURRENT,
            firmware_name="blinky",
            definition_path="/projects/blinky/looper.toml",
        )

    def ObserveRun(self, request: Any, context: Any) -> contract.RunState:
        self.asked.append("observe run")
        under_way = self.runs_still_under_way
        self.runs_still_under_way = max(0, under_way - 1)
        return contract.RunState(
            now_us=500_000,
            mode=contract.CLOCK_MODE_PACED,
            epoch=2,
            next_event_seq=9,
            target_us=600_000 if under_way else 0,
        )

    def ControlRun(self, request: Any, context: Any) -> contract.RunReply:
        self.asked.append(f"run for {request.run_for_us}")
        state = contract.RunState(target_us=600_000 if self.runs_still_under_way else 0)
        return contract.RunReply(ack=self.run_ack, state=state)

    def ReadEvents(self, request: Any, context: Any) -> contract.EventBatch:
        self.asked.append(
            f"events epoch {request.epoch} from {request.from_event_seq} "
            f"kinds {list(request.filter.kinds)}"
        )
        sample = contract.Event(
            event_seq=7, sim_us=500_000, sample=contract.Sample(channel_id=1, value=2.0)
        )
        pin = contract.Event(event_seq=8, sim_us=500_001, pin=contract.PinChange(pin_id=1))
        exchange = contract.Event(event_seq=9, sim_us=250_000, exchange=self.exchange)
        return contract.EventBatch(
            epoch=2,
            events=[sample, pin, exchange],
            lost=self.lost,
            next_event_seq=10,
            sim_now_us=500_000,
            epoch_changed=True,
        )

    def ClearRecordings(self, request: Any, context: Any) -> contract.Ack:
        self.asked.append(f"clear epoch {request.epoch}")
        return self.reply_ack

    def DrivePin(self, request: Any, context: Any) -> contract.PinDriven:
        self.asked.append(f"drive pin {request.pin_id} {request.WhichOneof('level')}")
        return contract.PinDriven(ack=self.reply_ack, high=True)

    def ObserveTimings(self, request: Any, context: Any) -> contract.TimingReportView:
        return contract.TimingReportView(
            entries=[
                contract.CallTimingView(function="adapter_gpio_write", calls=4, origin="adapter"),
                contract.CallTimingView(function="app_run", calls=9, origin="firmware"),
            ]
        )

    def ObserveMemory(self, request: Any, context: Any) -> contract.MemoryView:
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, "the build cannot be read")
        raise AssertionError("abort raises")

    def ObserveBuses(self, request: Any, context: Any) -> contract.BusList:
        context.abort(grpc.StatusCode.UNAVAILABLE, "the simulation closed the channel")
        raise AssertionError("abort raises")

    def ApplySignal(self, request: Any, context: Any) -> contract.Ack:
        self.signal = request
        return self.reply_ack

    def SendBusMessage(self, request: Any, context: Any) -> contract.BusMessageReply:
        self.bus_request = request
        return contract.BusMessageReply(ack=self.reply_ack, summary="701 - 1 bytes")

    def ListVariables(self, request: Any, context: Any) -> contract.VariableCatalogue:
        return self.catalogue

    def WatchVariable(self, request: Any, context: Any) -> contract.WatchStarted:
        self.asked.append(f"watch {request.variable_id}")
        return contract.WatchStarted(watch=A_WATCH, ack=self.reply_ack)

    def WriteVariable(self, request: Any, context: Any) -> contract.Ack:
        self.written = request
        return self.reply_ack

    def RemoveWatch(self, request: Any, context: Any) -> contract.Ack:
        self.asked.append(f"remove watch {request.channel_id}")
        return self.reply_ack

    def ObserveWatches(self, request: Any, context: Any) -> contract.WatchList:
        return contract.WatchList(watches=[A_WATCH])


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

    assert described.contract_version == contract.CONTRACT_VERSION_CURRENT
    assert described.definition_path == "/projects/blinky/looper.toml"


def test_the_run_state_says_where_the_clock_is_and_how_it_goes(inspector: GrpcInspector) -> None:
    state = inspector.run_state()

    assert (state.now_us, state.clock_mode, state.epoch) == (500_000, ClockMode.PACED, 2)
    assert (state.next_event_seq, state.target_us) == (9, 0)


def test_events_are_asked_for_by_epoch_position_and_kind(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    page = inspector.read_events(epoch=2, from_event_seq=7)

    kinds = [contract.EVENT_KIND_SAMPLE, contract.EVENT_KIND_EXCHANGE]
    assert servicer.asked == [f"events epoch 2 from 7 kinds {kinds}"]
    assert (page.samples[0].value, page.samples[0].sim_us, page.samples[0].event_seq) == (
        2.0,
        500_000,
        7,
    )
    assert (page.next_event_seq, page.sim_now_us, page.epoch_changed) == (10, 500_000, True)


def test_a_range_the_server_could_not_keep_becomes_a_count_of_events(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    servicer.lost = [
        contract.Lost(from_event_seq=3, to_event_seq=5),
        contract.Lost(from_event_seq=10, to_event_seq=10),
    ]

    assert inspector.read_events(2, 0).lost_events == 4


def test_a_held_clock_is_run_for_a_span_and_the_clear_names_its_epoch(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    inspector.run_for(250_000)
    inspector.clear_recordings(epoch=2)

    assert servicer.asked == ["run for 250000", "clear epoch 2"]


def test_a_run_still_under_way_is_waited_for(
    inspector: GrpcInspector, servicer: ScriptedServicer, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(grpc_inspector, "RUN_POLL_SECONDS", 0.001)
    servicer.runs_still_under_way = 3

    state = inspector.run_for(100_000)

    assert state.target_us == 0
    assert servicer.asked == ["run for 100000", *["observe run"] * 4]


def test_a_pin_is_toggled_by_the_server_and_the_level_it_set_comes_back(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    assert inspector.toggle_pin(3) == "high"
    assert servicer.asked == ["drive pin 3 toggle"]


def test_only_the_adapter_functions_count_as_calls(inspector: GrpcInspector) -> None:
    """The server ranks the profiled firmware functions beside them."""
    assert [one.function for one in inspector.read_timings()] == ["adapter_gpio_write"]


def test_a_refusal_keeps_its_reason(inspector: GrpcInspector) -> None:
    with pytest.raises(SimulationRefusedError, match="build cannot be read"):
        inspector.read_memory()


def test_anything_else_is_a_simulation_that_cannot_be_read(inspector: GrpcInspector) -> None:
    with pytest.raises(SimulationUnreachableError, match="closed the channel"):
        inspector.read_buses()


def test_a_change_the_server_declines_is_a_refusal_with_its_text(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    servicer.run_ack = REFUSED_BY_THE_CLOCK

    with pytest.raises(SimulationRefusedError, match="cannot be advanced"):
        inspector.run_for(1_000)


def test_a_refusal_without_a_text_names_the_refusal(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    servicer.reply_ack = contract.Ack(refusal=contract.REFUSAL_UNKNOWN_TARGET)

    with pytest.raises(SimulationRefusedError, match="REFUSAL_UNKNOWN_TARGET"):
        inspector.toggle_pin(3)


@pytest.mark.parametrize("change", ["signal", "message", "watch", "write", "remove", "clear"])
def test_every_change_checks_its_acknowledgement(
    inspector: GrpcInspector, servicer: ScriptedServicer, change: str
) -> None:
    servicer.reply_ack = REFUSED_BY_THE_CLOCK
    changes = {
        "signal": lambda: inspector.apply_signal(10, Signal()),
        "message": lambda: inspector.send_bus_message(BusMessage(2, 0x6FF, b"\x01")),
        "watch": lambda: inspector.watch_variable(7),
        "write": lambda: inspector.write_variable(100, 1.0),
        "remove": lambda: inspector.remove_watch(100),
        "clear": lambda: inspector.clear_recordings(2),
    }

    with pytest.raises(SimulationRefusedError, match="cannot be advanced"):
        changes[change]()


def test_a_signal_is_sent_as_the_contract_carries_it(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    inspector.apply_signal(10, Signal(waveform="sine", amplitude=5.0, frequency_hz=2.0))

    assert servicer.signal is not None
    assert servicer.signal.channel_id == 10
    assert servicer.signal.signal.waveform == "sine"


def test_an_exchange_keeps_what_a_recording_is_read_for(inspector: GrpcInspector) -> None:
    exchange = inspector.read_events(epoch=2, from_event_seq=0).exchanges[0]

    assert exchange.address == 0x123
    assert exchange.display_address == "0x123"
    assert exchange.direction == "inbound"
    assert exchange.payload == b"\x01\x02\x03\x04"
    assert exchange.response == b""
    assert exchange.length == 4
    assert not exchange.accepted
    assert (exchange.sim_us, exchange.event_seq) == (250_000, 9)


def test_an_address_is_formatted_here_in_capital_hexadecimal(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    servicer.exchange.address_value = 0x6FF
    servicer.exchange.response = b"\xff\x00"

    exchange = inspector.read_events(epoch=2, from_event_seq=0).exchanges[0]

    assert exchange.display_address == "0x6FF"
    assert exchange.response == b"\xff\x00"


def test_only_samples_and_exchanges_reach_the_page(inspector: GrpcInspector) -> None:
    """The pin change in the script is another kind of event."""
    page = inspector.read_events(epoch=2, from_event_seq=0)

    assert (len(page.samples), len(page.exchanges)) == (1, 1)


def test_a_bus_message_goes_out_nested_as_the_contract_carries_it(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    inspector.send_bus_message(BusMessage(bus_id=2, address=0x6FF, payload=b"\x01", extended=True))

    assert servicer.bus_request is not None
    message = servicer.bus_request.message
    assert (message.bus_id, message.address, message.payload, message.extended) == (
        2,
        0x6FF,
        b"\x01",
        True,
    )


def test_the_catalogue_becomes_variables(inspector: GrpcInspector) -> None:
    variable = inspector.list_variables()[0]

    assert (variable.variable_id, variable.path, variable.runtime_address) == (
        7,
        "config.gain",
        0x2000,
    )
    assert variable.is_writable
    assert variable.display_type == "uint 1 B"


def test_a_catalogue_that_is_unavailable_is_a_refusal_with_its_reason(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    servicer.catalogue = contract.VariableCatalogue(unavailable_reason="no debug information")

    with pytest.raises(SimulationRefusedError, match="no debug information"):
        inspector.list_variables()


def test_a_catalogue_beyond_the_default_message_size_is_taken(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    """A firmware of ordinary size lists some 45 000 variables, about 12 MB."""
    many = [
        contract.VariableView(variable_id=number, path=f"module_{number}." + "x" * 80)
        for number in range(60_000)
    ]
    servicer.catalogue = contract.VariableCatalogue(variables=many)

    assert servicer.catalogue.ByteSize() > 4 * 1024 * 1024
    assert len(inspector.list_variables()) == 60_000


def test_a_variable_is_watched_written_and_removed(
    inspector: GrpcInspector, servicer: ScriptedServicer
) -> None:
    watch = inspector.watch_variable(7)
    inspector.write_variable(watch.channel_id, 3.0)
    inspector.remove_watch(watch.channel_id)

    assert servicer.asked == ["watch 7", "remove watch 100"]
    assert servicer.written is not None
    assert (servicer.written.channel_id, servicer.written.value) == (100, 3.0)
    assert watch.range_text == "uint8, 0 to 255"
    assert inspector.read_watches() == (watch,)


def test_a_server_without_this_contract_is_a_mismatch_not_unreachable() -> None:
    """The package carries the version, so an older server knows none of the methods."""
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    try:
        with pytest.raises(ContractMismatchError, match="does not speak contract version 3"):
            connect(f"127.0.0.1:{port}")
    finally:
        server.stop(None)


def test_an_address_nothing_answers_at_is_unreachable() -> None:
    with pytest.raises(SimulationUnreachableError, match="no inspector server"):
        GrpcInspector("127.0.0.1:9", timeout_seconds=0.2)
