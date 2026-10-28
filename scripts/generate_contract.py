"""Regenerate the Python bindings of the inspector contract.

The schema is a copy of the one looper-core serves. It is compiled relative
to the source root so that the generated service module imports the message
module by its package path.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
SCHEMA = SOURCE_ROOT / "looper" / "infrastructure" / "contract" / "looper_inspector.proto"


def main() -> int:
    """Run protoc and report whether the bindings were written."""
    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{SOURCE_ROOT}",
        f"--python_out={SOURCE_ROOT}",
        f"--pyi_out={SOURCE_ROOT}",
        f"--grpc_python_out={SOURCE_ROOT}",
        str(SCHEMA),
    ]
    completed = subprocess.run(command, check=False)  # noqa: S603
    if completed.returncode != 0:
        print("protoc failed", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
