"""The chat path must not let a driver exception reach the page unredacted.

`ui.chat._run_query` is the one seam both question paths (typed and sample) use to call
`backend.answer_question`: it must catch any exception the backend raises
and hand it to the existing `ui.results.describe_error` -> `redact_dsn` path
instead of letting it escape to Streamlit's default traceback renderer, which
never sees `redact_dsn`.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import ui.chat as chat
from ui.results import describe_error
from ui.settings import Settings


def test_a_pipeline_exception_is_redacted_before_display() -> None:
    """A driver error echoing its DSN must not put a password on the page."""
    boom = RuntimeError("could not connect to postgresql://u:hunter2@db.example.com:5432/prod")
    with patch("ui.chat.backend.answer_question", side_effect=boom):
        answer = chat._run_query(
            "list customers",
            db_path="postgresql://x",
            model_name="gemini-2.5-flash",
            provider="gemini",
            use_rag=False,
            rag_top_k=3,
        )

    assert answer.sql == ""
    assert answer.result.error is not None

    # `describe_error` is exactly what `render_assistant_turn` passes to
    # `st.error`/`st.warning`, so redacting it here proves what actually
    # reaches the page, not just that an exception was caught.
    shown = describe_error(answer.result.error)

    assert "hunter2" not in shown
    assert "***" in shown


def test_a_successful_call_is_returned_unchanged() -> None:
    """The success path must not be altered by the seam."""
    from text_to_sql_agent import Answer, QueryResult

    expected = Answer(
        sql="SELECT 1",
        result=QueryResult(columns=["1"], rows=[(1,)], sql="SELECT 1", error=None),
        schema_text="CREATE TABLE t (x);",
        retrieval=None,
    )
    with patch("ui.chat.backend.answer_question", return_value=expected):
        actual = chat._run_query(
            "how many rows",
            db_path="some.db",
            model_name="gemini-2.5-flash",
            provider="gemini",
            use_rag=True,
            rag_top_k=5,
        )

    assert actual == expected


def test_the_apps_ollama_call_sends_think_false(customers_db: str, recording_ollama: Any) -> None:
    """The app passes no think flag, so Ollama gets the backend's default: thinking off."""
    recording_ollama.replies.append("SELECT name FROM customers")

    answer = chat._run_query(
        "list customers",
        db_path=customers_db,
        model_name="qwen3.5:9b-q4_K_M",
        provider="ollama",
        use_rag=False,
        rag_top_k=3,
    )

    assert answer.result.ok, answer.result.error
    assert answer.sql == "SELECT name FROM customers"
    assert recording_ollama.reasoning == [False]


def _settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "provider": "ollama",
        "model_name": "qwen3.5:9b-q4_K_M",
        "use_rag": True,
        "rag_top_k": 3,
        "db_path": None,
        "gemini_key": "",
        "key_ok": True,
        "source": "Demo database",
        "demo_name": "University",
        "source_label": "University",
    }
    values.update(overrides)
    return Settings(**values)


def test_a_turn_shows_exactly_the_schema_the_model_was_sent(
    customers_db: str, recording_ollama: Any
) -> None:
    """Codex, 2026-10-20: the context used to be re-retrieved after the answer."""
    recording_ollama.replies.append("SELECT name FROM customers")
    answer = chat._run_query(
        "list customers",
        db_path=customers_db,
        model_name="qwen3.5:9b-q4_K_M",
        provider="ollama",
        use_rag=True,
        rag_top_k=3,
    )

    turn = chat.answer_turn(answer, _settings(), database="customers.db")

    assert turn["schema_text"] in recording_ollama.calls[0].user_prompt
    assert "CREATE TABLE customers" in turn["schema_text"]
    assert "characters of schema text, not provider tokens" in turn["rag_report"]
    assert (turn["database"], turn["provider"], turn["model"]) == (
        "customers.db",
        "ollama",
        "qwen3.5:9b-q4_K_M",
    )
    assert turn["context"] == "schema RAG, top 3"


def test_rag_off_records_plain_ddl_and_no_retrieval_report(
    customers_db: str, recording_ollama: Any
) -> None:
    from text_to_sql_agent import get_schema

    answer = chat._run_query(
        "list customers",
        db_path=customers_db,
        model_name="m",
        provider="ollama",
        use_rag=False,
        rag_top_k=3,
    )
    turn = chat.answer_turn(answer, _settings(use_rag=False), database="customers.db")

    assert turn["schema_text"] == get_schema(customers_db)
    assert turn["rag_report"] is None
    assert turn["context"] == "full schema"
