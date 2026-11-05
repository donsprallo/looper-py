"""Lesson 8, the panel and pages of one's own.

The firmware does not change; the lesson's window project
``tutorial-project.toml`` is new. What the window shows of it cannot be
checked from here (the window has no report of its pages yet), but every
name the project binds to can: a variable, pin, channel, bus or model it
names that the simulation does not have would leave a control unbound.
"""

from __future__ import annotations

import tomllib
from typing import Any

import pytest

import looper
from tutorial.lessons import TUTORIAL, watch

pytestmark = pytest.mark.tutorial

LESSON = "08-panel"


def project() -> dict[str, Any]:
    """The lesson's window project, as its file says."""
    with (TUTORIAL / LESSON / "tutorial-project.toml").open("rb") as file:
        return tomllib.load(file)


def test_every_variable_the_project_names_is_in_the_build(
    lesson_simulation: looper.Simulation,
) -> None:
    named = {one["path"] for one in project()["variables"]}
    named |= {one["variable"] for one in project()["panels"][0]["controls"]}

    known = {one.path for one in lesson_simulation.variables()}

    assert named <= known, named - known


def test_every_pin_channel_and_bus_it_names_is_registered(
    lesson_simulation: looper.Simulation,
) -> None:
    lanes = project()["analyzers"][0]["lanes"]
    traces = [trace for scope in project()["scopes"] for trace in scope["traces"]]

    assert {one["pin"] for one in lanes if "pin" in one} <= {
        p.name for p in lesson_simulation.pins()
    }
    channels = {one["channel"] for one in [*lanes, *traces] if "channel" in one}
    assert channels <= {one.name for one in lesson_simulation.channels()}
    assert {one["bus"] for one in lanes if "bus" in one} <= {
        b.name for b in lesson_simulation.buses()
    }


def test_its_signal_graph_uses_a_model_the_project_offers(
    lesson_simulation: looper.Simulation,
) -> None:
    models = [one for one in project()["signal_graph"]["nodes"] if one["kind"] == "model"]

    for node in models:
        model = lesson_simulation.model(node["name"])
        assert set(node["parameters"]) <= {one.name for one in model.parameters}


def test_the_panel_slider_moves_the_setpoint_on_the_scope(
    lesson_simulation: looper.Simulation,
) -> None:
    slider = next(one for one in project()["panels"][0]["controls"] if one["kind"] == "slider")
    lesson_simulation.advance(0.5)

    lesson_simulation.write_variable(watch(lesson_simulation, slider["variable"]), 30.0)
    lesson_simulation.advance(0.05)

    assert lesson_simulation.channel("SETPOINT").value == 30.0
