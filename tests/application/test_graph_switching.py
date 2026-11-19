"""Switching groups and blocks of the applied graph from a test (#6).

What `Simulation` hands the port: every part of a switch in one request,
with the time it takes effect at, and the server's refusal raised as it is.
"""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import ChainGroupState, Simulation, SimulationRefusedError
from looper.domain.model import GraphPartSwitch
from looper.domain.model.graph_switches import SwitchTime


def _simulation() -> tuple[Simulation, ScriptedInspector]:
    inspector = ScriptedInspector()
    return Simulation(inspector), inspector


def test_a_variant_swap_goes_out_as_one_switch() -> None:
    simulation, inspector = _simulation()

    simulation.switch_groups({"plant": False, "ideal": True}, {"lowpass": True})

    assert inspector.part_switches == [
        (
            (
                GraphPartSwitch(group_key="plant", enabled=False),
                GraphPartSwitch(group_key="ideal", enabled=True),
                GraphPartSwitch(node_key="lowpass", enabled=True),
            ),
            SwitchTime(),
        )
    ]


def test_one_group_or_one_block_takes_effect_at_a_time_or_after_one() -> None:
    simulation, inspector = _simulation()

    simulation.switch_group("plant", True, at_s=3.0)
    simulation.switch_block("lowpass", False, after_s=0.0025)

    (group, at), (block, after) = inspector.part_switches
    assert (group, at) == ((GraphPartSwitch(group_key="plant"),), SwitchTime(at_us=3_000_000))
    assert (block, after) == (
        (GraphPartSwitch(node_key="lowpass", enabled=False),),
        SwitchTime(after_us=2_500),
    )


def test_a_time_and_a_delay_together_are_refused() -> None:
    simulation, _ = _simulation()

    with pytest.raises(ValueError, match="not both"):
        simulation.switch_group("plant", True, at_s=1.0, after_s=1.0)


def test_the_server_s_refusal_is_raised_with_its_sentence() -> None:
    simulation, inspector = _simulation()
    inspector.switch_refusal = "SPEED would have two writers on: Plant and Ideal."

    with pytest.raises(SimulationRefusedError, match="two writers on"):
        simulation.switch_group("ideal", True)


def test_a_group_is_found_by_its_key() -> None:
    simulation, inspector = _simulation()
    inspector.group_states = (ChainGroupState("plant", "Plant", enabled=False),)

    assert simulation.chain_group("plant").name == "Plant"
    with pytest.raises(KeyError, match="no group 'ideal'"):
        simulation.chain_group("ideal")
