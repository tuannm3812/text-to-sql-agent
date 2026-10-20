"""Turning a `QueryResult` into a dataframe, a chart and a rendered chat turn."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import text_to_sql_agent as backend
from ui.uploads import redact_dsn


def result_to_dataframe(result: backend.QueryResult) -> pd.DataFrame | None:
    """Convert a `QueryResult` to a dataframe, or None when it has no columns."""
    if not result.columns:
        return None
    return pd.DataFrame(result.rows, columns=result.columns)


def chartable_columns(df: pd.DataFrame) -> tuple[str, str] | None:
    """Return (category_col, value_col) if `df` is a two-column GROUP BY-shaped result."""
    if len(df.columns) != 2 or len(df) < 2:
        return None
    first, second = df.columns[0], df.columns[1]
    first_numeric = pd.api.types.is_numeric_dtype(df[first])
    second_numeric = pd.api.types.is_numeric_dtype(df[second])
    if first_numeric and not second_numeric:
        return second, first
    if second_numeric and not first_numeric:
        return first, second
    return None


_ERROR_MESSAGES = {
    "BLOCKED_UNSAFE_SQL": (
        "The request asked to change data, or the query was not read-only, so it was "
        "not run. This agent only reads data; it never inserts, updates, deletes or "
        "alters anything. Any SQL involved is in the SQL tab."
    ),
    "BLOCKED_UNSUPPORTED_COLUMN_TYPE": (
        "The generated SQL was not run because it uses a column whose data type "
        "comes from a database extension or a custom type with its own conversions "
        "or comparison rules (for example citext). The agent cannot guarantee such "
        "a query runs only built-in code or returns correct results, so it refuses "
        "it rather than risk a wrong answer. Try asking about other columns. "
        "The SQL is in the SQL tab."
    ),
    "UNANSWERABLE_WITH_GIVEN_SCHEMA": (
        "The question could not be answered from this database's schema. "
        "Try rephrasing it, or pick a database that holds the relevant tables."
    ),
    "EMPTY_GENERATED_SQL": (
        "The model returned no SQL at all, so there was nothing to run. "
        "This is a model failure, not a refusal; try asking again."
    ),
}

_TRUNCATED_PREFIX = "RESULT_TRUNCATED_TO_"
_ABORTED_PREFIX = "QUERY_ABORTED_AFTER_"


def describe_error(code: str | None) -> str:
    """Turn a `QueryResult.error` code into a message for a non-technical reader.

    Anything unrecognised is passed through, since the backend also puts raw
    exception text in this field - with any DSN password masked by
    `redact_dsn`, because a driver error can echo the connection string.

    Args:
        code: The `QueryResult.error` value, or None.

    Returns:
        A human-readable message, or `""` when `code` is None.
    """
    if not code:
        return ""
    if code in _ERROR_MESSAGES:
        return _ERROR_MESSAGES[code]
    if code.startswith(_TRUNCATED_PREFIX):
        limit = code[len(_TRUNCATED_PREFIX) :].removesuffix("_ROWS")
        return (
            f"Showing the first {limit} rows. The query matched more than that, "
            "so add a filter or an aggregate to narrow it down."
        )
    if code.startswith(_ABORTED_PREFIX) and code.endswith("_VM_STEPS"):
        budget = code[len(_ABORTED_PREFIX) :].removesuffix("_VM_STEPS")
        return (
            f"The query was stopped after {budget} database steps to keep the demo "
            "responsive. It was probably joining tables without a matching condition."
        )
    if code.startswith(_ABORTED_PREFIX) and code.endswith("_MS"):
        budget = code[len(_ABORTED_PREFIX) :].removesuffix("_MS")
        return (
            f"The query was stopped after {budget} ms to keep the demo "
            "responsive. It was probably joining tables without a matching condition."
        )
    # Raw exception text: a driver may echo the DSN it failed to reach.
    return redact_dsn(code)


# The page's one accent, a muted warm brown, so a chart sits in the same palette.
CHART_COLOR = "#9a6b3f"


def _render_chart(df: pd.DataFrame) -> None:
    """A bar chart when the result is a category and a number, in the query's row order."""
    chart_cols = chartable_columns(df)
    if not chart_cols:
        return
    category_col, value_col = chart_cols
    # Preserve the query's row order (e.g. ORDER BY ... DESC) instead of
    # letting the chart library re-sort categories alphabetically.
    labels = df[category_col].astype(str)
    unique_order = list(dict.fromkeys(labels))
    ordered = pd.Categorical(labels, categories=unique_order, ordered=True)
    chart_df = df.assign(**{category_col: ordered}).set_index(category_col)
    st.bar_chart(chart_df[value_col], color=CHART_COLOR, height=280)


def turn_caption(msg: dict) -> str:
    """`database · provider/model · context` for a turn, from what it recorded."""
    parts = [msg.get("database"), _model_label(msg), msg.get("context")]
    return " · ".join(str(part) for part in parts if part)


def _model_label(msg: dict) -> str:
    provider, model = msg.get("provider"), msg.get("model")
    if provider and model:
        return f"{provider} {model}"
    return str(provider or model or "")


def _render_result(msg: dict) -> None:
    df = msg.get("df")
    if msg.get("error_text"):
        message = describe_error(msg["error_text"])
        if df is not None:
            st.warning(message, icon=":material/info:")
        else:
            st.error(message, icon=":material/block:")
    if df is None:
        if not msg.get("error_text"):
            st.caption("The query returned no columns.")
        return
    if df.empty:
        st.caption("The query ran and returned no rows.")
        return
    st.caption(f"{len(df)} row{'s' if len(df) != 1 else ''}")
    st.dataframe(df, use_container_width=True, hide_index=True)
    _render_chart(df)


def _render_context(msg: dict) -> None:
    if not msg.get("schema_text"):
        st.caption("No schema was sent: the question failed before the model was called.")
        return
    if msg.get("rag_report"):
        st.caption(
            "Only the selected tables were sent, with sample values from low-cardinality text "
            "columns. Sizes are characters of schema text, not provider tokens."
        )
    else:
        st.caption("The full schema was sent, as DDL only.")
    st.code(msg["schema_text"], language="sql")
    if msg.get("rag_report"):
        with st.expander("Retrieval report", expanded=False):
            st.text(msg["rag_report"])


def render_assistant_turn(msg: dict) -> None:
    """Render one assistant message: plain text, or an answer with Result, SQL and Context.

    The three tabs show what the turn recorded when it was answered (`ui.chat.answer_turn`),
    never a re-computation, so they stay true after the sidebar changes.
    """
    with st.chat_message("assistant", avatar=":material/database:"):
        if msg.get("kind") == "text":
            st.markdown(msg.get("content", ""))
            return
        if msg.get("kind") != "result":
            return
        caption = turn_caption(msg)
        if caption:
            st.caption(caption)
        result_tab, sql_tab, context_tab = st.tabs(["Result", "SQL", "Context"])
        with result_tab:
            _render_result(msg)
        with sql_tab:
            sql = msg.get("sql_text") or msg.get("blocked_sql")
            if sql:
                st.code(sql, language="sql")
                if msg.get("error_text") and msg.get("df") is None:
                    st.caption("This SQL was not run, or did not complete; see Result.")
            else:
                st.caption("The model returned no SQL.")
        with context_tab:
            _render_context(msg)
