"""Reading the recorded event stream from an event number on.

The window reader next door cuts the stream by simulated time, because an
expectation is about a stretch of the run. This is the other way of asking:
a test that has already let time pass wants to walk the traffic itself --
every exchange on the buses, in the order the simulation recorded them.

Where to go on is an event number. The server keeps counting them across a
clear, so a test can hold on to the last one it saw and ask again later.
The epoch is read here rather than asked of the caller: a test counts
events, not recordings.
"""

from __future__ import annotations

from collections.abc import Iterator

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import EventPage, Exchange


class EventStream:
    """The recorded events, read page by page from an event number on."""

    def __init__(self, inspector: Inspector) -> None:
        self._inspector = inspector

    def read(self, since: int = 0) -> EventPage:
        """One page of the stream, from event number `since` on.

        The page says where the next one begins (`next_event_seq`); it may
        be empty while more events follow, so that is what a caller goes on
        and never the length of the page.

        Raises:
            SimulationRefusedError: If another client cleared the recording.
        """
        return self._page(self._inspector.run_state().epoch, since)

    def exchanges(self, since: int = 0) -> Iterator[Exchange]:
        """Every recorded exchange from event number `since` on, oldest first.

        Reads page after page and ends once the stream has been read to its
        present end. On a clock that runs by itself the end moves, so what
        is yielded is the traffic up to the moment the reading caught up.

        Raises:
            SimulationRefusedError: If another client cleared the recording.
        """
        epoch = self._inspector.run_state().epoch
        reached = since
        while True:
            page = self._page(epoch, reached)
            yield from page.exchanges
            if page.next_event_seq <= reached:
                return
            reached = page.next_event_seq

    def _page(self, epoch: int, since: int) -> EventPage:
        """One page, with a clear by another client turned into a refusal."""
        page = self._inspector.read_events(epoch, since)
        if page.epoch_changed:
            raise SimulationRefusedError(
                "the recording was cleared while it was being read; "
                "read again to start from the new recording"
            )
        return page
