"""Groups of signal blocks, labels, switching and sums on blinky, run in looper-srv (#6).

Two variants in groups of their own write one label, and one Read signal
drives blinky's button pin from it: a swap of the variants in one switch
gives the pin no edge, a chain's Switch group gives it one at the event's
microsecond, and with both variants off the label's fallback reaches the
pin. Two writers left on are refused with the server's sentence. A sum
subtracts by its signs, and a max reads eight inputs (looper-srv#31, #32).

Needs a looper-docs checkout beside this one, a C compiler, and a
looper-srv whose runtime switches groups; skips without them.
``LOOPER_FIXTURES`` points at the fixtures elsewhere.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator

import pytest

import looper
from server_under_test import FIXTURES, server_command

DEFINITION = FIXTURES / "blinky" / "looper.toml"

#: When the chain switches the variant off and on again, after the graph is applied.
CUT_AFTER_US, BACK_AFTER_US = 20_000, 30_000

#: A clock period long enough that each chain fires once in a test.
ONCE_US = 10_000_000


@pytest.fixture(scope="module")
def simulation() -> Iterator[looper.Simulation]:
    """Blinky, built, started on a held clock and attached to, for this module alone."""
    if not DEFINITION.is_file():
        pytest.skip(f"no fixture at {DEFINITION}")
    if shutil.which("gcc") is None and shutil.which("clang") is None:
        pytest.skip("no C compiler on PATH")
    with looper.run(DEFINITION, virtual=True, server=server_command()) as started:
        if "graph_groups" not in started.description.capabilities:
            pytest.skip("the server's runtime switches no groups")
        yield started


@pytest.fixture
def button(simulation: looper.Simulation) -> Iterator[looper.Pin]:
    """The button pin, an input; the graph is taken away afterwards."""
    yield simulation.pin("BUTTON_MODE")
    simulation.apply_signal_graph(looper.SignalGraph())


def _variants(pin_id: int, b_enabled: bool = False) -> looper.SignalGraph:
    """Sensor A and Sensor B both write LEVEL below the pin's threshold; its fallback is high."""
    return (
        looper.SignalGraph()
        .group("a", "Sensor A")
        .group("b", "Sensor B", enabled=b_enabled)
        .label("LEVEL", fallback=1.0)
        .value("a_level", 0.0, group="a")
        .set_signal("a_out", "LEVEL", source="a_level", group="a")
        .value("b_level", 0.25, group="b")
        .set_signal("b_out", "LEVEL", source="b_level", group="b")
        .read_signal("level", "LEVEL")
        .drive_pin(pin_id, "level")
        .probe("LEVEL", "level", sample_us=100)
    )


def test_a_variant_swap_in_one_switch_gives_the_pin_no_edge(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    simulation.apply_signal_graph(_variants(button.pin_id))
    simulation.advance(0.005)
    edges = simulation.signal_graph().pin_target(button.pin_id).edges

    probe = simulation.probe("LEVEL")
    check = simulation.expect()
    check.channel(probe.channel_id, probe.name).stays_between(0.0, 0.25)
    simulation.switch_groups({"a": False, "b": True}, after_s=0.005)
    report = check.evaluate(for_seconds=0.01)

    assert report, report.summary
    state = simulation.signal_graph()
    assert state.pin_target(button.pin_id).edges == edges, "neither the fallback nor a gap"
    level = state.label("LEVEL")
    assert (level.writer_node, level.value) == ("b_out", 0.25), "the writer's value while it is on"
    assert level.state_text == "now 0.25 · set by Sensor B"
    assert state.node_state("a_out").state_text == "Off – Sensor A is off."
    assert state.capacity.text.startswith("signal nodes 5 of 128 (2 switched off, 1 for labels)")


def test_a_chain_switches_a_group_at_its_event_s_microsecond(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    start_us = simulation.run_state().now_us
    graph = (
        _variants(button.pin_id)
        .group("faults", "Sensor fails")
        .when("cut_at", looper.Clock(ONCE_US, start_us + CUT_AFTER_US), group="faults")
        .switch_group("cut", "a", do="off", after="cut_at", group="faults")
        .when("back_at", looper.Clock(ONCE_US, start_us + BACK_AFTER_US), group="faults")
        .switch_group("back", "a", do="on", after="back_at", group="faults")
    )
    simulation.apply_signal_graph(graph)
    since = simulation.run_state().next_event_seq

    probe = simulation.probe("LEVEL")
    check = simulation.expect()
    check.pin("BUTTON_MODE").pulse_width_between(10_000, 10_000, unit="us")
    check.channel(probe.channel_id, probe.name).reaches(1.0, within_seconds=0.021)
    report = check.evaluate(for_seconds=0.05)

    assert report, report.summary
    switches = [(one.sim_us, one.enabled) for one in simulation.graph_switches(since)]
    assert switches == [(start_us + CUT_AFTER_US, False), (start_us + BACK_AFTER_US, True)]
    assert simulation.chain_group("a").switched_at_us == start_us + BACK_AFTER_US
    assert simulation.chain_group("a").switched_by_text.startswith('chain "Sensor fails" at ')


def test_with_both_variants_off_the_label_gives_its_fallback(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = _variants(button.pin_id).read_signal("orphan", "NOBODY").probe("ORPHAN", "orphan")
    simulation.apply_signal_graph(graph)

    simulation.switch_groups({"a": False, "b": False})
    simulation.advance(0.002)

    state = simulation.signal_graph()
    level = state.label("LEVEL")
    assert (level.on_fallback, level.value, level.writer_node) == (True, 1.0, "")
    assert state.pin_target(button.pin_id).high
    orphan = state.node_state("orphan")
    assert orphan.state is looper.BlockLiveness.LEFT_OUT
    assert orphan.state_text == "Off – NOBODY has no writer on and no fallback."
    assert not simulation.probe("ORPHAN").is_live
    off = simulation.chain_group("a").off_text
    assert off == "2 blocks off · LEVEL gives its fallback 1"


def test_two_writers_on_are_refused_with_the_server_s_sentence(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    simulation.apply_signal_graph(_variants(button.pin_id))

    with pytest.raises(looper.SimulationRefusedError) as refused:
        simulation.switch_group("b", True)

    assert str(refused.value) == (
        "LEVEL would have two writers on: Sensor A and Sensor B. Switch both in one request."
    )
    assert simulation.signal_graph().label("LEVEL").writer_node == "a_out"


def test_a_sum_adds_and_subtracts_by_its_signs(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = (
        looper.SignalGraph()
        .value("a", 3.0)
        .value("b", 1.0)
        .value("c", 0.5)
        .sum("total", ("a", +1), ("b", -1), ("c", +1))
        .operation("difference", looper.SignalNodeKind.SUBTRACT, "a", "b")
        .probe("TOTAL", "total", sample_us=1_000)
        .probe("DIFFERENCE", "difference", sample_us=1_000)
    )
    simulation.apply_signal_graph(graph)

    check = simulation.expect()
    for name, expected in (("TOTAL", 2.5), ("DIFFERENCE", 2.0)):
        probe = simulation.probe(name)
        check.channel(probe.channel_id, name).stays_between(expected, expected)
    report = check.evaluate(for_seconds=0.01)

    assert report, report.summary
    assert simulation.signal_graph().node("total").summary_text == "a − b + c"


def test_a_max_reads_eight_inputs_and_a_ninth_is_refused(
    simulation: looper.Simulation, button: looper.Pin
) -> None:
    graph = looper.SignalGraph()
    for index in range(8):
        graph = graph.value(f"in{index}", float(index + 1))
    eight = [f"in{index}" for index in range(8)]
    top = graph.operation("top", looper.SignalNodeKind.MAX, *eight)
    simulation.apply_signal_graph(top.probe("TOP", "top", sample_us=1_000))

    probe = simulation.probe("TOP")
    check = simulation.expect()
    check.channel(probe.channel_id, probe.name).stays_between(8.0, 8.0)
    report = check.evaluate(for_seconds=0.01)

    assert report, report.summary
    with pytest.raises(looper.SimulationRefusedError) as refused:
        simulation.apply_signal_graph(
            graph.operation("top", looper.SignalNodeKind.MAX, *eight, "in0")
        )
    assert str(refused.value) == "Node 'top' (max) takes 2 to 8 inputs, not 9"
