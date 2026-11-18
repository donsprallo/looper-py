"""Generators that move, selects, sample and hold, pins that hold pulses (#5, srv#29, #30)."""

from __future__ import annotations

import os
from typing import Any

import pytest

import looper
from looper.domain.model import (
    NodeOutput,
    SampleMode,
    SampleSettings,
    Signal,
    SignalGraph,
    SignalNodeKind,
    TableFile,
)


def test_a_linked_field_reads_its_node_in_the_contract_s_name() -> None:
    graph = SignalGraph().generator(
        "motor", Signal("sine", 1.0), frequency="ramp", amplitude=NodeOutput("env", 1)
    )

    (motor,) = graph.nodes
    assert motor.linked_fields == ("amplitude", "frequency_hz")
    assert motor.inputs == (NodeOutput("env", 1), NodeOutput("ramp"))


def test_a_generator_without_links_reads_nothing() -> None:
    (plain,) = SignalGraph().generator("mains", Signal("sine", 325.0)).nodes

    assert (plain.inputs, plain.linked_fields) == ((), ())


def test_a_select_reads_its_select_then_when_1_then_when_0() -> None:
    (select,) = SignalGraph().select("sel", "zc", "hi", NodeOutput("lo", 2)).nodes

    assert select.kind is SignalNodeKind.SELECT
    assert select.inputs == (NodeOutput("zc"), NodeOutput("hi"), NodeOutput("lo", 2))


def test_a_sample_and_hold_reads_its_input_and_trigger_and_keeps_its_settings() -> None:
    graph = SignalGraph().sample_hold("sh", "mains", "zc", mode=SampleMode.TRACK, initial=1.5)

    (hold,) = graph.nodes
    assert hold.kind is SignalNodeKind.SAMPLE_HOLD
    assert hold.inputs == (NodeOutput("mains"), NodeOutput("zc"))
    assert hold.sample == SampleSettings(SampleMode.TRACK, 1.5)


def test_an_unknown_sample_mode_is_refused_before_it_leaves() -> None:
    with pytest.raises(ValueError, match="sideways"):
        SignalGraph().sample_hold("sh", "mains", "zc", mode="sideways")  # type: ignore[arg-type]


def test_a_pin_holds_pulses_only_when_asked() -> None:
    held, plain = SignalGraph().pin("gate", 4, hold_pulses=True).pin("btn", 3).nodes

    assert (held.source, held.hold_pulses) == (4, True)
    assert not plain.hold_pulses


def test_a_pulse_is_set_by_its_levels_and_gives_its_offset_and_amplitude() -> None:
    gate = Signal.pulse(0.0, 3.3, 100.0, duty=0.25)

    assert (gate.waveform, gate.offset, gate.amplitude) == ("pulse", 1.65, 1.65)
    assert gate.levels == (0.0, 3.3)
    assert (gate.duty, gate.frequency_hz) == (0.25, 100.0)


def test_a_pulse_written_by_offset_and_amplitude_has_the_levels_they_stand_for() -> None:
    assert Signal("pulse", 1.65, 1.65, duty=0.25).levels == (0.0, 3.3)


def test_a_table_takes_its_points_as_times_and_values() -> None:
    table = Signal.table([(0.0, 1.0), (0.5, 2.0)], amplitude=2.0, end="hold")

    assert (table.waveform, table.amplitude, table.table_end) == ("table", 2.0, "hold")
    assert (table.table_times, table.table_values) == ((0.0, 0.5), (1.0, 2.0))


class Reader:
    """Answers `read_table` from a fixed file, and writes the asks down."""

    def __init__(self, read: TableFile) -> None:
        self.read = read
        self.asks: list[tuple[str, int, float, bool]] = []

    def read_table(
        self,
        path: str | os.PathLike[str],
        value_column: int = 0,
        max_error: float = 0.0,
        keep_every_point: bool = False,
    ) -> TableFile:
        self.asks.append((os.fspath(path), value_column, max_error, keep_every_point))
        return self.read


def test_a_csv_is_read_by_the_reader_and_played_at_scale_one() -> None:
    reader = Reader(TableFile("dip.csv", times=(0.0, 0.01), values=(325.0, 0.0)))

    played = Signal.from_csv("dip.csv", reader, value_column=1, max_error=0.5)

    assert reader.asks == [("dip.csv", 1, 0.5, False)]
    assert (played.table_times, played.table_values, played.amplitude) == (
        (0.0, 0.01),
        (325.0, 0.0),
        1.0,
    )


def test_a_csv_that_cannot_be_played_raises_the_server_s_sentence() -> None:
    sentence = 'dip.csv, line 14: "abc" is not a number.'
    reader = Reader(TableFile("dip.csv", problem_text=sentence))

    with pytest.raises(ValueError, match="is not a number"):
        Signal.from_csv("dip.csv", reader)


def _built(written: str) -> Any:
    namespace: dict[str, Any] = {}
    exec("from looper import *", namespace)  # noqa: S102 -- the export's own import line
    return eval(written, namespace)  # noqa: S307 -- looper-srv's export tests, verbatim


def test_the_calls_the_server_s_export_writes_build_the_nodes_it_means() -> None:
    graph = _built(
        "SignalGraph()"
        ".generator('gate', Signal('pulse', 1.65, 1.65, 0.0, 0.0, duty=0.25), frequency='ramp')"
        ".select('sel', 'zc', 'hi', 'lo')"
        ".sample_hold('sh', 'mains', 'zc', mode=SampleMode.TRACK, initial=1.5)"
        ".pin('gate_in', 4, hold_pulses=True)"
    )

    gate, select, hold, pin = graph.nodes
    assert (gate.signal.duty, gate.linked_fields, gate.inputs) == (
        0.25,
        ("frequency_hz",),
        (NodeOutput("ramp"),),
    )
    assert select.kind is SignalNodeKind.SELECT
    assert hold.sample == SampleSettings(SampleMode.TRACK, 1.5)
    assert pin.hold_pulses


def test_a_sweep_and_a_table_as_the_export_writes_them() -> None:
    sweep = _built(
        "Signal('sweep', 1.0, 0.0, 0.0, 0.0, sweep_from_hz=10.0, sweep_to_hz=100.0,"
        " sweep_seconds=1.0, sweep_spacing='linear', sweep_end='repeat')"
    )
    table = _built(
        "Signal('table', 1.0, 0.0, 0.0, 0.0, table_times=(0.0, 1.0), table_values=(2.0, 3.0),"
        " table_between='linear', table_end='repeat', table_time_scale=0.0)"
    )

    assert (sweep.sweep_from_hz, sweep.sweep_to_hz, sweep.sweep_end) == (10.0, 100.0, "repeat")
    assert (table.table_times, table.table_values) == ((0.0, 1.0), (2.0, 3.0))


def test_the_new_names_are_part_of_the_public_api() -> None:
    for name in ("SampleMode", "SampleSettings", "TableFile", "Starters", "PinDelay"):
        assert name in looper.__all__
