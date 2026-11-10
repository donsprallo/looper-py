"""Which server the integration tests start: looper-core, or looper-srv in front of it.

looper-srv replaces looper-core step by step and understands the same
commands, so the integration tests are the same calls against either.
``LOOPER_SERVER=srv`` starts looper-srv (``LOOPER_SRV_EXE``, by default the
debug build in a looper-srv checkout beside this one), which starts the
looper-core of ``LOOPER_CORE`` as its child for what it does not answer
itself. Without it the tests start looper-core directly, as before.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: The looper-core checkout the fixtures and the server come from.
CORE = Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))

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

#: The looper-srv executable started with ``LOOPER_SERVER=srv``.
SRV_EXE = Path(
    os.environ.get(
        "LOOPER_SRV_EXE",
        PROJECT_ROOT.parent / "looper-srv" / "target" / "debug" / "looper-srv.exe",
    )
)


def server_command() -> tuple[str, ...]:
    """The program and leading arguments that start the server under test."""
    if os.environ.get("LOOPER_SERVER", "core") != "srv":
        return CORE_COMMAND
    return (str(SRV_EXE), "--core", " ".join(CORE_COMMAND))
