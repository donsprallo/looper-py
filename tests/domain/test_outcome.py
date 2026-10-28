"""What a report says, and when it is true."""

from __future__ import annotations

from looper import ExpectationReport, Outcome

MET = Outcome("the firmware", "still calling the adapter", "12 calls", met=True)
FAILED = Outcome("P1A", "every sample within 0 .. 1", "0 .. 2 over 4 samples", met=False)


def test_a_report_is_true_only_when_everything_was_met() -> None:
    assert ExpectationReport((MET,))
    assert not ExpectationReport((MET, FAILED))


def test_a_failed_line_says_what_was_expected_and_what_was_seen() -> None:
    assert (
        FAILED.line == "FAIL  P1A: expected every sample within 0 .. 1, saw 0 .. 2 over 4 samples"
    )


def test_the_summary_puts_the_failures_first() -> None:
    lines = ExpectationReport((MET, FAILED)).summary.splitlines()

    assert lines == ["1 of 2 met", FAILED.line, MET.line]
