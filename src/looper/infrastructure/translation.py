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
    Description,
    Exchange,
    HeapUsage,
    MemoryUsage,
    Pin,
    Recordings,
    Sample,
    Signal,
    TimeMode,
    Variable,
    Watch,
)
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The origin the server gives a function measured at the adapter boundary.
#: The timings it answers with also rank the profiled firmware functions,
#: which say nothing about whether anything stood behind an adapter call.
ADAPTER_ORIGIN = "adapter"


def description_of(message: contract.Description) -> Description:
    """What the server is attached to."""
    return Description(
        contract_version=message.contract_version,
        firmware_name=message.firmware_name,
        time_mode=TimeMode(message.time_mode),
        definition_path=message.definition_path,
        reads_the_build=message.reads_the_build,
    )


def recordings_of(message: contract.Recordings) -> Recordings:
    """One page of both recordings."""
    return Recordings(
        samples=tuple(_sample_of(one) for one in message.trace.samples),
        next_sample=message.trace.next_sequence,
        exchanges=tuple(_exchange_of(one) for one in message.bus_trace.exchanges),
        next_exchange=message.bus_trace.next_sequence,
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
        bus_id=message.bus_id,
        address=message.address,
        payload=message.payload,
        extended=message.extended,
    )


def _sample_of(message: contract.SampleView) -> Sample:
    return Sample(
        channel_id=message.channel_id,
        seconds=message.seconds,
        value=message.value,
        sequence=message.sequence,
    )


def _exchange_of(message: contract.ExchangeView) -> Exchange:
    return Exchange(
        bus_id=message.bus_id,
        seconds=message.seconds,
        address=_address_of(message.address),
        display_address=message.address,
        direction=message.direction,
        payload=bytes.fromhex(message.payload),
        response=bytes.fromhex(message.response),
        length=message.length,
        accepted=message.accepted,
        sequence=message.sequence,
    )


def _address_of(display: str) -> int:
    """The number behind an address as the server shows it: ``0x123`` or ``0``."""
    if display.lower().startswith("0x"):
        return int(display, 16)
    return int(display, 10)
