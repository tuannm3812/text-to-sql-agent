"""A Gemini key typed into one app session must never reach another (Codex, 2026-10-20).

The sidebar used to copy a typed key into `os.environ`, where `ui.secrets` and the
process-level `GeminiManager` read it for every later session. The key now travels with
each call (`generate_sql(gemini_api_key=...)`) and is never written to the environment.
No real key and no network call is used: the Gemini SDK is replaced by a recorder.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from text_to_sql_agent import gemini_manager
from text_to_sql_agent.llm import generate_sql

KEY_ENV_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEYS", "GOOGLE_API_KEYS")


@pytest.fixture
def no_server_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in KEY_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("text_to_sql_agent.llm.load_env", lambda: None)
    monkeypatch.setattr(gemini_manager, "_DEFAULT_MANAGER", None)


def _recording_gemini(used: list[str]) -> Any:
    class Models:
        def __init__(self, api_key: str) -> None:
            self.api_key = api_key

        def generate_content(self, **_: Any) -> Any:
            used.append(self.api_key)
            return SimpleNamespace(text="SELECT 1", usage_metadata=None)

    genai = SimpleNamespace(Client=lambda api_key: SimpleNamespace(models=Models(api_key)))
    types = SimpleNamespace(GenerateContentConfig=lambda **kwargs: kwargs)
    return lambda: ("google-genai", genai, types)


def test_a_per_call_key_is_used_alone_and_not_kept(
    no_server_keys: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    used: list[str] = []
    with patch("text_to_sql_agent.llm._load_gemini_sdk", side_effect=_recording_gemini(used)):
        generate_sql("q", "CREATE TABLE t (x);", provider="gemini", gemini_api_key="key-a")
        monkeypatch.setenv("GEMINI_API_KEY", "server-key")
        generate_sql("q", "CREATE TABLE t (x);", provider="gemini")

    assert used == ["key-a", "server-key"]
    assert gemini_manager._DEFAULT_MANAGER is not None
    assert "key-a" not in gemini_manager._DEFAULT_MANAGER.keys


def _app() -> AppTest:
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30)
    app.run()
    return app


def test_a_key_typed_in_one_session_is_not_loaded_in_another(no_server_keys: None) -> None:
    import os

    first = _app()
    first.text_input(key="sb_gemini_key").input("typed-by-a").run()
    assert any("key loaded" in s.value for s in first.success)
    assert "typed-by-a" not in os.environ.values()

    second = _app()
    assert not any("key loaded" in s.value for s in second.success)
    assert second.text_input(key="sb_gemini_key").value == ""


def test_clearing_the_key_unloads_it(no_server_keys: None) -> None:
    app = _app()
    app.text_input(key="sb_gemini_key").input("typed").run()
    app.text_input(key="sb_gemini_key").input("").run()
    assert not any("key loaded" in s.value for s in app.success)
