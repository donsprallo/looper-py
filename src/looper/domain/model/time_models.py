"""Time models: how far simulated time moves between passes of the firmware's loop.

A simulation runs on one time model at a time -- looper-rt's ``fixed`` or
``adaptive``, or one of the project's own -- and can restart on another
without a build. Every text here is the server's: a test reads them, it does
not make its own.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeModelParameter:
    """One parameter a time model takes.

    Attributes:
        name: As ``[time]`` in looper.toml and ``time_params`` name it, such
            as ``max_step_us``.
        title: What a form calls it, such as ``Largest idle step``.
        description: What it sets, in the model's words.
        unit: ``µs``, ``ns``, or empty.
        default: The value when none is given.
        lowest: The smallest value taken; None when the model gives no bound.
        highest: The largest value taken; None when the model gives no bound.
    """

    name: str
    title: str
    description: str
    unit: str
    default: float
    lowest: float | None = None
    highest: float | None = None


@dataclass(frozen=True)
class TimeModel:
    """A time model the simulation can restart with.

    Attributes:
        name: What ``time_model=`` names it by.
        description: What it does, in its own words.
        source: ``built in``, or the C file of the project that defines it.
        built_in: Whether it is one of looper-rt's own.
        parameters: What it takes, in its order.
        problem: Why it cannot be chosen, with what to do; empty when it can.
    """

    name: str
    description: str
    source: str
    built_in: bool
    parameters: tuple[TimeModelParameter, ...] = ()
    problem: str = ""


@dataclass(frozen=True)
class ActiveTimeModel:
    """The time model a simulation runs on.

    Attributes:
        name: The model's name.
        parameters: Every parameter with its value, defaults included, in the
            model's order.
        origin: Where the choice comes from: ``default`` (looper.toml names
            none), ``definition`` (looper.toml), ``command_line``
            (``time_model=`` of `looper.run`) or ``restart``.
        short_text: The server's short name of it, such as ``fixed 250 µs``.
        summary_text: The line a recording carries, every parameter written
            out, such as ``adaptive · min_step_us=1 · max_step_us=500 ·
            time_read_cost_ns=1000``. Runs are comparable when it is equal.
        origin_text: Where it comes from, in a sentence.
        toml_text: The ``[time]`` table that keeps exactly this choice.
    """

    name: str
    parameters: tuple[tuple[str, float], ...]
    origin: str
    short_text: str
    summary_text: str
    origin_text: str = ""
    toml_text: str = ""

    def parameter(self, name: str) -> float | None:
        """The value of a parameter, or None when the model has none of that name."""
        return next((value for given, value in self.parameters if given == name), None)


@dataclass(frozen=True)
class RestartStep:
    """Where a restart of the simulation stands.

    Attributes:
        phase: ``running``, ``building`` (the old simulation runs on
            meanwhile) or ``restarting`` (the connection drops and comes back).
        generation: Restarts so far; tells one from the next.
        refused_text: Why the server refused the time model asked for; the
            simulation then runs on with its own. Empty when nothing was refused.
        refused_parameter: The parameter the refusal is about; empty for the
            choice as a whole.
        build_failed: Whether the last build asked for failed.
        build_summary: What the compiler said, in short, such as ``2 errors``.
        done_text: What the last restart did, such as ``Restarted at 0 s ·
            same build · time model adaptive (was fixed 250 µs)``.
    """

    phase: str
    generation: int
    refused_text: str = ""
    refused_parameter: str = ""
    build_failed: bool = False
    build_summary: str = ""
    done_text: str = ""
