"""Running a simulation until a chain's Sequence passes or fails, in simulated time.

The Sequence says itself whether it passed: its steps are the test. This
lets simulated time pass in short slices and reads the chain's Sequence
after each, so that the run stops close to where the Sequence ended.
"""

from __future__ import annotations

from looper.application.ports import Inspector
from looper.domain.model.chain_runs import ChainRun, SequenceProgress, SequenceState

SLICE_US = 10_000
"""How much simulated time passes between two looks at the Sequence."""
NO_SEQUENCE = "The chain {name} has no Sequence that says whether it passed."
TIMED_OUT = "The chain {name} neither passed nor failed within {seconds:g} s: {step}"


def run_until_chain(inspector: Inspector, name: str, timeout_us: int) -> ChainRun:
    """Let time pass until the Sequence of the chain called `name` (or keyed so) ends.

    Raises:
        ValueError: If no chain of that name or key has a Sequence.
    """
    state = _sequence_of(inspector, name)
    passed_us = 0
    while not state.ended and passed_us < timeout_us:
        step_us = min(SLICE_US, timeout_us - passed_us)
        inspector.run_for(step_us)
        passed_us += step_us
        state = _sequence_of(inspector, name)
    return _outcome(name, state, timeout_us)


def _sequence_of(inspector: Inspector, name: str) -> SequenceState:
    found = [
        state
        for state in inspector.read_sequences()
        if name in (state.group_name, state.group, state.key)
    ]
    if not found:
        raise ValueError(NO_SEQUENCE.format(name=name))
    return next((state for state in found if state.ended), found[0])


def _outcome(name: str, state: SequenceState, timeout_us: int) -> ChainRun:
    if state.ended:
        passed = state.progress is SequenceProgress.DONE
        return ChainRun(name, passed, state.failure_text, state)
    text = TIMED_OUT.format(name=name, seconds=timeout_us / 1e6, step=state.step_text)
    return ChainRun(name, passed=False, failure_text=text, sequence=state)
