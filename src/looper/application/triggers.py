"""What a test does with the simulation's triggers.

Arm a condition, let time pass, then ask when and how often it fired. The
simulation fires at the exact simulated instant, so a test reads the fire
time rather than catching the moment itself. A SINGLE trigger holds the
simulation `post_us` after it fires: on a held clock, `advance` returns
there, early, and the window shows the same moment.

Triggers outlive the connection and are shared with every client: what a
test arms on a simulation it shares with a window, it disarms again --
`disarm_own` does that for everything this test armed.
"""

from __future__ import annotations

import os

from looper.application.ports import Inspector, SimulationRefusedError
from looper.domain.model import Trigger, TriggerCondition, TriggerMode, TriggerRequest


def client_name() -> str:
    """What this process calls itself to other clients: display only, never an authorisation."""
    return f"looper-py {os.getpid()}"


class Triggers:
    """The triggers of one simulation, as a test arms and reads them."""

    def __init__(self, inspector: Inspector) -> None:
        self._inspector = inspector
        self._name = client_name()

    def arm(
        self,
        condition: TriggerCondition,
        *,
        mode: TriggerMode = TriggerMode.SINGLE,
        label: str = "",
        pre_us: int = 0,
        post_us: int = 0,
    ) -> Trigger:
        """Have the simulation watch for `condition` from now on.

        Raises:
            SimulationRefusedError: If the simulation cannot watch for it;
                the message says what it can.
        """
        request = TriggerRequest(condition, mode=mode, label=label, pre_us=pre_us, post_us=post_us)
        return self._inspector.arm_trigger(request, self._name)

    def disarm(self, trigger: Trigger | int) -> Trigger:
        """Stop a trigger, whichever client armed it, and say where it stood.

        Raises:
            SimulationRefusedError: If no such trigger was armed.
        """
        return self._inspector.disarm_trigger(_id_of(trigger), self._name)

    def disarm_own(self) -> tuple[Trigger, ...]:
        """Stop every trigger this process armed that still watches or holds."""
        return tuple(
            self.disarm(trigger) for trigger in self.all() if self._is_own_and_live(trigger)
        )

    def current(self, trigger: Trigger | int) -> Trigger:
        """A trigger as the simulation holds it now: its fires, its state.

        Raises:
            SimulationRefusedError: If the simulation holds no such trigger.
        """
        trigger_id = _id_of(trigger)
        for held in self.all():
            if held.trigger_id == trigger_id:
                return held
        raise SimulationRefusedError(f"the simulation holds no trigger {trigger_id}")

    def all(self) -> tuple[Trigger, ...]:
        """Every trigger the simulation holds, armed or not, from every client."""
        return self._inspector.read_triggers()

    def live(self) -> tuple[Trigger, ...]:
        """The triggers that still watch, or hold the place they fired at."""
        return tuple(trigger for trigger in self.all() if trigger.is_live)

    def _is_own_and_live(self, trigger: Trigger) -> bool:
        return trigger.armed_by == self._name and trigger.is_live


def _id_of(trigger: Trigger | int) -> int:
    return trigger if isinstance(trigger, int) else trigger.trigger_id
