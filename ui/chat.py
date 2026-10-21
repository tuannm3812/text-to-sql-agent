"""The Ask view: the question box, sample questions and the answers so far, newest first."""

from __future__ import annotations

from typing import Any

import sqlglot
import streamlit as st
from sqlglot import exp

import text_to_sql_agent as backend
from ui.constants import DEMO_DATABASES, SOURCE_DEMO
from ui.results import render_answer, result_to_dataframe
from ui.settings import Settings


def _run_query(
    prompt: str,
    *,
    db_path: str,
    model_name: str,
    provider: str,
    use_rag: bool,
    rag_top_k: int,
    gemini_api_key: str | None = None,
) -> backend.Answer:
    """Call the backend, turning any exception it raises into an `Answer` with an error.

    `backend.answer_question` talks to the configured database driver, and a driver
    error can embed the DSN it failed to reach, including its password. Left uncaught,
    that exception would escape to Streamlit's default traceback renderer, which never
    sees `ui.uploads.redact_dsn`. Catching it here and putting the raw exception text in
    `QueryResult.error` routes it through the one redaction `ui.results.describe_error`
    already applies to any unrecognised error code.

    Args:
        prompt: The user's question.
        db_path: The database path or DSN to query.
        model_name: Provider-specific model identifier.
        provider: `"gemini"` or `"ollama"`.
        use_rag: Whether to retrieve a relevant schema subset.
        rag_top_k: Number of schema chunks to retrieve when `use_rag` is set.
        gemini_api_key: This session's Gemini key, passed with the call and never
            stored process-wide; `None` uses the server's configured keys.

    Returns:
        The backend's `Answer`, whose `schema_text` and `retrieval` are exactly what the
        model was given; on an exception, an `Answer` with no SQL or context and the
        exception's text (not yet redacted) in `result.error`.
    """
    try:
        return backend.answer_question(
            prompt,
            db_path=db_path,
            model_name=model_name,
            provider=provider,
            use_rag=use_rag,
            rag_top_k=rag_top_k,
            gemini_api_key=gemini_api_key,
        )
    except Exception as exc:  # noqa: BLE001 - any backend/driver failure must reach
        # the page redacted, not as a raw Streamlit traceback.
        failed = backend.QueryResult(
            columns=[], rows=[], sql=None, error=f"{type(exc).__name__}: {exc}"
        )
        return backend.Answer(sql="", result=failed, schema_text="", retrieval=None)


# The schema a bare table name resolves to, per engine; PostgreSQL's is each chunk's own
# `home_schema` (`SchemaChunk`), so it is absent here.
_DEFAULT_SCHEMAS = {"sqlite": "main", "duckdb": "main"}


def _tables_in_sql(sql: str, dialect: str) -> set[str]:
    """Lowercased table references the SQL reads, schema-qualified where the SQL qualifies.

    CTE names are left out: they are not tables. Empty if the SQL does not parse.
    """
    try:
        tree = sqlglot.parse_one(sql, read=dialect)
    except Exception:  # noqa: BLE001 - any parse failure just means "unknown"
        return set()
    ctes = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    refs = set()
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if not name or (not table.db and name in ctes):
            continue
        refs.add(f"{table.db.lower()}.{name}" if table.db else name)
    return refs


def _chunk_spellings(chunk: Any, engine: str) -> set[str]:
    """Every reference that names exactly this chunk's table.

    `qualified_name` is the spelling a bare name resolves to, so a bare reference matches
    only a bare-spelled chunk; a schema-qualified reference matches the chunk in that
    schema, whether it is spelled bare (its home or default schema) or qualified.
    """
    spellings = {chunk.qualified_name.lower()}
    if not chunk.schema_name:
        home = chunk.home_schema or _DEFAULT_SCHEMAS.get(engine, "")
        if home:
            spellings.add(f"{home.lower()}.{chunk.table_name.lower()}")
    return spellings


def _retrieval_summary(
    answer: backend.Answer, db_path: str, engine: str, dialect: str
) -> dict[str, Any] | None:
    """What "How this was answered" says about table selection, from the recorded retrieval."""
    retrieval = answer.retrieval
    if retrieval is None:
        return None
    used = _tables_in_sql(answer.sql, dialect)
    tables = []
    terms: list[str] = []
    used_terms: list[str] = []
    for chunk in retrieval.chunks:
        reasons = chunk.match_reasons or []
        neighbour = any(reason.startswith("foreign-key neighbor") for reason in reasons)
        is_used = bool(_chunk_spellings(chunk, engine) & used)
        for reason in reasons:
            if reason.startswith(("table match: ", "column match: ")):
                for term in reason.split(": ", 1)[1].split(", "):
                    for bucket in (terms, used_terms) if is_used else (terms,):
                        if term not in bucket:
                            bucket.append(term)
        tables.append(
            {
                "name": chunk.qualified_name,
                "neighbour": neighbour,
                "used": is_used,
            }
        )
    try:
        total: int | None = len(backend.get_schema_chunks(db_path))
    except Exception:  # noqa: BLE001 - the count is a nicety, never a failure
        total = None
    return {
        "tables": tables,
        # The words that ranked the tables the SQL used, else every table's.
        "terms": used_terms or terms,
        "total_tables": total,
        "sent_chars": retrieval.sent_schema_chars,
        "vs_hints_pct": retrieval.change_vs_ddl_with_hints_pct,
    }


def answer_turn(
    answer: backend.Answer,
    settings: Settings,
    *,
    question: str,
    database: str,
    db_path: str,
) -> dict[str, Any]:
    """The history record of one question and its answer, with what it was given and by whom.

    Everything shown beside the result comes from `answer` itself, so the SQL and context
    stay the ones that produced it after the user switches database or model.
    """
    result = answer.result
    try:
        opened = backend.open_engine(db_path)
        engine, dialect = opened.name, opened.sqlglot_dialect
    except Exception:  # noqa: BLE001 - only a label
        engine, dialect = "", "sqlite"
    return {
        "role": "assistant",
        "kind": "result",
        "question": question,
        "error_text": result.error,
        "blocked_sql": result.sql if result.error else None,
        "df": result_to_dataframe(result) if result.columns else None,
        "sql_text": answer.sql,
        "schema_text": answer.schema_text or None,
        "rag_report": answer.retrieval.report if answer.retrieval is not None else None,
        "retrieval": _retrieval_summary(answer, db_path, engine, dialect),
        "database": database,
        "engine": engine,
        "provider": settings.provider,
        "model": settings.model_name,
        "context": (f"schema RAG, top {settings.rag_top_k}" if settings.use_rag else "full schema"),
    }


def _model_name(settings: Settings) -> str:
    return (settings.model_name or "").strip() or (
        backend.DEFAULT_MODEL_NAME
        if settings.provider == "gemini"
        else backend.DEFAULT_OLLAMA_MODEL
    )


def ask(prompt: str, settings: Settings, *, db_path: str, database: str) -> None:
    """Answer one question and add it to the history, newest first on the page.

    The one path for typed and sample questions alike, so both are guarded the same way.
    """
    with st.spinner("Writing SQL and running the query..."):
        answer = _run_query(
            prompt,
            db_path=db_path,
            model_name=_model_name(settings),
            provider=settings.provider,
            use_rag=settings.use_rag,
            rag_top_k=settings.rag_top_k,
            gemini_api_key=(settings.gemini_key or None) if settings.provider == "gemini" else None,
        )
    st.session_state.messages.append(
        answer_turn(answer, settings, question=prompt, database=database, db_path=db_path)
    )


def status_message(settings: Settings) -> str | None:
    """What stops a question being asked right now, as an instruction; `None` when ready."""
    if settings.open_error:
        return settings.open_error
    if settings.db_path is None:
        if settings.source == SOURCE_DEMO:
            return "The demo database file is missing. Create it under Change, then Advanced."
        return "Choose a database under Change to start."
    if not settings.key_ok:
        return "Add a Gemini API key under Change, or switch the model to Ollama."
    return None


def _queue_sample(key: str) -> None:
    """`st.pills` callback: put the chosen question in the box and clear the selection."""
    chosen = st.session_state.get(key)
    if chosen:
        st.session_state["question_box"] = chosen
        st.session_state["pending_question"] = chosen
    st.session_state[key] = None


def render_ask(settings: Settings) -> None:
    """The Ask view: the product line, the question box, sample questions, then answers."""
    answered = any(msg.get("kind") == "result" for msg in st.session_state.messages)
    # Once there is an answer, the subtitle gives way so the answer starts higher.
    subtitle = (
        ""
        if answered
        else "<p class='hero-sub'>Questions become read-only SQL that is checked before it "
        "runs. Every answer keeps the SQL and the schema the model saw.</p>"
    )
    st.markdown(
        f"<h1 class='hero'>Ask your data. Inspect the SQL.</h1>{subtitle}",
        unsafe_allow_html=True,
    )
    status = status_message(settings)
    ready = status is None and settings.db_path is not None

    with st.container(key="ask_box"), st.form("ask_form", clear_on_submit=False, border=False):
        box, button = st.columns([6, 1], vertical_alignment="center")
        question = box.text_input(
            "Question",
            key="question_box",
            placeholder="Ask a question about the selected database",
            label_visibility="collapsed",
        )
        submitted = button.form_submit_button(
            "Ask", type="primary", disabled=not ready, use_container_width=True
        )

    if settings.source == SOURCE_DEMO:
        demo = DEMO_DATABASES.get(settings.demo_name, next(iter(DEMO_DATABASES.values())))
        key = f"sample_{settings.demo_name}"
        labels = dict(zip(demo["questions"], demo["labels"], strict=True))
        st.pills(
            "Try",
            demo["questions"],
            format_func=labels.__getitem__,
            key=key,
            on_change=_queue_sample,
            args=(key,),
            disabled=not ready,
            label_visibility="visible",
        )
    st.markdown(
        "<p class='note'>Each question is answered on its own; earlier questions are not sent.</p>",
        unsafe_allow_html=True,
    )
    if status is not None:
        st.info(status, icon=":material/info:")

    pending = st.session_state.pop("pending_question", None)
    to_ask = pending or (question.strip() if submitted else "")
    if to_ask and ready and settings.db_path:
        ask(to_ask, settings, db_path=settings.db_path, database=settings.source_label)
        st.rerun()

    results = [msg for msg in st.session_state.messages if msg.get("kind") == "result"]
    for index, msg in reversed(list(enumerate(results))):
        render_answer(msg, key=f"answer_{index}")
