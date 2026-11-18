"""The models a project offers the signal graph, as the server lists them.

A model is stepped by the simulation on its own clock: a motor, a filter, a
TRIAC with its load. What a model is called, what it takes and gives, where
a library lists it and the words that find it all come from the server;
nothing here is worked out.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelParameter:
    """One parameter of a model, with the value it has when none is given.

    Attributes:
        name: What the model calls it.
        default_value: What it is when a graph leaves it out.
        unit: What it is measured in; empty for nothing.
        lowest: The lowest value the model accepts; None where it says nothing.
        highest: The highest value the model accepts; None where it says nothing.
        description: What it does, in the model's words; empty where it says nothing.
    """

    name: str
    default_value: float
    unit: str = ""
    lowest: float | None = None
    highest: float | None = None
    description: str = ""


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
        group: The heading a library lists it under, such as ``Power
            switches``; empty for none.
        keywords: Words a search finds it by besides its name, such as ``dimmer``.
    """

    name: str
    description: str = ""
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[ModelParameter, ...] = ()
    kind: str = ""
    origin: str = ""
    problem: str = ""
    group: str = ""
    keywords: tuple[str, ...] = ()

    def output(self, name: str) -> int:
        """The position of an output, for `SignalGraph.drive` and `SignalGraph.drive_pin`.

        Raises:
            ValueError: If the model has no output of that name.
        """
        if name not in self.outputs:
            raise ValueError(f"model {self.name} has no output {name!r}; it has {self.outputs}")
        return self.outputs.index(name)
