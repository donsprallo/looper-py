"""The delay from one pin's edges to another's, expected through the port (#5, looper-srv#30)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from doubles import ScriptedInspector
from looper import Pin, Polarity, SimulationRefusedError
from looper.application.expectations import Expectations
from looper.domain.model.pwm import PinMeasurement

ZC = Pin(pin_id=4, name="ZC", level="low", is_drivable=True)
GATE = Pin(pin_id=17, name="GATE", level="low", is_drivable=False)
TEXT = "ZC↑ → GATE↑ 5.00 ms (4.95 ms – 5.05 ms, 10 delays)"


def _delayed(**fields: object) -> PinMeasurement:
    measured = PinMeasurement(
        17,
        0,
        100_000,
        reference_pin_id=4,
        delays=10,
        delay_min_us=4_950,
        delay_max_us=5_050,
        delay_mean_us=5_000.0,
        delay_text=TEXT,
    )
    return replace(measured, **fields)  # type: ignore[arg-type]


@pytest.fixture
def inspector() -> ScriptedInspector:
    """A dimmer's firmware: GATE answers each ZC after about 5 ms."""
    built = ScriptedInspector()
    built.description = replace(built.description, capabilities=("pin_measure", "pin_delay"))
    built.pins = (ZC, GATE)
    built.pin_delays = {(17, 4): _delayed()}
    return built


def test_a_delay_within_its_range_is_met_and_shows_the_server_s_text(
    inspector: ScriptedInspector,
) -> None:
    inspector.run = replace(inspector.run, now_us=10_000)
    check = Expectations(inspector)
    check.pin("GATE").after("ZC").between(4.9, 5.1, unit="ms")

    report = check.evaluate(for_seconds=0.1)

    assert report, report.summary
    (outcome,) = report.outcomes
    assert (outcome.subject, outcome.observed) == ("ZC↑ → GATE↑", TEXT)
    rise = (Polarity.RISE, Polarity.RISE)
    assert inspector.delay_asks == [(17, 4, 10_000, 110_000, rise)]


def test_the_edges_asked_for_go_to_the_server(inspector: ScriptedInspector) -> None:
    check = Expectations(inspector)
    gate = check.pin("GATE")
    gate.after("ZC", reference_edge=Polarity.FALL, edge=Polarity.ANY).between(0, 10_000)

    report = check.evaluate(for_seconds=0.1)

    assert inspector.delay_asks[0][4] == (Polarity.FALL, Polarity.ANY)
    assert report.outcomes[0].subject == "ZC↓ → GATE↕"


def test_a_delay_outside_its_range_fails(inspector: ScriptedInspector) -> None:
    check = Expectations(inspector)
    check.pin("GATE").after("ZC").between(4.0, 5.0, unit="ms")

    assert not check.evaluate(for_seconds=0.1)


def test_a_reference_edge_left_unanswered_fails_even_within_range(
    inspector: ScriptedInspector,
) -> None:
    missed = TEXT + " · 2 ZC↑ without GATE↑"
    inspector.pin_delays = {(17, 4): _delayed(delays_missed=2, delay_text=missed)}
    check = Expectations(inspector)
    check.pin("GATE").after("ZC").between(4.9, 5.1, unit="ms")

    report = check.evaluate(for_seconds=0.1)

    assert not report
    assert report.outcomes[0].observed == missed


def test_no_delay_at_all_fails_with_the_server_s_sentence(inspector: ScriptedInspector) -> None:
    none = "No GATE↑ followed a ZC↑ in the stretch."
    inspector.pin_delays = {(17, 4): _delayed(delays=0, delay_text=none)}
    check = Expectations(inspector)
    check.pin("GATE").after("ZC").between(0, 1, unit="s")

    report = check.evaluate(for_seconds=0.1)

    assert not report
    assert report.outcomes[0].observed == none


def test_a_reference_the_firmware_did_not_register_is_named(inspector: ScriptedInspector) -> None:
    check = Expectations(inspector)
    check.pin("GATE").after("MAINS").between(0, 1, unit="s")

    report = check.evaluate(for_seconds=0.1)

    assert not report
    assert "no pin named 'MAINS'; the firmware registered GATE, ZC" in report.summary


def test_a_server_that_does_not_measure_delays_refuses_the_window(
    inspector: ScriptedInspector,
) -> None:
    inspector.description = replace(inspector.description, capabilities=("pin_measure",))
    check = Expectations(inspector)
    check.pin("GATE").after("ZC").between(0, 1, unit="s")

    with pytest.raises(SimulationRefusedError, match="CAPABILITY_PIN_DELAY"):
        check.evaluate(for_seconds=0.1)


def test_a_delay_in_an_unknown_unit_is_refused_before_the_window(
    inspector: ScriptedInspector,
) -> None:
    with pytest.raises(ValueError, match="us, ms or s, not min"):
        Expectations(inspector).pin("GATE").after("ZC").between(1, 2, unit="min")
