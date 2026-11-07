"""SQL presentation must preserve source text and never turn it into HTML."""

import html
import re

import pytest

from ui import results


def test_sql_highlighting_distinguishes_code_from_literals_and_comments() -> None:
    sql = "SELECT SUM(price) AS total FROM sales WHERE name = 'SELECT' -- FROM\n"
    rendered = results.highlight_sql(sql, "sqlite")
    assert '<span class="sql-keyword">SELECT</span>' in rendered
    assert '<span class="sql-function">SUM</span>' in rendered
    assert '<span class="sql-literal">&#x27;SELECT&#x27;</span>' in rendered
    assert '<span class="sql-comment"> -- FROM\n</span>' in rendered


@pytest.mark.parametrize("dialect", ["sqlite", "duckdb", "postgres"])
@pytest.mark.parametrize(
    "sql",
    [
        'SELECT "SELECT", SUM(price * 2.5)\n  FROM sales; -- trailing\n',
        "/* <script> */ SELECT '<img src=x onerror=alert(1)>', 'it''s & <';",
        "SELECT 'unterminated <script>",
        "-- comment only\n",
        "SELECT $$SELECT <b>$$, $tag$value$tag$;",
        "SELECT café FROM données WHERE x >= 2;",
        "",
    ],
)
def test_sql_highlighting_preserves_source_and_escapes_html(sql: str, dialect: str) -> None:
    rendered = results.highlight_sql(sql, dialect)
    assert html.unescape(re.sub(r'<span class="sql-[a-z]+">|</span>', "", rendered)) == sql
    assert "<script>" not in rendered
    assert "<img" not in rendered
