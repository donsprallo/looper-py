"""The applied signal graph as the simulation reports it now.

Where `SignalGraph` is what a test asks for, this is what it got: the trace
channel each probe records on, the level each input pin is held at and how
exact its edges are, and what each comparator, linked generator, select,
sample and hold block, limit and slew rate shows. Every text is
the server's; a test compares with it or prints it.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.model.graph_liveness import (
    BlockState,
    GraphCapacity,
    GraphValueState,
    LabelState,
)


@dataclass(frozen=True)
class GraphProbe:
    """One probe of the applied graph, and the channel its samples arrive on.

    Attributes:
        name: The name the graph gave it.
        channel_id: The trace channel it records on; an expectation on a
            channel takes it like any other, ``check.channel(probe.channel_id, probe.name)``.
        node: The key of the node it records.
        output: Which of the node's outputs.
        is_live: False while the node it records is not live: a gap in its samples.
    """

    name: str
    channel_id: int
    node: str = ""
    output: int = 0
    is_live: bool = True


@dataclass(frozen=True)
class PinTargetState:
    """One input pin the applied graph drives, as it is now.

    Attributes:
        pin_id: The pin driven.
        pin_name: What the firmware calls it.
        node: The key of the node that drives it.
        output: Which of the node's outputs.
        high: The level the graph holds the pin at.
        value_text: That level in words: ``high`` or ``low``.
        edges: The edges the graph gave the pin since it was applied.
        fault_text: Why the graph does not drive the pin now -- the firmware
            made it an output, or it chatters; empty while it drives it.
        resolution_text: How exact its edges are, such as ``exact to 1 µs``
            or ``at model steps of 100 µs``.
        check_text: How often the graph looks for an edge, as a sentence.
        level_text: How a number is read as a level, with the pin's polarity.
    """

    pin_id: int
    pin_name: str
    node: str
    output: int = 0
    high: bool = False
    value_text: str = ""
    edges: int = 0
    fault_text: str = ""
    resolution_text: str = ""
    check_text: str = ""
    level_text: str = ""


@dataclass(frozen=True)
class GraphNodeState:
    """One node of the applied graph whose block shows more than its symbol.

    A comparator, a generator with a linked field (or one the runtime
    stopped), a select, a sample and hold node, a limit or a slew rate.

    Attributes:
        node: The key the graph gave it.
        summary_text: Its settings in a line, such as ``rises above 0 · hysteresis 0.1``,
            ``sine · FM``, ``on rising trigger``, ``limit 0 … 3.3 V`` or
            ``slew ↑2 V/ms ↓1 V/ms``.
        value_text: ``high`` or ``low`` for a comparator that drives a pin,
            what a select passes, a sample and hold node holds or a limit or
            a slew rate gives (``3.21``); empty where the simulation does not
            report its value.
        hover_lines: Further facts, one a line: ``when 1 passes``,
            ``holds 3.21, sampled at 1.250000 s``.
        passing_port: A select: the input that passes now, ``when 1`` or
            ``when 0``; empty for every other node.
        value: A select, a sample and hold node, a limit or a slew rate:
            what it gives now; None for every other node.
        samples: A sample and hold node: how many samples it took since the
            graph was applied.
        sampled_us: The microsecond of its last sample; 0 before the first.
        fault_text: Why it does not do what it is drawn to, as the runtime
            finds it now: ``The low limit 2 is above the high limit 1: it
            gives the low limit.``; empty while it does.
    """

    node: str
    summary_text: str = ""
    value_text: str = ""
    hover_lines: tuple[str, ...] = ()
    passing_port: str = ""
    value: float | None = None
    samples: int = 0
    sampled_us: int = 0
    fault_text: str = ""


@dataclass(frozen=True)
class SignalGraphState:
    """What the applied graph records and drives now.

    Attributes:
        probes: Its probes, with their trace channels.
        pin_targets: The input pins it drives, in the order the graph named them.
        nodes: Its comparators, linked generators, selects, sample and
            hold nodes, limits and slew rates; Abs, Min and Max show nothing
            beyond their symbol.
        node_states: Every block that does not run now, with why.
        labels: Every label, as it stands now.
        capacity: How full the runtime's graph is.
        values: Its value nodes, with what each gives now.
        liveness_fault: Where the server's reckoning of what runs differs
            from the runtime's -- an internal fault; empty while they agree.
    """

    probes: tuple[GraphProbe, ...] = ()
    pin_targets: tuple[PinTargetState, ...] = ()
    nodes: tuple[GraphNodeState, ...] = ()
    node_states: tuple[BlockState, ...] = ()
    labels: tuple[LabelState, ...] = ()
    capacity: GraphCapacity = GraphCapacity()
    values: tuple[GraphValueState, ...] = ()
    liveness_fault: str = ""

    def pin_target(self, pin_id: int) -> PinTargetState:
        """The pin target that drives a pin.

        Raises:
            KeyError: If the graph drives no such pin.
        """
        for target in self.pin_targets:
            if target.pin_id == pin_id:
                return target
        raise KeyError(f"the applied graph drives no pin {pin_id}")

    def node(self, key: str) -> GraphNodeState:
        """The reported node of that key, as its block shows it.

        Raises:
            KeyError: If the graph reports no node of that key.
        """
        for one in self.nodes:
            if one.node == key:
                return one
        raise KeyError(f"the applied graph reports no node {key!r}")

    def node_state(self, key: str) -> BlockState:
        """Whether the block of that key runs; one the server does not list runs."""
        for one in self.node_states:
            if one.node == key:
                return one
        return BlockState(key)

    def label(self, name: str) -> LabelState:
        """The label of that name, as it stands now.

        Raises:
            KeyError: If the applied graph has no such label.
        """
        for one in self.labels:
            if one.name == name:
                return one
        raise KeyError(f"the applied graph has no label {name!r}")

    def value(self, key: str) -> GraphValueState:
        """The value node of that key, with what it gives now.

        Raises:
            KeyError: If the applied graph has no such value node.
        """
        for one in self.values:
            if one.node == key:
                return one
        raise KeyError(f"the applied graph has no value node {key!r}")
