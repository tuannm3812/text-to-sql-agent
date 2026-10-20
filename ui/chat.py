"""The chat surface: the demo sample question, the history replay and the input."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import streamlit as st

import text_to_sql_agent as backend
from ui.constants import DEMO_DATABASES
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


def render_sample_question(settings: Settings) -> None:
    """Render the active demo's blurb and its one-click sample question.

    Does nothing unless the sidebar's source is a demo database.

    Args:
        settings: The choices the sidebar collected for this render.
    """
    if settings.source == "Demo database":
        demo_name = settings.demo_name
        demo = DEMO_DATABASES.get(demo_name, DEMO_DATABASES["University"])
        st.markdown(f"**Active demo:** {demo_name} - {demo['description']}")
        sample_prompt = st.selectbox(
            "Try a sample question",
            [""] + demo["questions"],
            key="main_sample_question",
            label_visibility="collapsed",
        )
        if sample_prompt and st.button(
            "Use sample question", type="secondary", disabled=not settings.key_ok
        ):
            ask(
                sample_prompt,
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
    if not st.session_state.messages:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "kind": "text",
                "content": (
                    "Choose a database in the **sidebar**, then ask a question below. "
                    "I generate read-only SQL and show results as a table."
                ),
            }
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            safe = html.escape(str(msg.get("content", "")))
            st.markdown(
                "<div class='chat-user-wrap'>"
                "<div class='chat-user-row'>"
                f"<div class='chat-user-bubble'>{safe}</div>"
                "<div class='chat-user-avatar'>You</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            render_assistant_turn(msg)

    chat_disabled = settings.db_path is None or not settings.key_ok
    placeholder = (
        "Connect a database in the sidebar..."
        if settings.db_path is None
        else "Ask anything about your data..."
    )
    prompt = st.chat_input(placeholder, disabled=chat_disabled)

    if prompt and settings.db_path and settings.key_ok:
        ask(prompt.strip(), settings, db_path=settings.db_path, database=settings.source_label)
        st.rerun()
