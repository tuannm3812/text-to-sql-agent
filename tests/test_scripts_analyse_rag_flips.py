"""scripts/analyse_rag_flips.py's pure helpers, on synthetic outcomes and a tiny database.

The full script reads committed runs and the benchmark databases, which CI does not have, so
only the pieces whose rules the error analysis depends on are pinned here.
"""

from __future__ import annotations

import random
import sqlite3
from pathlib import Path

import pytest

import scripts.analyse_rag_flips as script
from text_to_sql_agent.evaluation_v2 import Case


def test_flips_sorts_numerically_and_splits_by_direction() -> None:
    old = {"10": False, "2": True, "9": False, "1": True}
    new = {"10": True, "2": False, "9": True, "1": True}
    assert script.flips(old, new, "helped") == ["9", "10"]
    assert script.flips(old, new, "hurt") == ["2"]
    with pytest.raises(ValueError, match="unknown direction"):
        script.flips(old, new, "both")


def test_draw_sample_shares_one_rng_across_groups_in_order() -> None:
    first = script.Group("hints", "bird_dev", "helped", 2)
    second = script.Group("hints", "bird_dev", "hurt", 3)
    pools = [(first, [str(i) for i in range(20)]), (second, [str(i) for i in range(30)])]
    rng = random.Random(7)
    expected = [sorted(rng.sample(pool, group.size), key=int) for group, pool in pools]
    assert script.draw_sample(pools, seed=7) == expected
    # Drawing the second group alone, from a fresh RNG, gives a different sample.
    assert script.draw_sample(pools[1:], seed=7)[0] != expected[1]


@pytest.mark.parametrize(
    ("old_text", "new_text", "old_tables", "new_tables", "kind"),
    [
        ("a\n\nb", "a\n\nb", {"a", "b"}, {"a", "b"}, "identical"),
        ("a\n\nb", "b\n\na", {"a", "b"}, {"a", "b"}, "order-only"),
        ("a\n\nb", "a", {"a", "b"}, {"a"}, "different-set"),
    ],
)
def test_classify_context_separates_identical_from_order_only(
    old_text: str, new_text: str, old_tables: set[str], new_tables: set[str], kind: str
) -> None:
    assert script.classify_context(old_text, new_text, old_tables, new_tables) == kind


def test_quoted_literals_reads_both_quotes_and_strips_like_wildcards() -> None:
    sql = """SELECT * FROM t WHERE a = 'It''s' AND b = "Sky Radio" AND c LIKE '%Mid%' AND d = ''"""
    assert script.quoted_literals(sql) == {"it's", "sky radio", "mid"}


def _case(db: Path, case_id: str, gold_sql: str, expected: str = "answerable") -> Case:
    return Case(
        suite="spider_dev",
        id=case_id,
        db_path=str(db),
        question="q",
        evidence="",
        gold_sql=gold_sql,
        hardness="easy",
        expected=expected,  # type: ignore[arg-type]
        expected_tables=("tv",),
    )


def test_hidden_literal_targets_finds_only_values_the_cap_hides(tmp_path: Path) -> None:
    db = tmp_path / "tv.sqlite"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE tv (id INTEGER PRIMARY KEY, series TEXT, short TEXT)")
        # series: 8 distinct values, "rare" least frequent, so the six-value cap hides it.
        rows = [(f"s{i}", "x") for i in range(7) for _ in range(10 - i)] + [("rare", "y")]
        conn.executemany("INSERT INTO tv (series, short) VALUES (?, ?)", rows)
    cases = [
        _case(db, "1", 'SELECT id FROM tv WHERE series = "Rare"'),
        _case(db, "2", "SELECT id FROM tv WHERE series = 's0'"),  # shown in the hint
        _case(db, "3", "SELECT id FROM tv WHERE short = 'rare'"),  # column never cut
        _case(db, "4", "SELECT id FROM tv WHERE id = 'rare'"),  # gold never names series
        _case(db, "5", "SELECT id FROM tv WHERE series = 'rare'", expected="expect_refusal"),
    ]
    targets = script.hidden_literal_targets("spider_dev", cases)
    assert targets == [script.Target("spider_dev", "1", "tv", "series", "rare", 8, 8)]
