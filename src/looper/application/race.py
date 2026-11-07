"""The race mode for the length of a with block (Pro).

    with simulation.race("TIM2") as race:
        simulation.advance(0.05)
        assert race.coverage().complete

Leaving the block switches the mode off, also when the block raised.
"""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING

from looper.domain.model.race import RaceCoverage

if TYPE_CHECKING:
    from looper.application.ports import Inspector


class Race:
    """The race mode on one source, switched on for a block."""

    def __init__(self, inspector: Inspector, source_id: int) -> None:
        self._inspector = inspector
        self._source_id = source_id

    def __enter__(self) -> Race:
        """Switch the mode on.

        Raises:
            ProFeatureLockedError: Without a licence for run findings.
        """
        self._inspector.set_race(True, self._source_id)
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Switch the mode off."""
        self._inspector.set_race(False, 0)

    def coverage(self) -> RaceCoverage:
        """What the mode did so far."""
        return self._inspector.read_race()
