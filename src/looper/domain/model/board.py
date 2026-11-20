"""The device as a block diagram, as the server describes it (free).

The MCU with its pins and channels, the buses and the chips on them, the
contract's interrupt sources, DMA channels and PWM outputs: what looper.toml,
component.toml and contract.toml say, joined with what the board code
registered. Each port -- a pin or an analog channel -- says what drives and
what reads it in the applied signal graph. Nothing here is worked out on this
side: every text and every key is the server's, and a key is a name such as
``pin:ZC`` or ``bus:SPI1``, never a position.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class BoardNodeKind(StrEnum):
    """What one part of the board is."""

    MCU = "mcu"
    #: A timer a PWM output runs on.
    PERIPHERAL = "peripheral"
    BUS = "bus"
    DEVICE = "device"
    PIN = "pin"
    CHANNEL = "channel"
    #: An interrupt source of the contract.
    SOURCE = "source"
    DMA = "dma"
    PWM = "pwm"
    #: Another device of the bench on a joined bus, drawn at the end of its rail.
    PEER = "peer"


class BoardEdgeKind(StrEnum):
    """What one wire between two parts carries."""

    #: A device on its bus: a tap, ``CS 1``, ``0x20``, ``port 2``.
    ON_BUS = "on_bus"
    LINE_TO_PIN = "line_to_pin"
    LINE_TO_SOURCE = "line_to_source"
    INPUT_FROM_PIN = "input_from_pin"
    ANALOG_OUT = "analog_out"
    SAMPLES = "samples"
    STREAM = "stream"
    DMA_ON_BUS = "dma_on_bus"
    SOURCE_ON_PIN = "source_on_pin"
    PWM_ON_PIN = "pwm_on_pin"


#: The kinds a port is: what the firmware and the signal graph meet at.
PORT_KINDS = (BoardNodeKind.PIN, BoardNodeKind.CHANNEL)


@dataclass(frozen=True)
class BoardGraphRef:
    """A block or a probe of the applied signal graph that reads a port.

    Attributes:
        text: The server's words for it, ``Model · Triac``, ``Probe "Led"``.
        node_key: The block's key; empty for a probe.
        probe: The probe's name; empty for a block.
    """

    text: str
    node_key: str = ""
    probe: str = ""


@dataclass(frozen=True)
class BoardNode:
    """One part of the board; a pin or a channel is a port.

    Attributes:
        key: ``mcu``, ``bus:SPI1``, ``device:SPI1:0``, ``pin:ZC``, ``channel:POT``.
        parent_key: What it lies on: ``mcu`` for a pin, a timer's key for a PWM output.
        title: ``SPI1``, ``AS8510``, ``ZC``.
        subtitle: ``SPI · 1 Mbit/s``, ``as8510 · CS 0``, ``input · active high``.
        runtime_id: The runtime's bus, pin or channel number; 0 when it has none.
        registered: False for what only a file names; ``unregistered_text`` says why.
        hand_wired: A chip the board code attached by hand; ``hand_wired_text`` says so.
        is_input: A port the firmware reads; False for one it drives.
        graph_can_drive: Whether the signal graph may drive this port;
            ``drive_text`` says why not.
        driven_by_text: What drives the port in the applied graph,
            ``Comparator``; empty while nothing does. ``driven_by_node_key`` is its key.
        read_by: What reads the port, in the graph's order; ``read_by_text``
            says it in one line, ``Model · Triac``, ``2 blocks``.
        reference_text: The port's reference as a row shows it:
            ``◁ Comparator``, ``not driven``, ``▷ 2 blocks``, ``not read``.
        reference_node_key: The block a click on the reference shows.
        endpoint_node_keys: The graph's source blocks that read this port.
        second_driver_text: Why a second driver is not made from here.
        empty_text: What the rail of a bus without a device says instead of
            taps, ``no devices on CAN1``; empty for every other node.
        joined_text: A bus joined on a bench: the rail's caption after its
            name, ``joined with gateway``; empty for every other node.
        join_hint_text: A CAN bus that could be joined, on its empty rail's
            second line; empty for every other node.
    """

    key: str
    kind: BoardNodeKind
    title: str
    parent_key: str = ""
    subtitle: str = ""
    bus_kind: str = ""
    runtime_id: int = 0
    registered: bool = True
    unregistered_text: str = ""
    hand_wired: bool = False
    hand_wired_text: str = ""
    is_input: bool = False
    graph_can_drive: bool = False
    graph_can_read: bool = False
    drive_text: str = ""
    hover_text: str = ""
    driven_by_text: str = ""
    driven_by_node_key: str = ""
    read_by: tuple[BoardGraphRef, ...] = ()
    read_by_text: str = ""
    reference_text: str = ""
    reference_node_key: str = ""
    endpoint_node_keys: tuple[str, ...] = ()
    second_driver_text: str = ""
    empty_text: str = ""
    joined_text: str = ""
    join_hint_text: str = ""

    @property
    def is_port(self) -> bool:
        """Whether it is a pin or an analog channel."""
        return self.kind in PORT_KINDS


@dataclass(frozen=True)
class BoardEdge:
    """One wire between two parts, from `from_key` to `to_key`.

    Attributes:
        text: ``CS 1``, ``0x20``, ``rising``; what the wire is labelled with.
        dashed: A digital line; analog and bus wires are solid.
        hover_text: ``store · spi_flash on SPI1, chip select 1``.
    """

    from_key: str
    to_key: str
    kind: BoardEdgeKind
    text: str = ""
    dashed: bool = False
    hover_text: str = ""


@dataclass(frozen=True)
class BoardNote:
    """What the picture cannot show, in one sentence.

    Attributes:
        node_key: The part it is about; empty for one about the whole board.
    """

    text: str
    node_key: str = ""


@dataclass(frozen=True)
class BoardTap:
    """A device on a bus, where it is reached.

    Attributes:
        device: The chip.
        bus_key: The bus it hangs on, ``bus:SPI1``.
        text: Where on the bus: ``CS 0``, ``0x20``, ``port 0``.
        hover_text: ``AS8510 on SPI1, chip select 0``.
    """

    device: BoardNode
    bus_key: str
    text: str
    hover_text: str = ""


@dataclass(frozen=True)
class BoardBus:
    """One bus of the board with the devices on it.

    Attributes:
        node: The bus as a part of the board.
        taps: The devices on it, in the order the server lists the wires.
    """

    node: BoardNode
    taps: tuple[BoardTap, ...] = ()

    @property
    def name(self) -> str:
        """What the firmware calls the bus, ``SPI1``."""
        return self.node.title

    def tap(self, device: str) -> BoardTap:
        """The tap of the device titled `device`, ``AS8510``.

        Raises:
            KeyError: If no device of that title hangs on this bus.
        """
        for tap in self.taps:
            if tap.device.title == device:
                return tap
        known = ", ".join(tap.device.title for tap in self.taps) or "none at all"
        raise KeyError(f"no device {device!r} hangs on {self.name}; it has {known}")


@dataclass(frozen=True)
class Board:
    """The device as a block diagram, at one revision.

    Attributes:
        title: ``blinky``, ``blinky · stm32l152``.
        nodes: The MCU first, then pins, channels, buses, devices, sources,
            DMA channels, timers and PWM outputs.
        edges: The wires between them.
        notes: What the picture cannot show.
        revision: Changes whenever anything above changes, from 1; a
            `BoardState` of another revision belongs to another picture.
        revision_text: What changed since the revision before, in the
            server's words; empty on the first.
        empty_text: Why there is nothing to show yet; empty once there is.
    """

    title: str = ""
    nodes: tuple[BoardNode, ...] = ()
    edges: tuple[BoardEdge, ...] = ()
    notes: tuple[BoardNote, ...] = ()
    revision: int = 0
    revision_text: str = ""
    empty_text: str = ""

    def node(self, key: str) -> BoardNode | None:
        """The part of that key, ``pin:ZC``, or None."""
        return next((node for node in self.nodes if node.key == key), None)

    def of_kind(self, kind: BoardNodeKind) -> tuple[BoardNode, ...]:
        """Every part of one kind, in the server's order."""
        return tuple(node for node in self.nodes if node.kind == kind)

    @property
    def mcu(self) -> BoardNode | None:
        """The MCU, or None on a board with nothing to show."""
        return next(iter(self.of_kind(BoardNodeKind.MCU)), None)

    @property
    def devices(self) -> tuple[BoardNode, ...]:
        """Every chip, on a bus or not."""
        return self.of_kind(BoardNodeKind.DEVICE)

    @property
    def ports(self) -> tuple[BoardNode, ...]:
        """Every pin and analog channel."""
        return tuple(node for node in self.nodes if node.is_port)

    @property
    def buses(self) -> tuple[BoardBus, ...]:
        """Every bus with the devices on it."""
        return tuple(
            BoardBus(node=bus, taps=self._taps_on(bus.key))
            for bus in self.of_kind(BoardNodeKind.BUS)
        )

    def port(self, name: str) -> BoardNode:
        """The pin or channel the firmware calls `name`, ``ZC``.

        Raises:
            KeyError: If there is none; the message lists the ports there are.
        """
        return _titled(self.ports, name, "port")

    def bus(self, name: str) -> BoardBus:
        """The bus the firmware calls `name`, ``SPI1``, with its taps.

        Raises:
            KeyError: If there is none; the message lists the buses there are.
        """
        node = _titled(self.of_kind(BoardNodeKind.BUS), name, "bus")
        return BoardBus(node=node, taps=self._taps_on(node.key))

    def _taps_on(self, bus_key: str) -> tuple[BoardTap, ...]:
        """The devices wired to one bus."""
        taps: list[BoardTap] = []
        for edge in self.edges:
            if edge.kind != BoardEdgeKind.ON_BUS or edge.to_key != bus_key:
                continue
            device = self.node(edge.from_key)
            if device is not None:
                taps.append(BoardTap(device, bus_key, edge.text, edge.hover_text))
        return tuple(taps)


def _titled(nodes: tuple[BoardNode, ...], title: str, kind: str) -> BoardNode:
    """The one part titled `title`, or a KeyError that says which there are."""
    for node in nodes:
        if node.title == title:
            return node
    known = ", ".join(node.title for node in nodes) or "none at all"
    raise KeyError(f"the board has no {kind} named {title!r}; it has {known}")
