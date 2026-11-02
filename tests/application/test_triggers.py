"""Triggers a test arms, reads and disarms through a simulation."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import (
    Edge,
    Polarity,
    Simulation,
    SimulationRefusedError,
    TriggerMode,
    TriggerState,
)
from looper.application.triggers import client_name
from looper.domain.model import Trigger


def test_a_trigger_is_armed_in_the_name_of_this_process() -> None:
    inspector = ScriptedInspector()

    armed = Simulation(inspector).triggers.arm(Edge(4, Polarity.FALL), post_us=1_000)

    assert inspector.armed[0].condition == Edge(4, Polarity.FALL)
    assert inspector.armed[0].post_us == 1_000
    assert armed.armed_by == client_name()
    assert armed.mode is TriggerMode.SINGLE


def test_what_the_simulation_refuses_is_a_refusal_with_its_reason() -> None:
    inspector = ScriptedInspector()
    inspector.refusal = "Sequence triggers are not supported yet"

    with pytest.raises(SimulationRefusedError, match="not supported yet"):
        Simulation(inspector).triggers.arm(Edge(4))


def test_the_current_state_is_read_from_the_simulation_each_time() -> None:
    inspector = ScriptedInspector()
    triggers = Simulation(inspector).triggers
    armed = triggers.arm(Edge(4))

    inspector.fire(armed.trigger_id, at_us=2_500_000)
    now = triggers.current(armed)

    assert (armed.has_fired, now.has_fired) == (False, True)
    assert now.state is TriggerState.HELD
    assert now.last_fired_at_us == 2_500_000


def test_asking_for_a_trigger_the_simulation_does_not_hold_is_a_refusal() -> None:
    with pytest.raises(SimulationRefusedError, match="no trigger 9"):
        Simulation(ScriptedInspector()).triggers.current(9)


def test_only_this_processs_live_triggers_are_disarmed_as_its_own() -> None:
    inspector = ScriptedInspector()
    triggers = Simulation(inspector).triggers
    own = triggers.arm(Edge(4))
    window = inspector.arm_trigger(inspector.armed[0], "window 1")
    triggers.disarm(triggers.arm(Edge(17)))

    disarmed = triggers.disarm_own()

    assert [trigger.trigger_id for trigger in disarmed] == [own.trigger_id]
    assert [trigger.trigger_id for trigger in triggers.live()] == [window.trigger_id]


def test_a_trigger_is_disarmed_by_its_number_or_as_read() -> None:
    inspector = ScriptedInspector()
    triggers = Simulation(inspector).triggers
    first: Trigger = triggers.arm(Edge(4))
    second = triggers.arm(Edge(17))

    triggers.disarm(first)
    triggers.disarm(second.trigger_id)

    assert triggers.live() == ()
    assert {trigger.disarmed_by for trigger in triggers.all()} == {client_name()}
