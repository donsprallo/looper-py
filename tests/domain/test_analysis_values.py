"""The profile and the findings, as a test reads them."""

from __future__ import annotations

from looper.domain.checks import HeaviestFunctionIs
from looper.domain.model import (
    Dependency,
    Finding,
    Findings,
    Observation,
    Profile,
    ProfileEntry,
)


def an_entry(name: str, self_nanoseconds: int, origin: str = "firmware") -> ProfileEntry:
    return ProfileEntry(
        name=name,
        origin=origin,
        calls=10,
        self_nanoseconds=self_nanoseconds,
        total_nanoseconds=self_nanoseconds * 2,
    )


PROFILE = Profile(
    functions=(
        an_entry("app_step", 500),
        an_entry("step", 900, origin="device model"),
        an_entry("median_filter", 700),
    ),
    measured_nanoseconds=2100,
    is_profiling=True,
)


def observed_with(profile: Profile) -> Observation:
    return Observation(samples=(), exchanges=(), timings=(), elapsed_seconds=1.0, profile=profile)


def test_the_ranking_is_by_self_time_heaviest_first() -> None:
    names = [one.name for one in PROFILE.heaviest_first()]

    assert names == ["step", "median_filter", "app_step"]


def test_the_ranking_can_be_narrowed_to_one_origin() -> None:
    heaviest = PROFILE.heaviest("firmware")

    assert heaviest is not None
    assert heaviest.name == "median_filter"


def test_a_function_is_found_by_name_and_an_unmeasured_one_is_none() -> None:
    entry = PROFILE.entry("app_step")

    assert entry is not None
    assert entry.self_nanoseconds == 500
    assert PROFILE.entry("main") is None
    assert Profile().heaviest() is None


def test_the_heaviest_firmware_function_is_checked_and_the_outcome_names_it() -> None:
    met = HeaviestFunctionIs("median_filter").evaluate(observed_with(PROFILE))
    missed = HeaviestFunctionIs("app_step").evaluate(observed_with(PROFILE))

    assert met.met
    assert not missed.met
    assert "median_filter the heaviest" in missed.observed


def test_a_build_that_is_not_profiled_fails_the_check_and_says_why() -> None:
    outcome = HeaviestFunctionIs("median_filter").evaluate(observed_with(Profile()))

    assert not outcome.met
    assert "not woven" in outcome.observed


def test_a_profile_with_nothing_of_the_origin_fails_the_check() -> None:
    outcome = HeaviestFunctionIs("x", origin="library").evaluate(observed_with(PROFILE))

    assert not outcome.met
    assert outcome.observed == "nothing of it was measured"


VIOLATION = Finding(
    key="violation:hal->app",
    kind="rule violation",
    severity="critical",
    title="hal uses app",
    dependencies=(Dependency("hal", "app"),),
    state="new",
)
ACCEPTED_LIMIT = Finding(
    key="limit:light_show_step",
    kind="limit exceeded",
    severity="noticeable",
    title="light_show_step: mccabe 12",
    modules=("light_show",),
    function="light_show_step",
    state="accepted",
)
FINDINGS = Findings(findings=(VIOLATION, ACCEPTED_LIMIT), is_complete=True)


def test_findings_are_picked_by_kind_and_by_the_dependency_they_are_about() -> None:
    assert FINDINGS.of_kind("rule violation") == (VIOLATION,)
    assert FINDINGS.between("hal", "app") == (VIOLATION,)
    assert FINDINGS.between("app", "hal") == ()


def test_only_what_the_baseline_does_not_accept_would_fail_an_audit() -> None:
    assert ACCEPTED_LIMIT.is_accepted
    assert VIOLATION.is_new
    assert FINDINGS.new() == (VIOLATION,)
