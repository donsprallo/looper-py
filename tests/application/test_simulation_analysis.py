"""The profile, the architecture findings and the signal graph, through the port."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import (
    Findings,
    Profile,
    ProfileEntry,
    SignalGraph,
    SignalModel,
    Simulation,
    SimulationRefusedError,
)
from looper.application import findings_reading
from looper.application.expectations import Expectations

MEDIAN = ProfileEntry("median_filter", "firmware", 1000, 700, 900, "src/filter.c", 12)
STEP = ProfileEntry("app_step", "firmware", 1000, 300, 1200, "src/app.c", 40)


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Look at the findings again at once, so that waiting costs the test nothing."""
    monkeypatch.setattr(findings_reading, "POLL_SECONDS", 0.0)


def test_the_profile_is_read_as_it_stands() -> None:
    inspector = ScriptedInspector()
    inspector.profile = Profile(functions=(STEP, MEDIAN), is_profiling=True)

    profile = Simulation(inspector).profile()

    assert profile.heaviest_first() == (MEDIAN, STEP)


def test_findings_are_read_again_until_every_file_is_read() -> None:
    inspector = ScriptedInspector()
    inspector.findings = [Findings(note="partial"), Findings(is_complete=True)]

    findings = Simulation(inspector).findings()

    assert findings.is_complete
    assert inspector.asked.count("read findings") == 2


def test_findings_still_partial_when_the_time_is_up_come_back_as_they_are() -> None:
    inspector = ScriptedInspector()
    inspector.findings = [Findings(note="partial")]

    findings = Simulation(inspector).findings(wait_seconds=0.0)

    assert not findings.is_complete
    assert findings.note == "partial"


def test_a_server_that_does_not_read_the_code_says_how_to_start_one_that_does() -> None:
    inspector = ScriptedInspector()
    inspector.findings = None

    with pytest.raises(SimulationRefusedError, match="looper-cli run") as refused:
        Simulation(inspector).findings()
    assert "does not read the project's code" in str(refused.value)


def test_a_graph_reaches_the_simulation_as_it_was_built() -> None:
    inspector = ScriptedInspector()
    graph = SignalGraph().channel("voltage", 5).model("motor", "DcMotor", ["voltage"])

    Simulation(inspector).apply_signal_graph(graph.drive(3, "motor"))

    assert inspector.graphs == [graph.drive(3, "motor")]


def test_a_graph_the_simulation_refuses_is_a_refusal_with_its_reason() -> None:
    inspector = ScriptedInspector()
    inspector.refusal = "model Nothing is not in the models directory"

    with pytest.raises(SimulationRefusedError, match="Nothing"):
        Simulation(inspector).apply_signal_graph(SignalGraph().model("m", "Nothing"))


def test_a_model_is_found_by_name_and_a_missing_one_lists_the_others() -> None:
    inspector = ScriptedInspector()
    inspector.models = (SignalModel("DcMotor"), SignalModel("LowPass"))
    simulation = Simulation(inspector)

    assert simulation.model("LowPass").name == "LowPass"
    with pytest.raises(SimulationRefusedError, match="offers no model named 'Pump'.*DcMotor"):
        simulation.model("Pump")


def test_a_simulation_without_models_refuses_to_list_them() -> None:
    inspector = ScriptedInspector()
    inspector.models = None

    with pytest.raises(SimulationRefusedError, match="no models directory"):
        Simulation(inspector).models()


def test_an_expectation_on_the_profile_checks_the_profile_of_the_window() -> None:
    inspector = ScriptedInspector()
    inspector.profile = Profile(functions=(STEP, MEDIAN), is_profiling=True)
    check = Expectations(inspector)
    check.profile().heaviest_is("median_filter")

    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary
    assert inspector.asked.index("clear measurements") < inspector.asked.index("read profile")


def test_a_window_without_an_expectation_on_the_profile_does_not_read_it() -> None:
    inspector = ScriptedInspector()
    check = Expectations(inspector)
    check.firmware_is_alive()

    check.evaluate(for_seconds=0.1)

    assert "read profile" not in inspector.asked
