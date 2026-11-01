"""Start or attach to a looper simulation, drive it, and expect things of it.

::

    import looper

    def test_the_led_blinks():
        with looper.run("examples/blinky/looper.toml", virtual=True) as simulation:
            check = simulation.expect()
            check.call("adapter_gpio_write").happened_at_least(2)
            check.memory().never_allocates()

            report = check.evaluate(for_seconds=1.0)
            assert report, report.summary

`run` starts `looper-cli run` for a build definition; `connect` attaches to
one that is already serving. Everything goes through the inspector contract
that `looper-cli run` serves, so the window and the test may look at one
simulation together.
"""

from __future__ import annotations

from looper.application.expectations import Expectations
from looper.application.ports import SimulationRefusedError, SimulationUnreachableError
from looper.application.simulation import Simulation
from looper.domain.model import (
    Bus,
    BusMessage,
    Channel,
    ClockMode,
    ExpectationReport,
    Outcome,
    Pin,
    Signal,
    Variable,
    Watch,
)
from looper.infrastructure.looper_cli import LooperCliError
from looper.starting import ContractMismatchError, connect, run

__version__ = "0.2.0"

__all__ = [
    "Bus",
    "BusMessage",
    "Channel",
    "ClockMode",
    "ContractMismatchError",
    "ExpectationReport",
    "Expectations",
    "LooperCliError",
    "Outcome",
    "Pin",
    "Signal",
    "Simulation",
    "SimulationRefusedError",
    "SimulationUnreachableError",
    "Variable",
    "Watch",
    "__version__",
    "connect",
    "run",
]
