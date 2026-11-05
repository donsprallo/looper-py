"""Lesson 11, tests with looper-py and CI.

The off-by-one of lesson 10 is fixed. The lesson's own tests live in its
folder (``tests/test_fanctl.py``: 6 firmware tests, and 2 of the room model)
and are what the reader runs; here the fix is checked, and that the
lesson's tests pass when pytest runs them.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

import looper
from tutorial.lessons import MODE_AUTO, TUTORIAL, definition_of, type_into_terminal, value_of, watch

pytestmark = pytest.mark.tutorial

LESSON = "11-tests"

#: The command the lesson's tests start looper-cli with, from the neighbouring checkout.
LOOPER_CLI_TEXT = "uv run --no-sync --project {core} python -m looper_core.presentation.cli.main"


def test_a_name_of_16_characters_is_refused_and_the_mode_stays(
    lesson_simulation: looper.Simulation,
) -> None:
    mode = watch(lesson_simulation, "unit.mode")
    lesson_simulation.advance(0.5)

    assert type_into_terminal(lesson_simulation, "name 0123456789abcdef\n") == "error\n"
    lesson_simulation.advance(0.05)

    assert value_of(lesson_simulation, mode) == MODE_AUTO


def test_the_lessons_own_tests_pass() -> None:
    definition = definition_of(LESSON)
    environment = {
        **os.environ,
        "LOOPER_CLI": LOOPER_CLI_TEXT.format(core=TUTORIAL.parents[1]),
    }
    ran = subprocess.run(  # noqa: S603 -- our own interpreter, the lesson's own tests
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(definition.parent / "tests"),
        ],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )

    assert ran.returncode == 0, ran.stdout[-3000:]
    assert "8 passed" in ran.stdout.splitlines()[-1]
