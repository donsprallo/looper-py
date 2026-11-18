"""Comparators driving an input pin of blinky, run in looper-srv (#4, looper-srv#28).

A 50 Hz mains sine through Abs and a comparator is a zero-cross detector:
its pulses reach blinky's button pin to the microsecond and are measured on
the pin like any other edges. Behind the project's LowPass model the edges
fall on the model's steps instead, and the graph says so. An output pin is
refused with the server's sentence, and a probe records on its own clock.

Needs a looper-docs checkout beside this one and a C compiler, and skips
without them. ``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"

#: Mains as the concept's dimmer sees it: 325 V peak, 50 Hz.
MAINS = looper.Signal("sine", amplitude=325.0, frequency_hz=50.0)


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky, built, started on a held clock and attached to, for this module alone.

    Its own start, because a pin the graph drove keeps its level afterwards.
    """
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        if "graph_edges" not in started.description.capabilities:
            pytest.skip("the server's runtime plans no graph edges")
        yield started


@pytest.fixture
def button(simulation: looper.Simulation) -> Iterator[looper.Pin]:
    """The button pin, an input; the graph is taken away and the button released afterwards."""
    yield simulation.pin("BUTTON_MODE")
    simulation.apply_signal_graph(looper.SignalGraph())
    released = simulation.pin("BUTTON_MODE")
    if released.level == "low":
        simulation.toggle_pin(released.pin_id)


def _zero_cross(pin_id: int) -> looper.SignalGraph:
    """The concept's detector: high while the mains is within 15 V of zero."""
    return (
        looper.SignalGraph()
        .generator("mains", MAINS)
        .operation("mains_abs", looper.SignalNodeKind.ABS, "mains")
        .compare("zc", "mains_abs", level=15.0, hysteresis=2.0, below=True)
        .drive_pin(pin_id, "zc")
    )


def test_a_zero_cross_detector_pulses_the_pin_once_a_half_cycle(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    simulation.apply_signal_graph(_zero_cross(button.pin_id))
    simulation.advance(0.05)

    check = simulation.expect()
    check.pin("BUTTON_MODE").frequency_between(99.0, 101.0)
    # High from |v| < 15 V to |v| > 17 V: (asin(15/325) + asin(17/325)) / (2 pi 50) = 314 us.
    check.pin("BUTTON_MODE").pulse_width_between(305, 325, unit="us")
    report = check.evaluate(for_seconds=0.2)

    assert report, report.summary
    target = simulation.signal_graph().pin_target(button.pin_id)
    assert target.resolution_text == "exact to 1 µs"
    assert target.edges > 0
    assert simulation.pin("BUTTON_MODE").is_driven_by_graph


def test_a_drive_on_a_pin_the_graph_drives_is_refused_with_the_server_s_sentence(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    simulation.apply_signal_graph(_zero_cross(button.pin_id))
    simulation.advance(0.001)

    with pytest.raises(looper.SimulationRefusedError, match="driven by the signal graph"):
        simulation.toggle_pin(button.pin_id)
    assert simulation.pin("BUTTON_MODE").set_by_text == "signal graph"


def test_a_comparator_behind_a_model_switches_on_the_model_s_steps(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        .generator("mains", MAINS)
        .model("filter", "LowPass", inputs=["mains"])
        .compare("zc", "filter", hysteresis=1.0)
        .drive_pin(button.pin_id, "zc")
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(0.05)

    check = simulation.expect()
    check.pin("BUTTON_MODE").frequency_between(49.0, 51.0)
    report = check.evaluate(for_seconds=0.2)

    assert report, report.summary
    target = simulation.signal_graph().pin_target(button.pin_id)
    assert target.resolution_text.startswith("at model steps of"), target.resolution_text


def test_an_output_pin_is_refused_as_a_target_with_the_server_s_sentence(
    simulation: looper.Simulation,
) -> None:
    led = simulation.pin("LED_STATUS")

    with pytest.raises(looper.SimulationRefusedError) as refused:
        simulation.apply_signal_graph(_zero_cross(led.pin_id))

    assert str(refused.value) == (
        "LED_STATUS is an output of this firmware; the graph cannot drive it. Choose an input pin."
    )


def test_a_probe_records_on_its_own_clock_and_is_found_by_name(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        .generator("mains", MAINS)
        .operation("size", looper.SignalNodeKind.ABS, "mains")
        .probe("SIZE", "size", sample_us=1_000)
    )
    simulation.apply_signal_graph(graph)
    probe = simulation.probe("SIZE")

    check = simulation.expect()
    check.channel(probe.channel_id, probe.name).stays_between(0.0, 325.0)
    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary
    (outcome,) = report.outcomes
    samples = int(re.search(r"over (\d+) samples", outcome.observed).group(1))  # type: ignore[union-attr]
    assert samples >= 90, "a sample every millisecond, without an ADC read"
