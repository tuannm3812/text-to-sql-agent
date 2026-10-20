"""The question surface: sample questions, the answers so far and the input."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import streamlit as st

import text_to_sql_agent as backend
from ui.constants import DEMO_DATABASES, SOURCE_DEMO
from ui.results import render_assistant_turn, result_to_dataframe
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


def answer_turn(answer: backend.Answer, settings: Settings, *, database: str) -> dict[str, Any]:
    """The chat-history record of one answer, with the context it was given and by whom.

    Everything shown beside the result comes from `answer` itself, so the SQL and context
    stay the ones that produced it after the user switches database or model.
    """
    result = answer.result
    return {
        "role": "assistant",
        "kind": "result",
        "error_text": result.error,
        "blocked_sql": result.sql if result.error else None,
        "df": result_to_dataframe(result) if result.columns else None,
        "sql_text": answer.sql,
        "schema_text": answer.schema_text or None,
        "rag_report": answer.retrieval.report if answer.retrieval is not None else None,
        "database": database,
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
    """Answer one question and append it and its answer to the chat history.

    The one path for typed and sample questions alike, so both are guarded the same way.
    """
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Generating SQL and running the query..."):
        answer = _run_query(
            prompt,
            db_path=db_path,
            model_name=_model_name(settings),
            provider=settings.provider,
            use_rag=settings.use_rag,
            rag_top_k=settings.rag_top_k,
            gemini_api_key=(settings.gemini_key or None) if settings.provider == "gemini" else None,
        )
    st.session_state.messages.append(answer_turn(answer, settings, database=database))


def _status_message(settings: Settings) -> str | None:
    """What stops a question being asked right now, as an instruction; `None` when ready."""
    if settings.db_path is None:
        if settings.source == SOURCE_DEMO:
            return "The demo database file is missing. Create it under **Advanced** in the sidebar."
        return "Choose a database in the sidebar to start."
    if not settings.key_ok:
        return "Add a Gemini API key in the sidebar, or switch the provider to Ollama."
    return None


def _queue_sample(key: str) -> None:
    """`st.pills` callback: remember the chosen question and clear the selection."""
    st.session_state["pending_sample"] = st.session_state.get(key)
    st.session_state[key] = None


def render_sample_question(settings: Settings) -> None:
    """Offer the active demo's sample questions as one-click pills.

    Does nothing unless the sidebar's source is a demo database. A click goes through
    `ask`, the same path a typed question takes.

    Args:
        settings: The choices the sidebar collected for this render.
    """
    if settings.source != SOURCE_DEMO:
        return
    demo_name = settings.demo_name
    demo = DEMO_DATABASES.get(demo_name, DEMO_DATABASES["University"])
    ready = settings.db_path is not None and settings.key_ok
    key = f"sample_{demo_name}"
    st.pills(
        f"Try a question about the {demo_name} demo ({demo['description'].lower()})",
        demo["questions"],
        key=key,
        on_change=_queue_sample,
        args=(key,),
        disabled=not ready,
    )
    question = st.session_state.pop("pending_sample", None)
    if question and ready:
        ask(
            str(question),
            settings,
            db_path=str(Path(demo["path"]).resolve()),
            database=demo_name,
        )
        st.rerun()


def render_chat(settings: Settings) -> None:
    """Render the conversation so far and handle a newly submitted question.

    Args:
        settings: The choices the sidebar collected for this render.
    """
    status = _status_message(settings)
    if status is not None:
        st.info(status, icon=":material/info:")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            safe = html.escape(str(msg.get("content", "")))
            st.markdown(
                f"<div class='chat-user-wrap'><div class='chat-user-bubble'>{safe}</div></div>",
                unsafe_allow_html=True,
            )
        else:
            render_assistant_turn(msg)

    prompt = st.chat_input(
        "Ask a question about the selected database",
        disabled=status is not None,
    )
    if prompt and status is None and settings.db_path:
        ask(prompt.strip(), settings, db_path=settings.db_path, database=settings.source_label)
        st.rerun()
