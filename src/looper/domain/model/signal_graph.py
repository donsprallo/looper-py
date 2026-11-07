"""A graph of signals that drives the simulation's analog inputs.

Where `Signal` puts one generated waveform on one input, a graph combines
them: generators, the values of channels, pins and watched variables, the
four operations, and models -- a motor, a filter -- that the simulation
steps on its own clock. A model fed from an output channel and driving an
input channel closes the loop around the firmware, which is how a test
puts a plant in front of a controller.

The graph is a value built step by step::

    graph = (
        SignalGraph()
        .channel("voltage", motor_voltage.channel_id)
        .model("motor", "DcMotor", inputs=["voltage"], parameters={"supply": 24.0})
        .drive(motor_speed.channel_id, "motor", output=0)
    )

Applying it replaces whatever graph the simulation ran before, for every
client. Whether it holds together -- a key read before it is made, an
input that is an output -- is the simulation's to say.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from enum import StrEnum

from looper.domain.model.chain_blocks import ChainGroup, EventBlock, EventLink
from looper.domain.model.chain_building import ChainBuilding
from looper.domain.model.requests import Signal


class SignalNodeKind(StrEnum):
    """What one node of the graph does, by the name the contract gives it."""

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


#: The kinds that combine two inputs into one value.
OPERATIONS = frozenset(
    {SignalNodeKind.ADD, SignalNodeKind.SUBTRACT, SignalNodeKind.MULTIPLY, SignalNodeKind.DIVIDE}
)


@dataclass(frozen=True)
class NodeOutput:
    """One output of a node, as another node reads it.

    Attributes:
        node: The key of the node read.
        output: Which of its outputs, counted from zero; only a model has more than one.
    """

    node: str
    output: int = 0


@dataclass(frozen=True)
class SignalNode:
    """One node of the graph.

    Attributes:
        key: What the test calls it; unique within the graph.
        kind: What it does.
        signal: What a generator produces.
        source: The channel, pin or watch channel a source node reads.
        inputs: What the node reads, in order: the two operands of an
            operation, the inputs of a model.
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
class SignalProbe:
    """A node output recorded as a trace of its own, without driving anything.

    Attributes:
        name: What the test calls it; unique within the graph. The trace
            channel follows the name.
        node: The key of the node watched.
        output: Which of the node's outputs.
    """

    name: str
    node: str
    output: int = 0


#: What a test may name an input with: a node's key for its first output,
#: or a `NodeOutput` for any other.
InputSpec = str | NodeOutput


@dataclass(frozen=True)
class SignalGraph(ChainBuilding):
    """The nodes, the inputs they drive and the probes on them, and its chains.

    Each method returns a new graph with one more part, so that a graph is
    written as one chain of calls and a half-built one can be reused. The
    event blocks, links and groups are the graph's chains (`chain_blocks`).
    """

    nodes: tuple[SignalNode, ...] = ()
    targets: tuple[SignalTarget, ...] = ()
    probes: tuple[SignalProbe, ...] = ()
    event_blocks: tuple[EventBlock, ...] = ()
    event_links: tuple[EventLink, ...] = ()
    groups: tuple[ChainGroup, ...] = ()

    def generator(self, key: str, signal: Signal) -> SignalGraph:
        """Add a node that produces a generated waveform."""
        return self._with(SignalNode(key, SignalNodeKind.GENERATOR, signal=signal))

    def channel(self, key: str, channel_id: int) -> SignalGraph:
        """Add a node that reads an analog channel -- an output closes a loop."""
        return self._with(SignalNode(key, SignalNodeKind.CHANNEL, source=channel_id))

    def pin(self, key: str, pin_id: int) -> SignalGraph:
        """Add a node that reads a pin as zero or one."""
        return self._with(SignalNode(key, SignalNodeKind.PIN, source=pin_id))

    def watch(self, key: str, channel_id: int) -> SignalGraph:
        """Add a node that reads a watched variable, by its watch channel."""
        return self._with(SignalNode(key, SignalNodeKind.WATCH, source=channel_id))

    def value(self, key: str, value: float) -> SignalGraph:
        """Add a node that gives a value a test sets, to an input or a model's parameter."""
        return self._with(SignalNode(key, SignalNodeKind.VALUE, value=value))

    def operation(
        self, key: str, kind: SignalNodeKind, first: InputSpec, second: InputSpec
    ) -> SignalGraph:
        """Add a node that adds, subtracts, multiplies or divides two others.

        Raises:
            ValueError: If `kind` is not one of the four operations.
        """
        if kind not in OPERATIONS:
            raise ValueError(f"{kind} is not an operation; use one of {sorted(OPERATIONS)}")
        return self._with(SignalNode(key, kind, inputs=_outputs_of((first, second))))

    def model(
        self,
        key: str,
        name: str,
        inputs: Iterable[InputSpec] = (),
        parameters: Mapping[str, float] | None = None,
        interpreted: bool = False,
        parameter_sources: Mapping[str, str] | None = None,
    ) -> SignalGraph:
        """Add a model the simulation steps, fed from `inputs` in the model's order.

        `parameter_sources` gives parameters from value nodes, by parameter
        name, so that `Simulation.set_graph_value` changes them later.
        """
        node = SignalNode(
            key,
            SignalNodeKind.MODEL,
            inputs=_outputs_of(inputs),
            model=name,
            parameters=tuple(sorted((parameters or {}).items())),
            interpreted=interpreted,
            parameter_sources=tuple(sorted((parameter_sources or {}).items())),
        )
        return self._with(node)

    def drive(self, channel_id: int, node: str, output: int = 0) -> SignalGraph:
        """Drive an analog input from one output of a node."""
        return replace(self, targets=(*self.targets, SignalTarget(channel_id, node, output)))

    def probe(self, name: str, node: str, output: int = 0) -> SignalGraph:
        """Record one output of a node as a trace of its own."""
        return replace(self, probes=(*self.probes, SignalProbe(name, node, output)))

    def _with(self, node: SignalNode) -> SignalGraph:
        return replace(self, nodes=(*self.nodes, node))


def _outputs_of(inputs: Iterable[InputSpec]) -> tuple[NodeOutput, ...]:
    """The inputs as outputs of nodes, a bare key standing for the first output."""
    return tuple(NodeOutput(one) if isinstance(one, str) else one for one in inputs)


@dataclass(frozen=True)
class ModelParameter:
    """One parameter of a model, with the value it has when none is given.

    Attributes:
        name: What the model calls it.
        default_value: What it is when a graph leaves it out.
        unit: What it is measured in; empty for nothing.
        lowest: The lowest value the model accepts; None where it says nothing.
        highest: The highest value the model accepts; None where it says nothing.
    """

    name: str
    default_value: float
    unit: str = ""
    lowest: float | None = None
    highest: float | None = None


@dataclass(frozen=True)
class SignalModel:
    """A model the project offers the signal graph.

    Attributes:
        name: What a model node names it with.
        description: What it is, in the model's own words.
        inputs: What its inputs are called, in order.
        outputs: What its outputs are called, in order.
        parameters: Its parameters and their defaults.
        kind: ``linear`` or ``state``.
        origin: ``project`` or ``built_in``.
        problem: Why it cannot be used; empty when it can.
    """

    name: str
    description: str = ""
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[ModelParameter, ...] = ()
    kind: str = ""
    origin: str = ""
    problem: str = ""

    def output(self, name: str) -> int:
        """The position of an output, for `SignalGraph.drive`.

        Raises:
            ValueError: If the model has no output of that name.
        """
        if name not in self.outputs:
            raise ValueError(f"model {self.name} has no output {name!r}; it has {self.outputs}")
        return self.outputs.index(name)
