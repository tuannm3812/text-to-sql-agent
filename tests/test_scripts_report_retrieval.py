"""scripts/report_retrieval.py on the committed demo suite (no model is called)."""

from __future__ import annotations

import scripts.report_retrieval as script


def test_the_report_covers_every_demo_case_with_gold_tables(capsys) -> None:
    assert script.main(["--suite", "demo", "--evidence", "off"]) == 0
    text = capsys.readouterr().out
    assert text.startswith("# Retrieval: `demo` / full, evidence off")
    assert "| recall@k |" in text
    assert "## By hardness" in text
    assert "## Gold tables most often not sent at top 6" in text
