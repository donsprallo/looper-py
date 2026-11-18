"""Table files and starters, asked of the server through the port (#5, looper-srv#29, #30)."""

from __future__ import annotations

from pathlib import Path

import pytest

from doubles import ScriptedInspector
from looper import Signal, Simulation, Starter, StarterNeeds, Starters, TableFile


def test_a_table_file_here_is_sent_by_its_whole_path(tmp_path: Path) -> None:
    recording = tmp_path / "dip.csv"
    recording.write_text("t,v\n0,1\n1,2\n", encoding="utf-8")
    inspector = ScriptedInspector()
    whole = str(recording.resolve())
    inspector.tables = {whole: TableFile(whole, times=(0.0, 1.0), values=(1.0, 2.0))}

    read = Simulation(inspector).read_table(recording, value_column=1, max_error=0.1, unit="V")

    assert inspector.table_asks == [(whole, 1, 0.1, False, "V")]
    assert read.values == (1.0, 2.0)


def test_a_table_file_not_here_is_left_for_the_server_to_find() -> None:
    inspector = ScriptedInspector()

    read = Simulation(inspector).read_table("tables/dip.pwl", keep_every_point=True)

    assert inspector.table_asks == [("tables/dip.pwl", 0, 0.0, True, "")]
    assert read.problem_text == "tables/dip.pwl does not exist."


def test_a_signal_is_read_from_a_csv_through_the_simulation() -> None:
    inspector = ScriptedInspector()
    inspector.tables = {"mains.csv": TableFile("mains.csv", times=(0.0, 0.02), values=(0.0, 1.0))}

    played = Signal.from_csv("mains.csv", Simulation(inspector))

    assert (played.waveform, played.table_values) == ("table", (0.0, 1.0))


def test_a_file_that_cannot_be_played_raises_with_the_server_s_sentence() -> None:
    with pytest.raises(ValueError, match="does not exist"):
        Signal.from_csv("gone.csv", Simulation(ScriptedInspector()))


def test_the_starters_are_listed_and_found_by_name() -> None:
    inspector = ScriptedInspector()
    dimmer = Starter(
        "phase_angle_dimmer",
        display_name="Phase-angle dimmer",
        needs=StarterNeeds(input_pins=1, output_pins=1, models=("Triac", "HalfCycleRms")),
        is_available=True,
    )
    inspector.starter_list = Starters((Starter("mains_zero_cross"), dimmer))

    starters = Simulation(inspector).starters()

    assert starters.names == ("mains_zero_cross", "phase_angle_dimmer")
    assert starters.named("phase_angle_dimmer").needs.models == ("Triac", "HalfCycleRms")
    assert len(starters) == 2
    with pytest.raises(KeyError, match="there are mains_zero_cross, phase_angle_dimmer"):
        starters.named("sweep")


def test_no_starters_say_why() -> None:
    inspector = ScriptedInspector()
    inspector.starter_list = Starters(unavailable_reason="The model library did not start.")

    starters = Simulation(inspector).starters()

    assert list(starters) == []
    with pytest.raises(KeyError, match="did not start"):
        starters.named("mains_zero_cross")
