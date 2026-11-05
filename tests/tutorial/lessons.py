"""What the tutorial's checkpoint tests share: where the lessons are, and small steps.

The tutorial in looper-core (``examples/tutorial``) has one folder per
lesson, and every "what you should see" of a lesson is a claim about the
simulation. These tests make each claim once more, through the contract, the
way a reader of lesson 11 would. They build the lesson's own folder -- into
its ``build/``, which git ignores -- and run it on a held clock, so every run
sees the same numbers.

They need a looper-core checkout beside this one (``LOOPER_CORE`` points at
one elsewhere) and a C compiler, and skip without them.
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import pytest

import looper

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("LOOPER_CORE", PROJECT_ROOT.parent / "looper-core"))
TUTORIAL = CORE / "examples" / "tutorial"

#: looper-cli from the neighbouring checkout, run as a module so that the
#: tests do not depend on its console script being installed.
LOOPER_CLI = (
    "uv",
    "run",
    "--no-sync",
    "--project",
    str(CORE),
    "python",
    "-m",
    "looper_core.presentation.cli.main",
)

#: The modes as the firmware's fan_mode_t (lesson 7 on) and its macros (2-6) count them.
MODE_OFF = 0
MODE_AUTO = 1
MODE_BOOST = 2
MODE_FAULT = 3

#: How long the server may take to have written the events of a window down.
EVENT_LOG_SECONDS = 0.3


def definition_of(lesson: str) -> Path:
    """The build definition of one lesson's folder, or a skip when there is none to build."""
    definition = TUTORIAL / lesson / "looper.toml"
    if not definition.is_file():
        pytest.skip(f"no tutorial lesson at {definition.parent}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    return definition


def watch(simulation: looper.Simulation, path: str) -> int:
    """Watch a variable by its path, and give the channel the watch samples on."""
    variable = next(one for one in simulation.variables() if one.path == path)
    return simulation.watch_variable(variable.variable_id).channel_id


def value_of(simulation: looper.Simulation, channel_id: int) -> float:
    """What a watch holds now."""
    return next(one.value for one in simulation.watches() if one.channel_id == channel_id)


def press(simulation: looper.Simulation, seconds: float) -> None:
    """Hold the mode button down for a while and let go; it is active low."""
    button = simulation.pin("BUTTON_MODE").pin_id
    simulation.toggle_pin(button)
    simulation.advance(seconds)
    simulation.toggle_pin(button)


def channel_value(simulation: looper.Simulation, name: str) -> float:
    """An analog channel's value now."""
    return simulation.channel(name).value


def pin_level(simulation: looper.Simulation, name: str) -> str:
    """A pin's level now, ``high`` or ``low``."""
    return simulation.pin(name).level


def sample(
    simulation: looper.Simulation, names: tuple[str, ...], seconds: float, step_seconds: float
) -> list[tuple[float, dict[str, float]]]:
    """Let time pass in steps and read channels after each: (seconds, value by name)."""
    samples = []
    for _ in range(round(seconds / step_seconds)):
        simulation.advance(step_seconds)
        values = {one.name: one.value for one in simulation.channels() if one.name in names}
        samples.append((simulation.simulated_seconds, values))
    return samples


def type_into_terminal(simulation: looper.Simulation, text: str, wait_seconds: float = 0.05) -> str:
    """Type a line into the terminal on UART1, and give what the firmware wrote back."""
    uart = simulation.bus("UART1").bus_id
    since = simulation.run_state().next_event_seq
    simulation.send_bus_message(looper.BusMessage(uart, 0, text.encode()))
    simulation.advance(wait_seconds)
    time.sleep(EVENT_LOG_SECONDS)
    written = (
        one.payload
        for one in simulation.exchanges(since)
        if one.bus_id == uart and one.direction == "outbound"
    )
    return b"".join(written).decode()


def room_in_the_loop(simulation: looper.Simulation, heat_watts: float = 40.0) -> None:
    """Close the loop of lesson 5: heat and the fan duty into the room, the room into the sensor."""
    graph = (
        looper.SignalGraph()
        .generator("heat", looper.Signal(offset=heat_watts))
        .channel("duty", simulation.channel("FAN_DUTY").channel_id)
        .model("room", "Room", inputs=("heat", "duty"))
        .drive(simulation.channel("TEMP_SENSOR").channel_id, "room")
    )
    simulation.apply_signal_graph(graph)
