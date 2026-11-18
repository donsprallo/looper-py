"""What a test asks a simulation to do, as values.

`Signal` lives with the table files it can play (`signal_waves`) and is
named here as before.
"""

from __future__ import annotations

from dataclasses import dataclass

from looper.domain.model.signal_waves import Signal

__all__ = ["BusMessage", "Signal"]


@dataclass(frozen=True)
class BusMessage:
    """One message put on a bus.

    Attributes:
        bus_id: The bus to send on.
        address: Where on the bus it is addressed.
        payload: The bytes it carries.
        extended: Whether the address is an extended, 29 bit CAN identifier.
    """

    bus_id: int
    address: int
    payload: bytes
    extended: bool = False
