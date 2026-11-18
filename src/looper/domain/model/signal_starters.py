"""The starters a signal graph can begin with, as the server lists them.

A starter is a small graph defined in looper-models beside its models --
*Mains with zero-cross*, *Frequency sweep*, *Phase-angle dimmer* -- that the
window pastes with its pins left to choose. Whether this firmware has what
one needs, and every sentence about it, is the server's.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class StarterNeeds:
    """What a starter needs to be inserted.

    Attributes:
        input_pins: Input pins the firmware reads, which the graph drives.
        output_pins: Output pins the firmware drives, which the graph reads.
        analog_inputs: Analog inputs the firmware reads, which the graph drives.
        models: Models, by name as `Simulation.models` lists them.
    """

    input_pins: int = 0
    output_pins: int = 0
    analog_inputs: int = 0
    models: tuple[str, ...] = ()


@dataclass(frozen=True)
class Starter:
    """One starter.

    Attributes:
        name: How it is told apart: ``mains_zero_cross``.
        display_name: ``Mains with zero-cross``.
        description: The library card's sentence.
        search_words: Words a search finds it by besides its name.
        graph_text: The blocks and links as the window's clipboard holds
            them, a JSON document marked ``looper_graph``.
        needs: What it needs to be inserted.
        needs_text: That as a sentence: ``an input pin, an output pin and the
            models Triac and HalfCycleRms``.
        is_available: Whether this firmware, runtime and models have it.
        unavailable_text: Why not, its name first; empty when it is.
    """

    name: str
    display_name: str = ""
    description: str = ""
    search_words: tuple[str, ...] = ()
    graph_text: str = ""
    needs: StarterNeeds = StarterNeeds()
    needs_text: str = ""
    is_available: bool = False
    unavailable_text: str = ""


@dataclass(frozen=True)
class Starters:
    """Every starter, in the library's order.

    Attributes:
        starters: The starters; empty when the model library did not start.
        unavailable_reason: Why there are none; empty when there are.
    """

    starters: tuple[Starter, ...] = ()
    unavailable_reason: str = ""

    def __iter__(self) -> Iterator[Starter]:
        return iter(self.starters)

    def __len__(self) -> int:
        return len(self.starters)

    @property
    def names(self) -> tuple[str, ...]:
        """The starters' names, in order."""
        return tuple(starter.name for starter in self.starters)

    def named(self, name: str) -> Starter:
        """The starter of that name.

        Raises:
            KeyError: If there is none; the message lists the names there are.
        """
        for starter in self.starters:
            if starter.name == name:
                return starter
        known = ", ".join(self.names) or self.unavailable_reason or "none at all"
        raise KeyError(f"no starter named {name!r}; there are {known}")
