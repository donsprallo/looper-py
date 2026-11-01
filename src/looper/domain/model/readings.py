"""What a simulation answers with, as this library holds it.

Plain values, one per thing the inspector contract describes and a check
looks at. They carry what the contract carries and nothing it does not:
where the contract offers a derived value -- whether an exchange was
refused, how many calls went unanswered -- it is a property here, worked
out from the fields alone.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ClockMode(StrEnum):
    """How a simulation's clock goes.

    Any client may switch it while the simulation runs, so it is read when
    it matters and not once at the start.
    """

    HELD = "held"
    PACED = "paced"
    MAX = "max"


@dataclass(frozen=True)
class Description:
    """What a server says about the simulation it serves.

    Attributes:
        contract_version: The version of the inspector contract it speaks.
        firmware_name: What the firmware calls itself.
        definition_path: The build definition it was started with, empty
            when it was started without one.
        reads_the_build: Whether the debug information could be read.
    """

    contract_version: int
    firmware_name: str
    definition_path: str = ""
    reads_the_build: bool = False


@dataclass(frozen=True)
class Sample:
    """One recorded value of an analog channel, at a simulated time in microseconds."""

    channel_id: int
    sim_us: int
    value: float
    event_seq: int


@dataclass(frozen=True)
class Exchange:
    """One recorded exchange on a bus.

    Attributes:
        bus_id: The bus it crossed.
        sim_us: When it ended, in simulated microseconds.
        address: Where on the bus it was addressed, as the number a caller
            matches on.
        display_address: The same address as this library shows it, in hexadecimal.
        direction: ``outbound`` when the firmware started it, ``inbound``
            otherwise.
        payload: The bytes it carried.
        response: The bytes that answered it, empty when nothing did.
        length: How many bytes the server counted in it.
        accepted: Whether something on the bus took it.
        event_seq: Its place in the event stream.
    """

    bus_id: int
    sim_us: int
    address: int
    display_address: str
    direction: str
    payload: bytes
    response: bytes
    length: int
    accepted: bool
    event_seq: int

    @property
    def was_refused(self) -> bool:
        """Whether nothing on the bus took it."""
        return not self.accepted


@dataclass(frozen=True)
class EventPage:
    """One page of the event stream, samples and exchanges only.

    Attributes:
        samples: The analog samples on the page.
        exchanges: The bus exchanges on the page.
        next_event_seq: Where the next page begins. Progress is judged by
            this and never by whether the page was empty: a filtered page
            can be empty while more events follow.
        sim_now_us: The simulated time when the server cut the page.
        lost_events: How many events this reader will not get.
        epoch_changed: Whether another client cleared the recording since
            the reader's last page.
    """

    samples: tuple[Sample, ...] = ()
    exchanges: tuple[Exchange, ...] = ()
    next_event_seq: int = 0
    sim_now_us: int = 0
    lost_events: int = 0
    epoch_changed: bool = False


@dataclass(frozen=True)
class RunStatus:
    """Where the clock is and how it goes.

    Attributes:
        now_us: Simulated microseconds since the start.
        clock_mode: How the clock goes now.
        epoch: The recording epoch; a clear starts the next one.
        next_event_seq: Where the event stream stands.
        target_us: Where a run under way ends, zero when none is.
        hold_reason: Why the firmware answers nothing right now, such as a
            debugger stopped at a line; empty while it runs.
    """

    now_us: int
    clock_mode: ClockMode
    epoch: int
    next_event_seq: int
    target_us: int = 0
    hold_reason: str = ""


@dataclass(frozen=True)
class CallTiming:
    """How often one adapter function was called, and how often answered."""

    function: str
    calls: int
    answered_calls: int

    @property
    def unanswered_calls(self) -> int:
        """Calls that were handed the zero value."""
        return self.calls - self.answered_calls


@dataclass(frozen=True)
class HeapUsage:
    """What passed through the allocator.

    Attributes:
        allocations: Calls that returned a block.
        frees: Blocks given back.
        live_bytes: What is out now.
        peak_bytes: The most that was ever out at once.
        is_watched: Whether the allocator is wrapped in this build.
    """

    allocations: int = 0
    frees: int = 0
    live_bytes: int = 0
    peak_bytes: int = 0
    is_watched: bool = False


@dataclass(frozen=True)
class MemoryUsage:
    """The heap and the deepest the stack went.

    Attributes:
        heap: What passed through the allocator.
        stack_bytes: Host stack in use at the deepest moment.
        stack_depth: Frames on the stack then; zero when nothing measured it.
    """

    heap: HeapUsage = HeapUsage()
    stack_bytes: int = 0
    stack_depth: int = 0


@dataclass(frozen=True)
class Pin:
    """One pin the firmware registered."""

    pin_id: int
    name: str
    level: str
    is_drivable: bool


@dataclass(frozen=True)
class Channel:
    """One analog channel the firmware registered.

    Attributes:
        channel_id: The number the simulation knows it by.
        name: What the firmware calls it.
        unit: The unit its values are in, empty when it has none.
        direction: ``input`` for what the firmware reads, ``output`` for
            what it publishes.
        value: The value now.
        is_drivable: Whether a signal may be applied to it.
        display_value: Value and unit as one string, or ``no data``.
    """

    channel_id: int
    name: str
    unit: str
    direction: str
    value: float
    is_drivable: bool
    display_value: str = ""


@dataclass(frozen=True)
class Bus:
    """One bus the simulation models.

    Attributes:
        bus_id: The number the simulation knows it by.
        kind: ``spi``, ``i2c``, ``can`` or ``uart``.
        name: What the firmware calls it.
        bitrate_bps: Its bit rate, zero when none was configured.
        accepts_messages: Whether a test may put a message on it. On SPI
            and I2C the firmware is the master and nothing else sends.
    """

    bus_id: int
    kind: str
    name: str
    bitrate_bps: int = 0
    accepts_messages: bool = False
