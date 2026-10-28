"""Reaching a simulation: the composition root.

The one place that names a concrete adapter. `run` starts `looper-cli run`
for a build definition and connects to the server it starts; `connect`
attaches to one that is already serving. Both check that the server speaks
the contract this library was built against, and hand back a `Simulation`.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from pathlib import Path

from looper.application.simulation import Simulation
from looper.infrastructure.grpc_inspector import CONTRACT_VERSION, GrpcInspector
from looper.infrastructure.looper_cli import LooperCliRun, RunCommand, program_of

#: Where the command that runs looper-cli can be given without code, for
#: example ``uv run --project ../looper-core looper-cli``.
LOOPER_CLI_VARIABLE = "LOOPER_CLI"
DEFAULT_LOOPER_CLI = "looper-cli"


class ContractMismatchError(RuntimeError):
    """The server speaks a version of the contract this library does not."""


def connect(address: str) -> Simulation:
    """Attach to a `looper-cli run` that is already serving at `address`.

    Raises:
        SimulationUnreachableError: If nothing answers there.
        ContractMismatchError: If it speaks another contract version.
    """
    inspector = GrpcInspector(address)
    return _attached(inspector, on_close=None)


def run(
    definition: str | Path | None = None,
    *,
    virtual: bool = False,
    build: bool = True,
    looper_cli: str | Sequence[str] | None = None,
) -> Simulation:
    """Build a simulation, start it, and attach to it.

    Args:
        definition: The build definition; ``looper.toml`` in the working
            directory when none is named.
        virtual: Run on a virtual clock, which only moves when told to.
        build: Build first, or start what was built last.
        looper_cli: The command that runs looper-cli. Defaults to the
            ``LOOPER_CLI`` environment variable, then to ``looper-cli``.

    Raises:
        LooperCliError: If looper-cli could not build, start or serve it.
        ContractMismatchError: If it speaks another contract version.
    """
    command = RunCommand(
        program=program_of(looper_cli or os.environ.get(LOOPER_CLI_VARIABLE, DEFAULT_LOOPER_CLI)),
        definition=Path(definition) if definition is not None else None,
        virtual=virtual,
        build=build,
    )
    process = LooperCliRun.start(command)
    try:
        inspector = GrpcInspector(process.address)
        return _attached(inspector, on_close=process.stop)
    except BaseException:
        process.stop()
        raise


def _attached(inspector: GrpcInspector, on_close: Callable[[], object] | None) -> Simulation:
    """A simulation over the inspector, once its contract is known to match."""
    simulation = Simulation(inspector, _discarding(on_close))
    spoken = simulation.description.contract_version
    if spoken != CONTRACT_VERSION:
        simulation.close()
        raise ContractMismatchError(
            f"the server speaks contract version {spoken}, this library {CONTRACT_VERSION}; "
            "update whichever is older"
        )
    return simulation


def _discarding(action: Callable[[], object] | None) -> Callable[[], None] | None:
    """The action, with whatever it returns left unread."""
    if action is None:
        return None

    def discarded() -> None:
        action()

    return discarded
