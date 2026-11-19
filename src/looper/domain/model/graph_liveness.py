"""What of the applied signal graph runs now: its blocks, its labels, its room and its values.

The server works it out under the runtime's switches and gives every text;
a test compares with it or prints it. A block that is not listed runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BlockLiveness(StrEnum):
    """Whether a block of the applied graph runs, and if not, why."""

    #: It runs.
    LIVE = "live"
    #: Its own switch or its group is off.
    SWITCHED_OFF = "switched_off"
    #: It is on, but something it reads is not live.
    LEFT_OUT = "left_out"


@dataclass(frozen=True)
class BlockState:
    """One block of the applied graph, and whether it runs.

    Attributes:
        node: The key the graph gave it.
        state: Whether it runs, and if not, why.
        state_text: Why not, in the server's words: ``Off – Sensor A is off.``,
            ``Off – fed by Sensor A, which is off.``; empty while it runs.
    """

    node: str
    state: BlockLiveness = BlockLiveness.LIVE
    state_text: str = ""

    @property
    def is_live(self) -> bool:
        """Whether the block runs."""
        return self.state is BlockLiveness.LIVE


@dataclass(frozen=True)
class LabelState:
    """One label of the applied graph, as it stands now.

    Attributes:
        name: The label's name.
        writer_node: The set signal block that gives it now; empty while none does.
        on_fallback: No writer is on, and its readers get its fallback.
        is_live: Its readers get a value: a writer is on, or it has a fallback.
        value: What its readers read now; None while it is not live.
        unit: What the value is measured in, where the server knows.
        writer_nodes: Every block that writes it, in the graph's order.
        reader_nodes: Every block that reads it.
        state_text: All of it in a line: ``now 2.31 · set by Sensor A``, or
            the sentence about two writers on.
        fallback: What its readers get while no writer is on; None for none.
    """

    name: str
    writer_node: str = ""
    on_fallback: bool = False
    is_live: bool = False
    value: float | None = None
    unit: str = ""
    writer_nodes: tuple[str, ...] = ()
    reader_nodes: tuple[str, ...] = ()
    state_text: str = ""
    fallback: float | None = None


@dataclass(frozen=True)
class GraphCapacity:
    """How full the runtime's graph is; switched-off blocks count, as they stay installed.

    Attributes:
        nodes_used: Signal nodes installed, labels' own among them.
        nodes_max: Signal nodes the runtime has room for.
        models_used: Models installed; `models_max` the room.
        linear_used: Linear systems installed; `linear_max` the room.
        probes_used: Probes installed; `probes_max` the room.
        text: All of it in a line, as the server says it:
            ``signal nodes 58 of 128 (12 switched off, 4 for labels) · ...``.
    """

    nodes_used: int = 0
    nodes_max: int = 0
    models_used: int = 0
    models_max: int = 0
    linear_used: int = 0
    linear_max: int = 0
    probes_used: int = 0
    probes_max: int = 0
    text: str = ""


@dataclass(frozen=True)
class GraphValueState:
    """One value node of the applied graph and what it gives now.

    Attributes:
        node: The key the graph gave it.
        value: What it gives now: the last value set, else what the graph said.
        unit: The unit of the first parameter it gives, where there is one.
        feeds_text: What it feeds, as a person reads it: ``DcMotor.inertia``.
        last_writer_text: Who set it last when a chain did:
            ``chain "Boost test" at 2.500000 s``; empty otherwise.
        state_text: Why what it gives reaches nothing now: ``group Plant is
            off: takes effect when it is switched on``; empty otherwise.
    """

    node: str
    value: float = 0.0
    unit: str = ""
    feeds_text: str = ""
    last_writer_text: str = ""
    state_text: str = ""
