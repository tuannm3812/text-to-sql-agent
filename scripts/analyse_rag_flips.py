"""Rebuild the inputs of `evaluation/results/rag_attribution/error_analysis.md`, read-only.

    uv run python scripts/analyse_rag_flips.py            # check and print a summary
    uv run python scripts/analyse_rag_flips.py --write    # also rewrite the two CSVs

Three things, none of which calls a model:

1. **The seeded sample.** Every helped and hurt pool between the attribution arms, sorted by
   numeric ID, drawn with one `random.Random(20261013)` in the report's group order. The drawn
   IDs must equal the hand labels in `flip_labels.csv`, or the script exits 1.
2. **What each BIRD selection flip changed.** Arm B's and arm C's schema text is re-rendered
   at HEAD for every B-to-C flip and sorted into `identical` (byte-identical text),
   `order-only` (same table set, different text) or `different-set`. Each table set must equal
   the run's `retrieved_tables` cell. Written to `selection_contexts.csv`.
3. **The hidden-literal target set.** Every answerable Spider and BIRD case whose gold SQL
   quotes a value of a hinted column that the six-value cap hides. Written to
   `hidden_literal_targets.csv`, and each suite's case IDs to `evaluation/suites/
   <suite>.hiddenlit.txt`, so a hint change can be run (`--subset hiddenlit`) and scored on a
   set frozen before it.

The literal match is a deliberately simple proxy: a quoted string in the gold SQL, with any
leading and trailing `%` removed, equal to a hidden value ignoring case, where the gold SQL
also names the column. Double quotes count, because Spider's gold SQL writes most literals that
way, although SQLite reads a double-quoted word as an identifier first. The column test is a
substring match, so the set can still over-count.

Benchmark databases are opened `mode=ro`. Exit codes: 0 every check passed, 1 a check failed.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sqlite3
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from text_to_sql_agent.config import (  # noqa: E402 - import must follow the sys.path insert
    DEFAULT_VALUE_HINT_LIMIT,
)
from text_to_sql_agent.evaluation_v2 import Case, load_suite  # noqa: E402
from text_to_sql_agent.evaluation_v2.gates import load_run  # noqa: E402
from text_to_sql_agent.evaluation_v2.runner import question_text, resolve_db_path  # noqa: E402
from text_to_sql_agent.rag import retrieve_schema_context  # noqa: E402
from text_to_sql_agent.schema import get_schema_chunks_and_plain_ddl  # noqa: E402

SEED = 20261013
RESULTS = ROOT_DIR / "evaluation" / "results"
OUT_DIR = RESULTS / "rag_attribution"
LABELS_FILE = OUT_DIR / "flip_labels.csv"
CONTEXTS_FILE = OUT_DIR / "selection_contexts.csv"
TARGETS_FILE = OUT_DIR / "hidden_literal_targets.csv"
SUITES_DIR = ROOT_DIR / "evaluation" / "suites"
TARGET_SUBSET = "hiddenlit"  # evaluation/suites/<suite>.hiddenlit.txt, for --subset hiddenlit

# Arm A: plain full DDL. Arm B: full DDL plus hints (top_k=0). Arm C: top-6 plus hints.
ARMS: dict[str, dict[str, str]] = {
    "spider_dev": {
        "A": "2026-10-11T033934_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-off-evidence-off-think-off_f934dfb5_9f67",
        "B": "2026-10-11T233024_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-on-k0-evidence-off-think-off_3a2be932_2dea",
        "C": "2026-10-10T071608_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-on-k6-evidence-off-think-off_a8ebee81_e6c2",
    },
    "bird_dev": {
        "A": "2026-10-11T042329_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-off-evidence-on-think-off_2e606bf4_a071",
        "B": "2026-10-12T001558_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-on-k0-evidence-on-think-off_8844615e_b6ed",
        "C": "2026-10-10T080619_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_"
        "rag-on-k6-evidence-on-think-off_22491cc9_3ef9",
    },
}
EVIDENCE = {"spider_dev": False, "bird_dev": True}


@dataclass(frozen=True)
class Group:
    """One sampled group: a factor's flips on one suite, in one direction."""

    factor: str  # "hints" (A to B) or "selection" (B to C)
    suite: str
    direction: str  # "helped" or "hurt"
    size: int


# The draw order is part of the seed's meaning: changing it changes every later group.
GROUPS: tuple[Group, ...] = (
    Group("hints", "bird_dev", "helped", 15),
    Group("hints", "bird_dev", "hurt", 15),
    Group("hints", "spider_dev", "helped", 10),
    Group("hints", "spider_dev", "hurt", 10),
    Group("selection", "bird_dev", "hurt", 15),
    Group("selection", "bird_dev", "helped", 10),
)
ARM_PAIR = {"hints": ("A", "B"), "selection": ("B", "C")}

Outcomes = dict[str, bool]  # case id -> correct


def flips(old: Outcomes, new: Outcomes, direction: str) -> list[str]:
    """IDs correct in `new` and not `old` ("helped") or the reverse, sorted numerically."""
    if direction == "helped":
        ids = [i for i in old if new[i] and not old[i]]
    elif direction == "hurt":
        ids = [i for i in old if old[i] and not new[i]]
    else:
        raise ValueError(f"unknown direction {direction!r}")
    return sorted(ids, key=int)


def draw_sample(pools: Sequence[tuple[Group, list[str]]], seed: int = SEED) -> list[list[str]]:
    """Draw each group from its pool with one shared RNG, in the order given."""
    rng = random.Random(seed)
    return [sorted(rng.sample(pool, group.size), key=int) for group, pool in pools]


def classify_context(
    old_text: str, new_text: str, old_tables: set[str], new_tables: set[str]
) -> str:
    """`identical`, `order-only` (same tables, different text) or `different-set`."""
    if old_text == new_text:
        return "identical"
    return "order-only" if old_tables == new_tables else "different-set"


_LITERAL = re.compile(r"'((?:[^']|'')*)'|\"((?:[^\"]|\"\")*)\"")


def quoted_literals(sql: str) -> set[str]:
    """Quoted strings in `sql`, either quote, unescaped, outer `%` removed, case-folded."""
    found = set()
    for match in _LITERAL.finditer(sql):
        single, double = match.groups()
        text = single.replace("''", "'") if single is not None else double.replace('""', '"')
        found.add(text.strip("%").casefold())
    return {literal for literal in found if literal.strip()}


def _outcomes(suite: str, arm: str) -> tuple[Outcomes, dict[str, str]]:
    _, rows = load_run(RESULTS / ARMS[suite][arm], f"{suite} arm {arm}", require_citable=True)
    return (
        {i: row["outcome"] == "correct" for i, row in rows.items()},
        {i: row["retrieved_tables"] for i, row in rows.items()},
    )


def _column_values(db_path: str, table: str, column: str) -> list[str]:
    """Every value the hint query could show, most frequent first, as the engine renders it."""
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    quoted_table = '"' + table.replace('"', '""') + '"'
    quoted_column = '"' + column.replace('"', '""') + '"'
    with sqlite3.connect(uri, uri=True) as conn:
        rows = conn.execute(
            f"SELECT {quoted_column}, COUNT(*) AS n FROM {quoted_table} "
            f"WHERE {quoted_column} IS NOT NULL GROUP BY {quoted_column} "
            f"ORDER BY n DESC, {quoted_column}"
        ).fetchall()
    return [str(row[0])[:60] for row in rows if str(row[0]).strip()]


@dataclass(frozen=True)
class Target:
    """One answerable case whose gold SQL quotes a value the hint cap hides."""

    suite: str
    id: str
    table: str
    column: str
    literal: str
    rank: int  # 1-based frequency rank of the hidden value
    distinct: int


def hidden_literal_targets(suite: str, cases: Iterable[Case]) -> list[Target]:
    """Every (case, column, literal) where the gold SQL quotes a value hidden by the cap."""
    hidden_cache: dict[tuple[str, str, str], dict[str, tuple[int, int]]] = {}
    targets: list[Target] = []
    for case in cases:
        if case.expected != "answerable":
            continue
        literals = quoted_literals(case.gold_sql)
        if not literals:
            continue
        db_path = resolve_db_path(case.db_path)
        gold = case.gold_sql.casefold()
        chunks, _ = get_schema_chunks_and_plain_ddl(db_path)
        for chunk in chunks:
            for column, shown in sorted((chunk.value_hints or {}).items()):
                if len(shown) < DEFAULT_VALUE_HINT_LIMIT or column.casefold() not in gold:
                    continue  # nothing was cut, or the gold SQL never names the column
                key = (db_path, chunk.table_name, column)
                if key not in hidden_cache:
                    values = _column_values(db_path, chunk.table_name, column)
                    hidden_cache[key] = {
                        value.casefold(): (rank, len(values))
                        for rank, value in enumerate(values, start=1)
                        if rank > len(shown)
                    }
                for literal in sorted(literals & hidden_cache[key].keys()):
                    rank, distinct = hidden_cache[key][literal]
                    targets.append(
                        Target(
                            suite, case.id, chunk.qualified_name, column, literal, rank, distinct
                        )
                    )
    return targets


def _write(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="rewrite the two output CSVs")
    args = parser.parse_args(argv)
    ok = True

    arms = {(s, a): _outcomes(s, a) for s in ARMS for a in ("A", "B", "C")}
    pools = []
    for group in GROUPS:
        old, new = ARM_PAIR[group.factor]
        pool = flips(arms[group.suite, old][0], arms[group.suite, new][0], group.direction)
        pools.append((group, pool))
    with LABELS_FILE.open(encoding="utf-8", newline="") as handle:
        labels = list(csv.DictReader(handle))
    print("1. Sample")
    for (group, pool), ids in zip(pools, draw_sample(pools), strict=True):
        labelled = sorted(
            (
                r["id"]
                for r in labels
                if (r["factor"], r["suite"], r["direction"])
                == (group.factor, group.suite, group.direction)
            ),
            key=int,
        )
        match = labelled == ids
        ok &= match
        print(
            f"   {group.factor} {group.suite} {group.direction}: pool {len(pool)}, "
            f"n {len(ids)}, labels {'match' if match else 'DIFFER'}"
        )
    print(f"   primary labels: {dict(Counter(r['primary'] for r in labels).most_common())}")

    print("2. BIRD selection flips (B to C)")
    suite = "bird_dev"
    cases = {case.id: case for case in load_suite(ROOT_DIR / "evaluation/suites/bird_dev.jsonl")}
    recorded = {arm: arms[suite, arm][1] for arm in ("B", "C")}
    context_rows: list[tuple[str, str, str]] = []
    for group, pool in pools:
        if group.factor != "selection":
            continue
        for case_id in pool:
            case = cases[case_id]
            question = question_text(case, evidence=EVIDENCE[suite])
            texts, tables = {}, {}
            for arm, top_k in (("B", 0), ("C", 6)):
                result = retrieve_schema_context(case.db_path, question, top_k=top_k)
                texts[arm] = result.schema_text
                tables[arm] = {chunk.qualified_name.lower() for chunk in result.chunks}
                if ", ".join(sorted(tables[arm])) != recorded[arm][case_id]:
                    ok = False
                    print(f"   MISMATCH: case {case_id} arm {arm} table set differs from the run")
            kind = classify_context(texts["B"], texts["C"], tables["B"], tables["C"])
            context_rows.append((case_id, group.direction, kind))
    tally = Counter((kind, direction) for _, direction, kind in context_rows)
    for kind in ("identical", "order-only", "different-set"):
        print(
            f"   {kind}: {tally[kind, 'hurt'] + tally[kind, 'helped']} "
            f"({tally[kind, 'hurt']} hurt, {tally[kind, 'helped']} helped)"
        )

    print("3. Hidden-literal targets")
    targets: list[Target] = []
    for name in ARMS:
        found = hidden_literal_targets(
            name, load_suite(ROOT_DIR / f"evaluation/suites/{name}.jsonl")
        )
        targets += found
        print(
            f"   {name}: {len({t.id for t in found})} cases, {len(found)} (column, literal) pairs"
        )

    if args.write:
        context_rows.sort(key=lambda row: int(row[0]))
        _write(CONTEXTS_FILE, ("id", "direction", "context_change"), context_rows)
        _write(
            TARGETS_FILE,
            ("suite", "id", "table", "column", "literal", "rank", "distinct"),
            ((t.suite, t.id, t.table, t.column, t.literal, t.rank, t.distinct) for t in targets),
        )
        for name in ARMS:
            ids = sorted({t.id for t in targets if t.suite == name}, key=int)
            subset = SUITES_DIR / f"{name}.{TARGET_SUBSET}.txt"
            subset.write_text("".join(f"{case_id}\n" for case_id in ids), encoding="utf-8")
        print(f"wrote {CONTEXTS_FILE.name}, {TARGETS_FILE.name} and the {TARGET_SUBSET} subsets")
    print("all checks passed" if ok else "A CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
