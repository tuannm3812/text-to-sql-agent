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


def _trace(at: AppTest) -> str:
    """The "How this was answered" panel's HTML (`st.html`), as one string."""
    return "".join(element.proto.body for element in at.get("html"))


def _turn(**overrides: object) -> dict[str, object]:
    turn: dict[str, object] = {
        "role": "assistant",
        "kind": "result",
        "question": "Which product categories generate the most revenue?",
        "error_text": None,
        "blocked_sql": None,
        "df": pd.DataFrame(
            {"category": ["Electronics", "Fashion"], "total_revenue": [173366, 29991]}
        ),
        "sql_text": "SELECT category, SUM(x) AS total_revenue FROM t GROUP BY category",
        "schema_text": "CREATE TABLE products (category TEXT);",
        "rag_report": "Schema RAG strategy: hybrid",
        "retrieval": {
            "tables": [
                {"name": "products", "neighbour": False, "used": True},
                {"name": "orders", "neighbour": True, "used": False},
            ],
            "terms": ["product", "category"],
            "total_tables": 11,
            "sent_chars": 4971,
            "vs_hints_pct": -15.4,
        },
        "database": "Retail Analytics",
        "engine": "sqlite",
        "provider": "ollama",
        "model": "qwen3.5:9b-q4_K_M",
        "context": "schema RAG, top 6",
    }
    turn.update(overrides)
    return turn


def test_the_ask_view_says_what_is_missing_and_that_questions_are_independent(
    no_server_keys: None,
) -> None:
    at = _app()
    assert not at.exception
    assert any("Ask your data. Inspect the SQL." in m.value for m in at.markdown)
    assert any("answered on its own" in m.value for m in at.markdown)
    assert any("Add a Gemini API key under Change" in i.value for i in at.info)
    assert at.pills(key="sample_University").disabled


def test_switching_to_ollama_clears_the_key_message(no_server_keys: None) -> None:
    at = _app()
    at.selectbox(key="sb_provider").select("ollama").run()
    assert not any("Add a Gemini API key" in i.value for i in at.info)
    assert not at.pills(key="sample_University").disabled


def test_an_answer_states_its_result_and_how_it_was_answered(no_server_keys: None) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["messages"] = [_turn()]
    at.run()
    assert not at.exception
    headline = next(m.value for m in at.markdown if "class='headline'" in m.value)
    assert "<em>Electronics</em> leads with 173,366</h2>" in headline
    assert "2 rows. More than the other one combined (29,991)." in headline
    trace = _trace(at)
    assert "Picked 1 of 11 tables, plus 1 joinable neighbour" in trace
    assert "<span class='hit'>products</span>" in trace
    assert "Sent 4,971 characters of schema: 15% less" in trace
    assert "SELECT category, SUM(x) AS total_revenue FROM t GROUP BY category" in trace
    assert "Read-only" in trace and "Ran it on SQLite" in trace
    assert "CREATE TABLE products (category TEXT);" in [c.value for c in at.code]


def test_the_models_own_refusal_is_called_a_decline_and_nothing_runs(
    no_server_keys: None,
) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    sql = "SELECT 'BLOCKED_UNSAFE_SQL' AS error;"
    at.session_state["messages"] = [
        _turn(df=None, error_text="BLOCKED_UNSAFE_SQL", sql_text=sql, blocked_sql=sql)
    ]
    at.run()
    assert not at.exception
    assert any("Not run: this agent only reads data." in m.value for m in at.markdown)
    trace = _trace(at)
    assert "Declined" in trace and "Nothing was sent to the database" in trace


def test_a_refused_write_is_called_refused(no_server_keys: None) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    sql = "DELETE FROM orders"
    at.session_state["messages"] = [
        _turn(df=None, error_text="BLOCKED_UNSAFE_SQL", sql_text=sql, blocked_sql=sql)
    ]
    at.run()
    assert "Refused" in _trace(at) and "DELETE FROM orders" in _trace(at)


def test_rag_off_says_the_full_schema_was_sent(no_server_keys: None) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state["messages"] = [_turn(retrieval=None, rag_report=None)]
    at.run()
    assert "Sent the full schema" in _trace(at)


def test_an_unsupported_type_is_not_called_a_write(no_server_keys: None) -> None:
    """Codex, 2026-10-21: a read-only SELECT refused for a column type was called a write."""
    at = AppTest.from_file(APP, default_timeout=60)
    sql = "SELECT name FROM contacts"
    at.session_state["messages"] = [
        _turn(df=None, error_text="BLOCKED_UNSUPPORTED_COLUMN_TYPE", sql_text=sql, blocked_sql=sql)
    ]
    at.run()
    headings = " ".join(m.value for m in at.markdown)
    assert "a column type the agent cannot check" in headings
    assert "only reads data" not in headings
    assert "not a read-only query" not in _trace(at)
    assert "casts or operators" in _trace(at)


def test_switching_provider_does_not_carry_the_other_providers_model(
    no_server_keys: None,
) -> None:
    """Found by the keyboard acceptance check: Ollama was asked for `gemini-2.5-flash`."""
    at = _app()
    at.selectbox(key="sb_provider").select("ollama").run()
    conn = next(m.value for m in at.markdown if "class='conn'" in m.value)
    assert "gemini" not in conn
    assert "local" in conn


@pytest.mark.parametrize(("first", "second"), [("gemini", "ollama"), ("ollama", "gemini")])
def test_a_custom_model_never_reaches_the_other_provider(
    no_server_keys: None, monkeypatch: pytest.MonkeyPatch, first: str, second: str
) -> None:
    """Codex, 2026-10-22: a custom name typed for one provider was sent to the other."""
    from text_to_sql_agent import Answer, QueryResult

    calls: list[tuple[str, str]] = []

    def fake_run_query(prompt: str, **kwargs: object) -> Answer:
        calls.append((str(kwargs["provider"]), str(kwargs["model_name"])))
        return Answer(sql="", result=QueryResult([], [], error="x"), schema_text="", retrieval=None)

    monkeypatch.setenv("GEMINI_API_KEY", "server-key")
    monkeypatch.setattr("ui.chat._run_query", fake_run_query)
    at = _app()
    at.selectbox(key="sb_provider").select(first).run()
    at.selectbox(key=f"sb_model_choice_{first}").select("Custom").run()
    at.text_input(key=f"sb_custom_model_{first}").input("custom-for-review").run()
    at.selectbox(key="sb_provider").select(second).run()
    at.text_input(key="question_box").input("How many students?").run()
    at.button(key="FormSubmitter:ask_form-Ask").click().run()

    assert calls and calls[-1][0] == second
    assert calls[-1][1] != "custom-for-review"
