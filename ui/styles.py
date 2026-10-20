"""The page-level CSS injected once per render by `app.py`.

A restrained warm-neutral palette: off-white page, a slightly darker sidebar, one muted
accent for the user's questions. Layout stays Streamlit's own; this only adjusts colour,
spacing and the question bubble, so narrow screens keep Streamlit's responsive stacking.
"""

from __future__ import annotations

CHAT_CSS = """
<style>
    .stApp, [data-testid="stHeader"] {
        background: #faf9f5;
    }
    [data-testid="stSidebar"] {
        background: #f1efe8 !important;
        border-right: 1px solid #e6e3da;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem;
    }
    .main .block-container {
        max-width: 54rem;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }
    .stMarkdown, [data-testid="stChatMessage"] {
        font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
        color: #1f1e1b;
    }
    .app-title {
        font-size: 1.75rem;
        font-weight: 650;
        color: #1f1e1b;
        margin: 0 0 0.25rem 0;
        padding: 0;
    }
    .app-subtitle {
        font-size: 0.98rem;
        color: #5f5c55;
        margin: 0 0 0.75rem 0;
        max-width: 44rem;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 0.9rem !important;
        border: 1px solid #e0dcd2 !important;
        background: #fff !important;
    }
    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid #ece9e1;
        border-radius: 0.9rem;
        padding: 0.75rem 0.9rem;
    }
    .chat-user-wrap {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin: 0.5rem 0;
    }
    .chat-user-bubble {
        max-width: min(40rem, 85%);
        background: #ece7dc;
        border: 1px solid #e0d9ca;
        color: #1f1e1b;
        padding: 0.55rem 0.85rem;
        border-radius: 0.9rem;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
</style>
"""
