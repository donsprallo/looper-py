"""Lesson 9, profile, timing and memory, with two bugs to find.

The build is woven for the profile and tracks the allocator. Two bugs are in
this lesson's folder, and its fix.patch removes both:

- the running median copies and bubble-sorts its 63 readings on every
  sample, so ``sort`` leads the profile (26 of 43 ms of self time in a
  measurement);
- a terminal command that fails never frees its log entry, so 20 such
  commands leave 20 blocks on the heap.
"""

from __future__ import annotations

import pytest

import looper
from tutorial.lessons import room_in_the_loop, type_into_terminal

pytestmark = pytest.mark.tutorial

LESSON = "09-profile-and-memory"


def bad_commands(simulation: looper.Simulation, count: int) -> None:
    """Commands the terminal does not know, ten to a message, to be read in the next pass."""
    uart = simulation.bus("UART1").bus_id
    for _ in range(count // 10):
        simulation.send_bus_message(looper.BusMessage(uart, 0, b"bogus\n" * 10))


def test_the_slow_median_leads_the_profile(lesson_simulation: looper.Simulation) -> None:
    room_in_the_loop(lesson_simulation)
    lesson_simulation.advance(2.0)

    check = lesson_simulation.expect()
    check.profile().heaviest_is("sort")
    report = check.evaluate(for_seconds=5.0)

    assert report, report.summary
    assert lesson_simulation.profile().is_profiling


def test_twenty_failing_commands_leave_twenty_blocks_on_the_heap(
    lesson_simulation: looper.Simulation,
) -> None:
    lesson_simulation.advance(1.0)

    bad_commands(lesson_simulation, 20)
    check = lesson_simulation.expect()
    check.memory().nothing_leaked()
    report = check.evaluate(for_seconds=1.0)

    assert not report
    assert report.outcomes[0].observed == "20 allocated, 0 freed"


def test_commands_that_work_give_their_memory_back(lesson_simulation: looper.Simulation) -> None:
    lesson_simulation.advance(1.0)
    before = lesson_simulation.memory().heap

    for _ in range(5):
        assert type_into_terminal(lesson_simulation, "set 30\n") == "ok\n"

    after = lesson_simulation.memory().heap
    assert after.allocations - before.allocations == 5
    assert after.frees - before.frees == 5


def test_the_firmware_stays_shallow(lesson_simulation: looper.Simulation) -> None:
    lesson_simulation.advance(1.0)

    check = lesson_simulation.expect()
    check.stack().no_deeper_than(8)  # five frames at the deepest in a measurement
    report = check.evaluate(for_seconds=1.0)

    assert report, report.summary
