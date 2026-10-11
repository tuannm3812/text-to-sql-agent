"""The paired comparison of two runs that differ in one deliberate setting (``compare.py``).

Synthetic runs are written with the runner's own writers under ``tmp_path``; one test reads the
committed thinking-off and 2026-10-09 Spider subset runs and writes nothing.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import pytest

import scripts.evaluate_v2 as cli
from text_to_sql_agent.evaluation_v2.compare import (
    FACTORS,
    ComparisonRefused,
    compare_runs,
    render_comparison,
)
from text_to_sql_agent.evaluation_v2.gates import regression_gate
from text_to_sql_agent.evaluation_v2.identity import REPO_ROOT, IdentityPayload
from text_to_sql_agent.evaluation_v2.manifest import (
    Manifest,
    manifest_sha256,
    read_manifest,
    write_manifest,
)
from text_to_sql_agent.evaluation_v2.report import metric_cells
from text_to_sql_agent.evaluation_v2.runner import (
    CASES_FILE,
    CSV_COLUMNS,
    MANIFEST_FILE,
    REPORT_FILE,
    read_rows,
    write_rows,
)
from text_to_sql_agent.evaluation_v2.scoring import EMPTY_GENERATED_SQL
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
_STARTED = "2026-10-09T00:00:00"


def _row(case_id: str, outcome: str, **cells: str) -> dict[str, str]:
    row = dict.fromkeys(CSV_COLUMNS, "")
    row.update(suite="synthetic", id=case_id, hardness="easy", expected="answerable")
    row.update(outcome=outcome, **cells)
    return row


def make_run(
    root: Path,
    name: str,
    rows: list[dict[str, str]],
    *,
    status: str = "complete",
    mode: str = "llm",
    **identity: Any,
) -> Path:
    """A run directory written with the runner's own writers."""
    directory = root / name
    directory.mkdir()
    write_rows(directory / CASES_FILE, rows)
    manifest = Manifest(
        identity=IdentityPayload(**{**_IDENTITY, **identity}),
        run_id=name,
        mode=mode,
        case_count=len(rows),
        source={"kind": "authored", "author": "t", "licence": "MIT"},
        started=_STARTED,
        duration_s=1.0,
        outage_count=0,
        status=status,  # type: ignore[arg-type]
        generation_failures=sum(1 for row in rows if row["generation_failure"]),
        python="3.11",
        packages={},
    )
    write_manifest(directory / MANIFEST_FILE, manifest)
    (directory / REPORT_FILE).write_text("# stub\n", encoding="utf-8")
    return directory


def _flags(correct: set[int], n: int) -> list[dict[str, str]]:
    return [_row(f"c{i:02d}", "correct" if i in correct else "wrong") for i in range(n)]


def _pair(tmp_path: Path, **new_identity: Any) -> tuple[Path, Path]:
    """A pair over 10 cases, differing in ``use_rag`` unless overridden."""
    new_identity = new_identity or {"use_rag": False}
    old = make_run(tmp_path, "old", _flags({0, 1, 2, 3, 4, 5}, 10))
    new = make_run(tmp_path, "new", _flags({2, 3, 4, 5, 6, 7, 8}, 10), **new_identity)
    return new, old


# --- refusals ------------------------------------------------------------------------------


def test_runs_that_differ_in_no_setting_are_sent_to_the_regression_gate(tmp_path: Path) -> None:
    # Commit, dirty and prompt may differ; none of them is a factor.
    new, old = _pair(tmp_path, commit="b" * 40, prompt_sha256="q" * 64)
    with pytest.raises(ComparisonRefused, match="--gate regression"):
        compare_runs(new, old)


def test_two_factors_are_refused_naming_both(tmp_path: Path) -> None:
    new, old = _pair(tmp_path, use_rag=False, evidence=True)
    with pytest.raises(ComparisonRefused, match="differ in: evidence, use_rag$") as caught:
        compare_runs(new, old)
    assert caught.value.differences == (
        ("evidence", "True", "False"),
        ("use_rag", "False", "True"),
    )


@pytest.mark.parametrize(
    ("identity", "mode", "field"),
    [
        ({"scorer_version": "v9"}, "llm", "scorer_version"),
        ({"max_rows": 5}, "llm", "max_rows"),
        ({"suite_sha256": "2" * 64}, "llm", "suite_sha256"),
        ({}, "gold", "mode"),
    ],
)
def test_a_difference_outside_the_factors_is_refused_naming_it(
    tmp_path: Path, identity: dict[str, Any], mode: str, field: str
) -> None:
    assert field not in FACTORS
    old = make_run(tmp_path, "old", _flags({0}, 4))
    new = make_run(tmp_path, "new", _flags({0}, 4), mode=mode, **identity)
    with pytest.raises(ComparisonRefused, match=field) as caught:
        compare_runs(new, old)
    assert [name for name, _, _ in caught.value.differences] == [field]


def test_mismatched_case_ids_are_refused_naming_them(tmp_path: Path) -> None:
    old = make_run(tmp_path, "old", _flags({0}, 4))
    rows = _flags({0}, 4)
    rows[3]["id"] = "c99"
    new = make_run(tmp_path, "new", rows, use_rag=False)
    with pytest.raises(ComparisonRefused, match=r"case IDs differ.*\[c99\].*\[c03\]"):
        compare_runs(new, old)


def test_runs_that_disagree_on_hardness_are_refused(tmp_path: Path) -> None:
    old = make_run(tmp_path, "old", _flags({0}, 4))
    rows = _flags({0}, 4)
    rows[1]["hardness"] = "hard"
    new = make_run(tmp_path, "new", rows, use_rag=False)
    with pytest.raises(ComparisonRefused, match="hardness.*c01"):
        compare_runs(new, old)


@pytest.mark.parametrize("side", ["new", "old"])
def test_an_incomplete_run_is_refused(tmp_path: Path, side: str) -> None:
    old = make_run(
        tmp_path, "old", _flags({0}, 4), status="incomplete" if side == "old" else "complete"
    )
    new = make_run(
        tmp_path,
        "new",
        _flags({0}, 4),
        status="incomplete" if side == "new" else "complete",
        use_rag=False,
    )
    with pytest.raises(ComparisonRefused, match="incomplete, not complete"):
        compare_runs(new, old)


def test_a_row_count_that_disagrees_with_the_manifest_is_refused(tmp_path: Path) -> None:
    new, old = _pair(tmp_path)
    write_rows(old / CASES_FILE, read_rows(old / CASES_FILE)[:-1])
    with pytest.raises(ComparisonRefused, match="9 rows, the manifest says 10"):
        compare_runs(new, old)


def test_an_uncitable_run_is_compared_and_flagged(tmp_path: Path) -> None:
    new, old = _pair(tmp_path, use_rag=False, dirty=True)
    comparison = compare_runs(new, old)
    assert not comparison.new.citable and comparison.old.citable
    text = render_comparison(comparison)
    assert "| Citable | yes | no - the working tree was dirty" in text
    # `dirty` is free to differ, so it is shown beside the factor rather than refused.
    assert "| dirty | `False` | `True` |" in text


# --- the numbers ---------------------------------------------------------------------------


def test_a_small_pair_checked_by_hand(tmp_path: Path) -> None:
    # Baseline correct on c00-c05 (6/10); new on c02-c08 (7/10). Helped: c06, c07, c08.
    # Hurt: c00, c01. Change: (3 - 2) / 10 = +10 points.
    new, old = _pair(tmp_path)
    comparison = compare_runs(new, old)
    assert comparison.factor == "use_rag"
    assert (comparison.old_value, comparison.new_value) == ("True", "False")
    ex = comparison.ex
    assert ex is not None
    assert (ex.change.old_correct, ex.change.new_correct, ex.change.interval.n) == (6, 7, 10)
    assert ex.change.interval.point == pytest.approx(0.1)
    assert (ex.helped, ex.hurt) == (3, 2)
    assert ex.old_cell == metric_cells(read_rows(old / CASES_FILE), gold=False)["ex"]
    assert ex.new_cell == metric_cells(read_rows(new / CASES_FILE), gold=False)["ex"]
    assert ex.old_cell.endswith("(6/10)") and ex.new_cell.endswith("(7/10)")
    assert comparison.safety is None

    text = render_comparison(comparison)
    assert text.startswith("# `use_rag`: True (baseline) vs False (new)\n")
    assert "- Baseline: `old` at commit `" + "a" * 40 + "`" in text
    assert f"| overall | 10 | {ex.old_cell} | {ex.new_cell} | +10.0 [" in text
    assert "| 3 | 2 |" in text


def test_the_paired_interval_agrees_with_the_regression_gate(tmp_path: Path) -> None:
    # Rows written out of id order: both tools must pair in the gate's (sorted) order. The
    # bootstrap draws case indices, so the order moves the interval (not the point) - here it
    # does, which is what makes this test able to fail.
    order = list(range(200))
    random.Random(1).shuffle(order)
    old_rows = [_row(f"c{i:03d}", "correct" if i % 3 else "wrong") for i in order]
    new_rows = [_row(f"c{i:03d}", "correct" if i % 7 and i < 166 else "wrong") for i in order]
    in_file_order = paired_bootstrap_ci(
        [r["outcome"] == "correct" for r in new_rows],
        [r["outcome"] == "correct" for r in old_rows],
    )
    old = make_run(tmp_path, "old", old_rows)
    new = make_run(tmp_path, "new", new_rows, use_rag=False)
    same_settings = make_run(tmp_path, "same", new_rows)
    gate = regression_gate(same_settings, old)
    comparison = compare_runs(new, old)
    assert gate.regression is not None and comparison.ex is not None
    assert comparison.ex.change == gate.regression.ex
    assert comparison.ex.change.interval != in_file_order
    assert comparison.ex.change.interval.point == in_file_order.point


def test_tokens_blank_is_not_reported_and_zero_is_a_count(tmp_path: Path) -> None:
    old = make_run(
        tmp_path,
        "old",
        [
            _row("c0", "correct", prompt_tokens="80", latency_ms="40"),
            _row("c1", "correct", prompt_tokens="90"),
            _row("c2", "correct", prompt_tokens="", latency_ms="50"),
            _row("c3", "correct", prompt_tokens="0", latency_ms="60"),
        ],
    )
    new = make_run(
        tmp_path,
        "new",
        [
            _row("c0", "correct", prompt_tokens="100", latency_ms="10", completion_tokens="5"),
            _row("c1", "correct", prompt_tokens="", latency_ms="20"),
            _row("c2", "correct", prompt_tokens="0"),
            _row("c3", "correct", prompt_tokens="50", latency_ms="30"),
        ],
        use_rag=False,
    )
    comparison = compare_runs(new, old)
    prompt, completion = comparison.tokens
    # Only c0 and c3 were reported by both; c3's explicit 0 counts, c2's blank does not.
    assert prompt.change is not None
    assert prompt.change.cases == 2
    assert (prompt.change.old_mean, prompt.change.new_mean) == (40.0, 75.0)
    assert prompt.change.change.point == pytest.approx(35.0)
    assert prompt.change.relative_percent == pytest.approx(87.5)
    # The baseline reported no completion tokens at all, though it reported prompt tokens.
    assert completion.change is None
    assert completion.note == "not reported by both runs for any case"

    # Latency: each run over its own timed cases; the change over cases both timed (c0, c3).
    assert (comparison.new.latency_mean, comparison.new.latency_median) == (20.0, 20.0)
    assert (comparison.old.latency_mean, comparison.old.latency_median) == (50.0, 50.0)
    assert (comparison.new.latency_cases, comparison.old.latency_cases) == (3, 3)
    latency = comparison.latency
    assert latency is not None and latency.cases == 2
    assert (latency.change.point, latency.change.low, latency.change.high) == (-30.0,) * 3

    text = render_comparison(comparison)
    assert "| prompt | 2 | 40.0 | 75.0 | +35.0 [" in text
    assert "- Completion tokens: not reported by both runs for any case." in text
    assert "over the 2 cases both runs timed: -30.0 [-30.0, -30.0] ms (-60.0%)" in text


def test_a_run_without_tokens_reads_not_recorded(tmp_path: Path) -> None:
    old = make_run(tmp_path, "old", [_row("c0", "correct"), _row("c1", "wrong")])
    new = make_run(
        tmp_path,
        "new",
        [
            _row("c0", "correct", prompt_tokens="10", completion_tokens="0"),
            _row("c1", "correct", prompt_tokens="12", completion_tokens="0"),
        ],
        use_rag=False,
    )
    comparison = compare_runs(new, old)
    assert all(token.change is None for token in comparison.tokens)
    text = render_comparison(comparison)
    assert "- Prompt tokens: not recorded (the baseline run has no token counts)." in text
    assert "- Completion tokens: not recorded (the baseline run has no token counts)." in text
    assert "| prompt |" not in text
    neither = compare_runs(
        make_run(tmp_path, "bare", [_row("c0", "x"), _row("c1", "y")], model="n"), old
    )
    assert neither.tokens[0].note == "not recorded (neither run has token counts)"
    assert "Paired difference: no case was timed in both runs." in text


def test_a_zero_baseline_mean_has_no_relative_change(tmp_path: Path) -> None:
    old = make_run(tmp_path, "old", [_row("c0", "correct", completion_tokens="0")])
    new = make_run(tmp_path, "new", [_row("c0", "correct", completion_tokens="7")], use_rag=False)
    comparison = compare_runs(new, old)
    completion = comparison.tokens[1]
    assert completion.change is not None and completion.change.relative_percent is None
    assert "| completion | 1 | 0.0 | 7.0 | +7.0 [+7.0, +7.0] | undefined (baseline mean 0) |" in (
        render_comparison(comparison)
    )


def test_per_difficulty_rows(tmp_path: Path) -> None:
    def rows(correct: set[str]) -> list[dict[str, str]]:
        spec = [("e1", "easy"), ("e2", "easy"), ("m1", "medium"), ("h1", "hard"), ("h2", "hard")]
        return [
            _row(i, "correct" if i in correct else "wrong", hardness=level) for i, level in spec
        ]

    old = make_run(tmp_path, "old", rows({"e1", "m1"}))
    new = make_run(tmp_path, "new", rows({"e1", "e2", "h1", "h2"}), use_rag=False)
    comparison = compare_runs(new, old)
    levels = [
        (row.population, row.cases, row.change.old_correct, row.change.new_correct, row.helped)
        + (row.hurt,)
        for row in comparison.by_difficulty
    ]
    # Ordered easy, medium, hard, extra; a level with no case (extra) has no row.
    assert levels == [("easy", 2, 1, 2, 1, 0), ("medium", 1, 1, 0, 0, 1), ("hard", 2, 0, 2, 2, 0)]
    old_rows = read_rows(old / CASES_FILE)
    for row in comparison.by_difficulty:
        subset = [r for r in old_rows if r["hardness"] == row.population]
        assert row.old_cell == metric_cells(subset, gold=False)["ex"]
    text = render_comparison(comparison)
    assert "| medium | 1 | 100.0% [100.0, 100.0] (1/1) | 0.0% [0.0, 0.0] (0/1) | -100.0 [" in text


def test_a_safety_suite_pairs_its_non_answerable_cases(tmp_path: Path) -> None:
    def rows(correct: set[int]) -> list[dict[str, str]]:
        expected = ["expect_refusal"] * 3 + ["expect_unanswerable"] * 2
        return [
            _row(f"s{i}", "correct" if i in correct else "unanswerable", expected=e)
            for i, e in enumerate(expected)
        ]

    old = make_run(tmp_path, "old", rows({0, 1, 2}))
    new = make_run(tmp_path, "new", rows({0, 1, 3, 4}), ollama_think="on")
    comparison = compare_runs(new, old)
    assert comparison.factor == "ollama_think"
    assert comparison.ex is None and comparison.by_difficulty == ()
    safety = comparison.safety
    assert safety is not None
    assert (safety.cases, safety.change.old_correct, safety.change.new_correct) == (5, 3, 4)
    assert safety.change.interval.point == pytest.approx(0.2)
    assert (safety.helped, safety.hurt) == (2, 1)
    assert safety.old_cell == metric_cells(read_rows(old / CASES_FILE), gold=False)["safety"]
    text = render_comparison(comparison)
    assert "No case is answerable, so EX is not applicable." in text
    assert "## Safety accuracy (refusal and unanswerable cases)" in text
    assert f"| overall | 5 | {safety.old_cell} | {safety.new_cell} | +20.0 [" in text


def test_other_counts(tmp_path: Path) -> None:
    old = make_run(
        tmp_path,
        "old",
        [
            _row("c0", "error", error=EMPTY_GENERATED_SQL, schema_recall="0.5"),
            _row("c1", "error", error="boom", generation_failure="1", schema_recall="1.0"),
            _row("c2", "correct"),
        ],
    )
    new = make_run(tmp_path, "new", [_row(f"c{i}", "correct") for i in range(3)], use_rag=False)
    comparison = compare_runs(new, old)
    assert (comparison.old.empty_sql, comparison.old.generation_failures) == (1, 1)
    assert (comparison.new.empty_sql, comparison.new.generation_failures) == (0, 0)
    assert comparison.old.recall_mean == pytest.approx(0.75)
    assert comparison.old.recall_cases == 2 and comparison.new.recall_mean is None
    text = render_comparison(comparison)
    assert "| Mean schema recall | 0.750 (n=2) | not applicable |" in text
    assert f"| `{EMPTY_GENERATED_SQL}` errors | 1 | 0 |" in text
    assert "| Generation failures | 1 | 0 |" in text


def _without_ollama_think(run_dir: Path) -> Path:
    """Rewrite ``run_dir``'s manifest as a runner from before ``ollama_think`` wrote it."""
    path = run_dir / MANIFEST_FILE
    data = read_manifest(path)
    del data["ollama_think"]
    data["manifest_sha256"] = manifest_sha256(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return run_dir


def test_a_legacy_manifest_compares_on_ollama_think(tmp_path: Path) -> None:
    old = _without_ollama_think(
        make_run(tmp_path, "old", _flags({0, 1}, 4), ollama_think="default")
    )
    new = make_run(tmp_path, "new", _flags({0, 1, 2}, 4), ollama_think="off")
    comparison = compare_runs(new, old)
    assert (comparison.factor, comparison.old_value, comparison.new_value) == (
        "ollama_think",
        "default",
        "off",
    )
    assert render_comparison(comparison).startswith(
        "# `ollama_think`: default (baseline) vs off (new)\n"
    )


def test_the_output_is_byte_identical_on_a_rerun(tmp_path: Path) -> None:
    new, old = _pair(tmp_path, use_rag=False, commit="b" * 40)
    first = render_comparison(compare_runs(new, old))
    second = render_comparison(compare_runs(new, old))
    assert first == second
    assert _STARTED not in first and "duration" not in first


# --- the committed runs --------------------------------------------------------------------

_RESULTS = REPO_ROOT / "evaluation" / "results"
_THINK_OFF = (
    "2026-10-10T061944_spider_dev_subset200_ollama_qwen3.5-9b-q4_K_M_"
    "rag-on-k6-evidence-off-think-off_bd62bfcf_0b75"
)
_DEFAULT = (
    "2026-10-09T053348_spider_dev_subset200_ollama_qwen3.5-9b-q4_K_M_"
    "rag-on-k6-evidence-off_d8f16b52_22eb"
)


def test_the_committed_thinking_off_spider_subset_pair() -> None:
    comparison = compare_runs(_RESULTS / _THINK_OFF, _RESULTS / _DEFAULT)
    assert comparison.factor == "ollama_think"
    ex = comparison.ex
    assert ex is not None
    assert (ex.change.new_correct, ex.change.old_correct, ex.cases) == (120, 103, 200)
    assert (ex.helped, ex.hurt) == (33, 16)
    assert ex.change.interval.point == pytest.approx(0.085)
    # Each run's EX cell is its own report.md's.
    for run, cell in ((_THINK_OFF, ex.new_cell), (_DEFAULT, ex.old_cell)):
        assert f"| overall | 200 | {cell} |" in (_RESULTS / run / REPORT_FILE).read_text("utf-8")


# --- the CLI -------------------------------------------------------------------------------


def test_the_cli_prints_writes_and_refuses(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    new, old = _pair(tmp_path)
    base = ["--compare", "--baseline", str(old), "--new"]
    assert cli.main([*base, str(new)]) == 0
    out = capsys.readouterr().out
    assert out == render_comparison(compare_runs(new, old))

    target = tmp_path / "comparison.md"
    assert cli.main([*base, str(new), "--out", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == out
    assert str(target) in capsys.readouterr().out

    both = make_run(tmp_path, "both", _flags({0}, 10), use_rag=False, evidence=True)
    assert cli.main([*base, str(both)]) == 2
    err = capsys.readouterr().err
    assert "comparison refused" in err
    assert "use_rag: new 'False' vs baseline 'True'" in err


@pytest.mark.parametrize(
    "extra",
    [
        ["--suite", "demo"],
        ["--mode", "llm"],
        ["--mode", "gold"],
        ["--gate", "regression"],
        ["--gate", "gold"],
        ["--resume", "x"],
    ],
)
def test_compare_with_a_run_option_is_a_usage_error(tmp_path: Path, extra: list[str]) -> None:
    with pytest.raises(SystemExit) as usage:
        cli.main(["--compare", "--new", "x", "--baseline", "y", *extra])
    assert usage.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ["--compare", "--new", "x"],
        ["--gate", "regression", "--new", "x", "--baseline", "y", "--out", "z.md"],
        ["--suite", "demo", "--out", "z.md"],
    ],
)
def test_compare_needs_both_runs_and_out_needs_compare(tmp_path: Path, argv: list[str]) -> None:
    with pytest.raises(SystemExit) as usage:
        cli.main([*argv, "--out-root", str(tmp_path / "out")])
    assert usage.value.code == 2
    assert not (tmp_path / "out").exists()
