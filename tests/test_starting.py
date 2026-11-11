"""Which server `looper.run` starts: the one the caller names, or the environment's."""

from __future__ import annotations

import pytest

from looper import starting


def test_without_a_variable_looper_srv_is_started(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOOPER_SRV", raising=False)
    monkeypatch.delenv("LOOPER_CLI", raising=False)

    assert starting._server_from_environment() == "looper-srv"


def test_the_older_looper_cli_is_still_read_with_a_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LOOPER_SRV", raising=False)
    monkeypatch.setenv("LOOPER_CLI", "uv run looper-cli")

    with pytest.deprecated_call(match="LOOPER_SRV"):
        assert starting._server_from_environment() == "uv run looper-cli"


def test_looper_srv_wins_over_the_older_looper_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOOPER_CLI", "uv run looper-cli")
    monkeypatch.setenv("LOOPER_SRV", "C:/looper/looper-srv.exe")

    assert starting._server_from_environment() == "C:/looper/looper-srv.exe"


def test_a_named_server_wins_over_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOOPER_SRV", "C:/looper/looper-srv.exe")

    assert starting._server_named("./looper-srv", None) == "./looper-srv"


def test_looper_cli_is_the_deprecated_name_of_server() -> None:
    with pytest.deprecated_call(match="server="):
        assert starting._server_named(None, ["looper-cli"]) == ["looper-cli"]


def test_the_server_cannot_be_named_twice() -> None:
    with pytest.raises(TypeError, match="once"):
        starting._server_named("looper-srv", "looper-cli")
