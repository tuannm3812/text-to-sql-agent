"""A Streamlit page that renders the real answer components for fixed, labelled states.

Used only by `scripts/ui_acceptance.py` to check rendered layout in a browser. Every
state is a fixture turn, not a model answer, and the page says so at the top.
`static` beside this file links to the repository's `static/`, because Streamlit serves
static files from the running script's own folder (the fonts).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ui.results import render_answer  # noqa: E402
from ui.styles import CHAT_CSS  # noqa: E402

TABLES: list[dict[str, object]] = [
    {"name": "fiscal_quarter_performance_summary_by_region", "neighbour": False, "used": True},
    {"name": "regions", "neighbour": True, "used": False},
]
RETRIEVAL: dict[str, object] = {
    "tables": TABLES,
    "terms": ["profit", "region"],
    "total_tables": 7,
    "sent_chars": 2210,
    "vs_hints_pct": -40.0,
}


def turn(state: str, question: str, **fields: object) -> dict[str, object]:
    base: dict[str, object] = {
        "role": "assistant",
        "kind": "result",
        "question": f"[{state}] {question}",
        "error_text": None,
        "blocked_sql": None,
        "df": None,
        "sql_text": "",
        "schema_text": "CREATE TABLE t (x INTEGER);",
        "rag_report": "Schema RAG strategy: hybrid",
        "retrieval": RETRIEVAL,
        "database": "Fixture",
        "engine": "sqlite",
        "provider": "ollama",
        "model": "fixture",
        "context": "schema RAG, top 6",
    }
    base.update(fields)
    return base


STATES = [
    turn(
        "signed",
        "Net profit by region",
        df=pd.DataFrame({"region": ["North", "South", "East"], "net_profit": [1250, -830, 40]}),
        sql_text="SELECT region, SUM(profit) AS net_profit FROM sales GROUP BY region",
    ),
    turn(
        "missing value",
        "Total by category",
        df=pd.DataFrame({"category": ["A", "B"], "total": [10.0, float("inf")]}),
        sql_text="SELECT category, SUM(x) AS total FROM t GROUP BY category",
    ),
    turn(
        "long names, many categories",
        "Revenue by product line",
        df=pd.DataFrame(
            {
                "product_line_description_including_subcategory": [
                    f"Extremely long product line name number {i} with qualifiers"
                    for i in range(15)
                ],
                "revenue": list(range(15000, 0, -1000)),
            }
        ),
        sql_text="SELECT product_line_description_including_subcategory, SUM(r) AS revenue "
        "FROM fiscal_quarter_performance_summary_by_region GROUP BY 1",
    ),
    turn("empty", "Orders in 1990", df=pd.DataFrame({"id": []}), sql_text="SELECT id FROM o"),
    turn(
        "unsupported type",
        "Contact names",
        error_text="BLOCKED_UNSUPPORTED_COLUMN_TYPE",
        sql_text="SELECT name FROM contacts",
        blocked_sql="SELECT name FROM contacts",
    ),
    # The shape `answer_question` records when generation raises after retrieval: the
    # retrieval is kept, no SQL, so no table is marked used.
    turn(
        "provider failure",
        "Anything",
        error_text="ConnectionError: could not reach the model server",
        sql_text="",
        retrieval={
            **RETRIEVAL,
            "tables": [{**t, "used": False} for t in TABLES],
        },
    ),
]

st.set_page_config(page_title="UI states", layout="wide")
st.markdown(CHAT_CSS, unsafe_allow_html=True)
st.markdown("<h1 class='hero'>UI states (fixtures, not model answers)</h1>", unsafe_allow_html=True)
only = st.query_params.get("state")
for index, msg in enumerate(STATES):
    if only and only not in str(msg["question"]):
        continue
    render_answer(msg, key=f"answer_{index}")
