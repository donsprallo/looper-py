"""A stand-in for a simulation, answering from what a test put into it.

It remembers what it was asked to do, so a test can say both what the
simulation answered and what was asked of it.
"""

from __future__ import annotations

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    Description,
    Exchange,
    MemoryUsage,
    Pin,
    Recordings,
    Sample,
    Signal,
    TimeMode,
    Variable,
    Watch,
)

#: How many records one page of a recording holds, so that paging is exercised.
PAGE_SIZE = 2


class ScriptedInspector(Inspector):
    """Answers from fixed state and writes down every request."""

    def __init__(self, time_mode: TimeMode = TimeMode.VIRTUAL) -> None:
        self.description = Description(
            contract_version=2, firmware_name="blinky", time_mode=time_mode
        )
        self.samples: tuple[Sample, ...] = ()
        self.exchanges: tuple[Exchange, ...] = ()
        self.timings: tuple[CallTiming, ...] = ()
        self.memory: MemoryUsage | None = MemoryUsage()
        self.pins: tuple[Pin, ...] = ()
        self.channels: tuple[Channel, ...] = ()
        self.buses: tuple[Bus, ...] = ()
        self.microseconds = 0
        self.asked: list[str] = []
        self.toggled: list[tuple[int, str]] = []
        self.signals: list[tuple[int, Signal]] = []
        self.messages: list[BusMessage] = []
        self.variables: tuple[Variable, ...] = ()
        self.watches: list[Watch] = []
        self.written: list[tuple[int, float]] = []
        self.closed = 0

    def describe(self) -> Description:
        return self.description

    def read_recordings(self, after_sample: int, after_exchange: int) -> Recordings:
        samples = tuple(one for one in self.samples if one.sequence >= after_sample)[:PAGE_SIZE]
        exchanges = tuple(one for one in self.exchanges if one.sequence >= after_exchange)
        exchanges = exchanges[:PAGE_SIZE]
        # As the server answers: the next sequence is where the recording has
        # got to, not where this page ends.
        return Recordings(
            samples=samples,
            next_sample=len(self.samples),
            exchanges=exchanges,
            next_exchange=len(self.exchanges),
        )

    def read_timings(self) -> tuple[CallTiming, ...]:
        return self.timings

    def read_memory(self) -> MemoryUsage:
        if self.memory is None:
            raise SimulationRefusedError("the build cannot be read")
        return self.memory

    def read_pins(self) -> tuple[Pin, ...]:
        return self.pins

    def read_channels(self) -> tuple[Channel, ...]:
        return self.channels

    def read_buses(self) -> tuple[Bus, ...]:
        return self.buses

    def simulated_microseconds(self) -> int:
        return self.microseconds

    def advance(self, microseconds: int) -> None:
        if self.description.time_mode is TimeMode.REAL_TIME:
            raise SimulationRefusedError("the host clock is not a client's to steer")
        self.asked.append(f"advance {microseconds}")
        self.microseconds += microseconds

    def clear_recordings(self) -> None:
        self.asked.append("clear recordings")

    def clear_measurements(self) -> None:
        self.asked.append("clear measurements")

    def toggle_pin(self, pin_id: int, current_level: str) -> str:
        self.toggled.append((pin_id, current_level))
        return "low" if current_level == "high" else "high"

    def apply_signal(self, channel_id: int, signal: Signal) -> None:
        self.signals.append((channel_id, signal))

    def send_bus_message(self, message: BusMessage) -> None:
        self.messages.append(message)

    def list_variables(self) -> tuple[Variable, ...]:
        return self.variables

    def watch_variable(self, variable_id: int) -> Watch:
        variable = next((one for one in self.variables if one.variable_id == variable_id), None)
        if variable is None:
            raise SimulationRefusedError(f"the catalogue has no variable {variable_id}")
        watch = Watch(
            channel_id=100 + len(self.watches),
            path=variable.path,
            name=variable.name,
            encoding=variable.encoding,
            byte_width=variable.byte_width,
            runtime_address=variable.runtime_address,
            is_writable=variable.is_writable,
            value=0.0,
        )
        self.watches.append(watch)
        return watch

    def write_variable(self, channel_id: int, value: float) -> None:
        self.written.append((channel_id, value))

    def remove_watch(self, channel_id: int) -> None:
        self.watches = [one for one in self.watches if one.channel_id != channel_id]

    def read_watches(self) -> tuple[Watch, ...]:
        return tuple(self.watches)

    def close(self) -> None:
        self.closed += 1
