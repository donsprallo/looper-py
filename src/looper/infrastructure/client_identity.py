"""Who this library is when it asks a server to describe itself.

looper-srv counts the windows, tests and scripts attached to it and shows the
count in its lists of servers. A test run by pytest says it is a test; any
other use of the library says it is a script. The server makes the texts.
"""

from __future__ import annotations

import os

from looper.infrastructure.contract import looper_inspector_pb2 as contract

#: Set by pytest while a test runs.
PYTEST_MARK = "PYTEST_CURRENT_TEST"


def describe_request() -> contract.DescribeRequest:
    """The request that names this client: its contract, what it is, and its process."""
    if PYTEST_MARK in os.environ:
        kind, word = contract.CLIENT_KIND_TEST, "test"
    else:
        kind, word = contract.CLIENT_KIND_SCRIPT, "script"
    return contract.DescribeRequest(
        client_contract_version=contract.CONTRACT_VERSION_CURRENT,
        client_name=f"looper-py {word} (pid {os.getpid()})",
        client_kind=kind,
    )
