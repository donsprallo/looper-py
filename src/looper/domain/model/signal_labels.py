"""Labels and switched-off blocks of a signal graph: its builder steps and the label itself.

A label is an internal signal with a name: ``set_signal`` blocks write it,
``read_signal`` blocks read it anywhere in the graph, across groups. Its
readers get the writer that is on and, while none is, its fallback. That is
how a test swaps variants -- a plant and an ideal plant, each in a group of
its own, both writing ``SPEED`` -- without a moment in which both or neither
give the value::

    graph = (
        SignalGraph()
        .group("plant", "Plant")
        .group("ideal", "Ideal plant", enabled=False)
        .label("SPEED", fallback=0.0)
        .value("measured", 1500.0, group="plant")
        .set_signal("plant_out", "SPEED", source="measured", group="plant")
        .value("nominal", 1450.0, group="ideal")
        .set_signal("ideal_out", "SPEED", source="nominal", group="ideal")
        .read_signal("speed", "SPEED")
    )

Whether a name is one, a label read upstream of its writer, or two writers
on at once is the server's to say.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Self

from looper.domain.model.signal_operations import NodeBuilding
from looper.domain.model.signal_parts import InputSpec, SignalNode, SignalNodeKind, outputs_of


@dataclass(frozen=True)
class SignalLabel:
    """A label of the graph and what its readers get while no writer is on.

    A label a block names that the graph does not list has no fallback:
    while no writer is on, its readers are left out.

    Attributes:
        name: Letters, digits and ``_``, from a letter, at most 32 characters.
        fallback: What its readers get while no writer is on; None for none.
    """

    name: str
    fallback: float | None = None


class LabelBuilding(NodeBuilding):
    """Builder steps for labels, their writers and readers, and a block's own switch."""

    labels: tuple[SignalLabel, ...]

    def label(self, name: str, fallback: float | None = None) -> Self:
        """List a label with the fallback its readers get while no writer is on."""
        labels = (*self.labels, SignalLabel(name, fallback))
        return replace(self, labels=labels)  # type: ignore[type-var]

    def set_signal(self, key: str, label: str, source: InputSpec, group: str = "") -> Self:
        """Add a block that writes `source` to a label while it is on.

        Two writers of one label may be in the graph while only one is on;
        with both on, the first in the graph's order gives the value.
        """
        node = SignalNode(
            key, SignalNodeKind.SET_SIGNAL, inputs=outputs_of((source,)), label=label, group=group
        )
        return self._with(node)

    def read_signal(self, key: str, label: str, group: str = "") -> Self:
        """Add a block that gives what a label gives: its writer that is on, else its fallback."""
        return self._with(SignalNode(key, SignalNodeKind.READ_SIGNAL, label=label, group=group))

    def switched_off(self, key: str) -> Self:
        """Save the block `key` as switched off on its own: left out, with what it feeds.

        `Simulation.switch_block` switches it on without applying the graph again.

        Raises:
            KeyError: If the graph has no signal block `key` yet.
        """
        return self._changed(key, switched_off=True)

    def title(self, key: str, text: str) -> Self:
        """Give the block `key` a title the server's sentences name it by (``Sensor A``).

        Raises:
            KeyError: If the graph has no signal block `key` yet.
        """
        return self._changed(key, title=text)

    def _changed(self, key: str, **changes: object) -> Self:
        keys = [node.key for node in self.nodes]
        if key not in keys:
            raise KeyError(f"the graph has no signal block {key!r} yet; add it first")
        nodes = tuple(replace(node, **changes) if node.key == key else node for node in self.nodes)  # type: ignore[arg-type]
        return replace(self, nodes=nodes)  # type: ignore[type-var]
