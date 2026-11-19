"""Limit and Slew rate in blinky's signal graph, run in looper-srv (#8, looper-srv#34).

A sine through a limit stays within it; a step through a slew rate ramps at
its rates, and a comparator behind it answers the step at the microsecond
the ramp crosses its level -- ``D / rise`` after it. A limit takes its high
limit from a value node it links, and a low limit above the high one gives
the low one and says so.

Needs a looper-docs checkout beside this one, a C compiler, and a
looper-srv whose runtime limits signals (looper-rt#29); skips without them.
``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from looper.domain.model import Sample
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"
NEEDED = {"signal_limits", "pin_delay"}

#: A sine of 1 at 50 Hz, the signal the limits hold.
SINE = looper.Signal("sine", 1.0, frequency_hz=50.0)
#: Low for 5 ms, high for 5 ms: a step up and a step down of 1 every 10 ms.
STEP = looper.Signal.pulse(0.0, 1.0, 100.0, 0.5)
#: The comparator's level behind the slew rate: between two microseconds of
#: the ramp, so that no sample sits on it.
LEVEL = 0.4995


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky, built, started on a held clock and attached to, for this module alone."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        missing = NEEDED - set(started.description.capabilities)
        if missing:
            pytest.skip(f"the server's runtime lacks {sorted(missing)}")
        yield started


@pytest.fixture
def graph_taken_away(simulation: looper.Simulation) -> Iterator[looper.Simulation]:
    """The simulation; the graph is taken away afterwards."""
    yield simulation
    simulation.apply_signal_graph(looper.SignalGraph())


def _recorded(simulation: looper.Simulation, probe: str) -> list[Sample]:
    """Every sample the probe recorded since the recording was last cleared, oldest first."""
    channel_id = simulation.probe(probe).channel_id
    found: list[Sample] = []
    since = 0
    while True:
        page = simulation.read_events(since)
        found += [one for one in page.samples if one.channel_id == channel_id]
        if page.next_event_seq == since:
            return found
        since = page.next_event_seq


def _slopes(samples: list[Sample]) -> list[float]:
    """Units per second between neighbouring samples that are both on the ramp."""
    on_ramp = [one for one in samples if 0.0 < one.value < 1.0]
    return [
        (later.value - earlier.value) / ((later.sim_us - earlier.sim_us) / 1e6)
        for earlier, later in zip(on_ramp, on_ramp[1:], strict=False)
        if later.sim_us - earlier.sim_us <= 100  # noqa: PLR2004 -- the probe's clock
    ]


def test_a_sine_through_a_limit_stays_within_it(graph_taken_away: looper.Simulation) -> None:
    simulation = graph_taken_away
    graph = (
        looper.SignalGraph()
        .generator("sine", SINE)
        .limit("clamp", "sine", low=-0.5, high=0.5)
        .probe("clamp", "clamp", sample_us=500)
    )
    simulation.apply_signal_graph(graph)
    probe = simulation.probe("clamp")

    check = simulation.expect()
    check.channel(probe.channel_id, probe.name).stays_between(-0.5, 0.5)
    check.channel(probe.channel_id, probe.name).reaches(0.5)
    check.channel(probe.channel_id, probe.name).reaches(-0.5)
    report = check.evaluate(for_seconds=0.04)

    assert report, report.summary
    clamp = simulation.signal_graph().node("clamp")
    assert clamp.value is not None and -0.5 <= clamp.value <= 0.5
    assert clamp.summary_text.startswith("limit −0.5 … 0.5"), clamp.summary_text
    assert clamp.fault_text == ""


def test_a_step_through_a_slew_rate_ramps_and_reaches_the_comparator_at_its_microsecond(
    graph_taken_away: looper.Simulation,
) -> None:
    simulation = graph_taken_away
    step_pin, edge_pin = simulation.pin("BUTTON_MODE"), simulation.pin("MCP_2")
    graph = (
        looper.SignalGraph()
        .generator("step", STEP)
        .slew_rate("ramp", "step", rise=1000.0, fall=2000.0)
        .compare("zc", "ramp", level=LEVEL)
        .drive_pin(step_pin.pin_id, "step")
        .drive_pin(edge_pin.pin_id, "zc")
        .probe("ramp", "ramp", sample_us=100)
    )
    simulation.apply_signal_graph(graph)
    simulation.advance(0.01)
    simulation.clear_recordings()

    check = simulation.expect()
    # Up at 1/ms: 0.4995 is 499.5 us after the step, so the edge is at 500 us.
    check.pin("MCP_2").after("BUTTON_MODE").between(500, 500, unit="us")
    # Down at 2/ms from 1: 0.4995 is 250.25 us after the step, so 251 us.
    fall = looper.Polarity.FALL
    check.pin("MCP_2").after("BUTTON_MODE", fall, fall).between(251, 251, unit="us")
    report = check.evaluate(for_seconds=0.05)

    assert report, report.summary
    slopes = _slopes(_recorded(simulation, "ramp"))
    rising, falling = [one for one in slopes if one > 0], [one for one in slopes if one < 0]
    assert rising and all(one == pytest.approx(1000.0) for one in rising), rising
    assert falling and all(one == pytest.approx(-2000.0) for one in falling), falling
    target = simulation.signal_graph().pin_target(edge_pin.pin_id)
    assert target.resolution_text == "exact to 1 µs"
    assert 'Slew rate "ramp"' in target.check_text, target.check_text


def test_a_limit_follows_the_high_limit_it_links(graph_taken_away: looper.Simulation) -> None:
    simulation = graph_taken_away
    graph = (
        looper.SignalGraph()
        .generator("sine", SINE)
        .value("ref", 0.25)
        .title("ref", "Ref")
        .limit("clamp", "sine", low=-1.0, high="ref")
        .probe("clamp", "clamp", sample_us=500)
    )
    simulation.apply_signal_graph(graph)
    probe = simulation.probe("clamp")

    linked = simulation.expect()
    linked.channel(probe.channel_id, probe.name).stays_between(-1.0, 0.25)
    linked.channel(probe.channel_id, probe.name).reaches(0.25)
    assert (report := linked.evaluate(for_seconds=0.04)), report.summary

    simulation.set_graph_value("ref", -0.25)
    simulation.advance(0.001)
    moved = simulation.expect()
    moved.channel(probe.channel_id, probe.name).stays_between(-1.0, -0.25)
    assert (report := moved.evaluate(for_seconds=0.04)), report.summary
    assert "▷Ref" in simulation.signal_graph().node("clamp").summary_text


def test_a_low_limit_above_the_high_one_gives_the_low_one_and_says_why(
    graph_taken_away: looper.Simulation,
) -> None:
    simulation = graph_taken_away
    graph = (
        looper.SignalGraph()
        .generator("sine", SINE)
        .limit("clamp", "sine", low=2.0, high=1.0)
        .probe("clamp", "clamp", sample_us=1_000)
    )
    simulation.apply_signal_graph(graph)
    probe = simulation.probe("clamp")

    check = simulation.expect()
    check.channel(probe.channel_id, probe.name).stays_between(2.0, 2.0)
    report = check.evaluate(for_seconds=0.01)

    assert report, report.summary
    clamp = simulation.signal_graph().node("clamp")
    assert clamp.value == 2.0
    assert clamp.fault_text == "The low limit 2 is above the high limit 1: it gives the low limit."
