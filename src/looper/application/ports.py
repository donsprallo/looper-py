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
    EventPage,
    MemoryUsage,
    Pin,
    RunStatus,
    Signal,
    Variable,
    Watch,
)


class SimulationRefusedError(ValueError):
    """The simulation refused what was asked of it, and says why."""


class SimulationUnreachableError(ConnectionError):
    """The simulation, or the server in front of it, stopped answering."""


class ContractNotServedError(SimulationUnreachableError):
    """The server answers, but does not offer the inspector contract this library speaks."""


class Inspector(ABC):
    """Everything this library asks of a running simulation."""

    @abstractmethod
    def describe(self) -> Description:
        """What the server is attached to."""

    @abstractmethod
    def read_events(self, epoch: int, from_event_seq: int) -> EventPage:
        """One page of samples and exchanges, from an event number on.

        The page may be empty while more events follow; where reading goes
        on is `next_event_seq`, not the length of the page.
        """

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
    def run_state(self) -> RunStatus:
        """Where the clock is and how it goes now."""

    @abstractmethod
    def run_for(self, microseconds: int) -> RunStatus:
        """Let time pass on a held clock, and return once it has.

        Raises:
            SimulationRefusedError: If the clock is not held, or a debugger
                holds the firmware.
        """

    @abstractmethod
    def clear_recordings(self, epoch: int) -> None:
        """Discard the recorded events, for every client, and begin the next epoch.

        Raises:
            SimulationRefusedError: If another client cleared since `epoch`.
        """

    @abstractmethod
    def clear_measurements(self) -> None:
        """Begin the call counts, the profile and the heap again."""

    @abstractmethod
    def toggle_pin(self, pin_id: int) -> str:
        """Drive the opposite of the level a pin is at, and say which.

        Raises:
            SimulationRefusedError: If the pin is unknown or the firmware drives it.
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
    def list_variables(self) -> tuple[Variable, ...]:
        """The catalogue of the firmware's variables, read out of the build.

        Raises:
            SimulationRefusedError: If there is no catalogue; the message says why.
        """

    @abstractmethod
    def watch_variable(self, variable_id: int) -> Watch:
        """Begin sampling a variable from the catalogue.

        Raises:
            SimulationRefusedError: If the catalogue has no such variable.
        """

    @abstractmethod
    def write_variable(self, channel_id: int, value: float) -> None:
        """Store a value in a watched variable.

        Raises:
            SimulationRefusedError: If the watch is unknown or not writable.
        """

    @abstractmethod
    def remove_watch(self, channel_id: int) -> None:
        """Stop sampling a watched variable."""

    @abstractmethod
    def read_watches(self) -> tuple[Watch, ...]:
        """Every variable being sampled, with its value now."""

    @abstractmethod
    def close(self) -> None:
        """Let go of the connection. Closing twice is allowed."""
