"""Expecting things of a run, and what the report says when they fail.

A check that only says "failed" sends someone back to the simulation with
prints. Every outcome here carries what was expected and what was seen, so
these tests are as much about the wording of a failure as about the
arithmetic behind it.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from doubles import ScriptedInspector
from looper.application.expectations import Expectations
from looper.domain.model import (
    CallTiming,
    Exchange,
    HeapUsage,
    MemoryUsage,
    Recordings,
    Sample,
    TimeMode,
)


def samples_of(channel: int, values: tuple[float, ...]) -> tuple[Sample, ...]:
    """One channel's samples, a millisecond apart."""
    return tuple(
        Sample(channel_id=channel, seconds=index / 1000, value=value, sequence=index)
        for index, value in enumerate(values)
    )


def an_exchange(sequence: int, accepted: bool = True) -> Exchange:
    """One recorded CAN frame on bus two."""
    return Exchange(bus_id=2, seconds=0.0, address="0x701", accepted=accepted, sequence=sequence)


@pytest.fixture
def inspector() -> ScriptedInspector:
    """A simulation that has already recorded a second of a run."""
    built = ScriptedInspector()
    built.samples = samples_of(0, (0.0, 0.5, 1.0, 1.0))
    built.exchanges = (an_exchange(0), an_exchange(1))
    built.timings = (CallTiming("adapter_spi_transfer_blocking", 8000, 8000),)
    return built


def expect(inspector: ScriptedInspector) -> Expectations:
    return Expectations(inspector, inspector.description.time_mode)


def test_a_channel_inside_its_range_passes(inspector: ScriptedInspector) -> None:
    check = expect(inspector)
    check.channel(0, "P1A").stays_between(0.0, 2.0)

    assert check.evaluate(for_seconds=1.0)


def test_every_page_of_a_recording_is_read(inspector: ScriptedInspector) -> None:
    """A check that counted one page would measure the page size, not the run."""
    check = expect(inspector)
    check.channel(0, "P1A").stays_between(0.0, 0.7)

    report = check.evaluate(for_seconds=1.0)

    assert not report
    assert "saw 0 .. 1 over 4 samples" in report.failures[0].line


def test_a_channel_that_was_never_recorded_fails_rather_than_passing(
    inspector: ScriptedInspector,
) -> None:
    """An expectation nothing could test is not an expectation that was met."""
    check = expect(inspector)
    check.channel(99, "absent").stays_between(0.0, 1.0)

    assert "nothing recorded" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_channel_that_arrives_too_late_says_how_long_it_took(
    inspector: ScriptedInspector,
) -> None:
    check = expect(inspector)
    check.channel(0, "P1A").reaches(1.0, tolerance=0.01, within_seconds=0.001)

    assert "reached after 0.002 s" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_channel_that_never_arrives_says_how_close_it_came(
    inspector: ScriptedInspector,
) -> None:
    check = expect(inspector)
    check.channel(0, "P1A").reaches(5.0, tolerance=0.01)

    assert "never closer than 1" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_refused_exchange_names_the_address(inspector: ScriptedInspector) -> None:
    inspector.exchanges = (an_exchange(0), an_exchange(1, accepted=False))
    check = expect(inspector)
    check.bus(2, "CAN2").nothing_refused()

    assert "1 of 2 refused at 0x701" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_call_nothing_answers_is_the_failure_it_should_be(
    inspector: ScriptedInspector,
) -> None:
    """The firmware was handed the zero value and believed it."""
    inspector.timings = (CallTiming("adapter_can_init", 1, 0),)
    check = expect(inspector)
    check.call("adapter_can_init").was_answered()

    assert "0 of 1 answered" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_rate_is_worked_out_from_the_time_that_passed(inspector: ScriptedInspector) -> None:
    check = expect(inspector)
    check.call("adapter_spi_transfer_blocking").happened_at(8000, tolerance=0.05)

    assert check.evaluate(for_seconds=1.0)


def test_a_firmware_making_no_calls_at_all_is_caught(inspector: ScriptedInspector) -> None:
    inspector.timings = ()

    assert not expect(inspector).firmware_is_alive().evaluate(for_seconds=1.0)


def test_the_recordings_are_cleared_before_the_window_and_the_clock_moved(
    inspector: ScriptedInspector,
) -> None:
    """A check must see its own window, not whatever happened before it."""
    expect(inspector).firmware_is_alive().evaluate(for_seconds=0.25)

    assert inspector.asked == ["clear recordings", "clear measurements", "advance 250000"]


def test_on_the_host_clock_the_window_is_waited_out(inspector: ScriptedInspector) -> None:
    inspector.description = replace(inspector.description, time_mode=TimeMode.REAL_TIME)

    expect(inspector).firmware_is_alive().evaluate(for_seconds=0.01)

    assert not any(one.startswith("advance") for one in inspector.asked)


def test_a_heap_that_was_used_is_reported_in_bytes(inspector: ScriptedInspector) -> None:
    inspector.memory = MemoryUsage(heap=HeapUsage(allocations=2, peak_bytes=96, is_watched=True))
    check = expect(inspector)
    check.memory().peak_below(64)

    assert "96 bytes at the peak" in check.evaluate(for_seconds=1.0).failures[0].line


def test_a_build_that_cannot_be_read_says_the_heap_is_not_watched(
    inspector: ScriptedInspector,
) -> None:
    """A refusal of the memory reading is not a broken simulation."""
    inspector.memory = None
    check = expect(inspector)
    check.memory().never_allocates()

    assert "not being watched" in check.evaluate(for_seconds=1.0).failures[0].line


def test_the_report_lists_the_failures_first(inspector: ScriptedInspector) -> None:
    check = expect(inspector)
    check.firmware_is_alive()
    check.channel(0, "P1A").stays_between(0.0, 0.1)

    summary = check.evaluate(for_seconds=1.0).summary

    assert summary.splitlines()[0] == "1 of 2 met"
    assert summary.splitlines()[1].startswith("FAIL")


def test_nothing_expected_is_said_rather_than_silently_passing(
    inspector: ScriptedInspector,
) -> None:
    assert expect(inspector).evaluate(for_seconds=1.0).summary == "nothing was expected"


class GrowingInspector(ScriptedInspector):
    """A firmware that keeps recording while it is read, as one on a free clock does."""

    def read_recordings(self, after_sample: int, after_exchange: int) -> Recordings:
        page = super().read_recordings(after_sample, after_exchange)
        sequence = len(self.samples)
        self.samples = (*self.samples, Sample(0, sequence / 1000, 1.0, sequence))
        return page


def test_a_recording_that_keeps_growing_is_read_to_where_it_stood() -> None:
    """A reader chasing a running firmware would never finish."""
    inspector = GrowingInspector()
    inspector.samples = samples_of(0, (0.0, 0.5, 1.0, 1.0))
    check = expect(inspector)
    check.channel(0, "P1A").stays_between(0.0, 2.0)

    report = check.evaluate(for_seconds=1.0)

    assert "over 4 samples" in report.outcomes[0].line
