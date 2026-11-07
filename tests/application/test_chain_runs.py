"""Running until a chain's Sequence passes or fails, through the port."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import SequenceProgress, SequenceState, Simulation


def _state(progress: SequenceProgress, failure_text: str = "") -> SequenceState:
    return SequenceState(
        "test", "boost", "Boost test", progress, step_text="▸ step 1", failure_text=failure_text
    )


def test_the_run_stops_once_the_sequence_is_done() -> None:
    inspector = ScriptedInspector()
    running = _state(SequenceProgress.RUNNING)
    inspector.sequence_states = [(running,), (running,), (_state(SequenceProgress.DONE),)]

    result = Simulation(inspector).run_until_chain("Boost test", timeout_s=1.0)

    assert result
    assert result.failure_text == ""
    assert [one for one in inspector.asked if one.startswith("advance")] == ["advance 10000"] * 2


def test_a_failed_sequence_says_why_in_the_server_s_words() -> None:
    inspector = ScriptedInspector()
    failure = "Failed at step 2: lit did not come within 200 ms · 0.210000 s"
    inspector.sequence_states = [(_state(SequenceProgress.FAILED, failure),)]

    result = Simulation(inspector).run_until_chain("boost")

    assert not result.passed
    assert result.failure_text == failure


def test_time_running_out_fails_the_run() -> None:
    inspector = ScriptedInspector()
    inspector.sequence_states = [(_state(SequenceProgress.RUNNING),)]

    result = Simulation(inspector).run_until_chain("Boost test", timeout_s=0.025)

    assert not result
    assert "neither passed nor failed within 0.025 s" in result.failure_text
    advanced = [one for one in inspector.asked if one.startswith("advance")]
    assert advanced == ["advance 10000", "advance 10000", "advance 5000"]


def test_a_chain_without_a_sequence_cannot_be_run_until_it_ends() -> None:
    with pytest.raises(ValueError, match="no Sequence"):
        Simulation(ScriptedInspector()).run_until_chain("Echo")
