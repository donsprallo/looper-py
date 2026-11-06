"""The bootloader's parts through the port: power cuts, the OTP, and power cuts in turn."""

from __future__ import annotations

import pytest

from doubles import ScriptedInspector
from looper import Simulation, sweep_power_cuts
from looper.infrastructure.boot_translation import power_cut_request
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def test_a_power_cut_is_armed_after_bytes_or_cut_now() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)

    simulation.power_cut(after_bytes=4096, during="flash.erase", off_for_us=1000, seed=7)
    simulation.power_cut()
    simulation.disarm_power_cut()

    assert inspector.power_cuts == [
        (4096, "flash.erase", 1000, 7, False),
        (None, "flash.write", 0, 0, False),
        (None, "any", 0, 0, True),
    ]


def test_a_cut_now_is_asked_for_at_the_change_s_own_time() -> None:
    now = power_cut_request(None, "any", 1000, 0, disarm=False)
    later = power_cut_request(64, "flash.write", 0, 3, disarm=False)

    assert now.WhichOneof("trigger") == "at"
    assert (later.after_bytes, later.during) == (64, contract.FLASH_ACTIVITY_WRITE)


def test_a_cut_during_something_else_is_refused_before_it_is_sent() -> None:
    with pytest.raises(ValueError, match="not flash.read"):
        power_cut_request(0, "flash.read", 0, 0, disarm=False)


def test_the_otp_only_gains_bits() -> None:
    simulation = Simulation(ScriptedInspector())

    simulation.otp().burn(0, b"\x01")
    simulation.otp().burn(0, b"\x02")

    assert simulation.otp().read(0, 1) == b"\x03"


def test_power_cuts_in_turn_lay_the_flash_down_again_and_reset_before_each() -> None:
    inspector = ScriptedInspector()
    simulation = Simulation(inspector)
    inspector.flash[0] = 0x42
    ran: list[int] = []

    def scenario(sim: Simulation) -> None:
        sim.flash().write(0, b"\x00", raw=True)
        ran.append(len(ran))

    points = list(sweep_power_cuts(simulation, scenario, total_bytes=12_000, every=4096))

    assert points == [0, 4096, 8192]
    assert inspector.reset_causes == ["power-on"] * 3
    assert [cut[0] for cut in inspector.power_cuts] == points
    assert inspector.flash_writes[-1] == (0, b"\x00", True)
    assert ran == [0, 1, 2]
