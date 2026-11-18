"""The parts a signal graph is made of: its nodes, and what they drive and record.

`SignalGraph` puts them together one call at a time; each part is a plain
value that goes out field for field as the contract's request. Whether
they hold together -- a key read before it is made, an output pin as a
target, a negative hysteresis -- is the simulation's to say.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from looper.domain.model.requests import Signal


class SignalNodeKind(StrEnum):
    """What one node of the graph does, by the name the contract gives it.

    ``COMPARE``, ``ABS``, ``MIN`` and ``MAX`` need a server whose runtime
    plans the graph's edges (capability ``graph_edges``), ``SELECT`` and
    ``SAMPLE_HOLD`` one whose runtime selects and samples (capability
    ``signal_logic``); an older one refuses them with a sentence that says so.
    """

    GENERATOR = "generator"
    CHANNEL = "channel"
    PIN = "pin"
    WATCH = "watch"
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    MODEL = "model"
    VALUE = "value"
    COMPARE = "compare"
    ABS = "abs"
    MIN = "min"
    MAX = "max"
    SELECT = "select"
    SAMPLE_HOLD = "sample_hold"


class SampleMode(StrEnum):
    """When a sample and hold node takes its input, by the contract's word."""

    #: At each rising edge of the trigger.
    RISING = "rising"
    #: At each falling edge of the trigger.
    FALLING = "falling"
    #: It follows its input while the trigger is high and holds it from the falling edge on.
    TRACK = "track"


#: A generator's fields a link may replace, by `SignalGraph.generator`'s
#: keyword, as the contract names them. Which of them a waveform lets be
#: linked is the server's to say.
LINKABLE_FIELDS = {
    "offset": "offset",
    "amplitude": "amplitude",
    "frequency": "frequency_hz",
    "duty": "duty",
}


#: The kinds that combine two inputs into one value.
OPERATIONS = frozenset(
    {
        SignalNodeKind.ADD,
        SignalNodeKind.SUBTRACT,
        SignalNodeKind.MULTIPLY,
        SignalNodeKind.DIVIDE,
        SignalNodeKind.MIN,
        SignalNodeKind.MAX,
    }
)

#: The kinds that make one value out of one input.
ONE_INPUT_OPERATIONS = frozenset({SignalNodeKind.ABS})


@dataclass(frozen=True)
class NodeOutput:
    """One output of a node, as another node reads it.

    Attributes:
        node: The key of the node read.
        output: Which of its outputs, counted from zero; only a model has more than one.
    """

    node: str
    output: int = 0


#: What a test may name an input with: a node's key for its first output,
#: or a `NodeOutput` for any other.
InputSpec = str | NodeOutput


@dataclass(frozen=True)
class CompareSettings:
    """What a comparator compares its input with, by the chain Threshold's rule.

    Above, it goes to one when the input rises above the threshold, and back
    to zero only when it falls below the threshold minus the hysteresis;
    below mirrors it.

    Attributes:
        level: The threshold, in the unit of the input; unused while `linked`.
        hysteresis: How far back past the threshold the input must go
            before the output returns.
        below: One while the input is below the threshold, instead of above.
        linked: The threshold is the comparator's second input, not `level`.
        check_us: Where no edge can be planned ahead -- noise or a divide
            upstream -- how often the input is checked; 0 is the server's Auto.
    """

    level: float = 0.0
    hysteresis: float = 0.0
    below: bool = False
    linked: bool = False
    check_us: int = 0


@dataclass(frozen=True)
class SampleSettings:
    """When a sample and hold node takes its input, and what it gives before.

    A trigger is high from 0.5 up; one high when the graph is installed is
    no edge.

    Attributes:
        mode: At the trigger's rising or falling edge, or tracking while it is high.
        initial: What it gives before its first sample.
    """

    mode: SampleMode = SampleMode.RISING
    initial: float = 0.0


@dataclass(frozen=True)
class SignalNode:
    """One node of the graph.

    Attributes:
        key: What the test calls it; unique within the graph.
        kind: What it does.
        signal: What a generator produces.
        source: The channel, pin or watch channel a source node reads.
        inputs: What the node reads, in order: the operands of an
            operation, the inputs of a model, a comparator's input and its
            linked threshold, a select's three, a sample and hold node's
            input and trigger, the signals of a generator's linked fields.
        model: The model a model node stands for, as `SignalModel.name` names it.
        parameters: The values its parameters are given, by name; one left
            out keeps the model's default.
        interpreted: Step the model in Python even if it could be compiled,
            so that a breakpoint in it is reached.
        value: What a value node gives until `Simulation.set_graph_value`
            changes it.
        parameter_sources: Parameters of a model node another node gives,
            by parameter name: the key of a value node or a constant
            generator. One given here overrides the same name in `parameters`.
        compare: What a comparator compares with.
        linked_fields: A generator's fields that take their value from a
            signal, by the contract's name: ``inputs[i]`` feeds
            ``linked_fields[i]``.
        sample: When a sample and hold node samples.
        hold_pulses: A pin source that a model reads as 1 at its step when
            the pin was high at any instant since the step before, so that a
            pulse shorter than the step is not missed.
    """

    key: str
    kind: SignalNodeKind
    signal: Signal = Signal()
    source: int = 0
    inputs: tuple[NodeOutput, ...] = ()
    model: str = ""
    parameters: tuple[tuple[str, float], ...] = ()
    interpreted: bool = False
    value: float = 0.0
    parameter_sources: tuple[tuple[str, str], ...] = ()
    compare: CompareSettings = CompareSettings()
    linked_fields: tuple[str, ...] = ()
    sample: SampleSettings = SampleSettings()
    hold_pulses: bool = False


@dataclass(frozen=True)
class SignalTarget:
    """An analog input the graph drives.

    Attributes:
        channel_id: The input channel driven.
        node: The key of the node that drives it.
        output: Which of the node's outputs; only a model has more than one.
    """

    channel_id: int
    node: str
    output: int = 0


@dataclass(frozen=True)
class SignalPinTarget:
    """A digital input pin the graph drives: high while the node gives 0.5 or more.

    The graph comes first on such a pin: a drive from a test does nothing
    while the graph drives it, and the pin keeps its last level when the
    graph lets go.

    Attributes:
        pin_id: The input pin driven.
        node: The key of the node that drives it, usually a comparator.
        output: Which of the node's outputs; only a model has more than one.
    """

    pin_id: int
    node: str
    output: int = 0


@dataclass(frozen=True)
class SignalProbe:
    """A node output recorded as a trace of its own, without driving anything.

    Attributes:
        name: What the test calls it; unique within the graph. The trace
            channel follows the name; `Simulation.probe` looks it up.
        node: The key of the node watched.
        output: Which of the node's outputs.
        sample_us: Microseconds between two records, on the probe's own
            clock; 0 is Auto, which the server chooses from what feeds it.
    """

    name: str
    node: str
    output: int = 0
    sample_us: int = 0


def outputs_of(inputs: Iterable[InputSpec]) -> tuple[NodeOutput, ...]:
    """The inputs as outputs of nodes, a bare key standing for the first output."""
    return tuple(NodeOutput(one) if isinstance(one, str) else one for one in inputs)
