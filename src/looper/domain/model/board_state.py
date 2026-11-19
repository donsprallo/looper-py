"""The board's live state, as the server computes it from what it records (free).

Pin levels and analog values, the exchanges per tap and per rail -- a rail
is a bus -- a chip's last values, and the ports whose driver in the signal
graph is off. Only the parts and taps with a state are listed. A state
belongs to the `Board` of its revision; another revision means the picture
changed and is to be read again. Every text is the server's; times are
simulated microseconds.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoardNodeState:
    """The live state of one part of the board, by its key.

    Attributes:
        key: The part's key, ``pin:ZC``, ``bus:SPI1``, ``device:SPI1:0``.
        state_text: A pin ``high``; a channel ``1.82 A`` or ``no data``; a
            bus ``412 exchanges · last 0.2 ms ago``; a chip its published values.
        active: A pin at its active level; a bus with an exchange in the last second.
        fault: A bus with exchanges no device answered; ``fault_text`` says so.
        driver_off: The block that drives this port is not live;
            ``reference_state_text`` says what the port does meanwhile.
        value: A channel's value, a pin's level as 1 or 0; None for the rest
            and for a channel without data.
        exchanges: A bus's exchanges so far.
        last_us: When a bus's last exchange ended; 0 before the first.
    """

    key: str
    state_text: str = ""
    active: bool = False
    fault: bool = False
    fault_text: str = ""
    driver_off: bool = False
    reference_state_text: str = ""
    value: float | None = None
    exchanges: int = 0
    last_us: int = 0


@dataclass(frozen=True)
class BoardTapState:
    """The live state of a tap: a device on its bus, from `from_key` to `to_key`.

    Attributes:
        state_text: ``412``; empty before the first exchange.
        active: An exchange in the last second.
        fault: Exchanges with this place that no device answered; ``fault_text``
            says how many, ``3 not answered``.
        hover_text: The tap with its count and when its last exchange was.
        exchanges: The exchanges with this place so far.
        unanswered: How many of them no device answered.
        last_us: When the last one ended; 0 before the first.
    """

    from_key: str
    to_key: str
    state_text: str = ""
    active: bool = False
    fault: bool = False
    fault_text: str = ""
    hover_text: str = ""
    exchanges: int = 0
    unanswered: int = 0
    last_us: int = 0


@dataclass(frozen=True)
class BoardState:
    """The board's live state at one moment of the run.

    Attributes:
        revision: The `Board` it belongs to.
        sim_us: When it was read.
        nodes: The parts with a state.
        taps: The taps with a state.
    """

    revision: int = 0
    sim_us: int = 0
    nodes: tuple[BoardNodeState, ...] = ()
    taps: tuple[BoardTapState, ...] = ()

    def node(self, key: str) -> BoardNodeState | None:
        """The state of the part of that key, or None when it has none."""
        return next((node for node in self.nodes if node.key == key), None)

    def pin(self, name: str) -> BoardNodeState | None:
        """The state of the pin the firmware calls `name`."""
        return self.node(f"pin:{name}")

    def channel(self, name: str) -> BoardNodeState | None:
        """The state of the analog channel the firmware calls `name`."""
        return self.node(f"channel:{name}")

    def rail(self, name: str) -> BoardNodeState | None:
        """The state of the bus the firmware calls `name`: its exchanges and the last one."""
        return self.node(f"bus:{name}")

    def tap(self, device_key: str) -> BoardTapState | None:
        """The state of the tap of the device of that key, ``device:SPI1:0``."""
        return next((tap for tap in self.taps if tap.from_key == device_key), None)
