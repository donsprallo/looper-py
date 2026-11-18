"""A graph of signals that drives the simulation's analog inputs and input pins.

Where `Signal` puts one generated waveform on one input, a graph combines
them: generators, the values of channels, pins and watched variables, the
operations, comparators, and models -- a motor, a filter -- that the
simulation steps on its own clock. A model fed from an output channel and
driving an input channel closes the loop around the firmware, which is how
a test puts a plant in front of a controller. A comparator driving an input
pin gives the firmware edges, exact to the microsecond where the runtime can
plan them: a zero-cross detector on a mains sine.

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

from looper.domain.model.chain_blocks import ChainGroup, EventBlock, EventLink
from looper.domain.model.chain_building import ChainBuilding
from looper.domain.model.requests import Signal
from looper.domain.model.signal_models import ModelParameter, SignalModel
from looper.domain.model.signal_parts import (
    ONE_INPUT_OPERATIONS,
    OPERATIONS,
    CompareSettings,
    InputSpec,
    NodeOutput,
    SignalNode,
    SignalNodeKind,
    SignalPinTarget,
    SignalProbe,
    SignalTarget,
    outputs_of,
)

__all__ = [
    "OPERATIONS",
    "CompareSettings",
    "InputSpec",
    "ModelParameter",
    "NodeOutput",
    "SignalGraph",
    "SignalModel",
    "SignalNode",
    "SignalNodeKind",
    "SignalPinTarget",
    "SignalProbe",
    "SignalTarget",
]


@dataclass(frozen=True)
class SignalGraph(ChainBuilding):
    """The nodes, what they drive and the probes on them, and its chains.

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
    pin_targets: tuple[SignalPinTarget, ...] = ()

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
        self, key: str, kind: SignalNodeKind, first: InputSpec, second: InputSpec | None = None
    ) -> SignalGraph:
        """Add a node that combines two others, or takes the size of one.

        ``ADD``, ``SUBTRACT``, ``MULTIPLY``, ``DIVIDE``, ``MIN`` and ``MAX``
        read `first` and `second`; ``ABS`` reads `first` alone.

        Raises:
            ValueError: If `kind` is no operation, or the inputs do not fit it.
        """
        if kind in ONE_INPUT_OPERATIONS:
            if second is not None:
                raise ValueError(f"{kind} reads one input; leave out the second")
            return self._with(SignalNode(key, kind, inputs=outputs_of((first,))))
        if kind not in OPERATIONS:
            known = sorted(OPERATIONS | ONE_INPUT_OPERATIONS)
            raise ValueError(f"{kind} is not an operation; use one of {known}")
        if second is None:
            raise ValueError(f"{kind} reads two inputs; name the second")
        return self._with(SignalNode(key, kind, inputs=outputs_of((first, second))))

    def compare(
        self,
        key: str,
        reads: InputSpec,
        level: float = 0.0,
        hysteresis: float = 0.0,
        below: bool = False,
        threshold: InputSpec | None = None,
        check_us: int = 0,
    ) -> SignalGraph:
        """Add a comparator: one while `reads` is above the threshold (or `below` it), else zero.

        It goes back only when the input has gone `hysteresis` past the
        threshold the other way. `threshold` names a node to compare with
        instead of the constant `level`. Its edges are planned to the
        microsecond where the runtime can; where it cannot -- noise or a
        divide upstream -- it is checked every `check_us` (0: the server's
        Auto). A negative hysteresis is the server's to refuse.
        """
        settings = CompareSettings(level, hysteresis, below, threshold is not None, check_us)
        reading = (reads,) if threshold is None else (reads, threshold)
        node = SignalNode(key, SignalNodeKind.COMPARE, inputs=outputs_of(reading), compare=settings)
        return self._with(node)

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
            inputs=outputs_of(inputs),
            model=name,
            parameters=tuple(sorted((parameters or {}).items())),
            interpreted=interpreted,
            parameter_sources=tuple(sorted((parameter_sources or {}).items())),
        )
        return self._with(node)

    def drive(self, channel_id: int, node: str, output: int = 0) -> SignalGraph:
        """Drive an analog input from one output of a node."""
        return replace(self, targets=(*self.targets, SignalTarget(channel_id, node, output)))

    def drive_pin(self, pin_id: int, node: str, output: int = 0) -> SignalGraph:
        """Drive a digital input pin from one output of a node: high from 0.5, low below.

        The edges reach the firmware as a real pin's would, its EXTI
        included. Only an input pin can be driven; the server refuses an
        output with a sentence.
        """
        target = SignalPinTarget(pin_id, node, output)
        return replace(self, pin_targets=(*self.pin_targets, target))

    def probe(self, name: str, node: str, output: int = 0, sample_us: int = 0) -> SignalGraph:
        """Record one output of a node as a trace of its own, every `sample_us`.

        A `sample_us` of 0 lets the server choose: the step of a model
        upstream, else a hundredth of the fastest generator's period; a
        comparator is recorded at its edges. `Simulation.probe` finds the
        trace channel by `name`.
        """
        probe = SignalProbe(name, node, output, sample_us)
        return replace(self, probes=(*self.probes, probe))

    def _with(self, node: SignalNode) -> SignalGraph:
        return replace(self, nodes=(*self.nodes, node))
