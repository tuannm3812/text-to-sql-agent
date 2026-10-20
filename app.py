"""
Streamlit UI for the Text-to-SQL agent (`text_to_sql_agent`).

Run locally:
    streamlit run app.py

Ensure `GEMINI_API_KEY` is set in `.env` in the project root (or in your environment).
"""

from __future__ import annotations

import streamlit as st

import text_to_sql_agent as backend
from ui.chat import render_chat, render_sample_question
from ui.evaluation import render_evaluation_view
from ui.sidebar import render_sidebar
from ui.styles import CHAT_CSS

backend.load_env()


def main() -> None:
    st.set_page_config(
        page_title="Text-to-SQL Agent",
        page_icon=":material/database:",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    settings = render_sidebar()

    st.markdown(
        "<h1 class='app-title'>Text-to-SQL Agent</h1>"
        "<p class='app-subtitle'>Ask a question in plain English. The agent writes read-only "
        "SQL for the selected database, checks it, runs it and shows the result with the SQL "
        "and the schema it was given.</p>",
        unsafe_allow_html=True,
    )
    view = st.segmented_control(
        "View",
        ["Ask", "Evaluation"],
        default="Ask",
        key="main_view",
        label_visibility="collapsed",
    )

    if view == "Evaluation":
        render_evaluation_view(settings)
        return

    st.caption("Each question is answered on its own: earlier questions are not sent to the model.")
    render_sample_question(settings)
    render_chat(settings)


if __name__ == "__main__":
    main()
