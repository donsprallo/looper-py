"""What the race mode did, as the server reports it (Pro).

The race mode raises one interrupt source at each interruption point of the
loop in turn, to provoke what an interrupt at an unlucky place breaks. It
finds nothing itself; a test's checks do.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RaceCoverage:
    """The race mode now.

    Attributes:
        on: Whether it raises a source.
        source: The source's name in contract.toml; empty while it is off.
        points_seen: Interruption points seen outside ISRs since it was switched on.
        points_covered: Points the source was raised at.
        cycles: Times it went round every point of a pass.
        text: The server's sentence, ``37 of 41 points, 2 cycles``.
        uncovered: Functions that hold points it has not raised at yet.
    """

    on: bool = False
    source: str = ""
    points_seen: int = 0
    points_covered: int = 0
    cycles: int = 0
    text: str = ""
    uncovered: tuple[str, ...] = ()

    @property
    def complete(self) -> bool:
        """Whether the source was raised at every point seen, once round at least."""
        return (
            self.on
            and self.points_seen > 0
            and self.points_covered == self.points_seen
            and self.cycles > 0
        )
