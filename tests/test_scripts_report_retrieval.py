"""scripts/report_retrieval.py on the committed demo suite (no model is called)."""

from __future__ import annotations

import shutil
from pathlib import Path

import scripts.report_retrieval as script
from text_to_sql_agent.evaluation_v2.contract import suite_sha256

ROOT = Path(__file__).resolve().parents[1]


def test_the_report_covers_every_demo_case_with_gold_tables(capsys) -> None:
    assert script.main(["--suite", "demo", "--evidence", "off"]) == 0
    text = capsys.readouterr().out
    assert text.startswith("# Retrieval: `demo` / full, evidence off")
    assert "| recall@k |" in text
    assert "## By hardness" in text
    assert "## Gold tables most often not sent at top 6" in text


def _suite_copy(tmp_path: Path) -> Path:
    suites = tmp_path / "suites"
    suites.mkdir()
    shutil.copy(ROOT / "evaluation" / "suites" / "demo.jsonl", suites / "demo.jsonl")
    return suites


def test_an_unknown_subset_id_is_refused_not_dropped(tmp_path: Path, capsys) -> None:
    suites = _suite_copy(tmp_path)
    (suites / "demo.typo.txt").write_text("not-a-case\n", encoding="utf-8")
    argv = ["--suite", "demo", "--subset", "typo", "--suites-dir", str(suites)]
    assert script.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not-a-case" in captured.err


def test_a_missing_subset_file_is_refused(tmp_path: Path, capsys) -> None:
    argv = ["--suite", "demo", "--subset", "absent", "--suites-dir", str(_suite_copy(tmp_path))]
    assert script.main(argv) == 2


def test_the_report_names_the_suite_file_it_measured(capsys) -> None:
    assert script.main(["--suite", "demo", "--evidence", "off"]) == 0
    expected = suite_sha256(ROOT / "evaluation" / "suites" / "demo.jsonl")
    assert f"Suite file SHA-256 `{expected}`." in capsys.readouterr().out
