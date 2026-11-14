"""The server the integration tests start: looper-srv.

looper-srv has replaced looper-core (M10); core is no longer started from
here, not even as a reference. The tests start the looper-srv of
``LOOPER_SRV_EXE``, by default the debug build in a looper-srv checkout
beside this one. The fixtures are the test firmware in ``fixtures/`` of the
looper-docs checkout beside this one (``LOOPER_FIXTURES`` points elsewhere).
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The test firmware, kept in looper-docs.
FIXTURES = Path(os.environ.get("LOOPER_FIXTURES", PROJECT_ROOT.parent / "looper-docs" / "fixtures"))

#: The looper-srv executable the tests start.
SRV_EXE = Path(
    os.environ.get(
        "LOOPER_SRV_EXE",
        PROJECT_ROOT.parent / "looper-srv" / "target" / "debug" / "looper-srv.exe",
    )
)


def server_command() -> tuple[str, ...]:
    """The program that starts the server under test."""
    return (str(SRV_EXE),)
