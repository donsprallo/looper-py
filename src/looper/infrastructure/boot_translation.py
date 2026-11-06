"""The bootloader's parts, from the contract's messages."""

from __future__ import annotations

from looper.domain.model import BootChain, BootStep, Image, PartitionHeader
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: The header states in the server's words; nothing for data or without the licence.
HEADER_STATES = {
    contract.HEADER_STATE_UNSPECIFIED: "",
    contract.HEADER_STATE_EMPTY: "empty",
    contract.HEADER_STATE_VALID: "valid",
    contract.HEADER_STATE_BROKEN: "broken",
    contract.HEADER_STATE_UNKNOWN_IMAGE: "unknown image",
}


def images_of(listing: contract.ImageList) -> tuple[Image, ...]:
    """Every image in every variant."""
    return tuple(
        Image(
            ref=one.ref,
            built=one.built,
            version_text=one.version_text,
            payload_size=one.payload_size,
            identity_hex=one.identity_hex,
            text=one.text,
        )
        for one in listing.images
    )


def headers_of(view: contract.FlashView) -> dict[str, PartitionHeader]:
    """What each partition holds, by name."""
    return {
        one.name: PartitionHeader(one.name, HEADER_STATES.get(one.header, ""), one.header_text)
        for one in view.partitions
    }


#: The flash calls a power cut counts, by the words a test uses.
ACTIVITIES = {
    "any": contract.FLASH_ACTIVITY_ANY,
    "flash.write": contract.FLASH_ACTIVITY_WRITE,
    "flash.erase": contract.FLASH_ACTIVITY_ERASE,
}


def chains_of(view: contract.BootChainView) -> tuple[BootChain, ...]:
    """Every boot chain of the run."""
    return tuple(
        BootChain(
            steps=tuple(
                BootStep(one.life, one.image, one.partition, one.at_us, one.text)
                for one in chain.steps
            ),
            started_by=_cause_word(chain.started_by),
            text=chain.text,
        )
        for chain in view.chains
    )


def _cause_word(cause: int) -> str:
    """``pin``, ``power-on``: the cause as the server words it."""
    if not cause:
        return ""
    name = str(contract.ResetCause.Name(cause))
    return name.removeprefix("RESET_CAUSE_").lower().replace("_", "-")


def power_cut_request(
    after_bytes: int | None, during: str, off_for_us: int, seed: int, disarm: bool
) -> contract.PowerCutRequest:
    """The contract's request for a cut.

    Raises:
        ValueError: If ``during`` is not a flash call a cut counts.
    """
    activity = ACTIVITIES.get(during)
    if activity is None:
        raise ValueError(f"a power cut counts {', '.join(ACTIVITIES)}, not {during}")
    request = contract.PowerCutRequest(
        during=activity, off_for_us=off_for_us, seed=seed, disarm=disarm
    )
    if after_bytes is None:
        request.at.CopyFrom(contract.When())
    else:
        request.after_bytes = after_bytes
    return request
