"""The checks of a firmware's interrupts, on the window's events and the server's findings."""

from __future__ import annotations

from looper.domain.checks.interrupt_checks import (
    HandledAtLeast,
    LatencyBelow,
    LockedAtMost,
    NeverLost,
    NoRunFindings,
    ShorterThanPeriod,
)
from looper.domain.model import Observation
from looper.domain.model.interrupt_facts import InterruptMark, RunFindingReading
from looper.domain.model.interrupts import Interrupts, InterruptSource

SOURCES = Interrupts(sources=(InterruptSource(1, "EXTI0"), InterruptSource(2, "TIM2")))


def _observed(*marks: InterruptMark, findings: tuple[RunFindingReading, ...] = ()) -> Observation:
    return Observation(
        samples=(),
        exchanges=(),
        timings=(),
        elapsed_seconds=0.01,
        interrupt_marks=marks,
        interrupts=SOURCES,
        run_findings=findings,
    )


def test_a_latency_below_its_limit_passes_and_one_above_fails() -> None:
    observed = _observed(
        InterruptMark(10, 1, "entered", latency_us=20),
        InterruptMark(20, 1, "entered", latency_us=70),
    )

    assert not LatencyBelow("EXTI0", 50).evaluate(observed).met
    assert LatencyBelow("EXTI0", 100).evaluate(observed).met


def test_a_lost_interrupt_fails_but_one_the_race_mode_raised_does_not() -> None:
    assert not NeverLost("TIM2").evaluate(_observed(InterruptMark(5, 2, "lost"))).met
    assert NeverLost("TIM2").evaluate(_observed(InterruptMark(5, 2, "lost", by_race=True))).met


def test_isrs_are_counted_by_their_entries() -> None:
    observed = _observed(*(InterruptMark(at, 2, "entered") for at in range(3)))

    assert HandledAtLeast("TIM2", 3).evaluate(observed).met
    assert not HandledAtLeast("TIM2", 4).evaluate(observed).met


def test_a_source_the_firmware_does_not_have_fails_and_says_so() -> None:
    outcome = NeverLost("EXTI9").evaluate(_observed())

    assert (outcome.met, outcome.observed) == (False, "no such interrupt source")


def test_the_lock_against_a_test_s_limit_or_the_project_s() -> None:
    locked = InterruptMark(2000, 0, "locked", duration_us=2000)
    finding = RunFindingReading("IRQ_LOCK_TOO_LONG", "Interrupts disabled for 2 ms (limit 1 ms)")

    assert not LockedAtMost(1000).evaluate(_observed(locked)).met
    assert LockedAtMost(5000).evaluate(_observed(locked)).met
    assert not LockedAtMost().evaluate(_observed(findings=(finding,))).met


def test_the_period_and_the_findings_are_the_server_s() -> None:
    too_long = RunFindingReading(
        "IRQ_LONGER_THAN_PERIOD", "TIM2's ISR ran 2 ms, longer than its period 1 ms"
    )

    assert not ShorterThanPeriod("TIM2").evaluate(_observed(findings=(too_long,))).met
    assert ShorterThanPeriod("EXTI0").evaluate(_observed(findings=(too_long,))).met
    assert not NoRunFindings().evaluate(_observed(findings=(too_long,))).met
    assert NoRunFindings(("IRQ_LOST",)).evaluate(_observed(findings=(too_long,))).met
