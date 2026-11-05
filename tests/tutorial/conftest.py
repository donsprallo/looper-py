"""The simulation of a lesson, for the tutorial's checkpoint tests; see lessons.py."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import looper
from tutorial.lessons import LOOPER_CLI, definition_of


@pytest.fixture
def lesson_simulation(request: pytest.FixtureRequest) -> Iterator[looper.Simulation]:
    """A fresh simulation of the module's ``LESSON`` on a held clock, for one test.

    Every test gets its own: a button pressed or a signal applied in one
    test must not change what the next one sees.
    """
    definition = definition_of(request.module.LESSON)
    with looper.run(definition, virtual=True, looper_cli=LOOPER_CLI) as started:
        yield started
