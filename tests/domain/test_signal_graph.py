"""Building a signal graph, one part at a time."""

from __future__ import annotations

import pytest

from looper.domain.model import (
    ModelParameter,
    NodeOutput,
    Signal,
    SignalGraph,
    SignalModel,
    SignalNodeKind,
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
