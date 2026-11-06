"""Start or attach to a looper simulation, drive it, and expect things of it.

::

    import looper

    def test_the_led_blinks():
        with looper.run("../looper-docs/examples/blinky/looper.toml", virtual=True) as simulation:
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

from looper.application.bootloader import Otp, sweep_power_cuts
from looper.application.expectations import Expectations
from looper.application.memories import Flash, FlashPartition, Retained
from looper.application.ports import (
    ProFeatureLockedError,
    SimulationRefusedError,
    SimulationUnreachableError,
)
from looper.application.simulation import Simulation
from looper.application.triggers import Triggers
from looper.domain.model import (
    BootChain,
    BootStep,
    Bus,
    BusMessage,
    CallTiming,
    Channel,
    ClockMode,
    Comparison,
    Dependency,
    Edge,
    EdgeWhile,
    EventPage,
    Exchange,
    ExpectationReport,
    Finding,
    Findings,
    FlashMark,
    HeapUsage,
    Image,
    Life,
    LifeDump,
    Lives,
    MemoryUsage,
    ModelParameter,
    NodeOutput,
    Outcome,
    PartitionHeader,
    Pattern,
    Pin,
    PinLevel,
    Polarity,
    Profile,
    ProfileEntry,
    Quiet,
    ResetMark,
    RunStatus,
    Signal,
    SignalGraph,
    SignalModel,
    SignalNodeKind,
    Trigger,
    TriggerMode,
    TriggerState,
    Value,
    Variable,
    Watch,
    Width,
)
from looper.infrastructure.looper_cli import LooperCliError
from looper.starting import ContractMismatchError, connect, run

__version__ = "0.2.0"

__all__ = [
    "BootChain",
    "BootStep",
    "Flash",
    "FlashMark",
    "FlashPartition",
    "Life",
    "LifeDump",
    "Lives",
    "ResetMark",
    "Retained",
    "Bus",
    "BusMessage",
    "CallTiming",
    "Channel",
    "ClockMode",
    "Comparison",
    "ContractMismatchError",
    "Dependency",
    "Edge",
    "EdgeWhile",
    "EventPage",
    "Exchange",
    "ExpectationReport",
    "Expectations",
    "Finding",
    "Findings",
    "HeapUsage",
    "Image",
    "LooperCliError",
    "MemoryUsage",
    "ModelParameter",
    "NodeOutput",
    "Otp",
    "Outcome",
    "PartitionHeader",
    "Pattern",
    "Pin",
    "PinLevel",
    "Polarity",
    "Profile",
    "ProfileEntry",
    "Quiet",
    "RunStatus",
    "Signal",
    "SignalGraph",
    "SignalModel",
    "SignalNodeKind",
    "Simulation",
    "ProFeatureLockedError",
    "SimulationRefusedError",
    "SimulationUnreachableError",
    "Trigger",
    "TriggerMode",
    "TriggerState",
    "Triggers",
    "Value",
    "Variable",
    "Watch",
    "Width",
    "__version__",
    "connect",
    "run",
    "sweep_power_cuts",
]
