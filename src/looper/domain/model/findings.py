"""What the architecture analysis found worth a look in the firmware's code.

The server indexes the project's code, judges its dependencies against the
rules the project keeps, and lists what breaks them or stands out: a
module reaching past its layer, a cycle, a function grown past a limit. A
test says which of them may be there -- typically none that the baseline
does not already accept.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The state of a finding the project's baseline does not hold: what an audit fails on.
NEW = "new"

#: The states of a finding the baseline holds -- taken in with the rest, or
#: accepted with a note of its own.
IN_THE_BASELINE = frozenset({"known", "accepted"})


@dataclass(frozen=True)
class Dependency:
    """One module using another, as a finding names it.

    Attributes:
        from_module: The module that uses.
        to_module: The module it uses.
    """

    from_module: str
    to_module: str


@dataclass(frozen=True)
class Finding:
    """One thing the architecture analysis found.

    Attributes:
        key: Kind and subject, stable across edits; what a baseline accepts.
        kind: What kind of thing it is, such as ``rule violation`` or ``cycle``.
        severity: ``good``, ``noticeable`` or ``critical``.
        title: One line naming it.
        explanation: What it means and what helps.
        modules: The modules it is about.
        dependencies: The dependencies it is about, such as the one that
            breaks a layer rule.
        function: The function it is about, or empty.
        state: ``new``, ``known`` or ``accepted``, against the project's baseline.
        note: What it was accepted with, or empty.
    """

    key: str
    kind: str
    severity: str
    title: str
    explanation: str = ""
    modules: tuple[str, ...] = ()
    dependencies: tuple[Dependency, ...] = ()
    function: str = ""
    state: str = ""
    note: str = ""

    @property
    def is_new(self) -> bool:
        """Whether the project's baseline does not hold it, so that an audit fails on it."""
        return self.state == NEW

    @property
    def is_accepted(self) -> bool:
        """Whether the project's baseline holds it, known or accepted with a note."""
        return self.state in IN_THE_BASELINE


@dataclass(frozen=True)
class Findings:
    """Every finding about the project's code, and how far the analysis got.

    Attributes:
        findings: What was found.
        is_complete: Whether every file was read. Some findings -- a
            function that could be static, one never named -- are only
            looked for once they all are.
        note: What the server says about the list, such as why it is partial.
        fixed: Keys the baseline accepts that are no longer found.
    """

    findings: tuple[Finding, ...] = ()
    is_complete: bool = False
    note: str = ""
    fixed: tuple[str, ...] = ()

    def of_kind(self, kind: str) -> tuple[Finding, ...]:
        """The findings of one kind, such as ``rule violation``."""
        return tuple(one for one in self.findings if one.kind == kind)

    def new(self) -> tuple[Finding, ...]:
        """The findings the baseline does not hold: what `looper-srv audit` would fail on."""
        return tuple(one for one in self.findings if one.is_new)

    def between(self, from_module: str, to_module: str) -> tuple[Finding, ...]:
        """The findings about one module using another."""
        wanted = Dependency(from_module, to_module)
        return tuple(one for one in self.findings if wanted in one.dependencies)
