"""A graph of signals that drives the simulation's analog inputs and input pins.

Where `Signal` puts one generated waveform on one input, a graph combines
them: generators -- their frequency or amplitude fed by another node --, the
values of channels, pins and watched variables, the operations, comparators,
selects, sample and hold nodes, and models -- a motor, a filter -- that the
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
from looper.domain.model.signal_labels import LabelBuilding, SignalLabel
from looper.domain.model.signal_limits import LimitBuilding, LimitSpec
from looper.domain.model.signal_models import ModelParameter, SignalModel
from looper.domain.model.signal_operations import OperationBuilding
from looper.domain.model.signal_parts import (
    LINKABLE_FIELDS,
    OPERATIONS,
    CompareSettings,
    InputSpec,
    LimitSettings,
    NodeOutput,
    SampleMode,
    SampleSettings,
    SignalNode,
    SignalNodeKind,
    SignalPinTarget,
    SignalProbe,
    SignalTarget,
    SlewSettings,
    outputs_of,
)

__all__ = [
    "OPERATIONS",
    "CompareSettings",
    "InputSpec",
    "LimitSettings",
    "LimitSpec",
    "ModelParameter",
    "NodeOutput",
    "SampleMode",
    "SampleSettings",
    "SignalGraph",
    "SignalLabel",
    "SignalModel",
    "SignalNode",
    "SignalNodeKind",
    "SignalPinTarget",
    "SignalProbe",
    "SignalTarget",
    "SlewSettings",
]


@dataclass(frozen=True)
class SignalGraph(OperationBuilding, LimitBuilding, LabelBuilding, ChainBuilding):
    """The nodes, what they drive and the probes on them, its labels, groups and chains.

    Each method returns a new graph with one more part, so that a graph is
    written as one chain of calls and a half-built one can be reused. The
    operations are `signal_operations`, limits and slew rates
    `signal_limits`, the labels `signal_labels`; the
    event blocks, links and groups are the graph's chains (`chain_blocks`).
    A group holds signal blocks too: every node step takes ``group=``.
    """

    nodes: tuple[SignalNode, ...] = ()
    targets: tuple[SignalTarget, ...] = ()
    probes: tuple[SignalProbe, ...] = ()
    event_blocks: tuple[EventBlock, ...] = ()
    event_links: tuple[EventLink, ...] = ()
    groups: tuple[ChainGroup, ...] = ()
    pin_targets: tuple[SignalPinTarget, ...] = ()
    labels: tuple[SignalLabel, ...] = ()

    def generator(
        self,
        key: str,
        signal: Signal,
        offset: InputSpec | None = None,
        amplitude: InputSpec | None = None,
        frequency: InputSpec | None = None,
        duty: InputSpec | None = None,
        group: str = "",
    ) -> SignalGraph:
        """Add a node that produces a generated waveform, some of its fields from other nodes.

        A field named here takes its value from that node instead of from
        `signal`: ``frequency="ramp"`` is the ramp in Hz, integrated into the
        phase so that the wave never jumps (FM); ``amplitude`` is AM. Which
        fields a waveform lets be linked is the server's to say; phase never.
        """
        named = {"offset": offset, "amplitude": amplitude, "frequency": frequency, "duty": duty}
        links = {LINKABLE_FIELDS[word]: read for word, read in named.items() if read is not None}
        node = SignalNode(
            key,
            SignalNodeKind.GENERATOR,
            signal=signal,
            inputs=outputs_of(links.values()),
            linked_fields=tuple(links),
            group=group,
        )
        return self._with(node)

    def channel(self, key: str, channel_id: int, group: str = "") -> SignalGraph:
        """Add a node that reads an analog channel -- an output closes a loop."""
        return self._with(SignalNode(key, SignalNodeKind.CHANNEL, source=channel_id, group=group))

    def pin(self, key: str, pin_id: int, hold_pulses: bool = False, group: str = "") -> SignalGraph:
        """Add a node that reads a pin as zero or one.

        With `hold_pulses`, a model reads it as 1 at its step when the pin was
        high at any instant since its step before, so that a gate pulse
        shorter than the step still reaches it; a comparator, an input pin
        or a probe read the level as it is.
        """
        node = SignalNode(
            key, SignalNodeKind.PIN, source=pin_id, hold_pulses=hold_pulses, group=group
        )
        return self._with(node)

    def watch(self, key: str, channel_id: int, group: str = "") -> SignalGraph:
        """Add a node that reads a watched variable, by its watch channel."""
        return self._with(SignalNode(key, SignalNodeKind.WATCH, source=channel_id, group=group))

    def value(self, key: str, value: float, group: str = "") -> SignalGraph:
        """Add a node that gives a value a test sets, to an input or a model's parameter."""
        return self._with(SignalNode(key, SignalNodeKind.VALUE, value=value, group=group))

    def model(
        self,
        key: str,
        name: str,
        inputs: Iterable[InputSpec] = (),
        parameters: Mapping[str, float] | None = None,
        interpreted: bool = False,
        parameter_sources: Mapping[str, str] | None = None,
        group: str = "",
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
            group=group,
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
