"""The top bar: product mark, Ask and Evaluation, and the connection summary with Change."""

from __future__ import annotations

import html

import streamlit as st

from ui.connection import render_connection_panel
from ui.settings import Settings

VIEWS = ["Ask", "Evaluation"]


def connection_summary(settings: Settings) -> str:
    """The top bar's one line about the connection: database, engine and model."""
    model = settings.model_name or ""
    where = "local" if settings.provider == "ollama" else "Gemini"
    ok = settings.db_path is not None and settings.key_ok and not settings.open_error
    dot = "dot" if ok else "dot off"
    return (
        f"<div class='conn'><span class='{dot}'></span><span><b>"
        f"{html.escape(settings.source_label or 'No database')}</b>"
        f"<span class='full'> · {html.escape(model)}, {where}</span></span></div>"
    )


def render_top_bar(settings: Settings) -> str:
    """Draw the bar and return the chosen view."""
    with st.container(key="topbar"):
        brand, nav, summary, change = st.columns([2.2, 2.2, 4.2, 1.1], vertical_alignment="center")
        brand.markdown(
            "<div class='brand'><div class='mark'>&gt;_</div>Text-to-SQL Agent</div>",
            unsafe_allow_html=True,
        )
        view = nav.segmented_control(
            "View", VIEWS, default="Ask", key="main_view", label_visibility="collapsed"
        )
        summary.markdown(connection_summary(settings), unsafe_allow_html=True)
        with change.popover("Change", use_container_width=True):
            render_connection_panel()
    return str(view or "Ask")
