"""Reaching a simulation: the composition root.

The one place that names a concrete adapter. `run` starts `looper-srv run`
for a build definition and connects to the server it starts; `connect`
attaches to one that is already serving. Both check that the server speaks
the contract this library was built against, and hand back a `Simulation`.
"""

from __future__ import annotations

import os
import warnings
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from looper.application.ports import ContractNotServedError
from looper.application.simulation import Simulation
from looper.infrastructure.grpc_inspector import CONTRACT_VERSION, GrpcInspector
from looper.infrastructure.looper_cli import LooperCliRun, RunCommand, program_of

#: Where the command that runs the server can be given without code, for
#: example ``C:/looper/looper-srv.exe``.
LOOPER_SRV_VARIABLE = "LOOPER_SRV"
#: The older name of that variable, from the days of looper-core's ``looper-cli``.
#: Deprecated: still read when ``LOOPER_SRV`` is not set, with a warning.
LOOPER_CLI_VARIABLE = "LOOPER_CLI"
#: The server a test starts when nothing names another: looper-srv on the ``PATH``.
DEFAULT_SERVER = "looper-srv"


class ContractMismatchError(RuntimeError):
    """The server speaks a version of the contract this library does not."""


def connect(address: str) -> Simulation:
    """Attach to a `looper-srv run` that is already serving at `address`.

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
    server: str | Sequence[str] | None = None,
    looper_cli: str | Sequence[str] | None = None,
    time_model: str | None = None,
    time_params: Mapping[str, int] | None = None,
) -> Simulation:
    """Build a simulation, start it, and attach to it.

    Args:
        definition: The build definition; ``looper.toml`` in the working
            directory when none is named.
        virtual: Run on a virtual clock, which only moves when told to.
        build: Build first, or start what was built last.
        server: The command that runs the server, as text or as a list, for
            example ``"../looper-srv/target/release/looper-srv"``. Defaults
            to the ``LOOPER_SRV`` environment variable, then ``looper-srv``
            on the ``PATH``.
        looper_cli: Deprecated: the old name of ``server``, from the days of
            looper-core's ``looper-cli``. Still taken, with a warning.
        time_model: The time model to run on in place of what looper.toml
            chooses, such as ``"adaptive"``; the run's `time_model` then says
            it came from here (``command_line``), and a restart keeps it.
        time_params: Its parameters, whole numbers, such as
            ``{"max_step_us": 500}``; one left out takes its default.

    Raises:
        ServerStartError: If the server could not build, start or serve it.
        ContractMismatchError: If it speaks another contract version.
        TypeError: If both ``server`` and ``looper_cli`` are given.
        ValueError: For ``time_params`` without ``time_model``.
    """
    command = RunCommand(
        program=program_of(_server_named(server, looper_cli)),
        definition=Path(definition) if definition is not None else None,
        virtual=virtual,
        build=build,
        time_model=time_model,
        time_params=_time_params(time_model, time_params),
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
    simulation = _described(inspector, on_close)
    spoken = simulation.description.contract_version
    if spoken != CONTRACT_VERSION:
        simulation.close()
        raise ContractMismatchError(
            f"the server speaks contract version {spoken}, this library {CONTRACT_VERSION}; "
            "update whichever is older"
        )
    return simulation


def _described(inspector: GrpcInspector, on_close: Callable[[], object] | None) -> Simulation:
    """A simulation over the inspector, or a mismatch when the server lacks the contract.

    A server that knows no method of this contract's service speaks another
    version of it: the package name carries the version.
    """
    try:
        return Simulation(inspector, _discarding(on_close))
    except ContractNotServedError as error:
        inspector.close()
        raise ContractMismatchError(
            f"the server does not speak contract version {CONTRACT_VERSION}; "
            "update whichever is older"
        ) from error


def _discarding(action: Callable[[], object] | None) -> Callable[[], None] | None:
    """The action, with whatever it returns left unread."""
    if action is None:
        return None

    def discarded() -> None:
        action()

    return discarded


def _server_named(
    server: str | Sequence[str] | None, looper_cli: str | Sequence[str] | None
) -> str | Sequence[str]:
    """The server the caller named, under its name or its deprecated one, or the environment's."""
    if looper_cli is not None:
        if server is not None:
            raise TypeError("name the server once: looper_cli= is the deprecated name of server=")
        warnings.warn(
            "looper.run(looper_cli=...) is deprecated; use looper.run(server=...)",
            DeprecationWarning,
            stacklevel=3,
        )
        return looper_cli
    return server or _server_from_environment()


def _time_params(
    time_model: str | None, given: Mapping[str, int] | None
) -> tuple[tuple[str, int], ...]:
    """The parameters as the command line takes them; only with a model."""
    if given and time_model is None:
        raise ValueError("time_params need a time_model to belong to")
    return tuple((name, int(value)) for name, value in (given or {}).items())


def _server_from_environment() -> str:
    """The server the environment names, or looper-srv."""
    named = os.environ.get(LOOPER_SRV_VARIABLE)
    if named:
        return named
    older = os.environ.get(LOOPER_CLI_VARIABLE)
    if older:
        warnings.warn(
            f"{LOOPER_CLI_VARIABLE} is deprecated; name the server in {LOOPER_SRV_VARIABLE}",
            DeprecationWarning,
            stacklevel=4,
        )
        return older
    return DEFAULT_SERVER
