"""Expectations of what a partition holds, checked against the headers the server read (Pro)."""

from __future__ import annotations

from looper.domain.checks import BootChainWent, PartitionHolds
from looper.domain.model import BootChain, BootStep, Observation, PartitionHeader

VALID = PartitionHeader("app_b", "valid", "valid · app@2.1 · v0x0201")
BROKEN = PartitionHeader("app_b", "broken", "broken: the payload CRC does not match")


def _observed(*headers: PartitionHeader) -> Observation:
    return Observation(
        samples=(),
        exchanges=(),
        timings=(),
        elapsed_seconds=1.0,
        headers={header.name: header for header in headers},
    )


def test_a_valid_header_naming_the_image_meets_is_valid() -> None:
    outcome = PartitionHolds("app_b", ("valid",), "app@2.1").evaluate(_observed(VALID))

    assert outcome.met
    assert outcome.observed == "valid · app@2.1 · v0x0201"


def test_a_valid_header_of_another_image_does_not() -> None:
    assert not PartitionHolds("app_b", ("valid",), "app@2.0").evaluate(_observed(VALID)).met


def test_a_broken_header_is_invalid_and_says_why() -> None:
    outcome = PartitionHolds("app_b", ("broken", "unknown image", "empty")).evaluate(
        _observed(BROKEN)
    )

    assert outcome.met
    assert "payload CRC" in outcome.observed


def test_without_a_state_the_check_is_not_met_and_says_so() -> None:
    outcome = PartitionHolds("app_b", ("valid",)).evaluate(_observed(PartitionHeader("app_b")))

    assert not outcome.met
    assert "looper Pro" in outcome.observed


def test_a_partition_there_is_not_is_said() -> None:
    outcome = PartitionHolds("app_c", ("valid",)).evaluate(_observed(VALID))

    assert (outcome.met, outcome.observed) == (False, "no such partition")


def _chains(*chains: BootChain) -> Observation:
    return Observation(
        samples=(), exchanges=(), timings=(), elapsed_seconds=1.0, boot_chains=chains
    )


TO_B = BootChain(
    steps=(
        BootStep(1, "stage0", "stage0"),
        BootStep(2, "stage1@1.0", "stage1_a"),
        BootStep(3, "app@2.1", "app_b"),
    ),
    started_by="pin",
    text="stage0 → stage1_a 1.0 → app_b 2.1",
)


def test_the_last_chain_going_through_the_partitions_meets_went() -> None:
    outcome = BootChainWent(("stage0", "stage1_a", "app_b")).evaluate(_chains(TO_B))

    assert outcome.met
    assert outcome.observed == "stage0 → stage1_a 1.0 → app_b 2.1"


def test_another_way_does_not_meet_went() -> None:
    assert not BootChainWent(("stage0", "stage1_a", "app_a")).evaluate(_chains(TO_B)).met
    assert not BootChainWent(("stage0",)).evaluate(_chains()).met
