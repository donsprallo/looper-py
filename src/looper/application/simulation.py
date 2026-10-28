"""What a test does with a running simulation.

Set the scene, let time pass, and say what should then be true. The
simulation behind it may have been started for the test or may be shared
with a window; either way, what is changed here is changed for everybody
looking, because there is one simulation.
"""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from looper.application.expectations import MICROSECONDS_PER_SECOND, Expectations
from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import Bus, BusMessage, Channel, Description, Pin, Signal, TimeMode


class Simulation:
    """One running simulation, as a test sees it.

    Use it as a context manager, or call `close` when done: closing lets go
    of the connection and, for a simulation that was started for the test,
    stops it.
    """

    def __init__(self, inspector: Inspector, on_close: Callable[[], None] | None = None) -> None:
        self._inspector = inspector
        self._on_close = on_close
        self._description = inspector.describe()
        self._closed = False

    @property
    def description(self) -> Description:
        """What the server said about the simulation when it was reached."""
        return self._description

    @property
    def firmware_name(self) -> str:
        """What the firmware calls itself."""
        return self._description.firmware_name

    @property
    def time_mode(self) -> TimeMode:
        """Where the simulation's clock comes from."""
        return self._description.time_mode

    @property
    def definition_path(self) -> str:
        """The build definition the simulation was started with, if the server said."""
        return self._description.definition_path

    @property
    def simulated_seconds(self) -> float:
        """How much simulated time has passed."""
        return self._inspector.simulated_microseconds() / MICROSECONDS_PER_SECOND

    def expect(self) -> Expectations:
        """Begin declaring what should be true of the next stretch of the run."""
        return Expectations(self._inspector, self.time_mode)

    def advance(self, seconds: float) -> None:
        """Let time pass on a virtual clock.

        Raises:
            SimulationRefusedError: If the clock is the host's.
        """
        self._inspector.advance(int(seconds * MICROSECONDS_PER_SECOND))

    def pins(self) -> tuple[Pin, ...]:
        """Every pin the firmware registered, with its level now."""
        return self._inspector.read_pins()

    def channels(self) -> tuple[Channel, ...]:
        """Every analog channel the firmware registered, with its value now."""
        return self._inspector.read_channels()

    def buses(self) -> tuple[Bus, ...]:
        """Every bus the simulation models."""
        return self._inspector.read_buses()

    def pin(self, name: str) -> Pin:
        """The pin the firmware calls `name`, as it is now.

        Raises:
            SimulationRefusedError: If there is none; the message lists the names there are.
        """
        return _named(self.pins(), name, "pin")

    def channel(self, name: str) -> Channel:
        """The analog channel the firmware calls `name`, as it is now.

        Raises:
            SimulationRefusedError: If there is none; the message lists the names there are.
        """
        return _named(self.channels(), name, "channel")

    def bus(self, name: str) -> Bus:
        """The bus the firmware calls `name`.

        Raises:
            SimulationRefusedError: If there is none; the message lists the names there are.
        """
        return _named(self.buses(), name, "bus")

    def toggle_pin(self, pin_id: int) -> str:
        """Drive the opposite of the level a pin is at now, and say which.

        Raises:
            SimulationRefusedError: If the pin is unknown or the firmware drives it.
        """
        current = next((pin for pin in self.pins() if pin.pin_id == pin_id), None)
        if current is None:
            raise SimulationRefusedError(f"the firmware registered no pin {pin_id}")
        return self._inspector.toggle_pin(pin_id, current.level)

    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        """Install a generated signal on an analog input.

        Raises:
            SimulationRefusedError: If the channel is not an input.
        """
        self._inspector.apply_signal(channel_id, signal)

    def send_bus_message(self, message: BusMessage) -> None:
        """Put one message on a bus.

        Raises:
            SimulationRefusedError: If the bus takes no messages.
        """
        self._inspector.send_bus_message(message)

    def close(self) -> None:
        """Let go of the simulation. Closing twice is allowed."""
        if self._closed:
            return
        self._closed = True
        self._inspector.close()
        if self._on_close is not None:
            self._on_close()

    def __enter__(self) -> Simulation:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def _named[Named: (Pin, Channel, Bus)](things: tuple[Named, ...], name: str, kind: str) -> Named:
    """The one thing called `name`, or a refusal that says what there is."""
    for thing in things:
        if thing.name == name:
            return thing
    known = ", ".join(sorted(thing.name for thing in things)) or "none at all"
    raise SimulationRefusedError(
        f"the firmware registered no {kind} named {name!r}; it has {known}"
    )
