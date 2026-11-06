"""The firmware's lives and the flash marks, from the contract's messages."""

from __future__ import annotations

from looper.domain.model import Life, LifeDump, Lives
from looper.infrastructure import analysis_translation, translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The causes a reset from outside may have, in the contract's numbers.
OUTSIDE_CAUSES = {"pin": contract.RESET_CAUSE_PIN, "power-on": contract.RESET_CAUSE_POWER_ON}


def life_of(view: contract.LifeView) -> Life:
    """One life."""
    cause = contract.ResetCause.Name(view.cause) if view.cause else ""
    return Life(
        number=view.life,
        started_at_us=view.started_at_us,
        ended_at_us=view.ended_at_us,
        cause=cause.removeprefix("RESET_CAUSE_").lower().replace("_", "-"),
        text=view.text,
        has_dump=view.has_dump,
    )


def lives_of(listing: contract.LifeList) -> Lives:
    """Every life of the run."""
    return Lives(
        lives=tuple(life_of(one) for one in listing.lives),
        resets=listing.resets,
        loop_finding=listing.loop_finding,
    )


def dump_of(view: contract.LifeDumpView) -> LifeDump:
    """What a life left behind."""
    return LifeDump(
        life=life_of(view.life),
        memory=translation.memory_of(view.memory),
        profile=analysis_translation.profile_of(view.profile),
        note=view.note,
    )
