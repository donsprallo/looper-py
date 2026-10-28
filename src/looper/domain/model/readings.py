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


class TimeMode(StrEnum):
    """Where a simulation's clock comes from."""

    REAL_TIME = "real_time"
    VIRTUAL = "virtual"


@dataclass(frozen=True)
class Description:
    """What a server says about the simulation it serves.

    Attributes:
        contract_version: The version of the inspector contract it speaks.
        firmware_name: What the firmware calls itself.
        time_mode: Where its clock comes from.
        definition_path: The build definition it was started with, empty
            when it was started without one.
        reads_the_build: Whether the debug information could be read.
    """

    contract_version: int
    firmware_name: str
    time_mode: TimeMode
    definition_path: str = ""
    reads_the_build: bool = False


@dataclass(frozen=True)
class Sample:
    """One recorded value of an analog channel."""

    channel_id: int
    seconds: float
    value: float
    sequence: int


@dataclass(frozen=True)
class Exchange:
    """One recorded exchange on a bus."""

    bus_id: int
    seconds: float
    address: str
    accepted: bool
    sequence: int

    @property
    def was_refused(self) -> bool:
        """Whether nothing on the bus took it."""
        return not self.accepted


@dataclass(frozen=True)
class Recordings:
    """One page of both recordings, and where the next one begins."""

    samples: tuple[Sample, ...] = ()
    next_sample: int = 0
    exchanges: tuple[Exchange, ...] = ()
    next_exchange: int = 0


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
