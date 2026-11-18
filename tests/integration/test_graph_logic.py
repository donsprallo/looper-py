"""Generators that move and signal logic on blinky's input pins, run in looper-srv (#5).

A pulse with a duty, a pulse whose frequency another node gives, a table
played from points and from a CSV the server reads, a select switching
between two pulses, a sample and hold node, a pin that holds pulses for a
model, the delay from one driven pin to another, and the starters the
server lists (looper-srv#29, #30).

Needs a looper-docs checkout beside this one, a C compiler, and a
looper-srv whose runtime moves generators and selects; skips without them.
``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"
NEEDED = {"moving_generators", "signal_logic", "pin_delay"}


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky, built, started on a held clock and attached to, for this module alone."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        missing = NEEDED - set(started.description.capabilities)
        if missing:
            pytest.skip(f"the server's runtime lacks {sorted(missing)}")
        yield started


@pytest.fixture
def button(simulation: looper.Simulation) -> Iterator[looper.Pin]:
    """The button pin, an input; the graph is taken away afterwards."""
    yield simulation.pin("BUTTON_MODE")
    simulation.apply_signal_graph(looper.SignalGraph())


def _pulses_on(pin: looper.Pin, signal: looper.Signal) -> looper.SignalGraph:
    return looper.SignalGraph().generator("wave", signal).drive_pin(pin.pin_id, "wave")


def test_a_pulse_with_a_duty_drives_the_pin_a_quarter_of_each_period(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    simulation.apply_signal_graph(_pulses_on(button, looper.Signal.pulse(0.0, 1.0, 100.0, 0.25)))

    check = simulation.expect()
    check.pin("BUTTON_MODE").frequency_between(99.0, 101.0)
    check.pin("BUTTON_MODE").pulse_width_between(2_450, 2_550, unit="us")
    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary


def test_a_linked_frequency_follows_the_node_that_gives_it(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        .value("rate", 200.0)
        .generator("gate", looper.Signal.pulse(0.0, 1.0, 1.0), frequency="rate")
        .drive_pin(button.pin_id, "gate")
    )
    simulation.apply_signal_graph(graph)

    fast = simulation.expect()
    fast.pin("BUTTON_MODE").frequency_between(199.0, 201.0)
    assert (report := fast.evaluate(for_seconds=0.05)), report.summary

    simulation.set_graph_value("rate", 50.0)
    simulation.advance(0.04)
    slow = simulation.expect()
    slow.pin("BUTTON_MODE").frequency_between(49.0, 51.0)
    assert (report := slow.evaluate(for_seconds=0.1)), report.summary


def _played(
    simulation: looper.Simulation, signal: looper.Signal, high_us: int
) -> looper.ExpectationReport:
    """Repeated every 10 ms, high for `high_us` of each, if the table is played as written."""
    simulation.apply_signal_graph(_pulses_on(simulation.pin("BUTTON_MODE"), signal))
    check = simulation.expect()
    check.pin("BUTTON_MODE").frequency_between(99.0, 101.0)
    check.pin("BUTTON_MODE").pulse_width_between(high_us - 10, high_us + 10, unit="us")
    return check.evaluate(for_seconds=0.1)


def test_a_table_is_played_step_by_step_and_repeated(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    table = looper.Signal.table([(0.0, 1.0), (0.003, 0.0), (0.01, 0.0)], between="steps")

    report = _played(simulation, table, high_us=3_000)

    assert report, report.summary


def test_a_csv_is_read_by_the_server_and_played(
    simulation: looper.Simulation, button: looper.Pin, tmp_path: Path
) -> None:
    recording = tmp_path / "gate.csv"
    recording.write_text("time,level\ns,V\n0,1\n0.003,0\n0.01,0\n", encoding="utf-8")

    read = simulation.read_table(recording, unit="V")
    # Straight lines between the points: from 1 at 0 s down to 0 at 3 ms, so 0.5 at 1.5 ms.
    report = _played(simulation, looper.Signal.from_csv(recording, simulation), high_us=1_500)

    assert (read.rows, read.columns, read.problem_text) == (3, ("time", "level"), "")
    assert read.summary_text.startswith("3 points")
    assert report, report.summary


def test_a_csv_that_cannot_be_played_says_why(
    simulation: looper.Simulation, tmp_path: Path
) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("0,1\n0.5,abc\n", encoding="utf-8")

    with pytest.raises(ValueError, match="broken.csv, line 2"):
        looper.Signal.from_csv(broken, simulation)


def test_a_select_passes_the_input_its_level_chooses(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        .value("choose", 1.0)
        .generator("fast", looper.Signal.pulse(0.0, 1.0, 200.0))
        .generator("slow", looper.Signal.pulse(0.0, 1.0, 50.0))
        .select("sel", "choose", "fast", "slow")
        .drive_pin(button.pin_id, "sel")
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(0.01)
    assert simulation.signal_graph().node("sel").passing_port == "when 1"

    simulation.set_graph_value("choose", 0.0)
    simulation.advance(0.02)
    check = simulation.expect()
    check.pin("BUTTON_MODE").frequency_between(49.0, 51.0)
    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary
    assert simulation.signal_graph().node("sel").passing_port == "when 0"


def test_a_sample_and_hold_takes_the_sine_at_each_rising_trigger(
    simulation: looper.Simulation,
) -> None:
    graph = (
        looper.SignalGraph()
        .generator("sine", looper.Signal("sine", 1.0, frequency_hz=50.0))
        .generator("trigger", looper.Signal.pulse(0.0, 1.0, 200.0, phase_degrees=45.0))
        .sample_hold("sh", "sine", "trigger", mode=looper.SampleMode.RISING, initial=-2.0)
        .probe("held", "sh")
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(0.02)

    held = simulation.signal_graph().node("sh")

    assert held.samples == 4, "a rising trigger every 5 ms"
    assert held.value is not None and -1.0 <= held.value <= 1.0
    assert held.sampled_us > 0
    assert held.value_text


def test_a_pin_that_holds_pulses_reaches_a_model_between_its_steps(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        # High from 30 us to 50 us of every millisecond: between two steps of 100 us.
        .generator("gate", looper.Signal.pulse(0.0, 1.0, 1000.0, 0.02, 10.8))
        .drive_pin(button.pin_id, "gate")
        .pin("held", button.pin_id, hold_pulses=True)
        .pin("plain", button.pin_id)
        .model("caught", "FirstOrderLag", inputs=["held"])
        .model("missed", "FirstOrderLag", inputs=["plain"])
        .probe("caught", "caught", sample_us=1_000)
        .probe("missed", "missed", sample_us=1_000)
    )
    simulation.apply_signal_graph(graph)
    caught, missed = simulation.probe("caught"), simulation.probe("missed")

    check = simulation.expect()
    check.channel(caught.channel_id, caught.name).stays_between(0.0, 0.0)
    check.channel(missed.channel_id, missed.name).stays_between(0.0, 0.0)
    report = check.evaluate(for_seconds=0.01)

    assert [outcome.met for outcome in report.outcomes] == [False, True], report.summary


def test_the_gate_follows_the_zero_cross_after_its_delay(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    gate = simulation.pin("MCP_2")
    graph = (
        looper.SignalGraph()
        .generator("zc", looper.Signal.pulse(0.0, 1.0, 100.0, 0.1))
        .generator("gate", looper.Signal.pulse(0.0, 1.0, 100.0, 0.05, phase_degrees=90.0))
        .drive_pin(button.pin_id, "zc")
        .drive_pin(gate.pin_id, "gate")
    )
    simulation.apply_signal_graph(graph)

    check = simulation.expect()
    check.pin("MCP_2").after("BUTTON_MODE").between(7.4, 7.6, unit="ms")
    check.pin("MCP_2").after("BUTTON_MODE").between(2.4, 2.6, unit="ms")
    report = check.evaluate(for_seconds=0.05)

    within, outside = report.outcomes
    assert within.met, report.summary
    assert within.observed.startswith("BUTTON_MODE↑ → MCP_2↑ 7.50 ms")
    assert not outside.met


def test_the_starters_are_listed_and_available_on_blinky(simulation: looper.Simulation) -> None:
    starters = simulation.starters()

    assert starters.names == ("mains_zero_cross", "frequency_sweep", "phase_angle_dimmer")
    assert all(starter.is_available for starter in starters), starters
    dimmer = starters.named("phase_angle_dimmer")
    assert "Triac" in dimmer.needs.models
    assert dimmer.graph_text.startswith("{")
