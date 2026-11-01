"""Reading one window of the event stream.

The server fills its event log from the firmware every so often in host
time, so right after a run the log may still be behind the clock. The reader
therefore asks until the log has reached the end of the window. Host time is
used for that waiting only; what the window holds is cut by simulated time.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from looper.application.ports import (
    Inspector,
    SimulationRefusedError,
    SimulationUnreachableError,
)
from looper.domain.model import EventPage, Exchange, RunStatus, Sample

#: How long to wait between two asks while the log is behind the clock.
POLL_SECONDS = 0.02

#: How long the log may take to reach the end of a window before the server
#: counts as stuck.
DEADLINE_SECONDS = 10.0


@dataclass(frozen=True)
class WindowEvents:
    """What the stream held between the start and the end of a window."""

    samples: tuple[Sample, ...]
    exchanges: tuple[Exchange, ...]
    lost_events: int


class WindowReader:
    """Collects the samples and exchanges of one window, page by page."""

    def __init__(self, inspector: Inspector, start: RunStatus, end_us: int) -> None:
        self._inspector = inspector
        self._epoch = start.epoch
        self._end_us = end_us
        self._next_event_seq = start.next_event_seq
        self._samples: list[Sample] = []
        self._exchanges: list[Exchange] = []
        self._lost_events = 0

    def read(self) -> WindowEvents:
        """Read until the window's end is in hand.

        Raises:
            SimulationRefusedError: If another client cleared the recording.
            SimulationUnreachableError: If the log never reaches the end.
        """
        give_up_at = time.monotonic() + DEADLINE_SECONDS
        while True:
            reached = self._next_event_seq
            if self._read_page():
                break
            if self._next_event_seq == reached:
                self._wait_for_the_log(give_up_at)
        return WindowEvents(tuple(self._samples), tuple(self._exchanges), self._lost_events)

    @staticmethod
    def _wait_for_the_log(give_up_at: float) -> None:
        """Pause before asking again, or give up when the log is stuck."""
        if time.monotonic() > give_up_at:
            raise SimulationUnreachableError(
                "the server's event log did not reach the end of the window in time"
            )
        time.sleep(POLL_SECONDS)

    def _read_page(self) -> bool:
        """Take one page; say whether the window is complete."""
        page = self._inspector.read_events(self._epoch, self._next_event_seq)
        if page.epoch_changed:
            raise SimulationRefusedError("the recording was cleared during the window")
        self._lost_events += page.lost_events
        self._keep_what_is_inside(page)
        moved = page.next_event_seq > self._next_event_seq
        self._next_event_seq = max(self._next_event_seq, page.next_event_seq)
        if self._has_events_beyond_the_window(page):
            return True
        return not moved and page.sim_now_us >= self._end_us

    def _keep_what_is_inside(self, page: EventPage) -> None:
        """Keep the events that happened at or before the window's end."""
        self._samples.extend(one for one in page.samples if one.sim_us <= self._end_us)
        self._exchanges.extend(one for one in page.exchanges if one.sim_us <= self._end_us)

    def _has_events_beyond_the_window(self, page: EventPage) -> bool:
        """Whether the stream has gone past the window, so nothing more belongs to it."""
        beyond_samples = any(one.sim_us > self._end_us for one in page.samples)
        return beyond_samples or any(one.sim_us > self._end_us for one in page.exchanges)
