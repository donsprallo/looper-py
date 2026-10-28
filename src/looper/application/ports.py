"""The port through which a test reaches a running simulation.

One method per question the use cases here ask, answered synchronously in
the values of the domain. Nothing above the port knows how it is answered:
`GrpcInspector` speaks the inspector contract to `looper-cli run`, a test
answers from a script.

How the port says no is part of what it promises. A refusal is something
the test did and can do differently -- a pin the firmware drives, a clock
that is the host's -- and a breakage means the simulation can no longer be
read at all. The two have types of their own, named here rather than by
the adapter behind the port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    Description,
    MemoryUsage,
    Pin,
    Recordings,
    Signal,
)


class SimulationRefusedError(ValueError):
    """The simulation refused what was asked of it, and says why."""


class SimulationUnreachableError(ConnectionError):
    """The simulation, or the server in front of it, stopped answering."""


class Inspector(ABC):
    """Everything this library asks of a running simulation."""

    @abstractmethod
    def describe(self) -> Description:
        """What the server is attached to."""

    @abstractmethod
    def read_recordings(self, after_sample: int, after_exchange: int) -> Recordings:
        """Samples and exchanges recorded since the given positions."""

    @abstractmethod
    def read_timings(self) -> tuple[CallTiming, ...]:
        """How often each adapter function was called since the last reset."""

    @abstractmethod
    def read_memory(self) -> MemoryUsage:
        """The heap and the stack.

        Raises:
            SimulationRefusedError: If the build cannot be read.
        """

    @abstractmethod
    def read_pins(self) -> tuple[Pin, ...]:
        """Every pin the firmware registered, with its level."""

    @abstractmethod
    def read_channels(self) -> tuple[Channel, ...]:
        """Every analog channel the firmware registered, with its value."""

    @abstractmethod
    def read_buses(self) -> tuple[Bus, ...]:
        """Every bus the simulation models."""

    @abstractmethod
    def simulated_microseconds(self) -> int:
        """How much simulated time has passed."""

    @abstractmethod
    def advance(self, microseconds: int) -> None:
        """Let time pass on a virtual clock.

        Raises:
            SimulationRefusedError: If the clock is the host's.
        """

    @abstractmethod
    def clear_recordings(self) -> None:
        """Discard the recorded samples and exchanges, for every client."""

    @abstractmethod
    def clear_measurements(self) -> None:
        """Begin the call counts, the profile and the heap again."""

    @abstractmethod
    def toggle_pin(self, pin_id: int, current_level: str) -> str:
        """Drive the opposite of the level a pin was seen at, and say which.

        Raises:
            SimulationRefusedError: If the firmware drives the pin itself.
        """

    @abstractmethod
    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        """Install a generated signal on an analog input.

        Raises:
            SimulationRefusedError: If the channel is not an input.
        """

    @abstractmethod
    def send_bus_message(self, message: BusMessage) -> None:
        """Put one message on a bus.

        Raises:
            SimulationRefusedError: If the bus takes no messages.
        """

    @abstractmethod
    def close(self) -> None:
        """Let go of the connection. Closing twice is allowed."""
