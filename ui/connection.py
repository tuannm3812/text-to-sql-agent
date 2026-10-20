"""The connection panel: the database first, then the model, then Advanced settings.

It opens from the top bar's Change button (`ui.layout.render_top_bar`), so the question
and answer own the page (Codex's visual review, 2026-10-21). Order follows what a visitor
decides first: which data to ask about, which model answers, and only then retrieval
tuning and the demo-data writer.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import text_to_sql_agent as backend
from ui.constants import (
    DEMO_DATABASES,
    GEMINI_MODELS,
    OLLAMA_MODELS,
    SOURCE_DEMO,
    SOURCE_DSN,
    SOURCE_PATH,
    SOURCE_UPLOAD_DB,
    SOURCES,
)
from ui.secrets import active_gemini_key, model_name_for_provider
from ui.settings import Settings
from ui.uploads import active_db_path, redact_dsn


def _render_database() -> None:
    st.markdown("**Database**")
    st.radio("Source", SOURCES, key="sb_source", label_visibility="collapsed")
    source = st.session_state.get("sb_source")

    if source == SOURCE_DEMO:
        demo_name = st.selectbox("Demo", list(DEMO_DATABASES), key="sb_demo_db")
        st.caption(DEMO_DATABASES[demo_name]["description"])

    elif source == SOURCE_PATH:
        st.text_input(
            "Path to a SQLite `.db` file", value="data/university_agent.db", key="sb_path_db"
        )
        path = Path(st.session_state.get("sb_path_db", "")).expanduser()
        if st.session_state.get("sb_path_db") and not path.is_file():
            st.caption("No file at that path. Check it, or create the demo file under Advanced.")

    elif source == SOURCE_UPLOAD_DB:
        st.file_uploader("SQLite file", type=["db"], key="sb_upload_db")

    elif source == SOURCE_DSN:
        st.text_input(
            "Connection string",
            key="sb_dsn",
            type="password",
            placeholder="duckdb:///path.duckdb or postgresql://user@host/db",
            help=(
                "SQLite, DuckDB or PostgreSQL. A bare file path means SQLite. "
                "Session-only: never written to disk."
            ),
        )
        dsn = (st.session_state.get("sb_dsn") or "").strip()
        if dsn:
            st.caption(f"Using `{redact_dsn(dsn)}`")

    else:
        st.file_uploader("CSV files", type=["csv"], accept_multiple_files=True, key="sb_upload_csv")
        st.caption("Each file becomes a table named after it, in a temporary SQLite file.")


def _render_model() -> None:
    """Provider, model and, for Gemini, the session-only key."""
    st.markdown("**Model**")
    provider = st.selectbox(
        "Provider",
        ["gemini", "ollama"],
        key="sb_provider",
        format_func={"gemini": "Gemini (cloud)", "ollama": "Ollama (local)"}.__getitem__,
    )
    model_options = GEMINI_MODELS if provider == "gemini" else OLLAMA_MODELS
    default_model = (
        backend.DEFAULT_MODEL_NAME if provider == "gemini" else backend.DEFAULT_OLLAMA_MODEL
    )
    default_index = model_options.index(default_model) if default_model in model_options else 0
    st.selectbox("Model", model_options, index=default_index, key="sb_model_choice")
    if st.session_state.get("sb_model_choice") == "Custom":
        st.text_input("Custom model name", value=default_model, key="sb_custom_model")

    gemini_key = ""
    if provider == "gemini":
        typed_key = st.text_input(
            "Gemini API key",
            type="password",
            key="sb_gemini_key",
            placeholder="Blank uses the server's key, if it has one",
            help="Kept in this browser session only and sent with each request.",
        )
        # Kept in this session only and passed with each call. Writing it to
        # `os.environ` made one visitor's key every session's (Codex, 2026-10-20).
        gemini_key = active_gemini_key(typed_key)

    key_ok = provider == "ollama" or bool(gemini_key)
    if provider == "gemini" and key_ok:
        st.success("Gemini API key loaded", icon=":material/check_circle:")
    elif provider == "gemini":
        st.warning("Add a Gemini API key to ask questions.", icon=":material/key:")
    else:
        st.caption("Runs on this machine; Ollama must be running.")


def _render_advanced() -> None:
    """Schema RAG on or off, how many tables, and the demo-data writer."""
    with st.expander("Advanced", expanded=False):
        st.toggle(
            "Select relevant tables (schema RAG)",
            value=True,
            key="sb_use_rag",
            help="Send the model only the most relevant tables, with sample values.",
        )
        st.slider(
            "Tables to select",
            min_value=1,
            max_value=12,
            value=backend.DEFAULT_RAG_TOP_K,
            key="sb_rag_top_k",
            disabled=not st.session_state.get("sb_use_rag", True),
        )
        st.divider()
        st.text_input(
            "Write the demo university database to",
            value="data/university_agent.db",
            key="sb_demo_path",
        )
        if st.button("Create demo database", use_container_width=True):
            demo_out = st.session_state.get("sb_demo_path", "data/university_agent.db")
            Path(demo_out).parent.mkdir(parents=True, exist_ok=True)
            try:
                backend.write_university_db(demo_out)
                st.success("Saved.")
            except Exception as e:
                st.error(redact_dsn(str(e)))


def render_connection_panel() -> None:
    """The panel's controls; their values live in session state under `sb_*` keys."""
    _render_database()
    st.divider()
    _render_model()
    st.divider()
    _render_advanced()
    if st.button("Clear answers", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def _model_state() -> tuple[str, str, str, bool]:
    """`(provider, model_name, gemini_key, key_ok)` from session state, no widgets drawn."""
    provider = str(st.session_state.get("sb_provider", "gemini"))
    model_name = model_name_for_provider(provider)
    gemini_key = (
        active_gemini_key(str(st.session_state.get("sb_gemini_key") or ""))
        if provider == "gemini"
        else ""
    )
    return provider, model_name, gemini_key, provider == "ollama" or bool(gemini_key)


def current_settings() -> Settings:
    """The choices the connection panel holds, read from session state.

    The panel's widgets are drawn inside a popover after the top bar reads these, so the
    summary and the page use the values of the last run, which Streamlit has already
    stored when a widget changed.
    """
    provider, model_name, gemini_key, key_ok = _model_state()
    db_path_to_query: str | None = None
    open_error: str | None = None
    try:
        db_path_to_query = active_db_path()
    except Exception as e:
        open_error = f"Could not open the database: {redact_dsn(str(e))}"
    return Settings(
        provider=provider,
        model_name=model_name,
        use_rag=bool(st.session_state.get("sb_use_rag", True)),
        rag_top_k=int(st.session_state.get("sb_rag_top_k", backend.DEFAULT_RAG_TOP_K)),
        db_path=db_path_to_query,
        gemini_key=gemini_key,
        key_ok=key_ok,
        source=str(st.session_state.get("sb_source", SOURCE_DEMO)),
        demo_name=str(st.session_state.get("sb_demo_db", next(iter(DEMO_DATABASES)))),
        source_label=source_label(),
        open_error=open_error,
    )


def source_label() -> str:
    """The active database as a turn records it: a name, never a local path or a password."""
    source = st.session_state.get("sb_source", SOURCE_DEMO)
    if source == SOURCE_DEMO:
        return str(st.session_state.get("sb_demo_db", "University"))
    if source == SOURCE_PATH:
        return Path(str(st.session_state.get("sb_path_db") or "")).name or "file on disk"
    if source == SOURCE_UPLOAD_DB:
        uploaded = st.session_state.get("sb_upload_db")
        return str(uploaded.name) if uploaded is not None else "uploaded file"
    if source == SOURCE_DSN:
        return redact_dsn((st.session_state.get("sb_dsn") or "").strip())
    files = st.session_state.get("sb_upload_csv") or []
    return f"{len(files)} uploaded CSV file(s)"
