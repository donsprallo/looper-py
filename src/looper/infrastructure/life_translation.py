"""The firmware's lives and the flash marks, from the contract's messages."""

from __future__ import annotations

from looper.domain.model import Life, LifeDump, Lives
from looper.infrastructure import analysis_translation, translation
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: Every cause of a reset, by its word, in the contract's numbers. Which of
#: them a reset from outside may have is the server's to say.
CAUSES = {
    "power-on": contract.RESET_CAUSE_POWER_ON,
    "software": contract.RESET_CAUSE_SOFTWARE,
    "watchdog": contract.RESET_CAUSE_WATCHDOG,
    "pin": contract.RESET_CAUSE_PIN,
    "brown-out": contract.RESET_CAUSE_BROWN_OUT,
}


#: How a life began, in the server's words.
ENTERED_BY = {
    contract.ENTERED_BY_RESET: "reset",
    contract.ENTERED_BY_JUMP: "jump",
    contract.ENTERED_BY_POWER_ON: "power-on",
}

#: How a life ended, in the server's words.
ENDED_BY = {
    contract.LIFE_END_REASON_RESET: "reset",
    contract.LIFE_END_REASON_JUMP: "jump",
    contract.LIFE_END_REASON_POWER_CUT: "power cut",
}


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
        image=view.image,
        partition=view.partition,
        entered_by=ENTERED_BY.get(view.entered_by, ""),
        ended_by=ENDED_BY.get(view.ended_by, ""),
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
