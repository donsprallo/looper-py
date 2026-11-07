"""Triggers: conditions the simulation watches for, and where each one stands.

The simulation watches, not this library: it fires at the exact simulated
instant a condition became true, where the facts are recorded, and a test
reads afterwards when and how often. Triggers are shared like the
simulation itself -- a window sees the ones a test armed, any client may
disarm any, and a SINGLE trigger holds the simulation for everybody.

Times are simulated microseconds, as everywhere in the event stream.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Polarity(StrEnum):
    """Which edges of a pin count."""

    RISE = "rise"
    FALL = "fall"
    ANY = "any"


class Comparison(StrEnum):
    """How a width or a value is compared with what was asked."""

    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="


class TriggerMode(StrEnum):
    """What a trigger does when it fires.

    There is no AUTO: that is a window's rule for showing a NORMAL trigger.
    """

    #: Fires once and holds the simulation `post_us` later, for every client.
    SINGLE = "single"
    #: Counts every fire and never holds.
    NORMAL = "normal"


class TriggerState(StrEnum):
    """Where a trigger stands."""

    ARMED = "armed"
    FIRED = "fired"
    HELD = "held"
    DISARMED = "disarmed"
    REFUSED = "refused"


@dataclass(frozen=True)
class Edge:
    """A pin changes level."""

    pin_id: int
    polarity: Polarity = Polarity.ANY


@dataclass(frozen=True)
class PinLevel:
    """A pin stands high or low."""

    pin_id: int
    high: bool


@dataclass(frozen=True)
class Pattern:
    """Every pin named stands at its level; fires on becoming true."""

    levels: tuple[PinLevel, ...]


@dataclass(frozen=True)
class EdgeWhile:
    """An edge, counted only while other pins stand at their levels."""

    edge: Edge
    levels: tuple[PinLevel, ...]


@dataclass(frozen=True)
class Width:
    """A high or low pulse whose length compares with `duration_us`.

    Longer than (GT, GE) fires the moment the length is exceeded; the
    others fire at the edge that closes the pulse.
    """

    pin_id: int
    high: bool
    comparison: Comparison
    duration_us: int


@dataclass(frozen=True)
class Quiet:
    """A pin does not change for `duration_us`."""

    pin_id: int
    duration_us: int


@dataclass(frozen=True)
class Value:
    """A watched variable compares with a number, or changes at all.

    Compared where the simulation reads the watch, so at most once a pass.

    Attributes:
        channel_id: The watch's channel.
        comparison: How the stored number, after `mask`, compares with `value`.
        value: The number compared with.
        mask: The bits compared; 0 means all of them.
        on_change: Fire on every change instead, ignoring the comparison.
    """

    channel_id: int
    comparison: Comparison = Comparison.EQ
    value: int = 0
    mask: int = 0
    on_change: bool = False


class Crossing(IntEnum):
    """Which way a message crosses a bus, from the firmware's side."""

    EITHER = 0
    FROM_FIRMWARE = 1
    TO_FIRMWARE = 2


@dataclass(frozen=True)
class BusReceived:
    """A message with an identifier, and if asked a content, crosses a bus.

    Attributes:
        bus_id: The bus.
        address: The identifier, or the address on I2C and SPI.
        address_mask: The identifier's bits that count; 0 for all.
        direction: From the firmware, to it, or either.
        pattern: The bytes the message starts with; empty for any.
        extended: A 29 bit CAN identifier.
    """

    bus_id: int
    address: int = 0
    address_mask: int = 0
    direction: Crossing = Crossing.FROM_FIRMWARE
    pattern: bytes = b""
    extended: bool = False


@dataclass(frozen=True)
class BusTimeout:
    """A message has not come for `duration_us`; once per gap."""

    bus_id: int
    address: int = 0
    duration_us: int = 100_000
    after_first_message: bool = False
    address_mask: int = 0
    extended: bool = False


@dataclass(frozen=True)
class Clock:
    """Fires at `phase_us`, then every `period_us`, in simulated time."""

    period_us: int = 100_000
    phase_us: int = 0


@dataclass(frozen=True)
class Start:
    """Fires at 0 s and, unless `first_life_only`, after every reset of the firmware."""

    first_life_only: bool = False


#: Everything the simulation can watch for today.
TriggerCondition = (
    Edge | Pattern | EdgeWhile | Width | Quiet | Value | BusReceived | BusTimeout | Clock | Start
)


@dataclass(frozen=True)
class TriggerRequest:
    """A trigger as a test arms it.

    Attributes:
        condition: What to watch for.
        mode: Fire once and hold, or count every fire.
        label: What other clients are shown; the server describes the
            condition itself as well.
        pre_us: How much before a fire a window shows.
        post_us: How long after the fire a SINGLE trigger holds the
            simulation, and how much after it a window shows.
        replaces_trigger_id: A trigger this one takes the place of.
    """

    condition: TriggerCondition
    mode: TriggerMode = TriggerMode.SINGLE
    label: str = ""
    pre_us: int = 0
    post_us: int = 0
    replaces_trigger_id: int | None = None


@dataclass(frozen=True)
class Trigger:
    """A trigger as the simulation holds it.

    Attributes:
        trigger_id: The number the server gave it.
        label: What the client that armed it wrote.
        description: The condition in the server's words, such as
            ``BUTTON falls``.
        state: Where it stands.
        mode: Fire once and hold, or count every fire.
        fires: How often it fired.
        armed_at_us: When it was armed.
        last_fired_at_us: When it last fired; 0 before the first fire.
        hold_at_us: SINGLE and fired: when the simulation holds.
        armed_by: The client that armed it.
        disarmed_by: The client that disarmed it, empty while armed.
    """

    trigger_id: int
    label: str
    description: str
    state: TriggerState
    mode: TriggerMode
    fires: int = 0
    armed_at_us: int = 0
    last_fired_at_us: int = 0
    hold_at_us: int = 0
    armed_by: str = ""
    disarmed_by: str = ""

    @property
    def has_fired(self) -> bool:
        """Whether the condition became true at least once."""
        return self.fires > 0

    @property
    def is_live(self) -> bool:
        """Whether it still watches, or holds the place it fired at."""
        return self.state in (TriggerState.ARMED, TriggerState.FIRED, TriggerState.HELD)
