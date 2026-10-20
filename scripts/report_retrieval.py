"""Retrieval quality on a suite's gold tables: recall@k, coverage@k and MRR, no model called.

    uv run python scripts/report_retrieval.py --suite bird_train_large [--subset full]
        [--evidence on|off] [--top-k 6]

For every case that lists `expected_tables`, the question (evidence appended when `--evidence
on`, as the runner sends it) is ranked by `rag.rank_schema_chunks`, and each gold table's
rank is read off (`evaluation_v2.retrieval`). The report, Markdown on stdout, gives:

- recall@k, coverage@k (every gold table in the first k) and MRR over the ranking itself,
  before foreign-key neighbours are added;
- the same cases at the shipped setting (`--top-k`, neighbours included), which is what a
  run's `schema_recall` column records;
- both split by hardness and by database;
- the gold tables the shipped setting drops most often, with where they ranked.

Read-only; no model is called. Exit 0 always; the numbers are the result.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from text_to_sql_agent.config import DEFAULT_RAG_TOP_K  # noqa: E402 - after the sys.path insert
from text_to_sql_agent.evaluation_v2 import Case, load_suite  # noqa: E402
from text_to_sql_agent.evaluation_v2.retrieval import (  # noqa: E402
    DEFAULT_KS,
    CaseRanks,
    case_ranks,
    summarise,
)
from text_to_sql_agent.evaluation_v2.runner import (  # noqa: E402
    question_text,
    read_subset_ids,
    resolve_db_path,
)
from text_to_sql_agent.rag import rank_schema_chunks, retrieve_schema_context  # noqa: E402

HARDNESS_ORDER = ("easy", "medium", "hard", "extra")


@dataclass(frozen=True)
class CaseResult:
    """One case's ranks, and what the shipped setting sent of its gold tables."""

    case: Case
    ranks: CaseRanks
    sent: frozenset[str]

    @property
    def sent_recall(self) -> float:
        return sum(1 for table in self.ranks.ranks if table in self.sent) / len(self.ranks.ranks)

    @property
    def sent_covered(self) -> bool:
        return all(table in self.sent for table in self.ranks.ranks)


def evaluate(cases: Sequence[Case], *, evidence: bool, top_k: int) -> list[CaseResult]:
    """Rank every case with gold tables and record what `top_k` retrieval sends."""
    results = []
    for case in cases:
        db_path = resolve_db_path(case.db_path)
        question = question_text(case, evidence=evidence)
        ranking = [chunk.qualified_name for chunk in rank_schema_chunks(db_path, question)]
        ranks = case_ranks(case.id, ranking, case.expected_tables)
        if ranks is None:
            continue
        sent = retrieve_schema_context(db_path, question, top_k=top_k).chunks
        results.append(
            CaseResult(case, ranks, frozenset(chunk.qualified_name.lower() for chunk in sent))
        )
    return results


def _pct(value: float) -> str:
    return f"{100 * value:.1f}"


def _group_table(title: str, groups: dict[str, list[CaseResult]], top_k: int) -> list[str]:
    lines = [
        f"## By {title}",
        "",
        f"| {title.capitalize()} | Cases | MRR | recall@{top_k} | coverage@{top_k} | "
        f"sent recall | sent coverage |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, group in groups.items():
        summary = summarise([r.ranks for r in group], (top_k,))
        sent_recall = sum(r.sent_recall for r in group) / len(group)
        sent_covered = sum(r.sent_covered for r in group) / len(group)
        lines.append(
            f"| {name} | {len(group)} | {summary.mrr:.3f} | {_pct(summary.recall[top_k])} | "
            f"{_pct(summary.coverage[top_k])} | {_pct(sent_recall)} | {_pct(sent_covered)} |"
        )
    return lines + [""]


def render(
    suite: str, subset: str, results: Sequence[CaseResult], *, evidence: bool, top_k: int
) -> str:
    """The Markdown report."""
    ks = tuple(sorted({*DEFAULT_KS, top_k}))
    summary = summarise([r.ranks for r in results], ks)
    sent_recall = sum(r.sent_recall for r in results) / len(results) if results else 0.0
    sent_covered = sum(r.sent_covered for r in results) / len(results) if results else 0.0
    lines = [
        f"# Retrieval: `{suite}` / {subset}, evidence {'on' if evidence else 'off'}",
        "",
        f"{summary.cases} cases with gold tables. Ranking = `rag.rank_schema_chunks`, before "
        f"foreign-key neighbours. Sent = `retrieve_schema_context(top_k={top_k})`, "
        "neighbours included, what a run's `schema_recall` records. Percentages.",
        "",
        "| k | " + " | ".join(str(k) for k in ks) + " |",
        "|---|" + "---:|" * len(ks),
        "| recall@k | " + " | ".join(_pct(summary.recall[k]) for k in ks) + " |",
        "| coverage@k | " + " | ".join(_pct(summary.coverage[k]) for k in ks) + " |",
        "",
        f"MRR {summary.mrr:.3f}. Sent at top {top_k}: recall {_pct(sent_recall)}, every gold "
        f"table sent in {_pct(sent_covered)} % of cases.",
        "",
    ]
    by_hardness: dict[str, list[CaseResult]] = defaultdict(list)
    by_database: dict[str, list[CaseResult]] = defaultdict(list)
    for result in results:
        by_hardness[result.case.hardness].append(result)
        by_database[Path(result.case.db_path).stem].append(result)
    lines += _group_table(
        "hardness", {h: by_hardness[h] for h in HARDNESS_ORDER if h in by_hardness}, top_k
    )
    if len(by_database) > 1:
        lines += _group_table(
            "database",
            dict(sorted(by_database.items(), key=lambda item: (-len(item[1]), item[0]))),
            top_k,
        )

    dropped: Counter[tuple[str, str]] = Counter()
    dropped_ranks: dict[tuple[str, str], list[int]] = defaultdict(list)
    for result in results:
        for table, rank in result.ranks.ranks.items():
            if table not in result.sent:
                key = (Path(result.case.db_path).stem, table)
                dropped[key] += 1
                if rank is not None:
                    dropped_ranks[key].append(rank)
    lines += [
        f"## Gold tables most often not sent at top {top_k}",
        "",
        f"{sum(dropped.values())} gold-table misses over "
        f"{sum(not r.sent_covered for r in results)} cases.",
        "",
        "| Database | Table | Misses | Median rank when missed |",
        "|---|---|---:|---:|",
    ]
    for (database, table), count in dropped.most_common(15):
        ranks = dropped_ranks[(database, table)]
        median = f"{statistics.median(ranks):g}" if ranks else "unranked"
        lines.append(f"| `{database}` | `{table}` | {count} | {median} |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--suite", required=True)
    parser.add_argument("--subset", default="full")
    parser.add_argument("--evidence", choices=("on", "off"), default="on")
    parser.add_argument("--top-k", type=int, default=DEFAULT_RAG_TOP_K)
    parser.add_argument("--suites-dir", type=Path, default=ROOT_DIR / "evaluation" / "suites")
    args = parser.parse_args(argv)
    cases = load_suite(args.suites_dir / f"{args.suite}.jsonl")
    if args.subset != "full":
        wanted = set(read_subset_ids(args.suites_dir / f"{args.suite}.{args.subset}.txt"))
        cases = [case for case in cases if case.id in wanted]
    evidence = args.evidence == "on"
    results = evaluate(cases, evidence=evidence, top_k=args.top_k)
    sys.stdout.write(render(args.suite, args.subset, results, evidence=evidence, top_k=args.top_k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
