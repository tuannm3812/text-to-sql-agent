"""
Streamlit UI for the Text-to-SQL agent (`text_to_sql_agent`).

Run locally:
    streamlit run app.py

Ensure `GEMINI_API_KEY` is set in `.env` in the project root (or in your environment).
"""

from __future__ import annotations

import streamlit as st

import text_to_sql_agent as backend
from ui.chat import render_ask
from ui.connection import current_settings
from ui.evaluation import render_evaluation_view
from ui.layout import render_top_bar
from ui.styles import CHAT_CSS

backend.load_env()


def main() -> None:
    st.set_page_config(
        page_title="Text-to-SQL Agent",
        page_icon=":material/database:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    settings = current_settings()
    view = render_top_bar(settings)

    if view == "Evaluation":
        render_evaluation_view(settings)
        return
    render_ask(settings)


if __name__ == "__main__":
    main()
