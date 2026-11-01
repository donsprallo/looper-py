"""Contract messages, turned into the values of the domain.

One function per message, and each takes only the fields a check or the
simulation facade reads. What is left out is not lost: it is still on the
message, for whoever wants to draw it.
"""

from __future__ import annotations

from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    ClockMode,
    Description,
    EventPage,
    Exchange,
    HeapUsage,
    MemoryUsage,
    Pin,
    RunStatus,
    Sample,
    Signal,
    Variable,
    Watch,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The origin the server gives a function measured at the adapter boundary.
#: The timings it answers with also rank the profiled firmware functions,
#: which say nothing about whether anything stood behind an adapter call.
ADAPTER_ORIGIN = "adapter"

CLOCK_MODES = {
    contract.CLOCK_MODE_HELD: ClockMode.HELD,
    contract.CLOCK_MODE_PACED: ClockMode.PACED,
    contract.CLOCK_MODE_MAX: ClockMode.MAX,
}

DIRECTIONS = {
    contract.DIRECTION_OUTBOUND: "outbound",
    contract.DIRECTION_INBOUND: "inbound",
}


def description_of(message: contract.Description) -> Description:
    """What the server is attached to."""
    return Description(
        contract_version=message.contract_version,
        firmware_name=message.firmware_name,
        definition_path=message.definition_path,
        reads_the_build=message.reads_the_build,
    )


def run_status_of(message: contract.RunState) -> RunStatus:
    """Where the clock is and how it goes."""
    return RunStatus(
        now_us=message.now_us,
        clock_mode=CLOCK_MODES[message.mode],
        epoch=message.epoch,
        next_event_seq=message.next_event_seq,
        target_us=message.target_us,
        hold_reason=message.hold_reason,
    )


def event_page_of(message: contract.EventBatch) -> EventPage:
    """One page of the event stream: its samples and exchanges, and where it stands."""
    return EventPage(
        samples=tuple(_sample_of(one) for one in message.events if one.HasField("sample")),
        exchanges=tuple(_exchange_of(one) for one in message.events if one.HasField("exchange")),
        next_event_seq=message.next_event_seq,
        sim_now_us=message.sim_now_us,
        lost_events=sum(one.to_event_seq - one.from_event_seq + 1 for one in message.lost),
        epoch_changed=message.epoch_changed,
    )


def timings_of(message: contract.TimingReportView) -> tuple[CallTiming, ...]:
    """The adapter functions and how often they were called and answered."""
    return tuple(
        CallTiming(function=one.function, calls=one.calls, answered_calls=one.answered_calls)
        for one in message.entries
        if one.origin == ADAPTER_ORIGIN
    )


def memory_of(message: contract.MemoryView) -> MemoryUsage:
    """The heap, and the deepest the stack went."""
    heap = message.heap
    return MemoryUsage(
        heap=HeapUsage(
            allocations=heap.allocations,
            frees=heap.frees,
            live_bytes=heap.live_bytes,
            peak_bytes=heap.peak_bytes,
            is_watched=heap.is_watched,
        ),
        stack_bytes=message.stack.deepest_bytes,
        stack_depth=message.stack.deepest_depth,
    )


def pins_of(message: contract.SimulationView) -> tuple[Pin, ...]:
    """Every pin the firmware registered."""
    return tuple(
        Pin(pin_id=one.pin_id, name=one.name, level=one.level, is_drivable=one.is_drivable)
        for one in message.pins
    )


def channels_of(message: contract.ChannelList) -> tuple[Channel, ...]:
    """Every analog channel the firmware registered."""
    return tuple(
        Channel(
            channel_id=one.channel_id,
            name=one.name,
            unit=one.unit,
            direction=one.direction,
            value=one.value,
            is_drivable=one.is_drivable,
            display_value=one.display_value,
        )
        for one in message.channels
    )


def buses_of(message: contract.BusList) -> tuple[Bus, ...]:
    """Every bus the simulation models."""
    return tuple(
        Bus(
            bus_id=one.bus_id,
            kind=one.kind,
            name=one.name,
            bitrate_bps=one.bitrate_bps,
            accepts_messages=one.accepts_messages,
        )
        for one in message.buses
    )


def variables_of(message: contract.VariableCatalogue) -> tuple[Variable, ...]:
    """The firmware's variables, as the catalogue lists them."""
    return tuple(
        Variable(
            variable_id=one.variable_id,
            path=one.path,
            name=one.name,
            encoding=one.encoding,
            byte_width=one.byte_width,
            runtime_address=one.runtime_address,
            is_writable=one.is_writable,
            bit_offset=one.bit_offset,
            bit_width=one.bit_width,
            display_type=one.display_type,
            display_address=one.display_address,
        )
        for one in message.variables
    )


def watch_of(message: contract.WatchView) -> Watch:
    """One variable that is being sampled."""
    return Watch(
        channel_id=message.channel_id,
        path=message.path,
        name=message.name,
        encoding=message.encoding,
        byte_width=message.byte_width,
        runtime_address=message.runtime_address,
        is_writable=message.is_writable,
        value=message.value,
        bit_offset=message.bit_offset,
        bit_width=message.bit_width,
        display_value=message.display_value,
        range_text=message.range_text,
    )


def watches_of(message: contract.WatchList) -> tuple[Watch, ...]:
    """Every variable being sampled."""
    return tuple(watch_of(one) for one in message.watches)


def signal_request_of(channel_id: int, signal: Signal) -> contract.SignalRequest:
    """A signal for an analog input, as the contract carries it."""
    return contract.SignalRequest(
        channel_id=channel_id,
        signal=contract.SignalView(
            waveform=signal.waveform,
            amplitude=signal.amplitude,
            offset=signal.offset,
            frequency_hz=signal.frequency_hz,
            phase_degrees=signal.phase_degrees,
        ),
    )


def bus_message_request_of(message: BusMessage) -> contract.BusMessageRequest:
    """A message for a bus, as the contract carries it."""
    return contract.BusMessageRequest(
        message=contract.BusMessage(
            bus_id=message.bus_id,
            address=message.address,
            payload=message.payload,
            extended=message.extended,
        )
    )


def _sample_of(event: contract.Event) -> Sample:
    return Sample(
        channel_id=event.sample.channel_id,
        sim_us=event.sim_us,
        value=event.sample.value,
        event_seq=event.event_seq,
    )


def _exchange_of(event: contract.Event) -> Exchange:
    exchange = event.exchange
    return Exchange(
        bus_id=exchange.bus_id,
        sim_us=event.sim_us,
        address=exchange.address_value,
        display_address=f"0x{exchange.address_value:X}",
        direction=DIRECTIONS.get(exchange.direction, ""),
        payload=bytes(exchange.payload),
        response=bytes(exchange.response),
        length=exchange.payload_length,
        accepted=exchange.accepted,
        event_seq=event.event_seq,
    )
