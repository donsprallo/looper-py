"""What every check is: one thing expected of a run.

Each check reads what the simulation already recorded and says what it
expected and what it saw. None of them makes the simulation do anything;
the scenario is the caller's, and these only look.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from looper.domain.model import Observation, Outcome

#: What a check saw when there was nothing to see.
NOTHING_RECORDED = "nothing recorded"


class Check(ABC):
    """One thing expected of a run."""

    @abstractmethod
    def evaluate(self, observed: Observation) -> Outcome:
        """Say whether what was seen matches what was expected."""
