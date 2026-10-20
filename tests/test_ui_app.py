"""The Ask view: header, explicit states and an answer's Result, SQL and Context tabs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture
def no_server_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEYS", "GOOGLE_API_KEYS"):
        monkeypatch.delenv(name, raising=False)


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    return at


def test_the_ask_view_says_what_is_missing_and_that_questions_are_independent(
    no_server_keys: None,
) -> None:
    at = _app()
    assert not at.exception
    assert any("Text-to-SQL Agent" in m.value for m in at.markdown)
    assert any("answered on its own" in c.value for c in at.caption)
    assert any("Add a Gemini API key" in i.value for i in at.info)
    assert at.pills(key="sample_University").disabled


def test_switching_to_ollama_clears_the_key_message(no_server_keys: None) -> None:
    at = _app()
    at.sidebar.selectbox(key="sb_provider").select("ollama").run()
    assert not any("Add a Gemini API key" in i.value for i in at.info)
    assert not at.pills(key="sample_University").disabled


def test_an_answer_shows_its_recorded_database_model_sql_and_context(
    no_server_keys: None,
) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["messages"] = [
        {"role": "user", "content": "How many students?"},
        {
            "role": "assistant",
            "kind": "result",
            "error_text": None,
            "blocked_sql": None,
            "df": pd.DataFrame({"major": ["CS", "Math"], "n": [3, 2]}),
            "sql_text": "SELECT major, COUNT(*) AS n FROM students GROUP BY major",
            "schema_text": "CREATE TABLE students (id INTEGER, major TEXT);",
            "rag_report": "Schema RAG strategy: hybrid",
            "database": "University",
            "provider": "ollama",
            "model": "qwen3.5:9b-q4_K_M",
            "context": "schema RAG, top 6",
        },
    ]
    at.run()
    assert not at.exception
    assert any(
        c.value == "University · ollama qwen3.5:9b-q4_K_M · schema RAG, top 6" for c in at.caption
    )
    assert [t.label for t in at.tabs] == ["Result", "SQL", "Context"]
    codes = [c.value for c in at.code]
    assert "SELECT major, COUNT(*) AS n FROM students GROUP BY major" in codes
    assert "CREATE TABLE students (id INTEGER, major TEXT);" in codes
    assert any(c.value == "2 rows" for c in at.caption)


def test_a_refusal_is_explained_and_its_sql_kept(no_server_keys: None) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["messages"] = [
        {
            "role": "assistant",
            "kind": "result",
            "error_text": "BLOCKED_UNSAFE_SQL",
            "blocked_sql": "DELETE FROM students",
            "df": None,
            "sql_text": "DELETE FROM students",
            "schema_text": "CREATE TABLE students (id INTEGER);",
            "rag_report": None,
            "database": "University",
            "provider": "ollama",
            "model": "m",
            "context": "full schema",
        }
    ]
    at.run()
    assert not at.exception
    assert any("only reads data" in e.value for e in at.error)
    assert "DELETE FROM students" in [c.value for c in at.code]
