"""A test reads the interrupt sources and raises one by its name."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper.application.simulation import Simulation


def _simulation() -> tuple[Simulation, ScriptedInspector]:
    inspector = ScriptedInspector()
    return Simulation(inspector), inspector


def test_the_sources_are_read_with_the_server_s_texts() -> None:
    simulation, _ = _simulation()

    interrupts = simulation.interrupts()

    assert interrupts.source("TIM2").kind_text == "timer, every 1 ms"
    assert interrupts.source("TIM2").handled == 9


def test_a_source_is_raised_by_its_name_now_or_later() -> None:
    simulation, inspector = _simulation()

    simulation.raise_interrupt("EXTI0")
    simulation.raise_interrupt("TIM2", after_us=500)

    assert inspector.raised == [(1, 0), (2, 500)]


def test_a_source_that_is_not_there_is_named() -> None:
    simulation, _ = _simulation()

    with pytest.raises(KeyError, match="EXTI9"):
        simulation.raise_interrupt("EXTI9")
