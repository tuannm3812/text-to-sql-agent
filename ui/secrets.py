"""Resolving API keys and model names from Streamlit widgets, env vars and secrets."""

from __future__ import annotations

import os

import streamlit as st

import text_to_sql_agent as backend
from ui.constants import GEMINI_MODELS, OLLAMA_MODELS


def streamlit_secret(name: str) -> str:
    """Read a value from `st.secrets`, tolerating the absence of a secrets file."""
    try:
        return str(st.secrets.get(name, "") or "")
    except Exception:
        return ""


def active_gemini_key(typed_key: str) -> str:
    """Resolve the Gemini API key from the sidebar input, env var or Streamlit secrets."""
    return (
        (typed_key or "").strip()
        or (os.environ.get("GEMINI_API_KEY") or "").strip()
        or streamlit_secret("GEMINI_API_KEY").strip()
    )


def model_keys(provider: str) -> tuple[str, str]:
    """`(model choice key, custom name key)` in session state, one pair per provider."""
    return f"sb_model_choice_{provider}", f"sb_custom_model_{provider}"


def model_name_for_provider(provider: str) -> str:
    """Resolve the selected model name for `provider` from the connection panel's state.

    Both the model choice and the custom name are stored per provider (`model_keys`), so
    switching provider can never carry the other provider's model, built-in or custom
    (Codex, 2026-10-22). An unknown stored choice falls back to the provider's default.
    """
    default = backend.DEFAULT_MODEL_NAME if provider == "gemini" else backend.DEFAULT_OLLAMA_MODEL
    options = GEMINI_MODELS if provider == "gemini" else OLLAMA_MODELS
    choice_key, custom_key = model_keys(provider)
    selected = st.session_state.get(choice_key, "")
    if selected == "Custom":
        return (st.session_state.get(custom_key) or "").strip() or default
    return str(selected) if selected in options else default
