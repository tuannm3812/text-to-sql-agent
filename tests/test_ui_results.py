from __future__ import annotations

import pandas as pd
import pytest

from ui import results
from ui.results import answer_headline, bar_chart

KNOWN_CODES = [
    "BLOCKED_UNSAFE_SQL",
    "BLOCKED_UNSUPPORTED_COLUMN_TYPE",
    "UNANSWERABLE_WITH_GIVEN_SCHEMA",
    "RESULT_TRUNCATED_TO_1000_ROWS",
    "QUERY_ABORTED_AFTER_100000_VM_STEPS",
    "QUERY_ABORTED_AFTER_5000_MS",
    "EMPTY_GENERATED_SQL",
]


def test_the_empty_sql_code_is_not_described_as_a_refusal() -> None:
    message = results.describe_error("EMPTY_GENERATED_SQL")
    assert "no SQL" in message
    assert "not a refusal" in message
    assert "read-only" not in message


@pytest.mark.parametrize("code", KNOWN_CODES)
def test_describe_error_returns_a_human_message(code: str) -> None:
    message = results.describe_error(code)
    assert message != code, f"{code} is still shown raw to the user"
    assert message[0].isupper()
    assert len(message) > 20


def test_describe_error_mentions_read_only_for_blocked_sql() -> None:
    assert "read-only" in results.describe_error("BLOCKED_UNSAFE_SQL")


def test_the_column_type_refusal_does_not_claim_the_sql_was_not_read_only() -> None:
    """A `citext` comparison is read-only; the message must name the real reason."""
    message = results.describe_error("BLOCKED_UNSUPPORTED_COLUMN_TYPE")
    assert "read-only" not in message
    assert "data type" in message


def test_describe_error_mentions_schema_for_unanswerable() -> None:
    assert "schema" in results.describe_error("UNANSWERABLE_WITH_GIVEN_SCHEMA")


def test_describe_error_includes_the_row_cap_in_the_truncation_message() -> None:
    assert "1000" in results.describe_error("RESULT_TRUNCATED_TO_1000_ROWS")


def test_describe_error_includes_the_step_budget_in_the_abort_message() -> None:
    assert "100000" in results.describe_error("QUERY_ABORTED_AFTER_100000_VM_STEPS")


def test_describe_error_passes_through_an_unrecognised_message() -> None:
    assert results.describe_error("RuntimeError: boom") == "RuntimeError: boom"


def test_describe_error_handles_none() -> None:
    assert results.describe_error(None) == ""


def test_describe_error_reports_duckdb_abort_in_ms_not_steps() -> None:
    message = results.describe_error("QUERY_ABORTED_AFTER_5000_MS")
    assert "5000 ms" in message
    assert "steps" not in message


def test_describe_error_redacts_a_dsn_password_in_raw_exception_text() -> None:
    raw = "could not connect to postgresql://u:hunter2@host/db"
    assert "hunter2" not in results.describe_error(raw)


def test_blocked_message_reads_correctly_for_a_refusal_the_model_made() -> None:
    message = results.describe_error("BLOCKED_UNSAFE_SQL")
    assert "asked to change data" in message
    assert "generated SQL was blocked" not in message


# --- Codex's redesign review, 2026-10-21 ------------------------------------------------


def _domain(df: pd.DataFrame) -> list[float]:
    built = bar_chart(df)
    assert built is not None
    spec = built[0].to_dict()
    return list(spec["layer"][0]["encoding"]["x"]["scale"]["domain"])


def test_a_chart_domain_spans_negative_and_positive_values() -> None:
    low, high = _domain(pd.DataFrame({"segment": ["Loss", "Gain"], "net_profit": [-20, 10]}))
    assert low < -20 and high > 10


def test_an_all_negative_chart_ends_at_zero() -> None:
    low, high = _domain(pd.DataFrame({"segment": ["A", "B"], "change": [-5, -2]}))
    assert low < -5 and high == 0


def test_an_all_zero_chart_still_has_a_range() -> None:
    assert _domain(pd.DataFrame({"segment": ["A", "B"], "n": [0, 0]})) == [0.0, 1.0]


def test_non_finite_values_are_left_out_of_the_chart_and_said_so() -> None:
    df = pd.DataFrame({"segment": ["A", "B", "C"], "n": [1.0, float("nan"), float("inf")]})
    built = bar_chart(df)
    assert built is not None
    assert "2 rows without a number not drawn" in built[1]


def test_a_long_result_draws_the_first_twelve_rows_and_says_so() -> None:
    df = pd.DataFrame({"segment": [f"s{i}" for i in range(15)], "n": list(range(15, 0, -1))})
    built = bar_chart(df)
    assert built is not None
    assert built[1] == "first 12 of 15 rows drawn"


def test_the_headline_is_short_and_sums_only_a_measure_the_sql_summed() -> None:
    revenue = pd.DataFrame({"category": ["Electronics", "Fashion"], "total_revenue": [100, 40]})
    sql = "SELECT category, SUM(price) AS total_revenue FROM t GROUP BY category"
    additive = results.additive_measures(sql, "sqlite")
    assert additive == frozenset({"total_revenue"})
    headline, facts = answer_headline(revenue, additive=additive)
    assert headline == "<em>Electronics</em> leads with 100"
    assert "More than the other one combined (40)" in facts

    # A name is not evidence: `score` can be an average.
    score = pd.DataFrame({"course": ["A", "B", "C"], "score": [90.0, 20.0, 10.0]})
    avg_sql = "SELECT course, AVG(mark) AS score FROM t GROUP BY course"
    assert results.additive_measures(avg_sql, "sqlite") == frozenset()
    assert "combined" not in answer_headline(score)[1]

    signed = pd.DataFrame({"segment": ["Gain", "Loss"], "net_profit": [10, -20]})
    assert "combined" not in answer_headline(signed, additive=frozenset({"net_profit"}))[1]


@pytest.mark.parametrize(
    ("values", "missing"),
    [([10.0, float("inf")], 1), ([10.0, None], 1), ([float("nan"), float("-inf")], 2)],
)
def test_no_leader_or_total_is_claimed_when_a_value_is_missing(
    values: list[float | None], missing: int
) -> None:
    """Codex, 2026-10-21: `10` beside `1e999` was headlined "A leads with 10"."""
    df = pd.DataFrame({"category": ["A", "B"], "total": values})
    headline, facts = answer_headline(df, additive=frozenset({"total"}))
    assert headline == "2 rows returned."
    assert "leads" not in headline and "combined" not in facts
    assert facts.startswith(f"{missing} of them")


def test_a_real_sqlite_infinity_gets_no_winner() -> None:
    import sqlite3

    from text_to_sql_agent import QueryResult
    from ui.results import result_to_dataframe

    with sqlite3.connect(":memory:") as conn:
        cursor = conn.execute("SELECT 'A' AS category, 10.0 AS total UNION ALL SELECT 'B', 1e999")
        rows = cursor.fetchall()
    df = result_to_dataframe(QueryResult(columns=["category", "total"], rows=rows))
    assert df is not None
    assert answer_headline(df)[0] == "2 rows returned."
