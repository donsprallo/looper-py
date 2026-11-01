"""A stand-in for a simulation, answering from what a test put into it.

It remembers what it was asked to do, so a test can say both what the
simulation answered and what was asked of it.
"""

from __future__ import annotations

from dataclasses import replace

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import (
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    ClockMode,
    Description,
    EventPage,
    Exchange,
    MemoryUsage,
    Pin,
    RunStatus,
    Sample,
    Signal,
    Variable,
    Watch,
)

#: How many events one page of the stream holds, so that paging is exercised.
PAGE_SIZE = 2


class ScriptedInspector(Inspector):
    """Answers from fixed state and writes down every request."""

    def __init__(self, clock_mode: ClockMode = ClockMode.HELD) -> None:
        self.description = Description(contract_version=3, firmware_name="blinky")
        self.run = RunStatus(now_us=0, clock_mode=clock_mode, epoch=1, next_event_seq=0)
        self.samples: tuple[Sample, ...] = ()
        self.exchanges: tuple[Exchange, ...] = ()
        self.timings: tuple[CallTiming, ...] = ()
        self.memory: MemoryUsage | None = MemoryUsage()
        self.pins: tuple[Pin, ...] = ()
        self.channels: tuple[Channel, ...] = ()
        self.buses: tuple[Bus, ...] = ()
        self.asked: list[str] = []
        self.refusal: str | None = None
        self.empty_pages = 0
        self.polls_before_the_log_catches_up = 0
        self.log_is_stuck = False
        self.lost_events = 0
        self.epoch_changes_while_reading = False
        self.reads = 0
        self.toggled: list[int] = []
        self.signals: list[tuple[int, Signal]] = []
        self.messages: list[BusMessage] = []
        self.variables: tuple[Variable, ...] = ()
        self.watches: list[Watch] = []
        self.written: list[tuple[int, float]] = []
        self.closed = 0

    def describe(self) -> Description:
        return self.description

    def read_events(self, epoch: int, from_event_seq: int) -> EventPage:
        self.reads += 1
        self.asked.append(f"read events epoch {epoch} from {from_event_seq}")
        events = sorted((*self.samples, *self.exchanges), key=lambda one: one.event_seq)
        if self.reads <= self.empty_pages:
            return self._page((), from_event_seq + 1)
        page = tuple(one for one in events if one.event_seq >= from_event_seq)[:PAGE_SIZE]
        next_event_seq = page[-1].event_seq + 1 if page else from_event_seq
        return self._page(page, next_event_seq)

    def _page(self, events: tuple[Sample | Exchange, ...], next_event_seq: int) -> EventPage:
        caught_up = self.reads > self.polls_before_the_log_catches_up and not self.log_is_stuck
        return EventPage(
            samples=tuple(one for one in events if isinstance(one, Sample)),
            exchanges=tuple(one for one in events if isinstance(one, Exchange)),
            next_event_seq=next_event_seq,
            sim_now_us=self.run.now_us if caught_up else 0,
            lost_events=self.lost_events if self.reads == 1 else 0,
            epoch_changed=self.epoch_changes_while_reading,
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

    def run_state(self) -> RunStatus:
        return self.run

    def run_for(self, microseconds: int) -> RunStatus:
        if self.run.clock_mode is not ClockMode.HELD:
            raise SimulationRefusedError("the clock runs in real time and cannot be advanced")
        self.asked.append(f"advance {microseconds}")
        self.run = replace(self.run, now_us=self.run.now_us + microseconds)
        return self.run

    def clear_recordings(self, epoch: int) -> None:
        self.asked.append(f"clear recordings epoch {epoch}")
        if self.refusal is not None:
            raise SimulationRefusedError(self.refusal)
        self.run = replace(self.run, epoch=epoch + 1)

    def clear_measurements(self) -> None:
        self.asked.append("clear measurements")

    def toggle_pin(self, pin_id: int) -> str:
        pin = next((one for one in self.pins if one.pin_id == pin_id), None)
        if pin is None:
            raise SimulationRefusedError("unknown pin, or the pin is an output")
        self.toggled.append(pin_id)
        return "low" if pin.level == "high" else "high"

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
