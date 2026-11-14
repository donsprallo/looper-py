"""A chain exported by looper-srv as a pytest, and the exported test run against blinky.

The server writes the test of a chain group from looper-py's builder calls
(looper Pro); this runs that very text against the simulation it came from,
so that an export that no longer matches this library's API fails here.

Needs a looper-docs checkout beside this one and a C compiler, and skips
without them. ``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable, Iterator
from typing import Any

import pytest

import looper
from server_under_test import FIXTURES, server_command

# The export is part of looper Pro, which the development switch unlocks.
os.environ["LOOPER_DEV_EDITION"] = "pro"

DEFINITION = FIXTURES / "blinky" / "looper.toml"


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """The blinky example, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        yield started


def _press_until_lit(simulation: looper.Simulation) -> looper.SignalGraph:
    """Every 100 ms a Sequence presses the button, then waits for the LED to rise."""
    button = simulation.pin("BUTTON_MODE")
    led = simulation.pin("LED_STATUS")
    steps = looper.Sequence(
        (
            looper.Step(looper.StepKind.DO, "press"),
            looper.Step(looper.StepKind.WAIT_FOR, "lit", 1_000_000),
        )
    )
    return (
        looper.SignalGraph()
        .group("press", "Press until lit")
        .when("tick", looper.Clock(period_us=100_000), group="press")
        .sequence("test", steps, after="tick", group="press")
        .set_pin("push", looper.SetPin(button.pin_id, looper.PinDo.PRESS, 50_000), group="press")
        .when("rises", looper.Edge(led.pin_id, looper.Polarity.RISE), group="press")
        .link("test", "push", from_port=looper.step_port(steps, 0))
        .link("rises", "test", to_port=looper.step_port(steps, 1))
    )


def _exported_test(text: str, file_name: str) -> Callable[[looper.Simulation], Any]:
    """The test function of an exported file, made from its text."""
    namespace: dict[str, Any] = {}
    exec(compile(text, file_name, "exec"), namespace)  # noqa: S102 -- the server's own export
    return namespace[f"test_{file_name.removeprefix('test_').removesuffix('.py')}"]  # type: ignore[no-any-return]


def test_a_sequence_runs_until_it_passes(simulation: looper.Simulation) -> None:
    simulation.apply_signal_graph(_press_until_lit(simulation))
    try:
        result = simulation.run_until_chain("Press until lit", timeout_s=2.0)
    finally:
        simulation.apply_signal_graph(looper.SignalGraph())

    assert result, result.failure_text
    assert result.sequence is not None
    assert result.sequence.step_count == 2


def test_an_exported_chain_runs_as_a_test(simulation: looper.Simulation) -> None:
    simulation.apply_signal_graph(_press_until_lit(simulation))
    try:
        written = simulation.export_chain("press")
        exported = _exported_test(written.text, written.file_name)
        exported(simulation)
    finally:
        simulation.apply_signal_graph(looper.SignalGraph())

    assert written.file_name == "test_press_until_lit.py"
    assert ".run_until_chain(" in written.text
    assert written.warnings == ()
