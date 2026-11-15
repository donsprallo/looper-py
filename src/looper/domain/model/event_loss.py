"""Events a reader will not get, by where they were lost.

Three places lose events, and each wants another remedy. The simulation's
own ring is overwritten when the firmware makes events faster than the
server takes them; a larger ring in ``looper.toml`` or less recording helps.
A client that reads too slowly loses what its buffer on the server could
not hold; reading more often helps. And the server keeps only so much; a
window that starts further back than that has lost its beginning. A note
that only counted them would not say which of these to try.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RingCount:
    """What one ring of the simulation dropped, in the server's words.

    Attributes:
        ring: Which ring: ``interrupts``, ``exchanges``, ``samples``, ...
        dropped: How many records.
        text: What they are and what keeps more, without the count:
            ``interrupt events; a larger [interrupts] ring keeps more``.
    """

    ring: str
    dropped: int
    text: str


def _merged(rings: tuple[RingCount, ...], more: tuple[RingCount, ...]) -> tuple[RingCount, ...]:
    """Both lists as one, each ring once, its counts added."""
    merged = list(rings)
    for count in more:
        place = next((index for index, one in enumerate(merged) if one.ring == count.ring), None)
        if place is None:
            merged.append(count)
        else:
            known = merged[place]
            merged[place] = RingCount(known.ring, known.dropped + count.dropped, count.text)
    return tuple(merged)


@dataclass(frozen=True)
class EventLoss:
    """How many events were lost, by where.

    Attributes:
        in_the_ring: Overwritten in the simulation's ring before the server read them.
        by_the_client: Not read by this client before its buffer on the server overflowed.
        by_retention: Older than the server keeps.
        unexplained: Lost for a reason this library does not know.
        rings: Of those overwritten in the ring, which rings dropped them, as
            far as the simulation counted; empty for a looper-rt that does not.
    """

    in_the_ring: int = 0
    by_the_client: int = 0
    by_retention: int = 0
    unexplained: int = 0
    rings: tuple[RingCount, ...] = ()

    @property
    def total(self) -> int:
        """Every event lost."""
        return self.in_the_ring + self.by_the_client + self.by_retention + self.unexplained

    def __add__(self, other: EventLoss) -> EventLoss:
        return EventLoss(
            self.in_the_ring + other.in_the_ring,
            self.by_the_client + other.by_the_client,
            self.by_retention + other.by_retention,
            self.unexplained + other.unexplained,
            _merged(self.rings, other.rings),
        )

    def note(self) -> str:
        """``, and 7 events the recording could not keep (7 overwritten in ...)``, or nothing."""
        if self.total == 0:
            return ""
        return f", and {self.total} events the recording could not keep ({self._where()})"

    def _where(self) -> str:
        places = (
            (self.in_the_ring, "overwritten in the simulation's ring" + self._which_rings()),
            (self.by_the_client, "not read in time by this client"),
            (self.by_retention, "older than the server keeps"),
            (self.unexplained, "lost for a reason not given"),
        )
        return ", ".join(f"{count} {place}" for count, place in places if count > 0)

    def _which_rings(self) -> str:
        """`` – 640 interrupt events; a larger [interrupts] ring keeps more``, or nothing."""
        if not self.rings:
            return ""
        return " – " + ", ".join(f"{one.dropped} {one.text}" for one in self.rings)
