"""The request that names this library to a server, so that the server counts it."""

from __future__ import annotations

import os

import pytest

from looper.infrastructure.client_identity import PYTEST_MARK, describe_request
from looper.infrastructure.contract import looper_inspector_pb2 as contract


def test_a_test_under_pytest_says_it_is_a_test() -> None:
    request = describe_request()

    assert request.client_kind == contract.CLIENT_KIND_TEST
    assert request.client_name == f"looper-py test (pid {os.getpid()})"
    assert request.client_contract_version == contract.CONTRACT_VERSION_CURRENT


def test_anything_else_says_it_is_a_script(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(PYTEST_MARK)

    request = describe_request()

    assert request.client_kind == contract.CLIENT_KIND_SCRIPT
    assert request.client_name.startswith("looper-py script")
