"""What a test asks a simulation to do, as values."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    """A generated signal for an analog input, evaluated by the simulation.

    Attributes:
        waveform: One of the waveforms the simulation offers, such as
            ``constant`` or ``sine``.
        amplitude: How far the signal swings around the offset.
        offset: Where it swings around; the whole value of a constant.
        frequency_hz: How often it repeats.
        phase_degrees: Where in its period it starts.
    """

    waveform: str = "constant"
    amplitude: float = 0.0
    offset: float = 0.0
    frequency_hz: float = 0.0
    phase_degrees: float = 0.0


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
