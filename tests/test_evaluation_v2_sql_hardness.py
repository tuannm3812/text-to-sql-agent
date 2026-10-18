"""sql_hardness: Spider's hardness rule counted from SQL text instead of Spider's parse."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from text_to_sql_agent.evaluation_v2.spider_hardness import spider_hardness
from text_to_sql_agent.evaluation_v2.sql_hardness import sql_hardness

SPIDER_DEV = Path(__file__).resolve().parents[1] / "data" / "benchmarks" / "spider" / "dev.json"


@pytest.mark.parametrize(
    ("sql", "label"),
    [
        ("SELECT count(*) FROM singer", "easy"),
        ("SELECT name FROM singer WHERE age > 20 ORDER BY age", "medium"),
        ("SELECT name, age FROM singer WHERE age > 20 AND country = 'US'", "medium"),
        # Three component-1 items (join, where, group by) and one "other" (two columns).
        (
            "SELECT s.name, count(*) FROM singer s JOIN concert c ON s.id = c.singer_id "
            "WHERE c.year > 2000 GROUP BY s.id",
            "hard",
        ),
        ("SELECT name FROM singer WHERE id NOT IN (SELECT singer_id FROM concert)", "hard"),
        (
            "SELECT name FROM singer WHERE age > (SELECT avg(age) FROM singer) "
            "AND country = 'US' ORDER BY age",
            "extra",
        ),
        # A chain of set operations nests once, as Spider's parser has it.
        ("SELECT a FROM t UNION SELECT a FROM u EXCEPT SELECT a FROM v", "hard"),
    ],
)
def test_sql_hardness_labels(sql: str, label: str) -> None:
    assert sql_hardness(sql) == label


def test_unparseable_sql_is_a_value_error() -> None:
    with pytest.raises(ValueError, match="hardness"):
        sql_hardness("SELECT FROM WHERE (")


@pytest.mark.skipif(not SPIDER_DEV.is_file(), reason="run scripts/prepare_benchmarks.py first")
def test_agrees_with_the_official_label_on_every_spider_dev_query() -> None:
    dev = json.loads(SPIDER_DEV.read_text(encoding="utf-8"))
    disagreements = [
        (i, record["query"])
        for i, record in enumerate(dev)
        if sql_hardness(record["query"]) != spider_hardness(record["sql"])
    ]
    assert disagreements == []
