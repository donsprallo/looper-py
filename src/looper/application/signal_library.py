"""What the signal graph can be built from, asked of the server: table files and starters.

A mixin of `Simulation`, so that both files stay readable. Reading a table
file -- its separators, its header, simplifying a long recording -- is the
server's, as it is for the window, so that a test plays the points the
window would; the starters and what each needs are the server's too.
"""

from __future__ import annotations

import os
from pathlib import Path

from looper.application.ports import Inspector
from looper.domain.model.signal_starters import Starters
from looper.domain.model.signal_waves import TableFile


class SignalLibrary:
    """Table files for a Table generator, and the starters a graph can begin with."""

    _inspector: Inspector

    def read_table(
        self,
        path: str | os.PathLike[str],
        value_column: int = 0,
        max_error: float = 0.0,
        keep_every_point: bool = False,
        unit: str = "",
    ) -> TableFile:
        """A CSV or PWL file's points for a Table generator, read and simplified by the server.

        The path is on the server's disk; one that exists here is sent
        whole, so that a server started here finds it. `value_column` 0 is
        the column after the time. A recording of more than 1 000 points, or
        any with `max_error`, is simplified so that no point moves further
        than `max_error` (0: half a percent of the values' span);
        `keep_every_point` plays them all. A file that cannot be played
        comes back with its ``problem_text``; `TableFile.signal` raises it.
        """
        local = Path(path)
        sent = str(local.resolve()) if local.exists() else os.fspath(path)
        return self._inspector.read_table(sent, value_column, max_error, keep_every_point, unit)

    def starters(self) -> Starters:
        """The starters a signal graph can begin with, as looper-models defines them.

        Each says what it needs and whether this firmware has it; none, with
        the reason, when the model library did not start.
        """
        return self._inspector.list_starters()
