"""What a test does with a running simulation.

Set the scene, let time pass, and say what should then be true. The
simulation behind it may have been started for the test or may be shared
with a window; either way, what is changed here is changed for everybody
looking, because there is one simulation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from looper.application.event_stream import EventStream
from looper.application.expectations import MICROSECONDS_PER_SECOND, Expectations
from looper.application.findings_reading import complete_findings
from looper.application.ports import Inspector, SimulationRefusedError
from looper.application.triggers import Triggers
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    ClockMode,
    Description,
    EventPage,
    Exchange,
    Findings,
    MemoryUsage,
    Pin,
    Profile,
    RunStatus,
    Signal,
    SignalGraph,
    SignalModel,
    Variable,
    Watch,
)


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
        self._events = EventStream(inspector)
        self._triggers = Triggers(inspector)
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
    def clock_mode(self) -> ClockMode:
        """How the clock goes now: held, paced or at full speed.

        Read from the simulation each time, because any client may switch it.
        """
        return self._inspector.run_state().clock_mode

    @property
    def definition_path(self) -> str:
        """The build definition the simulation was started with, if the server said."""
        return self._description.definition_path

    @property
    def simulated_seconds(self) -> float:
        """How much simulated time has passed."""
        return self._inspector.run_state().now_us / MICROSECONDS_PER_SECOND

    def run_state(self) -> RunStatus:
        """Where the clock is, how it goes, and where the recording stands.

        One reading of everything the server says about the run: the time,
        the clock mode, the recording epoch, the next event number -- a
        starting point for `exchanges(since=...)` -- and why the firmware is
        held, when it is.
        """
        return self._inspector.run_state()

    @property
    def triggers(self) -> Triggers:
        """The conditions the simulation watches for, shared with every client."""
        return self._triggers

    def expect(self) -> Expectations:
        """Begin declaring what should be true of the next stretch of the run."""
        return Expectations(self._inspector)

    def advance(self, seconds: float) -> None:
        """Run a held clock for a span of simulated time.

        Raises:
            SimulationRefusedError: If the clock is not held; the message
                says why and what to do.
        """
        self.advance_microseconds(round(seconds * MICROSECONDS_PER_SECOND))

    def advance_microseconds(self, microseconds: int) -> None:
        """Run a held clock for a span given in whole simulated microseconds.

        The same as `advance`, for a span that is awkward in seconds: a bit
        period, a sampling interval, a timeout the firmware counts in
        microseconds. Seconds go through a float and are rounded here, so a
        test that already knows the microseconds says them.

        Raises:
            SimulationRefusedError: If the clock is not held; the message
                says why and what to do.
        """
        self._inspector.run_for(microseconds)

    def read_events(self, since: int = 0) -> EventPage:
        """One page of the recorded event stream, from event number `since` on.

        Where the next page begins is the page's `next_event_seq`, never the
        length of the page: a page can be empty while more events follow.

        Raises:
            SimulationRefusedError: If another client cleared the recording
                while it was being read.
        """
        return self._events.read(since)

    def exchanges(self, since: int = 0) -> Iterator[Exchange]:
        """Every recorded exchange from event number `since` on, oldest first.

        Reads on until the stream has been read to its present end, so a
        test that let time pass on a held clock walks exactly the traffic of
        the recording. Each exchange carries its `event_seq`; keep the last
        one and ask again from one beyond it to go on where this left off.

        Raises:
            SimulationRefusedError: If another client cleared the recording
                while it was being read.
        """
        return self._events.exchanges(since)

    def clear_recordings(self) -> None:
        """Throw away the recorded events and begin the next recording.

        What a test wants between two phases: let the first one happen, then
        clear, so that what is read afterwards is the second phase alone.
        Event numbers keep counting across the clear, so one held from
        before the clear still says where to go on.

        The clearing reaches every client of the simulation, a window
        included: there is one simulation and one recording.

        Raises:
            SimulationRefusedError: If another client cleared in the moment
                between reading the epoch and asking.
        """
        self._inspector.clear_recordings(self._inspector.run_state().epoch)

    def clear_measurements(self) -> None:
        """Begin the call counts, the profile and the heap figures again."""
        self._inspector.clear_measurements()

    def timings(self) -> tuple[CallTiming, ...]:
        """How often each adapter function was called since the last clearing."""
        return self._inspector.read_timings()

    def memory(self) -> MemoryUsage:
        """The heap and the deepest the stack went.

        Raises:
            SimulationRefusedError: If the build cannot be read; the message
                says why.
        """
        return self._inspector.read_memory()

    def profile(self) -> Profile:
        """Where the simulation spent its time, function by function, since the last clearing.

        Clear the measurements first, with `clear_measurements`, to profile
        one phase of a test alone. In a build that is not woven for
        profiling every figure is zero; `Profile.is_profiling` says so.
        """
        return self._inspector.read_profile()

    def findings(self, wait_seconds: float = 60.0) -> Findings:
        """What the architecture analysis found in the project's code.

        Waits up to `wait_seconds` for the analysis to have read every
        file, since some findings are only looked for then; what comes back
        says in `is_complete` whether it got that far.

        Raises:
            SimulationRefusedError: If the server does not analyse the
                project's code: it does when `looper-cli run` or
                `looper-cli inspect` was started from a looper.toml whose
                sources it can read.
        """
        return complete_findings(self._inspector, wait_seconds)

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

        The simulation does the toggling, so two clients cannot both toggle
        to high.

        Raises:
            SimulationRefusedError: If the pin is unknown or the firmware drives it.
        """
        return self._inspector.toggle_pin(pin_id)

    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        """Install a generated signal on an analog input.

        Raises:
            SimulationRefusedError: If the channel is not an input.
        """
        self._inspector.apply_signal(channel_id, signal)

    def apply_signal_graph(self, graph: SignalGraph) -> None:
        """Drive analog inputs from a graph of signals, models among them.

        The graph replaces whatever graph ran before, for every client; an
        input it no longer drives goes back to its own signal. Applying an
        empty `SignalGraph` removes the graph.

        Raises:
            SimulationRefusedError: If the graph does not hold together, a
                model is unknown or does not fit its inputs, or a target is
                not an input.
        """
        self._inspector.apply_signal_graph(graph)

    def models(self) -> tuple[SignalModel, ...]:
        """The models the project offers the signal graph, read afresh from its files.

        Raises:
            SimulationRefusedError: If the simulation knows of nowhere to find models.
        """
        return self._inspector.list_models()

    def model(self, name: str) -> SignalModel:
        """The model the project offers under `name`, with its inputs, outputs and parameters.

        Raises:
            SimulationRefusedError: If there is none; the message lists the names there are.
        """
        return _named(self.models(), name, "model", "the project offers")

    def send_bus_message(self, message: BusMessage) -> None:
        """Put one message on a bus.

        A message longer than the bus carries is refused here rather than
        sent: cut short on the way, it would arrive as a different message.

        Raises:
            SimulationRefusedError: If the bus takes no messages, or the
                message is longer than one message on it may be.
        """
        self._refuse_if_too_long(message)
        self._inspector.send_bus_message(message)

    def _refuse_if_too_long(self, message: BusMessage) -> None:
        """Refuse a payload longer than the bus says one message carries."""
        bus = next((one for one in self.buses() if one.bus_id == message.bus_id), None)
        if bus is None or bus.max_payload_bytes == 0:
            return
        if len(message.payload) <= bus.max_payload_bytes:
            return
        raise SimulationRefusedError(
            f"{bus.name} carries at most {bus.max_payload_bytes} bytes in one message, "
            f"and this one has {len(message.payload)}; send it as several"
        )

    def variables(self) -> tuple[Variable, ...]:
        """The catalogue of the firmware's variables.

        Raises:
            SimulationRefusedError: If the build could not be read; the message says why.
        """
        return self._inspector.list_variables()

    def watch_variable(self, variable_id: int) -> Watch:
        """Begin sampling a variable from the catalogue.

        Raises:
            SimulationRefusedError: If the catalogue has no such variable.
        """
        return self._inspector.watch_variable(variable_id)

    def write_variable(self, channel_id: int, value: float) -> None:
        """Store a value in a watched variable.

        Raises:
            SimulationRefusedError: If the watch is unknown or not writable.
        """
        self._inspector.write_variable(channel_id, value)

    def remove_watch(self, channel_id: int) -> None:
        """Stop sampling a watched variable."""
        self._inspector.remove_watch(channel_id)

    def watches(self) -> tuple[Watch, ...]:
        """Every variable being sampled, with its value now."""
        return self._inspector.read_watches()

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


def _named[Named: (Pin, Channel, Bus, SignalModel)](
    things: tuple[Named, ...], name: str, kind: str, whose: str = "the firmware registered"
) -> Named:
    """The one thing called `name`, or a refusal that says what there is."""
    for thing in things:
        if thing.name == name:
            return thing
    known = ", ".join(sorted(thing.name for thing in things)) or "none at all"
    raise SimulationRefusedError(f"{whose} no {kind} named {name!r}; it has {known}")
