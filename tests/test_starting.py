"""Which server `looper.run` starts when the caller names none."""

from __future__ import annotations

import pytest

from looper import starting


def test_without_a_variable_looper_srv_is_started(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOOPER_SRV", raising=False)
    monkeypatch.delenv("LOOPER_CLI", raising=False)

    assert starting._server_from_environment() == "looper-srv"


def test_looper_srv_wins_over_the_older_looper_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOOPER_CLI", "uv run looper-cli")
    assert starting._server_from_environment() == "uv run looper-cli"

    monkeypatch.setenv("LOOPER_SRV", "C:/looper/looper-srv.exe")
    assert starting._server_from_environment() == "C:/looper/looper-srv.exe"
