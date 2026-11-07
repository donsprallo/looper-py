"""The scenario half of a chain: sequences, switched signals, faults, interrupts and resets.

A Sequence (looper Pro) goes through its steps one after the other: *do*
passes an event on from the step's own output, *wait* lets time pass,
*wait for* listens at the step's own input for an event and fails at its
limit, *expect none* fails when an event comes within its span. Its ports
are ``start`` (input 0), ``done`` and ``failed`` (outputs 0 and 1); each
*do* adds an output from 2, each *wait for* and *expect none* an input from
1, in step order (`step_port`)::

    graph = (
        SignalGraph()
        .when("go", Start(), group="boost")
        .sequence("test", Sequence((Step(StepKind.DO, "press"),
                                    Step(StepKind.WAIT_FOR, "lit", 200_000))), group="boost")
        .link("go", "test")
    )

Switch signal is free; Inject fault, like the Sequence, is looper Pro.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class StepKind(IntEnum):
    """What one step of a Sequence does; the contract's numbers."""

    DO = 0
    WAIT = 1
    WAIT_FOR = 2
    EXPECT_NONE = 3

    @property
    def listens(self) -> bool:
        """Whether the step has an input of its own: *wait for* and *expect none*."""
        return self in (StepKind.WAIT_FOR, StepKind.EXPECT_NONE)


@dataclass(frozen=True)
class Step:
    """One step: its kind, the name of its port, and its time.

    ``duration_us`` is the wait of a *wait*, the limit of a *wait for* (0:
    none) and the span of an *expect none*.
    """

    kind: StepKind
    label: str = ""
    duration_us: int = 0


@dataclass(frozen=True)
class Sequence:
    """Steps in order (looper Pro); a start while it runs starts it again only if asked."""

    steps: tuple[Step, ...]
    restart_on_start: bool = False


#: The ports a Sequence always has.
SEQUENCE_START, SEQUENCE_DONE, SEQUENCE_FAILED = 0, 0, 1


def step_port(sequence: Sequence, step_index: int) -> int:
    """The port of one step: an input from 1 for a listening step, otherwise an output from 2.

    Raises:
        IndexError: If the sequence has no such step.
    """
    kind = sequence.steps[step_index].kind
    before = sequence.steps[:step_index]
    if kind.listens:
        return 1 + sum(1 for step in before if step.kind.listens)
    if kind is not StepKind.DO:
        raise IndexError(f"Step {step_index + 1} is a wait and has no port")
    return 2 + sum(1 for step in before if step.kind is StepKind.DO)


class SignalDo(IntEnum):
    """What a Switch signal does to its node or channel; the contract's numbers."""

    START = 0
    STOP = 1
    STEP = 2
    RAMP = 3
    SET = 4
    HOLD_AT = 5


@dataclass(frozen=True)
class SwitchSignal:
    """Start, stop, step or ramp a generator, set a value node, or hold an input channel.

    ``node`` names a generator or value node of the graph; ``channel_id`` an
    analog input for *hold at*. ``over_us`` is a ramp's time.
    """

    node: str = ""
    channel_id: int = 0
    do: SignalDo = SignalDo.SET
    to: float = 0.0
    over_us: int = 1_000_000


class FaultKind(IntEnum):
    """A fault a chain injects; the contract's numbers."""

    STICK = 0
    NOISE_ON = 1
    NOISE_OFF = 2
    DROP = 3
    ERROR_FRAME = 4
    FLIP = 5
    POWER_CUT = 6


@dataclass(frozen=True)
class Fault:
    """A sensor that sticks or is noisy, CAN messages dropped or flipped, a power cut (Pro).

    ``for_us`` 0 lasts until the chain is switched off; for a power cut it is
    the time the board stays off. ``next`` is how many matching messages a
    drop or a flip takes.
    """

    kind: FaultKind
    channel_id: int = 0
    for_us: int = 0
    amplitude: float = 0.0
    bus_id: int = 0
    address: int = 0
    address_mask: int = 0
    next: int = 1  # the contract's name, which the pytest export writes
    byte_index: int = 0
    bit: int = 0


@dataclass(frozen=True)
class RaiseInterrupt:
    """Make an interrupt source pending, as its peripheral would."""

    source_id: int


@dataclass(frozen=True)
class ResetFirmware:
    """Reset the firmware: 4 as its reset pin would, 1 a power-on, 5 a brown-out."""

    cause: int = 4
