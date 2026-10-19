"""Paired EX change of one run against another, broken down by database.

    uv run python scripts/compare_by_database.py --new DIR --baseline DIR [--suites-dir DIR]

`scripts/evaluate_v2.py --compare` pairs two runs over the whole suite and by hardness. This
adds the split by database, which matters on a suite whose databases differ in size: a
selection gain that comes from the two largest schemas and not the others is a different
finding from a uniform one. Same pairing, same statistic (`paired_bootstrap_ci`, seed 0), one
Markdown table on stdout. The suite file is read for each case's database. Read-only.

The two runs may differ in the treatment (RAG, evidence, model, commit), but not in what they
measured: every `POPULATION_FIELDS` identity field must match, and the suite file read for
the database split must hash to the runs' `suite_sha256`. Shared case IDs alone do not show
that the questions and database contents were the same (Codex, 2026-10-19). Exit codes: 0
compared, 2 refused.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from text_to_sql_agent.evaluation_v2 import load_suite  # noqa: E402 - after the sys.path insert
from text_to_sql_agent.evaluation_v2.contract import suite_sha256  # noqa: E402
from text_to_sql_agent.evaluation_v2.gates import (  # noqa: E402
    RegressionRefused,
    aligned_ids,
    describe_field,
    load_run,
)
from text_to_sql_agent.evaluation_v2.manifest import Manifest  # noqa: E402
from text_to_sql_agent.evaluation_v2.stats import Interval, paired_bootstrap_ci  # noqa: E402

Outcomes = Mapping[str, bool]

# The identity fields that fix the population: which questions, which database bytes, which
# gold references and scorer. A treatment may change anything else.
POPULATION_FIELDS: tuple[str, ...] = (
    "suite",
    "suite_sha256",
    "subset",
    "subset_sha256",
    "source_release",
    "database_fingerprint",
    "adapter_version",
    "scorer_version",
)


def population_mismatch(new: Manifest, old: Manifest, suite_file: Path) -> list[str]:
    """Why the pair does not measure the same population; empty when it does."""
    reasons = [
        describe_field(name, new, old)
        for name in POPULATION_FIELDS
        if getattr(new.identity, name) != getattr(old.identity, name)
    ]
    if not suite_file.is_file():
        reasons.append(f"suite file {suite_file} is missing")
    elif suite_sha256(suite_file) != new.identity.suite_sha256:
        reasons.append(f"suite file {suite_file} does not hash to the runs' suite_sha256")
    return reasons


@dataclass(frozen=True)
class DatabaseRow:
    """One database's paired result."""

    database: str
    cases: int
    baseline_correct: int
    new_correct: int
    change: Interval


def by_database(
    new: Outcomes, baseline: Outcomes, database_of: Mapping[str, str], ids: Sequence[str]
) -> list[DatabaseRow]:
    """One row per database over `ids`, in descending case count then name."""
    groups: dict[str, list[str]] = defaultdict(list)
    for case_id in ids:
        groups[database_of[case_id]].append(case_id)
    rows = []
    for database, members in groups.items():
        members = sorted(members, key=lambda i: (len(i), i))
        change = paired_bootstrap_ci([new[i] for i in members], [baseline[i] for i in members])
        rows.append(
            DatabaseRow(
                database,
                len(members),
                sum(baseline[i] for i in members),
                sum(new[i] for i in members),
                change,
            )
        )
    return sorted(rows, key=lambda r: (-r.cases, r.database))


def render(rows: Sequence[DatabaseRow]) -> str:
    """The Markdown table."""
    lines = [
        "| Database | Cases | Baseline EX | New EX | Paired change (points) |",
        "|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r.database}` | {r.cases} | {100 * r.baseline_correct / r.cases:.1f} % "
            f"({r.baseline_correct}/{r.cases}) | {100 * r.new_correct / r.cases:.1f} % "
            f"({r.new_correct}/{r.cases}) | {100 * r.change.point:+.1f} "
            f"[{100 * r.change.low:+.1f}, {100 * r.change.high:+.1f}] |"
        )
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--suites-dir", type=Path, default=ROOT_DIR / "evaluation" / "suites")
    args = parser.parse_args(argv)
    try:
        new_manifest, new_rows = load_run(args.new, "new", require_citable=False)
        old_manifest, old_rows = load_run(args.baseline, "baseline", require_citable=False)
        suite_file = args.suites_dir / f"{new_manifest.identity.suite}.jsonl"
        mismatch = population_mismatch(new_manifest, old_manifest, suite_file)
        if mismatch:
            raise RegressionRefused(
                "the runs do not measure the same population: " + "; ".join(mismatch)
            )
        ids = aligned_ids(new_rows, old_rows)
    except RegressionRefused as exc:
        sys.stderr.write(f"comparison refused: {exc}\n")
        return 2
    database_of = {case.id: Path(case.db_path).stem for case in load_suite(suite_file)}
    rows = by_database(
        {i: new_rows[i]["outcome"] == "correct" for i in ids},
        {i: old_rows[i]["outcome"] == "correct" for i in ids},
        database_of,
        ids,
    )
    sys.stdout.write(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
