"""Reading the architecture findings once the analysis has read every file.

The server indexes the project's code in the background, from the moment
it starts. Until every file is read, the findings it answers with are
partial -- and partial in a way that matters to a test: a function that
could be static, or one never named, is only looked for at the end. A
test that asserted on the first answer would pass or fail by how fast the
host indexes, so the reading waits for the complete one.
"""

from __future__ import annotations

import time

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import Findings

#: How long to wait between two looks at an analysis still under way.
POLL_SECONDS = 0.2

#: What a test is told when the server does not answer architecture questions.
NOT_SERVED = (
    "the server does not analyse the project's architecture ({reason}); "
    "it does when started by `looper-cli run` or `looper-cli inspect` from a "
    "looper.toml whose sources it can read"
)


def complete_findings(inspector: Inspector, wait_seconds: float) -> Findings:
    """The findings once every file is read, or the partial ones when time runs out.

    Raises:
        SimulationRefusedError: If the server does not analyse the project's code.
    """
    give_up_at = time.monotonic() + wait_seconds
    findings = _read(inspector)
    while not findings.is_complete and time.monotonic() < give_up_at:
        time.sleep(POLL_SECONDS)
        findings = _read(inspector)
    return findings


def _read(inspector: Inspector) -> Findings:
    """One reading, with a refusal that says how to get an answer."""
    try:
        return inspector.read_findings()
    except SimulationRefusedError as refusal:
        raise SimulationRefusedError(NOT_SERVED.format(reason=refusal)) from refusal
