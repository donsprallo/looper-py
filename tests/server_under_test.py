"""Which server the integration tests start: looper-srv, or looper-core as the reference.

looper-srv has replaced looper-core (M10) and understands the same commands,
so the integration tests are the same calls against either. By default they
start looper-srv (``LOOPER_SRV_EXE``, by default the debug build in a
looper-srv checkout beside this one) on its own. ``LOOPER_TEST_SERVER=core``
starts the looper-core of ``LOOPER_CORE`` instead, as long as it exists, to
compare with the reference. The fixtures are core's test firmware, copied to
``fixtures/`` of the looper-docs checkout beside this one so that they outlive
core (``LOOPER_FIXTURES`` points elsewhere); both servers run the same copy.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The looper-core checkout the reference server comes from.
CORE = Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))

#: The test firmware: core's fixtures, kept in looper-docs.
FIXTURES = Path(os.environ.get("LOOPER_FIXTURES", PROJECT_ROOT.parent / "looper-docs" / "fixtures"))

#: looper-cli from that checkout, run as a module so that the tests do not
#: depend on its console script being installed.
CORE_COMMAND = (
    "uv",
    "run",
    "--no-sync",
    "--project",
    str(CORE),
    "python",
    "-m",
    "looper_core.presentation.cli.main",
)

#: The looper-srv executable started with ``LOOPER_TEST_SERVER=srv``.
SRV_EXE = Path(
    os.environ.get(
        "LOOPER_SRV_EXE",
        PROJECT_ROOT.parent / "looper-srv" / "target" / "debug" / "looper-srv.exe",
    )
)


#: What makes a debug build of looper-srv leave out the finding kinds core never served (D7).
SRV_CORE_FINDINGS = {"LOOPER_SRV_CORE_FINDINGS": "1"}


def server_command() -> tuple[str, ...]:
    """The program and leading arguments that start the server under test."""
    if os.environ.get("LOOPER_TEST_SERVER", "srv") == "core":
        return CORE_COMMAND
    # srv reads the code of a simulation itself since its step 6.3 and knows finding kinds core
    # never served (stack-*, isr-*); the tests compare with core, so srv leaves them out as in its
    # conformance suite (deviation D7, read only by a debug build).
    os.environ.update(SRV_CORE_FINDINGS)
    return (str(SRV_EXE),)
