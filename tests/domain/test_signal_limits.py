"""Limit and Slew rate as the builder makes them, and as looper-srv's export writes them (#8)."""

from __future__ import annotations

from typing import Any

from looper.domain.model import (
    LimitSettings,
    NodeOutput,
    SignalGraph,
    SignalNodeKind,
    SlewSettings,
)


def _built(written: str) -> Any:
    namespace: dict[str, Any] = {}
    exec("from looper import *", namespace)  # noqa: S102 -- the export's own import line
    return eval(written, namespace)  # noqa: S307 -- looper-srv's export tests, verbatim


def test_a_limit_of_two_numbers_reads_its_input_alone() -> None:
    (clamp,) = SignalGraph().limit("clamp", "sine", low=-0.5, high=0.5).nodes

    assert (clamp.kind, clamp.inputs) == (SignalNodeKind.LIMIT, (NodeOutput("sine"),))
    assert clamp.limit == LimitSettings(low=-0.5, high=0.5)


def test_a_linked_high_limit_is_the_input_after_in() -> None:
    (clamp,) = SignalGraph().limit("clamp", "sine", low=0, high="ref").nodes

    assert clamp.inputs == (NodeOutput("sine"), NodeOutput("ref"))
    assert clamp.limit == LimitSettings(low=0.0, high=0.0, high_linked=True)


def test_both_linked_limits_follow_in_the_low_one_first() -> None:
    (clamp,) = (
        SignalGraph()
        .limit("clamp", "sine", low=NodeOutput("band", 1), high="top", group="plant")
        .nodes
    )

    assert clamp.inputs == (NodeOutput("sine"), NodeOutput("band", 1), NodeOutput("top"))
    assert (clamp.limit.low_linked, clamp.limit.high_linked) == (True, True)
    assert clamp.group == "plant"


def test_a_slew_rate_reads_one_input_and_keeps_its_rates() -> None:
    (ramp,) = SignalGraph().slew_rate("ramp", NodeOutput("motor", 1), rise=2000.0).nodes

    assert (ramp.kind, ramp.inputs) == (SignalNodeKind.SLEW_RATE, (NodeOutput("motor", 1),))
    assert ramp.slew == SlewSettings(rise=2000.0, fall=0.0)


def test_the_other_nodes_keep_both_settings_unset() -> None:
    (sine,) = SignalGraph().value("sine", 1.0).nodes

    assert (sine.limit, sine.slew) == (LimitSettings(), SlewSettings())


def test_the_calls_the_server_s_export_writes_build_the_limit_and_slew_rate_it_means() -> None:
    graph = _built(
        "SignalGraph()"
        ".limit('clamp', 'sine', low=0.0, high='ref')"
        ".slew_rate('ramp', 'step', rise=2000.0, fall=0.0)"
    )

    clamp, ramp = graph.nodes
    assert clamp.limit == LimitSettings(low=0.0, high_linked=True)
    assert clamp.inputs == (NodeOutput("sine"), NodeOutput("ref"))
    assert (ramp.kind, ramp.slew) == (SignalNodeKind.SLEW_RATE, SlewSettings(2000.0, 0.0))
