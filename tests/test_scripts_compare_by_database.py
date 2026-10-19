"""scripts/compare_by_database.py: the per-database pairing, on synthetic outcomes."""

from __future__ import annotations

import scripts.compare_by_database as script
from text_to_sql_agent.evaluation_v2.stats import paired_bootstrap_ci


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
