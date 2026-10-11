"""The evaluation script must not write a DSN password to its results CSV.

`evaluate_case` puts `result.error` straight into the row dict `main` writes
with `csv.DictWriter`, and `--out-dir` defaults to `evaluation/results`, a
git-tracked directory. A PostgreSQL driver error commonly echoes the DSN it
failed to reach, including its password (Phase 3b), so that value must
already be redacted by the time it lands in the row - there is no further
transform between here and the file. Every test here points `--out-dir` at a
`tmp_path`; none writes to `evaluation/results/`.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import scripts.evaluate_text_to_sql as script
from text_to_sql_agent import CaseScore, QueryResult, SchemaRetrievalResult


def _case() -> dict:
    return {
        "id": "case-1",
        "dataset": "postgres_demo",
        "difficulty": "easy",
        "question": "how many customers?",
        "db_path": "postgresql://u:hunter2@db.example.com:5432/prod",
        "expected_tables": ["customers"],
    }


def test_evaluate_case_redacts_a_dsn_password_in_the_error_field() -> None:
    case = _case()
    gold_result = QueryResult(
        columns=[],
        rows=[],
        sql=None,
        error="could not connect to postgresql://u:hunter2@db.example.com:5432/prod: timed out",
    )
    with (
        patch(
            "scripts.evaluate_text_to_sql.agent.run_gold", return_value=("SELECT 1", gold_result)
        ),
        patch(
            "scripts.evaluate_text_to_sql.agent.score_case",
            return_value=CaseScore(
                executed=False, row_match=False, value_match=False, exact_match=False
            ),
        ),
        patch("scripts.evaluate_text_to_sql.agent.open_engine", return_value=object()),
        patch("scripts.evaluate_text_to_sql.agent.is_safe_query", return_value=True),
        patch(
            "scripts.evaluate_text_to_sql.agent.retrieve_schema_context",
            return_value=SchemaRetrievalResult(
                chunks=[], query_tokens=[], expanded_tokens=[], top_k=3
            ),
        ),
    ):
        row = script.evaluate_case(
            case,
            mode="gold",
            provider="gemini",
            model_name="gemini-2.5-flash",
            use_rag=False,
            rag_top_k=3,
        )

    assert "hunter2" not in row["error"]
    assert "***" in row["error"]


def test_main_does_not_write_a_dsn_password_to_the_results_csv(tmp_path: Path) -> None:
    case = _case()
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(json.dumps([case]), encoding="utf-8")
    out_dir = tmp_path / "results"

    gold_result = QueryResult(
        columns=[],
        rows=[],
        sql=None,
        error="could not connect to postgresql://u:hunter2@db.example.com:5432/prod: timed out",
    )
    argv = [
        "evaluate_text_to_sql.py",
        "--cases",
        str(cases_path),
        "--mode",
        "gold",
        "--out-dir",
        str(out_dir),
    ]
    with (
        patch.object(sys, "argv", argv),
        patch(
            "scripts.evaluate_text_to_sql.agent.run_gold", return_value=("SELECT 1", gold_result)
        ),
        patch(
            "scripts.evaluate_text_to_sql.agent.score_case",
            return_value=CaseScore(
                executed=False, row_match=False, value_match=False, exact_match=False
            ),
        ),
        patch("scripts.evaluate_text_to_sql.agent.open_engine", return_value=object()),
        patch("scripts.evaluate_text_to_sql.agent.is_safe_query", return_value=True),
        patch(
            "scripts.evaluate_text_to_sql.agent.retrieve_schema_context",
            return_value=SchemaRetrievalResult(
                chunks=[], query_tokens=[], expanded_tokens=[], top_k=3
            ),
        ),
    ):
        script.main()

    csv_path = out_dir / "evaluation_gold.csv"
    assert csv_path.exists()
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "hunter2" not in csv_text
    assert "***" in csv_text

    md_text = (out_dir / "evaluation_gold.md").read_text(encoding="utf-8")
    assert "hunter2" not in md_text


# --- Signed schema-size columns (Codex review 2026-10-12, P2 item 1) -------------------


def _one_table_case(tmp_path: Path) -> dict:
    """Codex's one-table reproduction: 29 chars of plain DDL, 72 sent under RAG."""
    db_path = tmp_path / "one.db"
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("CREATE TABLE t (status TEXT)")
        conn.execute("INSERT INTO t VALUES ('active')")
        conn.execute("INSERT INTO t VALUES ('inactive')")
        conn.commit()
    return {
        "id": "one-table",
        "dataset": "fixture",
        "difficulty": "easy",
        "question": "status",
        "db_path": str(db_path),
        "gold_sql": "SELECT status FROM t ORDER BY status",
        "expected_tables": ["t"],
    }


def test_rows_carry_signed_size_columns_under_new_names(tmp_path: Path) -> None:
    row = script.evaluate_case(
        _one_table_case(tmp_path),
        mode="gold",
        provider="ollama",
        model_name="unused",
        use_rag=True,
        rag_top_k=6,
    )

    assert "prompt_saved_pct" not in row, "the old name must not change meaning silently"
    assert row[script.CHANGE_VS_PLAIN_DDL] == round((72 - 29) / 29 * 100, 1)
    assert row[script.CHANGE_VS_DDL_WITH_HINTS] == 0.0


def test_markdown_names_units_baselines_and_shows_growth(tmp_path: Path) -> None:
    case = _one_table_case(tmp_path)
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(json.dumps([case]), encoding="utf-8")
    out_dir = tmp_path / "results"
    argv = ["evaluate_text_to_sql.py", "--cases", str(cases_path), "--out-dir", str(out_dir)]
    with patch.object(sys, "argv", argv):
        script.main()

    md_text = (out_dir / "evaluation_gold.md").read_text(encoding="utf-8")
    assert "characters of schema text (not provider tokens)" in md_text
    assert "average change vs plain full DDL, what RAG off sends: +148.3%" in md_text
    assert "average change vs full DDL plus value hints, all tables: +0.0%" in md_text
    assert "| +148.3% |" in md_text
    assert "saved" not in md_text.lower()
    header = (out_dir / "evaluation_gold.csv").read_text(encoding="utf-8").splitlines()[0]
    assert script.CHANGE_VS_PLAIN_DDL in header
    assert "prompt_saved_pct" not in header


def test_resume_from_a_csv_with_the_old_column_re_evaluates(tmp_path: Path) -> None:
    case = _one_table_case(tmp_path)
    cases_path = tmp_path / "cases.json"
    cases_path.write_text(json.dumps([case]), encoding="utf-8")
    out_dir = tmp_path / "results"
    out_dir.mkdir()
    (out_dir / "evaluation_gold.csv").write_text(
        "id,execution_ok,prompt_saved_pct\none-table,True,0.0\n", encoding="utf-8"
    )
    argv = [
        "evaluate_text_to_sql.py",
        "--cases",
        str(cases_path),
        "--out-dir",
        str(out_dir),
        "--resume",
    ]
    with patch.object(sys, "argv", argv):
        script.main()

    header = (out_dir / "evaluation_gold.csv").read_text(encoding="utf-8").splitlines()[0]
    assert script.CHANGE_VS_PLAIN_DDL in header
    assert "prompt_saved_pct" not in header
