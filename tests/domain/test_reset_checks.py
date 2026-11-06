"""Expectations of the firmware's resets and of its flash, checked against an observation."""

from __future__ import annotations

from looper.domain.checks import NoFlashViolation, NoResetLoop, ResetHappened
from looper.domain.model import FlashMark, Observation, ResetMark

WATCHDOG = ResetMark(sim_us=120_000, cause="watchdog", life=1)
SOFTWARE = ResetMark(sim_us=300_000, cause="software", life=2)


def _observed(
    resets: tuple[ResetMark, ...] = (),
    flash_marks: tuple[FlashMark, ...] = (),
    loop_finding: str = "",
) -> Observation:
    return Observation(
        samples=(),
        exchanges=(),
        timings=(),
        elapsed_seconds=1.0,
        resets=resets,
        flash_marks=flash_marks,
        loop_finding=loop_finding,
    )


def test_a_reset_of_a_cause_is_found_among_the_window_s_resets() -> None:
    outcome = ResetHappened("watchdog").evaluate(_observed(resets=(WATCHDOG, SOFTWARE)))

    assert outcome.met
    assert "watchdog at 0.120000 s" in outcome.observed


def test_exactly_once_is_not_twice() -> None:
    outcome = ResetHappened(times=1).evaluate(_observed(resets=(WATCHDOG, SOFTWARE)))

    assert not outcome.met


def test_no_reset_at_all_says_so() -> None:
    outcome = ResetHappened().evaluate(_observed())

    assert not outcome.met
    assert outcome.observed == "no reset"


def test_a_reset_loop_is_the_server_s_finding() -> None:
    looping = _observed(loop_finding="Reset loop: 10 resets within 1 s (watchdog each time).")

    assert not NoResetLoop().evaluate(looping).met
    assert NoResetLoop().evaluate(_observed(resets=(WATCHDOG,))).met


def test_a_write_against_the_flash_s_rules_breaks_the_expectation() -> None:
    violation = FlashMark(sim_us=5, kind="violation", offset=0x3000, length=4, partition="config")
    written = FlashMark(sim_us=4, kind="write", offset=0x3000, length=4, partition="config")

    assert NoFlashViolation().evaluate(_observed(flash_marks=(written,))).met
    outcome = NoFlashViolation().evaluate(_observed(flash_marks=(written, violation)))
    assert not outcome.met
    assert outcome.observed == "at 0x3000 (config)"
