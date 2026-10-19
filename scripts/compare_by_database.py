"""Paired EX change of one run against another, broken down by database.

    uv run python scripts/compare_by_database.py --new DIR --baseline DIR [--suites-dir DIR]

`scripts/evaluate_v2.py --compare` pairs two runs over the whole suite and by hardness. This
adds the split by database, which matters on a suite whose databases differ in size: a
selection gain that comes from the two largest schemas and not the others is a different
finding from a uniform one. Same pairing, same statistic (`paired_bootstrap_ci`, seed 0), one
Markdown table on stdout. The suite file is read for each case's database. Read-only.
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
from text_to_sql_agent.evaluation_v2.gates import aligned_ids, load_run  # noqa: E402
from text_to_sql_agent.evaluation_v2.stats import Interval, paired_bootstrap_ci  # noqa: E402

Outcomes = Mapping[str, bool]


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
    _, new_rows = load_run(args.new, "new", require_citable=False)
    _, old_rows = load_run(args.baseline, "baseline", require_citable=False)
    suite = next(iter(new_rows.values()))["suite"]  # every row carries its suite name
    database_of = {
        case.id: Path(case.db_path).stem for case in load_suite(args.suites_dir / f"{suite}.jsonl")
    }
    ids = aligned_ids(new_rows, old_rows)
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
