"""The firmware's DMA channels, as the server reports them (free).

Where a transfer stands, what it moved, and what the guard over its buffer
does; every text is the server's. The guard itself is Pro: without the
licence a receive channel's guard is ``locked``.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DmaChannel:
    """One DMA channel and what it moved in this life.

    Attributes:
        dma_id: Its number.
        name: Its name in contract.toml, ``USART2_RX``.
        peripheral_text: ``UART 2 -> rx_buf``.
        buffer_name: The variable its transfer writes into; empty where unknown.
        buffer_bytes: That variable's size from the debug information; 0 unknown.
        position: The element written next.
        announced: Elements the firmware was told of by half, end or idle.
        guard: ``off``, ``precise``, ``coarse``, ``downgraded``, ``unavailable``,
            ``debugger``, ``stack`` or ``locked``.
        neighbours: Variables on the buffer's pages, which the guard traps too.
        state_text: ``running, lap 3, at 12 of 64``.
    """

    dma_id: int
    name: str
    peripheral_text: str = ""
    direction: str = ""
    mode: str = ""
    running: bool = False
    buffer_name: str = ""
    buffer_bytes: int = 0
    length: int = 0
    width: int = 1
    position: int = 0
    announced: int = 0
    laps: int = 0
    elements: int = 0
    overruns: int = 0
    unclaimed: int = 0
    guard: str = "off"
    guard_text: str = ""
    neighbours: tuple[str, ...] = ()
    state_text: str = ""


@dataclass(frozen=True)
class DmaChannels:
    """Every channel of the board.

    Attributes:
        installed: Whether the firmware started a transfer yet, so that the counts are live.
        note: Why nothing is there, or what the guard does.
    """

    channels: tuple[DmaChannel, ...] = field(default_factory=tuple)
    installed: bool = False
    note: str = ""

    def channel(self, name: str) -> DmaChannel:
        """The channel of a name.

        Raises:
            KeyError: If there is none.
        """
        for channel in self.channels:
            if channel.name == name:
                return channel
        raise KeyError(f"there is no DMA channel called {name}")
