"""The event half of a signal graph: conditions and actions joined into chains.

A condition fires inside the simulation at the instant its fact happens --
an edge, a value read -- and every action linked to it runs at that same
simulated time: a message on a bus, a pin set or pressed, a marker, a hold.
A test builds them as it builds the rest of the graph::

    graph = (
        SignalGraph()
        .when("falls", Edge(BUTTON, Polarity.FALL), group="echo")
        .mark("noted", "button fell", after="falls", group="echo")
        .group("echo", "Echo")
    )

Whether a chain holds together -- an action nothing fires, a pin that is an
output -- is the server's to say; it keeps the rest running and reports the
problem at its place (`Simulation.chains`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from looper.domain.model.chain_scenarios import (
    Fault,
    RaiseInterrupt,
    ResetFirmware,
    Sequence,
    SwitchSignal,
)
from looper.domain.model.triggers import Polarity, TriggerCondition


class PinDo(IntEnum):
    """What a Set pin does."""

    HIGH = 0
    LOW = 1
    PRESS = 2


@dataclass(frozen=True)
class SetPin:
    """Set an input high or low, or press it for a time at its active level."""

    pin_id: int
    do: PinDo = PinDo.PRESS
    press_us: int = 50_000


@dataclass(frozen=True)
class Field:
    """One field of a message built when it goes out (looper Pro), placed as a DBC says.

    Its value is `constant`, unless it reads the graph's node `signal` --
    raw = round((value - offset) / scale) -- counts (``count``: 0, 1, 2 ...
    one per message), or quotes the request a reply answers from
    `request_bit`.

    Attributes:
        name: What the field is called.
        start_bit: Where it begins, as a DBC numbers bits.
        length: Its width in bits.
        big_endian: Motorola order; otherwise Intel.
    """

    name: str
    start_bit: int = 0
    length: int = 8
    constant: int = 0
    signal: str = ""
    count: bool = False
    request_bit: int | None = None
    big_endian: bool = False
    is_signed: bool = False
    scale: float = 1.0
    offset: float = 0.0


@dataclass(frozen=True)
class BusSend:
    """Send fixed bytes on a CAN or UART bus; on UART a text, when there are no bytes.

    With `fields` (looper Pro) the message is `length` bytes built from them.
    """

    bus_id: int
    address: int = 0
    payload: bytes = b""
    extended: bool = False
    text: str = ""
    fields: tuple[Field, ...] = ()
    length: int = 0


@dataclass(frozen=True)
class BusReply:
    """Answer the received message, at once or after `answer_after_us` (looper Pro)."""

    bus_id: int
    address: int = 0
    payload: bytes = b""
    extended: bool = False
    answer_after_us: int = 0
    fields: tuple[Field, ...] = ()
    length: int = 0


@dataclass(frozen=True)
class Threshold:
    """Fires when the graph's node `signal` goes beyond `level`; holds while it is.

    It is armed again once the signal is back by `hysteresis`; `check_us` is
    how often it is looked at, 0 the server's choice.
    """

    signal: str
    level: float = 0.0
    hysteresis: float = 0.0
    direction: Polarity = Polarity.RISE
    check_us: int = 0


class WhileWaiting(IntEnum):
    """What a delay does with an event that comes while one waits."""

    QUEUED = 0
    RESTART = 1
    DROPPED = 2


@dataclass(frozen=True)
class Delay:
    """Pass each event on after `delay_us`."""

    delay_us: int = 10_000
    while_waiting: WhileWaiting = WhileWaiting.QUEUED


@dataclass(frozen=True)
class Counter:
    """Pass every n-th event on, or with `only_nth` only the n-th."""

    n: int = 3
    only_nth: bool = False


@dataclass(frozen=True)
class Logic:
    """A logic block without settings: ``once``, ``and``, ``or`` or ``gate``."""

    kind: str


@dataclass(frozen=True)
class Mark:
    """Put a marker with a text on Logic's ruler."""

    text: str


@dataclass(frozen=True)
class Hold:
    """Hold the simulation, this long after the event -- as a single trigger does."""

    after_us: int = 0


ChainAction = (
    SetPin
    | BusSend
    | BusReply
    | Mark
    | Hold
    | SwitchSignal
    | Fault
    | RaiseInterrupt
    | ResetFirmware
)
ChainLogic = Delay | Counter | Logic | Sequence
BlockSettings = TriggerCondition | Threshold | ChainLogic | ChainAction


@dataclass(frozen=True)
class EventBlock:
    """One condition or action of the graph.

    Attributes:
        key: What the test calls it; unique within the graph.
        kind: The block's kind by the contract's name, such as ``pin_edge``.
        settings: What it watches for or does.
        group: The group it belongs to; empty for none.
        min_gap_us: A condition: the least time between two fires.
    """

    key: str
    kind: str
    settings: BlockSettings
    group: str = ""
    min_gap_us: int = 0


@dataclass(frozen=True)
class EventLink:
    """An event passed from one block's output to another block's input."""

    from_node: str
    to_node: str
    from_port: int = 0
    to_port: int = 0


@dataclass(frozen=True)
class ChainGroup:
    """A named chain, and whether it runs."""

    key: str
    name: str
    enabled: bool = True


@dataclass(frozen=True)
class ChainBlockState:
    """How one block of a chain is doing, in the server's words.

    Attributes:
        key: The block's key; ``logic:<trigger_id>:condition`` for a Logic trigger's.
        group: Its group's key.
        installed: Whether it runs: not switched off, stopped by a problem, or needing Pro.
        fires: How often it fired or acted.
        last_fired_at_us: When it last did.
        state_text: Its chip, as Logic words it: ``✶ fired 3× · last 1.500000 s``.
        summary_text: What it watches for or does: ``BUTTON falls``.
        problem: Why it does not run; empty when it does.
    """

    key: str
    group: str
    installed: bool
    fires: int
    last_fired_at_us: int
    state_text: str
    summary_text: str
    problem: str
