"""Lesson 12, architecture and state machines (looper Pro).

The sources lie in ``app/``, ``drivers/`` and ``hal/``, and
``architecture.toml`` says each layer may use only the one below it. Two
findings are there on purpose: the application reads the button from the
HAL past the drivers, and the status LED and the temperature driver use each
other. The analysis finds 8 in all, every one new without a baseline.

Not checked here: the state machine diagram of ``unit_t.mode`` (4 states, 8
transitions), which looper-py cannot read.
"""

from __future__ import annotations

import os

import pytest

import looper

pytestmark = pytest.mark.tutorial

# The Architect is part of looper Pro. looper-cli is started from a checkout,
# where the development switch unlocks Pro, so no licence is needed here.
os.environ["LOOPER_DEV_EDITION"] = "pro"

LESSON = "12-architecture"


def test_the_findings_name_exactly_one_layer_violation(
    lesson_simulation: looper.Simulation,
) -> None:
    findings = lesson_simulation.findings()

    assert findings.is_complete, findings.note
    violations = findings.of_kind("rule violation")
    assert [one.modules for one in violations] == [("app/app", "hal/pins")]
    assert violations[0].severity == "critical"


def test_the_findings_name_exactly_one_cycle(lesson_simulation: looper.Simulation) -> None:
    findings = lesson_simulation.findings()

    cycles = findings.of_kind("cycle")
    assert [one.modules for one in cycles] == [("drivers/status_led", "drivers/temperature")]


def test_without_a_baseline_every_finding_is_new(lesson_simulation: looper.Simulation) -> None:
    findings = lesson_simulation.findings()

    assert len(findings.new()) == len(findings.findings) == 8
