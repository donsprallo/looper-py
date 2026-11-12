"""The port through which a test reaches a running simulation.

One method per question the use cases here ask, answered synchronously in
the values of the domain. Nothing above the port knows how it is answered:
`GrpcInspector` speaks the inspector contract to `looper-srv run`, a test
answers from a script.

How the port says no is part of what it promises. A refusal is something
the test did and can do differently -- a pin the firmware drives, a clock
that is the host's -- and a breakage means the simulation can no longer be
read at all. The two have types of their own, named here rather than by
the adapter behind the port.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.application.boot_port import BootInspector
from looper.application.chain_port import ChainInspector
from looper.application.interrupt_port import InterruptInspector
from looper.application.life_port import LifeInspector
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    Description,
    EventPage,
    Findings,
    MemoryUsage,
    Pin,
    Profile,
    RunStatus,
    Signal,
    SignalGraph,
    SignalModel,
    Trigger,
    TriggerRequest,
    Variable,
    Watch,
)


class SimulationRefusedError(ValueError):
    """The simulation refused what was asked of it, and says why."""


class ProFeatureLockedError(SimulationRefusedError):
    """A part of looper Pro was asked for, and the server's licence does not unlock it.

    A kind of refusal, so code that handles refusals handles this too; its
    own type, so that a test or a pipeline can tell a missing licence from a
    firmware that said no. In CI the licence goes into ``LOOPER_LICENSE``.
    """


class SimulationUnreachableError(ConnectionError):
    """The simulation, or the server in front of it, stopped answering."""


class ContractNotServedError(SimulationUnreachableError):
    """The server answers, but does not offer the inspector contract this library speaks."""


class Inspector(LifeInspector, BootInspector, InterruptInspector, ChainInspector, ABC):
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
    def read_profile(self) -> Profile:
        """Where the simulation spent its time, function by function, since the last clearing."""

    @abstractmethod
    def read_findings(self) -> Findings:
        """What the architecture analysis found in the project's code, so far.

        Raises:
            SimulationRefusedError: If the server does not read the project's code.
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
    def set_pace(self, ratio: float) -> RunStatus:
        """Let the clock run at `ratio` times real time, and return at once.

        Raises:
            SimulationRefusedError: If the server declines the pace.
        """

    @abstractmethod
    def run_at_max(self) -> RunStatus:
        """Let the clock run as fast as the computer allows, with no pacing.

        Raises:
            SimulationRefusedError: If the server declines.
        """

    @abstractmethod
    def hold(self) -> RunStatus:
        """Stop the clock at the next boundary, so it advances only on demand.

        Raises:
            SimulationRefusedError: If the server declines.
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
    def apply_signal_graph(self, graph: SignalGraph) -> None:
        """Replace the graph of signals that drives the analog inputs.

        Raises:
            SimulationRefusedError: If the graph does not hold together, a
                model is unknown or does not fit, or a target is not an input.
        """

    @abstractmethod
    def set_graph_value(self, node: str, value: float) -> None:
        """Change what one value node of the applied graph gives.

        Raises:
            SimulationRefusedError: If the graph has no value node of that key,
                or the value is outside a parameter it gives.
        """

    @abstractmethod
    def list_models(self) -> tuple[SignalModel, ...]:
        """The models the project offers the signal graph.

        Raises:
            SimulationRefusedError: If the simulation knows of nowhere to find models.
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
    def arm_trigger(self, request: TriggerRequest, armed_by: str) -> Trigger:
        """Have the simulation watch for a condition.

        Raises:
            SimulationRefusedError: If the simulation cannot watch for it;
                the message says what it can.
        """

    @abstractmethod
    def disarm_trigger(self, trigger_id: int, by_client: str) -> Trigger:
        """Stop a trigger, whichever client armed it.

        Raises:
            SimulationRefusedError: If no such trigger was armed.
        """

    @abstractmethod
    def read_triggers(self) -> tuple[Trigger, ...]:
        """Every trigger the simulation holds, armed or not, from every client."""

    @abstractmethod
    def close(self) -> None:
        """Let go of the connection. Closing twice is allowed."""
