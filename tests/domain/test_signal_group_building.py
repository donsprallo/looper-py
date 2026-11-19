"""Groups of signal blocks, labels, switched-off blocks and operations of more inputs (#6).

The builder steps as a test writes them, and the calls looper-srv's pytest
export writes (looper-srv#31, #32), evaluated as the exported file would.
"""

from __future__ import annotations

from typing import Any

import pytest

import looper
from looper.domain.model import (
    GroupDo,
    NodeOutput,
    SignalGraph,
    SignalLabel,
    SignalNodeKind,
    SwitchGroup,
)


def _built(written: str) -> Any:
    namespace: dict[str, Any] = {}
    exec("from looper import *", namespace)  # noqa: S102 -- the export's own import line
    return eval(written, namespace)  # noqa: S307 -- looper-srv's export tests, verbatim


def test_two_variants_write_one_label_and_one_reader_reads_it() -> None:
    graph = (
        SignalGraph()
        .group("plant", "Plant")
        .group("ideal", "Ideal plant", enabled=False)
        .label("SPEED", fallback=0.0)
        .value("measured", 1500.0, group="plant")
        .set_signal("plant_out", "SPEED", source="measured", group="plant")
        .value("nominal", 1450.0, group="ideal")
        .set_signal("ideal_out", "SPEED", source=NodeOutput("nominal"), group="ideal")
        .read_signal("speed", "SPEED")
    )

    assert graph.labels == (SignalLabel("SPEED", 0.0),)
    assert [(one.key, one.group) for one in graph.nodes] == [
        ("measured", "plant"),
        ("plant_out", "plant"),
        ("nominal", "ideal"),
        ("ideal_out", "ideal"),
        ("speed", ""),
    ]
    writer, reader = graph.nodes[1], graph.nodes[4]
    assert (writer.kind, writer.label, writer.inputs) == (
        SignalNodeKind.SET_SIGNAL,
        "SPEED",
        (NodeOutput("measured"),),
    )
    assert (reader.kind, reader.label, reader.inputs) == (SignalNodeKind.READ_SIGNAL, "SPEED", ())
    assert [group.enabled for group in graph.groups] == [True, False]


def test_a_label_without_a_fallback_has_none_rather_than_zero() -> None:
    assert SignalGraph().label("LOAD").labels == (SignalLabel("LOAD", None),)


def test_every_node_step_takes_its_group() -> None:
    graph = (
        SignalGraph()
        .generator("wave", looper.Signal("sine", 1.0), group="g")
        .channel("adc", 1, group="g")
        .pin("button", 4, group="g")
        .watch("speed", 7, group="g")
        .model("motor", "DcMotor", inputs=["adc"], group="g")
        .compare("zc", "wave", group="g")
        .select("sel", "zc", "wave", "adc", group="g")
        .sample_hold("sh", "wave", "zc", group="g")
        .operation("size", SignalNodeKind.ABS, "wave", group="g")
    )

    assert {one.group for one in graph.nodes} == {"g"}


def test_a_block_is_saved_switched_off_and_titled_for_the_server_s_sentences() -> None:
    graph = SignalGraph().value("load", 0.5).switched_off("load").title("load", "Load step")

    (load,) = graph.nodes
    assert (load.switched_off, load.title) == (True, "Load step")
    with pytest.raises(KeyError, match="no signal block 'motor'"):
        graph.switched_off("motor")


def test_add_multiply_min_and_max_read_up_to_eight_inputs() -> None:
    eight = [f"in{index}" for index in range(8)]
    graph = (
        SignalGraph()
        .operation("total", SignalNodeKind.ADD, "a", "b", "c")
        .operation("product", SignalNodeKind.MULTIPLY, "a", "b", "c", "d")
        .operation("lowest", SignalNodeKind.MIN, "a", NodeOutput("motor", 1), "c")
        .operation("highest", SignalNodeKind.MAX, *eight)
    )

    assert [len(one.inputs) for one in graph.nodes] == [3, 4, 3, 8]
    assert graph.nodes[2].inputs[1] == NodeOutput("motor", 1)


def test_a_ninth_input_is_left_for_the_server_to_refuse() -> None:
    graph = SignalGraph().operation("highest", SignalNodeKind.MAX, *"abcdefghi")

    assert len(graph.nodes[0].inputs) == 9


def test_a_sum_takes_a_sign_beside_each_input() -> None:
    graph = SignalGraph().sum("error", ("setpoint", +1), ("speed", -1), ("offset", 1))

    (error,) = graph.nodes
    assert error.kind is SignalNodeKind.SUM
    assert error.inputs == (NodeOutput("setpoint"), NodeOutput("speed"), NodeOutput("offset"))
    assert error.negated_inputs == (False, True, False)


def test_a_sign_other_than_plus_or_minus_one_is_refused() -> None:
    with pytest.raises(ValueError, match="takes \\+1 or -1"):
        SignalGraph().sum("error", ("a", 1), ("b", 2))


def test_subtract_and_divide_keep_two_inputs_and_abs_one() -> None:
    graph = SignalGraph().operation("diff", SignalNodeKind.SUBTRACT, "a", "b")

    assert len(graph.nodes[0].inputs) == 2
    with pytest.raises(ValueError, match="exactly two"):
        SignalGraph().operation("diff", SignalNodeKind.SUBTRACT, "a", "b", "c")
    with pytest.raises(ValueError, match="exactly two"):
        SignalGraph().operation("ratio", SignalNodeKind.DIVIDE, "a")
    with pytest.raises(ValueError, match="reads one input"):
        SignalGraph().operation("size", SignalNodeKind.ABS, "a", "b")
    with pytest.raises(ValueError, match="two inputs or more"):
        SignalGraph().operation("total", SignalNodeKind.ADD, "a")


def test_a_chain_switches_a_group_off_on_or_over() -> None:
    graph = (
        SignalGraph()
        .when("t2", looper.Clock(0, 20_000), group="faults")
        .switch_group("cut", "plant", do="off", after="t2", group="faults")
        .switch_group("back", group_key="plant", do=GroupDo.TOGGLE)
    )

    cut, back = graph.event_blocks[1:]
    assert (cut.kind, cut.settings, cut.group) == ("switch_group", SwitchGroup("plant"), "faults")
    assert back.settings == SwitchGroup("plant", GroupDo.TOGGLE)
    assert graph.event_links[0].from_node == "t2"
    with pytest.raises(ValueError, match="'flip'"):
        SignalGraph().switch_group("cut", "plant", do="flip")


def test_the_calls_the_server_s_export_writes_build_the_groups_and_labels_it_means() -> None:
    graph = _built(
        "SignalGraph()"
        ".group('plant', 'Plant')"
        ".value('motor', 1.5, group='plant')"
        ".set_signal('motor_out', 'SPEED', source='motor', group='plant')"
        ".read_signal('speed', 'SPEED')"
        ".operation('error', SignalNodeKind.SUM, 'speed', 'motor', NodeOutput('m', 1),"
        " negated=(False, True, False,), group='plant')"
        ".operation('total', SignalNodeKind.SUM, 'speed', 'motor')"
        ".operation('top', SignalNodeKind.MAX, 'a', 'b', 'c', group='plant')"
        ".pin('gate', 4, hold_pulses=True, group='plant')"
        ".compare('zc', 'speed', level=0.0, hysteresis=0.0, below=False,"
        " threshold=None, check_us=0, group='plant')"
        ".generator('wave', Signal('sine', 1.0, 0.0, 50.0, 0.0), group='plant')"
        ".switch_group('cut', group_key='plant', do='off', group='faults')"
    )

    motor, out, speed, error, total, top, gate, zc, wave = graph.nodes
    assert (motor.group, out.label, out.inputs) == ("plant", "SPEED", (NodeOutput("motor"),))
    assert (speed.kind, speed.group) == (SignalNodeKind.READ_SIGNAL, "")
    assert error.negated_inputs == (False, True, False)
    assert total.negated_inputs == ()
    assert (len(top.inputs), gate.hold_pulses, zc.group, wave.group) == (3, True, "plant", "plant")
    (cut,) = graph.event_blocks
    assert (cut.settings, cut.group) == (SwitchGroup("plant", GroupDo.OFF), "faults")


def test_the_new_names_are_part_of_the_public_api() -> None:
    names = (
        "SignalLabel",
        "SwitchGroup",
        "GroupDo",
        "LabelState",
        "BlockState",
        "BlockLiveness",
        "GraphCapacity",
        "ChainGroupState",
        "GraphSwitchMark",
    )
    for name in names:
        assert name in looper.__all__
