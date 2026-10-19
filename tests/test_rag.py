from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

import text_to_sql_agent as agent
from text_to_sql_agent import SchemaRetrievalResult, rag
from text_to_sql_agent.types import render_schema_text


def test_retrieve_schema_chunks_selects_relevant_tables(
    customers_sales_courses_db: str,
) -> None:
    chunks = agent.retrieve_schema_chunks(
        customers_sales_courses_db,
        "total sales amount by customer",
        top_k=1,
    )
    names = {chunk.table_name for chunk in chunks}

    assert "sales" in names
    assert "customers" in names
    assert "courses" not in names


def test_schema_rag_expands_business_synonyms(customers_sales_courses_db: str) -> None:
    context = agent.retrieve_schema_context(
        customers_sales_courses_db,
        "revenue by client",
        top_k=1,
    )
    names = {chunk.table_name for chunk in context.chunks}

    assert "sales" in names
    assert "customers" in names
    assert "revenue" in context.expanded_tokens
    assert "customer" in context.expanded_tokens
    assert "Schema RAG strategy" in context.report


def test_retrieve_relevant_schema_returns_only_selected_ddl(customers_courses_db: str) -> None:
    schema = agent.retrieve_relevant_schema(customers_courses_db, "customer names", top_k=1)

    assert "CREATE TABLE customers" in schema
    assert "CREATE TABLE courses" not in schema


# --- Prompt-size accounting (Codex review 2026-10-12, P2 item 1) -----------------------
#
# Every count must be `len()` of a string the pipeline actually sends: plain full DDL is
# what RAG off sends (`get_schema`), full DDL plus value hints is what RAG on sends with
# `top_k=0`, and the sent text is `schema_text`. The strings below are written out by hand
# rather than rebuilt with the code under test.


def _write_db(path: Path, statements: list[str]) -> str:
    with closing(sqlite3.connect(path)) as conn:
        for statement in statements:
            conn.execute(statement)
        conn.commit()
    return str(path)


@pytest.fixture
def one_table_with_hints_db(tmp_path: Path) -> str:
    """Codex's reproduction: one text column whose two values become value hints."""
    return _write_db(
        tmp_path / "one.db",
        [
            "CREATE TABLE t (status TEXT)",
            "INSERT INTO t VALUES ('active')",
            "INSERT INTO t VALUES ('inactive')",
        ],
    )


@pytest.fixture
def two_tables_with_hints_db(tmp_path: Path) -> str:
    """Two unrelated tables, each with value hints, so `top_k=1` keeps only one."""
    return _write_db(
        tmp_path / "two.db",
        [
            "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, status TEXT)",
            "CREATE TABLE courses (course_id INTEGER PRIMARY KEY, course_name TEXT)",
            "INSERT INTO orders VALUES (1, 'awaiting_payment')",
            "INSERT INTO orders VALUES (2, 'cancelled_by_customer')",
            "INSERT INTO orders VALUES (3, 'delivered')",
            "INSERT INTO orders VALUES (4, 'pending')",
            "INSERT INTO courses VALUES (1, 'Algebra')",
            "INSERT INTO courses VALUES (2, 'Biology')",
        ],
    )


def test_one_table_with_hints_reports_growth_against_plain_ddl(
    one_table_with_hints_db: str,
) -> None:
    plain = "CREATE TABLE t (status TEXT);"
    sent = plain + "\n\n-- status sample values: active, inactive"
    assert (len(plain), len(sent)) == (29, 72)

    context = agent.retrieve_schema_context(one_table_with_hints_db, "status", top_k=6)

    assert agent.get_schema(one_table_with_hints_db) == plain
    assert context.schema_text == sent
    assert context.plain_ddl_chars == 29
    assert context.sent_schema_chars == 72
    assert context.ddl_with_hints_chars == 72
    assert context.change_vs_plain_ddl_chars == 43
    assert context.change_vs_plain_ddl_pct == 148.3
    assert context.change_vs_ddl_with_hints_chars == 0
    assert context.change_vs_ddl_with_hints_pct == 0.0


def test_the_old_clamped_savings_figure_is_gone(one_table_with_hints_db: str) -> None:
    context = agent.retrieve_schema_context(one_table_with_hints_db, "status", top_k=6)

    for removed in (
        "prompt_savings_pct",
        "full_schema_chars",
        "retrieved_schema_chars",
    ):
        assert not hasattr(context, removed), removed


def test_selection_shrinks_against_ddl_with_hints_but_grows_against_plain_ddl(
    two_tables_with_hints_db: str,
) -> None:
    orders_ddl = "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, status TEXT);"
    courses_ddl = "CREATE TABLE courses (course_id INTEGER PRIMARY KEY, course_name TEXT);"
    orders_hints = (
        "-- status sample values: awaiting_payment, cancelled_by_customer, delivered, pending"
    )
    courses_hints = "-- course_name sample values: Algebra, Biology"
    plain = f"{courses_ddl}\n\n{orders_ddl}"
    with_hints = f"{courses_ddl}\n\n{courses_hints}\n\n{orders_ddl}\n\n{orders_hints}"
    sent = f"{orders_ddl}\n\n{orders_hints}"

    context = agent.retrieve_schema_context(two_tables_with_hints_db, "order status", top_k=1)

    assert [chunk.table_name for chunk in context.chunks] == ["orders"]
    assert agent.get_schema(two_tables_with_hints_db) == plain
    assert context.schema_text == sent
    assert context.plain_ddl_chars == len(plain)
    assert context.ddl_with_hints_chars == len(with_hints)
    assert context.sent_schema_chars == len(sent)
    # Table selection saves characters against everything RAG could have sent ...
    assert context.change_vs_ddl_with_hints_chars == len(sent) - len(with_hints) < 0
    assert context.change_vs_ddl_with_hints_pct == round(
        (len(sent) - len(with_hints)) / len(with_hints) * 100, 1
    )
    # ... yet still sends more than RAG off does, because the hints outweigh the table cut.
    assert context.change_vs_plain_ddl_chars == len(sent) - len(plain) > 0
    assert context.change_vs_plain_ddl_pct == round((len(sent) - len(plain)) / len(plain) * 100, 1)


def test_top_k_zero_sends_exactly_full_ddl_plus_hints(two_tables_with_hints_db: str) -> None:
    context = agent.retrieve_schema_context(two_tables_with_hints_db, "anything", top_k=0)

    assert context.sent_schema_chars == len(context.schema_text)
    assert context.sent_schema_chars == context.ddl_with_hints_chars
    assert context.change_vs_ddl_with_hints_chars == 0
    assert context.change_vs_ddl_with_hints_pct == 0.0
    assert context.plain_ddl_chars == len(agent.get_schema(two_tables_with_hints_db))


def test_without_hints_plain_ddl_equals_ddl_with_hints(customers_sales_courses_db: str) -> None:
    context = agent.retrieve_schema_context(customers_sales_courses_db, "sales", top_k=0)

    assert all(not chunk.value_hints for chunk in context.chunks)
    assert context.schema_text == agent.get_schema(customers_sales_courses_db)
    assert context.plain_ddl_chars == context.ddl_with_hints_chars == context.sent_schema_chars


def test_report_names_its_units_and_both_baselines(one_table_with_hints_db: str) -> None:
    report = agent.retrieve_schema_context(one_table_with_hints_db, "status", top_k=6).report

    assert "characters of schema text, not provider tokens" in report
    assert "sent: 72 chars" in report
    assert "plain full DDL, what RAG off sends: 29 chars; change +43 chars (+148.3%)" in report
    assert "full DDL plus value hints, all tables: 72 chars; change +0 chars (+0.0%)" in report
    assert "saved=" not in report


def test_percent_changes_are_undefined_against_an_empty_baseline() -> None:
    empty = SchemaRetrievalResult(chunks=[], query_tokens=[], expanded_tokens=[], top_k=3)

    assert empty.sent_schema_chars == 0
    assert empty.change_vs_plain_ddl_chars == 0
    assert empty.change_vs_plain_ddl_pct is None
    assert empty.change_vs_ddl_with_hints_pct is None


def _status_db(tmp_path: Path) -> str:
    """`status` has 8 non-blank values, most frequent first, and a frequent blank one."""
    db = tmp_path / "statuses.db"
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE t (status TEXT)")
        rows = [(f"s{i}",) for i in range(8) for _ in range(20 - i)] + [("  ",)] * 15
        conn.executemany("INSERT INTO t VALUES (?)", rows)
        conn.commit()
    return str(db)


def test_a_cut_hint_list_says_how_many_values_it_shows(tmp_path: Path) -> None:
    context = agent.retrieve_schema_context(_status_db(tmp_path), "status", top_k=6)

    # The blank value ranks among the six most frequent and is dropped, as before, so five
    # values are shown of the column's eight non-blank ones.
    assert context.schema_text.endswith(
        "-- status sample values (5 of 8 shown): s0, s1, s2, s3, s4"
    )
    assert context.chunks[0].value_hint_totals == {"status": 8}


def test_a_complete_hint_list_renders_without_a_label() -> None:
    chunk = agent.SchemaChunk(
        table_name="t",
        ddl="CREATE TABLE t (status TEXT);",
        columns=["status"],
        foreign_tables=[],
        search_text="t status",
        value_hints={"status": ["active", "inactive"], "kind": ["a"]},
        value_hint_totals={"status": 2},
    )

    assert render_schema_text([chunk]).splitlines()[-2:] == [
        "-- kind sample values: a",
        "-- status sample values: active, inactive",
    ]


def test_the_scoring_index_is_cached_between_questions(customers_sales_courses_db: str) -> None:
    """A second question on the same schema must not re-index every chunk."""
    agent.retrieve_schema_context(customers_sales_courses_db, "total sales by customer", top_k=1)
    before = rag.get_retrieval_index_cache_info()
    agent.retrieve_schema_context(customers_sales_courses_db, "how many courses", top_k=1)
    after = rag.get_retrieval_index_cache_info()

    assert after.hits == before.hits + 1, "the second question must hit the index cache"
    assert after.misses == before.misses


def test_the_scoring_index_misses_after_the_schema_changes(tmp_path: Path) -> None:
    """The index shares the chunks' fingerprint key, so a new table is scored at once."""
    db = tmp_path / "c.db"
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE customers (id INTEGER, name TEXT)")
        conn.commit()
    agent.retrieve_schema_context(str(db), "customer name", top_k=1)
    before = rag.get_retrieval_index_cache_info()

    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE invoices (id INTEGER, amount REAL, customer_id INTEGER)")
        conn.commit()
    context = agent.retrieve_schema_context(str(db), "invoice amount", top_k=1)
    after = rag.get_retrieval_index_cache_info()

    assert after.misses == before.misses + 1, "a changed schema must rebuild the index"
    assert [chunk.table_name for chunk in context.chunks] == ["invoices"]


# --- Question value matching (2026-10-19, off by default) ------------------------------
#
# On `bird_train_large` half the literals gold SQL filters on sit in text columns with more
# than 20 distinct values, which never get a value hint. Value matching lists the stored
# values a question names, from any text column of the tables the prompt carries.


def _teams_db(tmp_path: Path) -> str:
    return _write_db(
        tmp_path / "teams.db",
        [
            "CREATE TABLE teams (team_id INTEGER PRIMARY KEY, name TEXT, city TEXT)",
            "CREATE TABLE players (player_id INTEGER PRIMARY KEY, last_name TEXT, "
            "team_id INTEGER REFERENCES teams(team_id))",
            "CREATE TABLE venues (venue_id INTEGER PRIMARY KEY, venue_name TEXT)",
            "INSERT INTO teams VALUES (1, 'St. Louis Blues', 'St. Louis'), "
            "(2, 'Montreal Canadiens', 'Montréal')",
            "INSERT INTO players VALUES (1, 'Hall', 1), (2, 'Louis', 2), (3, 'O''Neil', 1)",
            "INSERT INTO venues VALUES (1, 'Blues Arena')",
        ],
    )


def test_value_matching_is_off_by_default_and_leaves_the_text_unchanged(tmp_path: Path) -> None:
    db = _teams_db(tmp_path)
    question = "How many players did the St. Louis Blues have?"

    default = rag.retrieve_schema_context(db, question, top_k=0)
    on = rag.retrieve_schema_context(db, question, top_k=0, value_matches=True)

    assert default.value_matches == ()
    assert "Stored values" not in default.schema_text
    assert on.schema_text.startswith(render_schema_text(default.chunks))


def test_the_longest_phrase_wins_and_its_parts_are_not_matched_again(tmp_path: Path) -> None:
    db = _teams_db(tmp_path)

    result = rag.retrieve_schema_context(
        db, "How many players did the St. Louis Blues have?", top_k=0, value_matches=True
    )

    assert result.value_matches == (
        agent.types.ValueMatch(table="teams", column="name", values=("St. Louis Blues",)),
    )
    assert result.schema_text.endswith(
        "-- Stored values that match words in the question:\n-- teams.name: 'St. Louis Blues'"
    )


def test_accents_fold_and_quotes_are_escaped_in_the_literal(tmp_path: Path) -> None:
    db = _teams_db(tmp_path)

    result = rag.retrieve_schema_context(
        db, "Which team is from Montreal, and who is O'Neil?", top_k=0, value_matches=True
    )

    rendered = result.schema_text
    assert "-- teams.city: 'Montréal'" in rendered
    assert "-- players.last_name: 'O''Neil'" in rendered


def test_a_lone_ordinary_word_does_not_match_a_stored_name(tmp_path: Path) -> None:
    db = _teams_db(tmp_path)

    lower = rag.retrieve_schema_context(
        db, "who entered the hall first", top_k=0, value_matches=True
    )
    capital = rag.retrieve_schema_context(
        db, "Is there a player named Hall", top_k=0, value_matches=True
    )

    assert lower.value_matches == ()
    assert [m.values for m in capital.value_matches] == [("Hall",)]


def test_only_tables_the_prompt_carries_are_matched() -> None:
    index = {
        "blues arena": (("venues", "venue_name", "Blues Arena"),),
        "louis": (("players", "last_name", "Louis"),),
    }

    matches = rag.match_question_values(index, "Games at Blues Arena with Louis", {"players"})

    assert matches == (agent.types.ValueMatch("players", "last_name", ("Louis",)),)


def test_matches_are_capped_per_phrase_and_in_all() -> None:
    index = {"smith": tuple((f"t{i}", "name", "Smith") for i in range(6))}
    tables = {f"t{i}" for i in range(6)}

    per_phrase = rag.match_question_values(index, "Find Smith", tables, columns_per_phrase=4)
    capped = rag.match_question_values(index, "Find Smith", tables, limit=2)

    assert [m.table for m in per_phrase] == ["t0", "t1", "t2", "t3"]
    assert sum(len(m.values) for m in capped) == 2
