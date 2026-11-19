"""The board and its live state, read through the port."""

from __future__ import annotations

import pytest

from board_doubles import BOARD, STATE
from doubles import ScriptedInspector
from looper import Simulation, SimulationRefusedError

NO_BOARD = (
    "The device of a project without a simulation is not shown yet – it is coming. "
    "Run the simulation to see it now."
)


def test_the_board_and_its_state_are_the_server_s() -> None:
    simulation = Simulation(ScriptedInspector())

    assert simulation.board() == BOARD
    assert simulation.board_state() == STATE


def test_a_refusal_is_raised_with_the_server_s_sentence() -> None:
    inspector = ScriptedInspector()
    inspector.board_refusal = NO_BOARD
    simulation = Simulation(inspector)

    for read in (simulation.board, simulation.board_state):
        with pytest.raises(SimulationRefusedError) as refused:
            read()
        assert str(refused.value) == NO_BOARD
