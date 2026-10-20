"""Turning a `QueryResult` into a dataframe, a chart and a rendered chat turn."""

from __future__ import annotations

import html

import altair as alt
import pandas as pd
import streamlit as st

import text_to_sql_agent as backend
from text_to_sql_agent.control import control_statement_code
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
        "alters anything. Any SQL involved is shown under How this was answered."
    ),
    "BLOCKED_UNSUPPORTED_COLUMN_TYPE": (
        "The generated SQL was not run because it uses a column whose data type "
        "comes from a database extension or a custom type with its own conversions "
        "or comparison rules (for example citext). The agent cannot guarantee such "
        "a query runs only built-in code or returns correct results, so it refuses "
        "it rather than risk a wrong answer. Try asking about other columns. "
        "The SQL is shown under How this was answered."
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


ENGINE_NAMES = {"sqlite": "SQLite", "duckdb": "DuckDB", "postgres": "PostgreSQL"}
_REFUSAL_CODES = ("BLOCKED_UNSAFE_SQL", "BLOCKED_UNSUPPORTED_COLUMN_TYPE")


def humanize(column: str) -> str:
    """`total_revenue` -> `Total revenue`: a column name as a person would say it."""
    words = column.replace("_", " ").strip()
    return words[:1].upper() + words[1:] if words else column


def format_number(value: object) -> str:
    """Thousands separators; whole numbers without decimals, others to two places."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return str(value)
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def answer_headline(df: pd.DataFrame) -> tuple[str, str]:
    """`(headline, facts)` stated from the result rows alone, never from the model.

    A category-and-number result names the largest category, and says when it outweighs
    all the others together; a single value is stated; anything else is counted.
    """
    rows = len(df)
    facts = f"{rows} row{'s' if rows != 1 else ''}, values as stored in the database"
    if rows == 0:
        return "No rows matched the question.", "The query ran and returned nothing."
    if rows == 1 and len(df.columns) == 1:
        column = str(df.columns[0])
        return f"{humanize(column)}: {format_number(df.iloc[0, 0])}", facts
    chart_cols = chartable_columns(df)
    if chart_cols:
        category_col, value_col = chart_cols
        values = pd.to_numeric(df[value_col], errors="coerce")
        top = int(values.idxmax())
        top_value = float(values.iloc[top])
        rest = float(values.drop(values.index[top]).sum())
        label = humanize(value_col).lower()
        name = html.escape(str(df[category_col].iloc[top]))
        if top_value > rest:
            others = _COUNT_WORDS.get(rows - 1, str(rows - 1))
            return (
                f"<em>{name}</em> leads with {format_number(top_value)} in {label}, more than "
                f"the other {others} combined ({format_number(rest)}).",
                facts,
            )
        return f"<em>{name}</em> has the highest {label}: {format_number(top_value)}.", facts
    return f"{rows} row{'s' if rows != 1 else ''} returned.", facts


_COUNT_WORDS = dict(
    enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"])
)

# The page's one accent and its light tint (`ui.styles`).
TEAL = "#0e6e66"
TEAL_LIGHT = "#9cc5bf"


def _render_chart(df: pd.DataFrame) -> None:
    """Horizontal bars for a category-and-number result, in the query's row order."""
    chart_cols = chartable_columns(df)
    if not chart_cols:
        return
    category_col, value_col = chart_cols
    data = df[[category_col, value_col]].copy()
    data[category_col] = data[category_col].astype(str)
    order = list(dict.fromkeys(data[category_col]))
    top = data[value_col].astype(float).idxmax()
    data["is_top"] = data.index == top
    data["label"] = data[value_col].map(format_number)
    title = humanize(value_col)
    base = alt.Chart(data).encode(
        y=alt.Y(f"{category_col}:N", sort=order, title=None, axis=alt.Axis(labelLimit=180)),
        x=alt.X(
            f"{value_col}:Q",
            axis=None,
            scale=alt.Scale(domain=[0, float(data[value_col].astype(float).max()) * 1.3]),
        ),
    )
    bars = base.mark_bar(cornerRadiusEnd=3, height={"band": 0.7}).encode(
        color=alt.condition("datum.is_top", alt.value(TEAL), alt.value(TEAL_LIGHT)),
        tooltip=[
            alt.Tooltip(f"{category_col}:N", title=humanize(category_col)),
            alt.Tooltip("label:N", title=title),
        ],
    )
    labels = base.mark_text(align="left", dx=6, color="#1c2430").encode(text="label:N")
    by = html.escape(humanize(category_col).lower())
    st.markdown(f"<p class='chart-title'>{html.escape(title)} by {by}</p>", unsafe_allow_html=True)
    st.altair_chart(
        (bars + labels)
        .properties(height=34 * len(data) + 10, background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelFont="IBM Plex Sans",
            titleFont="IBM Plex Sans",
            labelColor="#5d6672",
            titleColor="#5d6672",
        ),
        use_container_width=True,
    )


def _render_table(df: pd.DataFrame) -> None:
    shown = df.rename(columns={c: humanize(str(c)) for c in df.columns})
    config = {
        humanize(str(c)): st.column_config.NumberColumn(format="localized")
        for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    }
    st.dataframe(shown, use_container_width=True, hide_index=True, column_config=config)
    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="answer.csv",
        mime="text/csv",
        key=f"csv_{id(df)}",
        type="tertiary",
    )


def _render_result_card(msg: dict) -> None:
    question = html.escape(str(msg.get("question") or ""))
    if question:
        st.markdown(f"<p class='q'>{question}</p>", unsafe_allow_html=True)
    df = msg.get("df")
    error = msg.get("error_text")
    if error:
        message = describe_error(error)
        refused = error in _REFUSAL_CODES
        if df is not None:
            st.warning(message, icon=":material/info:")
        elif refused:
            st.markdown(
                f"<h2 class='headline refused'>Not run: this agent only reads data.</h2>"
                f"<p class='facts'>{html.escape(message)}</p>",
                unsafe_allow_html=True,
            )
            return
        else:
            st.error(message, icon=":material/block:")
            return
    if df is None:
        st.caption("The query returned no columns.")
        return
    headline, facts = answer_headline(df)
    st.markdown(
        f"<h2 class='headline'>{headline}</h2><p class='facts'>{html.escape(facts)}</p>",
        unsafe_allow_html=True,
    )
    if df.empty:
        return
    _render_chart(df)
    _render_table(df)


def _chips(tables: list[dict]) -> str:
    out = []
    for table in tables:
        cls = "hit" if table.get("used") else ""
        out.append(f"<span class='{cls}'>{html.escape(str(table['name']))}</span>")
    return f"<div class='tables'>{''.join(out)}</div>"


def _step_tables(msg: dict) -> str:
    retrieval = msg.get("retrieval")
    if not retrieval:
        full_chars = len(msg.get("schema_text") or "")
        return (
            "<li><h3>Sent the full schema</h3>"
            f"<p>Every table's DDL, {full_chars:,} characters, no sample values.</p></li>"
        )
    tables = retrieval["tables"]
    picked = sum(1 for t in tables if not t["neighbour"])
    neighbours = len(tables) - picked
    total = retrieval.get("total_tables")
    of_total = f" of {total}" if total else ""
    title = f"Picked {picked}{of_total} tables"
    if neighbours:
        title += f", plus {neighbours} joinable neighbour{'s' if neighbours != 1 else ''}"
    terms = retrieval.get("terms") or []
    why = (
        "Ranked by the question's words ("
        + ", ".join(f"<span class='mono'>{html.escape(t)}</span>" for t in terms[:6])
        + ")"
        if terms
        else "Ranked by similarity to the question"
    )
    if any(t["used"] for t in tables):
        why += "; the SQL used the highlighted ones."
    else:
        why += "."
    pct = retrieval.get("vs_hints_pct")
    size = f"Sent {retrieval['sent_chars']:,} characters of schema"
    if pct is not None and pct != 0:
        direction = "less" if pct < 0 else "more"
        size += f": {abs(pct):.0f}% {direction} than every table with sample values."
    else:
        size += "."
    return f"<li><h3>{title}</h3><p>{why}</p>{_chips(tables)}<p class='size'>{size}</p></li>"


_DIALECTS = {"sqlite": "sqlite", "duckdb": "duckdb", "postgres": "postgres"}


def _is_model_verdict(msg: dict) -> bool:
    """Whether the SQL is the model's own refusal statement rather than a refused query."""
    sql = str(msg.get("sql_text") or msg.get("blocked_sql") or "")
    dialect = _DIALECTS.get(str(msg.get("engine") or ""), "sqlite")
    return bool(sql) and control_statement_code(sql, dialect=dialect) == msg.get("error_text")


def _step_check_and_run(msg: dict) -> str:
    error = msg.get("error_text")
    df = msg.get("df")
    engine = ENGINE_NAMES.get(str(msg.get("engine") or ""), "the database")
    if error in _REFUSAL_CODES and _is_model_verdict(msg):
        check = "<span class='bad'>Declined</span>: the model answered that it changes data."
        run = "<li><h3>Not run</h3><p>Nothing was sent to the database.</p></li>"
    elif error in _REFUSAL_CODES:
        check = "<span class='bad'>Refused</span>: it was not a read-only query."
        run = "<li><h3>Not run</h3><p>Nothing was sent to the database.</p></li>"
    elif error == "UNANSWERABLE_WITH_GIVEN_SCHEMA":
        check = "The model said this schema cannot answer it."
        run = "<li><h3>Not run</h3><p>There was no query to run.</p></li>"
    elif not msg.get("sql_text"):
        check = "There was no SQL to check."
        run = "<li><h3>Not run</h3><p>The model returned no SQL.</p></li>"
    else:
        check = "<span class='ok'>Read-only</span>: one statement, no internal tables."
        if df is not None:
            rows = len(df)
            note = " (cut at the row limit)" if error else ""
            plural = "s" if rows != 1 else ""
            run = f"<li><h3>Ran it on {engine}</h3><p>{rows:,} row{plural}{note}.</p></li>"
        else:
            run = (
                f"<li><h3>Ran it on {engine}</h3><p>It failed; see the message beside it.</p></li>"
            )
    return f"<li><h3>Checked it</h3><p>{check}</p></li>{run}"


def _render_trace(msg: dict) -> None:
    sql = msg.get("sql_text") or msg.get("blocked_sql") or ""
    sql_step = (
        f"<li><h3>Wrote SQL</h3><pre>{html.escape(sql)}</pre></li>"
        if sql
        else "<li><h3>Wrote SQL</h3><p>The model returned none.</p></li>"
    )
    model = " ".join(str(x) for x in (msg.get("provider"), msg.get("model")) if x)
    st.html(
        "<div class='trace'><h2>How this was answered</h2>"
        f"<p class='who'>{html.escape(str(msg.get('database') or ''))}, "
        f"{html.escape(model)}</p><ol>"
        f"{_step_tables(msg)}{sql_step}{_step_check_and_run(msg)}</ol></div>"
    )
    if msg.get("schema_text"):
        with st.expander("Full schema sent"):
            st.code(msg["schema_text"], language="sql")
    if msg.get("rag_report"):
        with st.expander("Retrieval report"):
            st.text(msg["rag_report"])


def render_answer(msg: dict) -> None:
    """One answer: the result card beside "How this was answered", one column when narrow.

    Everything shown is what the turn recorded when it was answered (`ui.chat.answer_turn`),
    never a re-computation, so it stays true after the connection changes.
    """
    left, right = st.columns([1.55, 1], gap="medium")
    with left, st.container(border=True):
        _render_result_card(msg)
    with right, st.container(border=True):
        _render_trace(msg)
