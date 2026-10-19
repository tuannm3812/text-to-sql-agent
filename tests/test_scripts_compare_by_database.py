"""scripts/compare_by_database.py: the per-database pairing, on synthetic outcomes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import scripts.compare_by_database as script
from text_to_sql_agent.evaluation_v2.contract import suite_sha256
from text_to_sql_agent.evaluation_v2.identity import IdentityPayload
from text_to_sql_agent.evaluation_v2.manifest import Manifest, write_manifest
from text_to_sql_agent.evaluation_v2.runner import (
    CASES_FILE,
    CSV_COLUMNS,
    MANIFEST_FILE,
    REPORT_FILE,
    write_rows,
)
from text_to_sql_agent.evaluation_v2.stats import paired_bootstrap_ci

_IDENTITY: dict[str, Any] = {
    "commit": "a" * 40,
    "dirty": False,
    "suite": "synthetic",
    "suite_sha256": "1" * 64,
    "subset": "full",
    "subset_sha256": "",
    "source_release": "n/a",
    "database_fingerprint": (("data/x.db", "f" * 64),),
    "adapter_version": "n/a",
    "scorer_version": "v2.0",
    "prompt_sha256": "p" * 64,
    "provider": "ollama",
    "model": "m",
    "evidence": False,
    "use_rag": True,
    "rag_top_k": 5,
    "work_limit": 1000,
    "max_rows": 100,
    "max_repair_attempts": 1,
    "retry_policy": "0x20.0",
    "ollama_think": "off",
}


def test_by_database_groups_pairs_and_orders_by_size() -> None:
    ids = [str(i) for i in range(10)]
    database_of = {i: ("big" if int(i) < 7 else "small") for i in ids}
    new = {i: int(i) % 2 == 0 for i in ids}
    old = {i: int(i) % 3 == 0 for i in ids}
    rows = script.by_database(new, old, database_of, ids)
    assert [(r.database, r.cases) for r in rows] == [("big", 7), ("small", 3)]
    big = [i for i in ids if database_of[i] == "big"]
    assert rows[0].new_correct == sum(new[i] for i in big)
    assert rows[0].baseline_correct == sum(old[i] for i in big)
    assert rows[0].change == paired_bootstrap_ci([new[i] for i in big], [old[i] for i in big])


def test_render_is_one_markdown_row_per_database() -> None:
    rows = script.by_database(
        {"1": True, "2": False}, {"1": False, "2": False}, {"1": "a", "2": "a"}, ["1", "2"]
    )
    text = script.render(rows)
    assert text.splitlines()[2].startswith("| `a` | 2 | 0.0 % (0/2) | 50.0 % (1/2) | +50.0 [")


# --- refusing a pair that does not measure the same population (Codex, 2026-10-19) -------


def _suite_file(directory: Path, ids: list[str]) -> Path:
    path = directory / "synthetic.jsonl"
    records = [
        {
            "suite": "synthetic",
            "id": case_id,
            "db_path": f"data/{'olddb' if i % 2 else 'newdb'}.sqlite",
            "question": "q",
            "evidence": "",
            "gold_sql": "SELECT 1",
            "hardness": "easy",
            "expected": "answerable",
            "expected_tables": [],
        }
        for i, case_id in enumerate(ids)
    ]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return path


def _run(root: Path, name: str, correct: set[str], ids: list[str], **identity: Any) -> Path:
    directory = root / name
    directory.mkdir()
    rows = []
    for case_id in ids:
        row = dict.fromkeys(CSV_COLUMNS, "")
        row.update(suite="synthetic", id=case_id, hardness="easy", expected="answerable")
        row.update(outcome="correct" if case_id in correct else "wrong")
        rows.append(row)
    write_rows(directory / CASES_FILE, rows)
    manifest = Manifest(
        identity=IdentityPayload(**{**_IDENTITY, **identity}),
        run_id=name,
        mode="llm",
        case_count=len(rows),
        source={"kind": "authored", "author": "t", "licence": "MIT"},
        started="2026-10-19T00:00:00",
        duration_s=1.0,
        outage_count=0,
        status="complete",
        generation_failures=0,
        python="3.11",
        packages={},
    )
    write_manifest(directory / MANIFEST_FILE, manifest)
    (directory / REPORT_FILE).write_text("# stub\n", encoding="utf-8")
    return directory


_IDS = ["1", "2"]


def _setup(tmp_path: Path, **new_identity: Any) -> list[str]:
    suites = tmp_path / "suites"
    suites.mkdir()
    sha = suite_sha256(_suite_file(suites, _IDS))
    old = _run(tmp_path, "old", set(), _IDS, suite_sha256=sha)
    new = _run(tmp_path, "new", set(_IDS), _IDS, **{"suite_sha256": sha, **new_identity})
    return ["--new", str(new), "--baseline", str(old), "--suites-dir", str(suites)]


def test_a_treatment_difference_is_compared(tmp_path: Path, capsys) -> None:
    argv = _setup(tmp_path, use_rag=False, commit="b" * 40)
    assert script.main(argv) == 0
    assert "| `newdb` | 1 |" in capsys.readouterr().out


@pytest.mark.parametrize(
    "field, value",
    [
        ("database_fingerprint", (("data/x.db", "e" * 64),)),
        ("suite_sha256", "2" * 64),
        ("subset", "subset200"),
        ("scorer_version", "v3.0"),
    ],
)
def test_a_population_difference_is_refused(tmp_path: Path, capsys, field: str, value: Any) -> None:
    assert script.main(_setup(tmp_path, **{field: value})) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"not measure the same population: {field}" in captured.err


def test_a_suite_file_that_is_not_the_runs_suite_is_refused(tmp_path: Path, capsys) -> None:
    argv = _setup(tmp_path)
    (tmp_path / "suites" / "synthetic.jsonl").write_text("changed\n", encoding="utf-8")
    assert script.main(argv) == 2
    assert "does not hash to the runs' suite_sha256" in capsys.readouterr().err
