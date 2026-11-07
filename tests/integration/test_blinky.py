"""The blinky test firmware of looper-core, run and checked from a test.

The whole path a user takes: looper-cli builds the firmware, starts it on a
virtual clock and serves it; this library attaches, sets the scene and
expects things of it. The firmware blinks every 500 ms, and every 100 ms
while the button is pressed.

Needs a looper-core checkout beside this one and a C compiler, and skips
without them. ``LOOPER_CORE`` points at a checkout elsewhere.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

import looper

# The findings are part of looper Pro. looper-cli is started from a checkout,
# where the development switch unlocks Pro, so no licence is needed here.
os.environ["LOOPER_DEV_EDITION"] = "pro"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))
DEFINITION = CORE / "tests" / "fixtures" / "blinky" / "looper.toml"

#: looper-cli from the neighbouring checkout, run as a module so that the
#: test does not depend on its console script being installed.
LOOPER_CLI = ("uv", "run", "--no-sync", "--project", str(CORE), "python", "-m")
CLI_MODULE = "looper_core.presentation.cli.main"


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """The blinky example, built, started on a held clock and attached to."""
    if not DEFINITION.is_file():
        pytest.skip(f"no looper-core checkout at {CORE}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, looper_cli=(*LOOPER_CLI, CLI_MODULE)) as started:
        yield started


def test_the_server_says_what_it_runs(simulation: looper.Simulation) -> None:
    assert simulation.firmware_name == "blinky"
    assert simulation.clock_mode is looper.ClockMode.HELD
    assert Path(simulation.definition_path) == DEFINITION.resolve()


def test_the_clock_stands_still_until_time_is_let_pass(simulation: looper.Simulation) -> None:
    before = simulation.simulated_seconds

    assert simulation.simulated_seconds == before
    simulation.advance(0.5)
    assert simulation.simulated_seconds - before == pytest.approx(0.5, abs=0.001)


def test_the_led_blinks_and_the_firmware_stays_shallow(simulation: looper.Simulation) -> None:
    check = simulation.expect()
    check.firmware_is_alive()
    check.call("adapter_blinky_gpio_set").happened_at_least(2)
    check.stack().no_deeper_than(64)

    report = check.evaluate(for_seconds=1.0)

    assert report, report.summary


def test_pressing_the_button_makes_it_blink_faster(simulation: looper.Simulation) -> None:
    button = next(pin for pin in simulation.pins() if pin.name == "BUTTON_MODE")
    pressed = simulation.toggle_pin(button.pin_id)

    check = simulation.expect()
    check.call("adapter_blinky_gpio_set").happened_at(10.0, tolerance=0.05)
    report = check.evaluate(for_seconds=2.0)

    simulation.toggle_pin(button.pin_id)
    assert report, f"button driven {pressed}\n{report.summary}"


def test_a_single_trigger_holds_the_run_just_after_the_led_changes(
    simulation: looper.Simulation,
) -> None:
    led = simulation.pin("LED_STATUS")
    trigger = simulation.triggers.arm(looper.Edge(led.pin_id), post_us=1_000)
    try:
        simulation.advance(2.0)
        fired = simulation.triggers.current(trigger)
        held_at_us = round(simulation.simulated_seconds * 1_000_000)
    finally:
        simulation.triggers.disarm_own()

    assert fired.state is looper.TriggerState.HELD
    assert fired.fires == 1
    assert held_at_us == fired.last_fired_at_us + 1_000


def test_a_normal_trigger_counts_every_edge_and_lets_the_run_go_on(
    simulation: looper.Simulation,
) -> None:
    led = simulation.pin("LED_STATUS")
    rising = looper.Edge(led.pin_id, looper.Polarity.RISE)
    trigger = simulation.triggers.arm(rising, mode=looper.TriggerMode.NORMAL)
    before = simulation.simulated_seconds
    try:
        simulation.advance(2.0)
        counted = simulation.triggers.current(trigger)
    finally:
        simulation.triggers.disarm_own()

    assert simulation.simulated_seconds - before == pytest.approx(2.0, abs=0.001)
    assert counted.fires >= 2
    assert counted.state is looper.TriggerState.ARMED


def test_the_profile_ranks_the_application_step_heaviest_of_the_firmware(
    simulation: looper.Simulation,
) -> None:
    check = simulation.expect()
    check.profile().heaviest_is("app_step")

    report = check.evaluate(for_seconds=0.5)
    app_step = simulation.profile().entry("app_step")

    assert report, report.summary
    assert app_step is not None
    assert app_step.calls >= 400
    assert Path(app_step.source_path).name == "app.c"


def test_the_architecture_holds_no_finding_the_baseline_does_not(
    simulation: looper.Simulation,
) -> None:
    findings = simulation.findings()

    assert findings.is_complete, findings.note
    assert findings.findings
    assert findings.new() == (), [one.title for one in findings.new()]


def test_a_motor_model_closes_the_loop_around_the_speed_controller(
    simulation: looper.Simulation,
) -> None:
    motor = simulation.model("DcMotor")
    voltage = simulation.channel("MOTOR_VOLTAGE")
    graph = (
        looper.SignalGraph()
        .generator("setpoint", looper.Signal("constant", offset=100.0))
        .generator("no load", looper.Signal("constant"))
        .channel("voltage", voltage.channel_id)
        .model("motor", motor.name, inputs=["voltage", "no load"])
        .drive(simulation.channel("SPEED_SETPOINT").channel_id, "setpoint")
        .drive(simulation.channel("MOTOR_SPEED").channel_id, "motor", motor.output("speed"))
    )
    simulation.apply_signal_graph(graph)
    try:
        simulation.advance(0.5)
        speed = simulation.channel("MOTOR_SPEED").value
    finally:
        simulation.apply_signal_graph(looper.SignalGraph())

    assert speed > 1.0


def test_a_chain_marks_every_rise_of_the_led_inside_the_simulation(
    simulation: looper.Simulation,
) -> None:
    led = simulation.pin("LED_STATUS")
    graph = (
        looper.SignalGraph()
        .when("rises", looper.Edge(led.pin_id, looper.Polarity.RISE), group="echo")
        .mark("noted", "LED on", after="rises", group="echo")
        .group("echo", "Echo")
    )
    simulation.apply_signal_graph(graph)
    try:
        simulation.advance(2.0)
        states = {state.key: state for state in simulation.chains()}
    finally:
        simulation.apply_signal_graph(looper.SignalGraph())

    assert states["rises"].fires >= 2
    assert states["noted"].fires == states["rises"].fires
    assert states["rises"].summary_text == "LED_STATUS rises"
