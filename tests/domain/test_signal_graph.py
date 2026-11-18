"""Building a signal graph, one part at a time."""

from __future__ import annotations

import pytest

from looper.domain.model import (
    CompareSettings,
    GraphNodeState,
    ModelParameter,
    NodeOutput,
    PinTargetState,
    Signal,
    SignalGraph,
    SignalGraphState,
    SignalModel,
    SignalNodeKind,
    SignalPinTarget,
)


def test_a_closed_loop_is_written_as_one_chain() -> None:
    graph = (
        SignalGraph()
        .channel("voltage", 5)
        .model("motor", "DcMotor", inputs=["voltage"], parameters={"supply": 24.0})
        .drive(3, "motor", output=0)
        .drive(4, "motor", output=1)
        .probe("speed", "motor")
    )

    source, motor = graph.nodes
    assert (source.kind, source.source) == (SignalNodeKind.CHANNEL, 5)
    assert motor.kind is SignalNodeKind.MODEL
    assert motor.inputs == (NodeOutput("voltage", 0),)
    assert motor.parameters == (("supply", 24.0),)
    assert [(one.channel_id, one.output) for one in graph.targets] == [(3, 0), (4, 1)]
    assert graph.probes[0].name == "speed"


def test_building_on_a_graph_leaves_it_as_it_was() -> None:
    base = SignalGraph().generator("sine", Signal("sine", amplitude=1.0, frequency_hz=2.0))

    base.drive(0, "sine")

    assert base.targets == ()


def test_an_operation_reads_two_outputs_of_any_nodes() -> None:
    graph = SignalGraph().operation(
        "sum", SignalNodeKind.ADD, "noise", NodeOutput("motor", output=1)
    )

    assert graph.nodes[0].inputs == (NodeOutput("noise"), NodeOutput("motor", 1))


def test_a_kind_that_is_no_operation_is_refused_as_one() -> None:
    with pytest.raises(ValueError, match="not an operation"):
        SignalGraph().operation("x", SignalNodeKind.MODEL, "a", "b")


def test_a_model_names_the_position_of_its_outputs() -> None:
    motor = SignalModel(
        name="DcMotor",
        inputs=("voltage", "load"),
        outputs=("speed", "current"),
        parameters=(ModelParameter("supply", 24.0, "V"),),
    )

    assert motor.output("current") == 1
    with pytest.raises(ValueError, match="no output 'torque'"):
        motor.output("torque")


def test_a_value_node_gives_a_model_s_parameter() -> None:
    graph = SignalGraph().value("k", 0.5).model("m", "Gain", parameter_sources={"gain": "k"})

    value, model = graph.nodes
    assert (value.kind, value.value) == (SignalNodeKind.VALUE, 0.5)
    assert model.parameter_sources == (("gain", "k"),)


def test_a_comparator_compares_with_a_level_and_keeps_its_settings() -> None:
    graph = SignalGraph().compare("zc", "size", level=15.0, hysteresis=2.0, below=True)

    (comparator,) = graph.nodes
    assert comparator.kind is SignalNodeKind.COMPARE
    assert comparator.inputs == (NodeOutput("size"),)
    assert comparator.compare == CompareSettings(level=15.0, hysteresis=2.0, below=True)


def test_a_comparator_with_a_threshold_reads_it_as_its_second_input() -> None:
    graph = SignalGraph().compare("zc", "size", threshold=NodeOutput("ref", 1), check_us=20)

    (comparator,) = graph.nodes
    assert comparator.inputs == (NodeOutput("size"), NodeOutput("ref", 1))
    assert comparator.compare.linked
    assert comparator.compare.check_us == 20


def test_a_negative_hysteresis_is_left_for_the_server_to_refuse() -> None:
    graph = SignalGraph().compare("zc", "mains", hysteresis=-1.0)

    assert graph.nodes[0].compare.hysteresis == -1.0


def test_abs_reads_one_input_and_min_and_max_read_two() -> None:
    graph = (
        SignalGraph()
        .operation("size", SignalNodeKind.ABS, "mains")
        .operation("low", SignalNodeKind.MIN, "a", "b")
        .operation("high", SignalNodeKind.MAX, "a", NodeOutput("motor", 1))
    )

    size, low, high = graph.nodes
    assert (size.kind, size.inputs) == (SignalNodeKind.ABS, (NodeOutput("mains"),))
    assert low.inputs == (NodeOutput("a"), NodeOutput("b"))
    assert high.inputs == (NodeOutput("a"), NodeOutput("motor", 1))


def test_abs_with_two_inputs_and_min_with_one_are_refused() -> None:
    with pytest.raises(ValueError, match="reads one input"):
        SignalGraph().operation("size", SignalNodeKind.ABS, "a", "b")
    with pytest.raises(ValueError, match="reads two inputs"):
        SignalGraph().operation("low", SignalNodeKind.MIN, "a")


def test_a_pin_is_driven_by_one_output_of_a_node() -> None:
    graph = SignalGraph().compare("zc", "mains").drive_pin(4, "zc").drive_pin(5, "model", output=2)

    assert graph.pin_targets == (SignalPinTarget(4, "zc"), SignalPinTarget(5, "model", 2))
    assert graph.targets == ()


def test_a_probe_records_on_its_own_clock() -> None:
    graph = SignalGraph().probe("rms", "meter", sample_us=1_000).probe("mains", "mains")

    assert [(one.name, one.sample_us) for one in graph.probes] == [("rms", 1_000), ("mains", 0)]


def test_the_calls_the_server_s_export_writes_build_the_nodes_it_means() -> None:
    namespace = {"SignalGraph": SignalGraph, "SignalNodeKind": SignalNodeKind}
    namespace["NodeOutput"] = NodeOutput
    written = (
        "SignalGraph()"
        ".operation('size', SignalNodeKind.ABS, 'mains')"
        ".operation('low', SignalNodeKind.MIN, 'a', 'b')"
        ".compare('zc', 'size', level=15.0, hysteresis=2.0, below=True,"
        " threshold=NodeOutput('ref', 1), check_us=20)"
        ".compare('plain', 'size', level=0.0, hysteresis=0.0, below=False,"
        " threshold=None, check_us=0)"
    )

    graph = eval(written, namespace)  # noqa: S307 -- looper-srv's pytest_export_tests, verbatim

    kinds = [node.kind for node in graph.nodes]
    assert kinds == ["abs", "min", "compare", "compare"]
    assert graph.nodes[2].compare == CompareSettings(15.0, 2.0, True, True, 20)
    assert graph.nodes[3].inputs == (NodeOutput("size"),)


def test_the_applied_graph_finds_a_pin_target_and_a_comparator() -> None:
    state = SignalGraphState(
        pin_targets=(PinTargetState(4, "BUTTON_MODE", "zc"),),
        nodes=(GraphNodeState("zc", "rises above 0"),),
    )

    assert state.pin_target(4).pin_name == "BUTTON_MODE"
    assert state.node("zc").summary_text == "rises above 0"
    with pytest.raises(KeyError, match="no pin 5"):
        state.pin_target(5)
    with pytest.raises(KeyError, match="no node 'gate'"):
        state.node("gate")
