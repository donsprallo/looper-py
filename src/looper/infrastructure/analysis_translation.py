"""The profile and the architecture findings, from contract messages into the domain.

Both are analyses the server makes of the firmware -- one of where its time
goes, one of how its code depends on itself -- and both arrive as views
drawn for a window: groups for a tree, node and edge ids for a graph. Here
they become the flat values a test asserts on.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from looper.domain.model import Dependency, Finding, Findings, Profile, ProfileEntry
from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: How the contract names a module as a node of the architecture graph.
MODULE_PREFIX = "module:"

#: How the contract joins the two ends of an edge of the architecture graph.
EDGE_SEPARATOR = "->"

SEVERITIES = {
    contract.TIER_GOOD: "good",
    contract.TIER_NOTICEABLE: "noticeable",
    contract.TIER_CRITICAL: "critical",
}


def profile_of(message: contract.ProfileView) -> Profile:
    """Every measured function, and what the measurement covered.

    The functions are the leaves of the server's tree of groups, because
    its own ranking of the heaviest stops after a dozen and a test may ask
    about any function.
    """
    return Profile(
        functions=tuple(_entry_of(one) for one in _measured(message.groups)),
        measured_nanoseconds=message.measured_nanoseconds,
        is_profiling=message.is_profiling,
        note=message.note,
    )


def findings_of(message: contract.FindingList) -> Findings:
    """Every finding, and how far the analysis got."""
    return Findings(
        findings=tuple(_finding_of(one) for one in message.findings),
        is_complete=message.complete,
        note=message.note,
        fixed=tuple(message.fixed),
    )


def _measured(groups: Iterable[contract.ProfileGroupView]) -> Iterator[contract.ProfileEntryView]:
    """The measurement of every function in a tree of groups, depth first."""
    for group in groups:
        if group.HasField("entry"):
            yield group.entry
        yield from _measured(group.children)


def _entry_of(message: contract.ProfileEntryView) -> ProfileEntry:
    return ProfileEntry(
        name=message.name,
        origin=message.origin,
        calls=message.calls,
        self_nanoseconds=message.self_nanoseconds,
        total_nanoseconds=message.total_nanoseconds,
        source_path=message.source_path,
        line=message.line,
    )


def _finding_of(message: contract.ArchitectureFinding) -> Finding:
    return Finding(
        key=message.key,
        kind=message.kind,
        severity=SEVERITIES.get(message.severity, ""),
        title=message.title,
        explanation=message.explanation,
        modules=tuple(_module_of(one) for one in message.node_ids),
        dependencies=tuple(_dependency_of(one) for one in message.edge_ids),
        function=message.function,
        state=message.state,
        note=message.note,
    )


def _dependency_of(edge_id: str) -> Dependency:
    """The two modules an edge id joins."""
    user, _, used = edge_id.partition(EDGE_SEPARATOR)
    return Dependency(from_module=_module_of(user), to_module=_module_of(used))


def _module_of(node_id: str) -> str:
    """A module's name, from the id the graph gives its node."""
    return node_id.removeprefix(MODULE_PREFIX)
