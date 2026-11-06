"""The bootloader's parts, from the contract's messages."""

from __future__ import annotations

from looper.domain.model import Image, PartitionHeader
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
