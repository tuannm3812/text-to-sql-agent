from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

import text_to_sql_agent as agent
from text_to_sql_agent import schema
from text_to_sql_agent.types import SchemaChunk


def test_get_schema_excludes_internal_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()

    schema_sql = agent.get_schema(str(db_path))

    assert "CREATE TABLE customers" in schema_sql
    assert "sqlite_" not in schema_sql


def test_schema_chunks_are_cached_between_calls(tmp_path: Path) -> None:
    db = tmp_path / "c.db"
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE t (a INTEGER)")
        conn.commit()

    agent.get_schema_chunks(str(db))
    before = schema.get_schema_chunk_cache_info()
    agent.get_schema_chunks(str(db))
    after = schema.get_schema_chunk_cache_info()

    assert after.hits == before.hits + 1, "the second call must hit the cache"


def test_the_cache_misses_after_the_schema_changes(tmp_path: Path) -> None:
    """The fingerprint is what makes a stale chunk list impossible."""
    db = tmp_path / "c.db"
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE t (a INTEGER)")
        conn.commit()
    first = {c.table_name for c in agent.get_schema_chunks(str(db))}

    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE t2 (b INTEGER)")
        conn.commit()
    second = {c.table_name for c in agent.get_schema_chunks(str(db))}

    assert first == {"t"}
    assert second == {"t", "t2"}, "a schema change must invalidate the cache"


def test_identical_schemas_in_different_files_keep_separate_value_hints(
    tmp_path: Path,
) -> None:
    """Two SQLite files with the same DDL but different data must not share hints.

    This cannot actually fail for SQLite today: `SQLiteEngine.schema_fingerprint`
    embeds the resolved path (`(str(path), mtime_ns, size)`), so two different
    files always produce two different fingerprints regardless of whether the
    cache key includes the DSN. The test still documents the property the
    design point requires, and it is proven load-bearing by
    `test_a_path_free_fingerprint_would_collide_across_dsns_without_the_dsn_in_the_key`
    below, which uses a stand-in engine whose fingerprint omits the DSN — the
    situation Phase 3b's PostgreSQL catalogue-hash fingerprint will actually be
    in. That test genuinely fails if the cache is keyed on the fingerprint
    alone; this one cannot.
    """
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    for db, value in ((db_a, "north"), (db_b, "south")):
        with closing(sqlite3.connect(db)) as conn:
            conn.execute("CREATE TABLE region (name TEXT)")
            conn.execute("INSERT INTO region (name) VALUES (?)", (value,))
            conn.commit()

    chunks_a = {c.table_name: c for c in agent.get_schema_chunks(str(db_a))}
    chunks_b = {c.table_name: c for c in agent.get_schema_chunks(str(db_b))}

    assert chunks_a["region"].value_hints == {"name": ["north"]}
    assert chunks_b["region"].value_hints == {"name": ["south"]}


def test_a_path_free_fingerprint_would_collide_across_dsns_without_the_dsn_in_the_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Proves the DSN, not just the fingerprint, must be part of the cache key.

    A stand-in engine stands in for a future engine (e.g. Phase 3b's
    PostgreSQL adapter) whose `schema_fingerprint` is a hash of the catalogue
    rather than anything containing the DSN, so two differently-named
    databases with identical schemas produce the identical fingerprint. If
    `get_schema_chunks` cached on the fingerprint alone, the second DSN's
    call would return the first DSN's chunks — including its row-derived
    value hints. Keying on `(dsn, fingerprint)`, as `schema.py` does, keeps
    them apart.
    """

    class _StandInEngine:
        def __init__(self, dsn: str) -> None:
            self._dsn = dsn

        def schema_fingerprint(self) -> tuple[object, ...]:
            # Deliberately omits the DSN: every instance of this engine
            # reports the same fingerprint, however it was constructed.
            return ("same-catalogue-hash",)

        def schema_chunks(self) -> list[SchemaChunk]:
            return [
                SchemaChunk(
                    table_name="region",
                    ddl="CREATE TABLE region (name TEXT);",
                    columns=["name"],
                    foreign_tables=[],
                    search_text="region name",
                    value_hints={"name": [self._dsn]},
                )
            ]

    monkeypatch.setattr(schema, "open_engine", lambda dsn: _StandInEngine(dsn))
    schema._cached_schema_chunks.cache_clear()

    chunks_a = agent.get_schema_chunks("db-a")
    chunks_b = agent.get_schema_chunks("db-b")

    assert chunks_a[0].value_hints == {"name": ["db-a"]}
    assert chunks_b[0].value_hints == {"name": ["db-b"]}, (
        "a fingerprint-only cache key would have returned db-a's value hints for db-b"
    )


def test_plain_ddl_for_prompt_sizing_is_cached_with_the_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Measuring the RAG-off baseline must not cost each question a catalogue query.

    `retrieve_schema_context` reports the plain full DDL's size, so it needs
    `raw_schema()`. That read is cached on the chunks' own `(dsn, fingerprint)` key:
    repeated questions read it once, a schema change reads it again, and a second DSN
    with the same fingerprint gets its own DDL rather than the first one's.
    """
    calls: list[str] = []
    fingerprints = {"db-a": ("v1",), "db-b": ("v1",)}

    class _CountingEngine:
        def __init__(self, dsn: str) -> None:
            self._dsn = dsn

        def schema_fingerprint(self) -> tuple[object, ...]:
            return fingerprints[self._dsn]

        def schema_chunks(self) -> list[SchemaChunk]:
            return [
                SchemaChunk(
                    table_name="t",
                    ddl="CREATE TABLE t (a TEXT);",
                    columns=["a"],
                    foreign_tables=[],
                    search_text="t a",
                )
            ]

        def raw_schema(self) -> str:
            calls.append(self._dsn)
            return f"CREATE TABLE t (a TEXT); -- {self._dsn} {fingerprints[self._dsn][0]}"

    monkeypatch.setattr(schema, "open_engine", lambda dsn: _CountingEngine(dsn))
    schema._cached_schema_chunks.cache_clear()
    schema._cached_raw_schema.cache_clear()

    first = agent.retrieve_schema_context("db-a", "a", top_k=6)
    second = agent.retrieve_schema_context("db-a", "a", top_k=6)
    assert calls == ["db-a"], "the second question must reuse the cached DDL"
    assert (
        first.plain_ddl_chars
        == second.plain_ddl_chars
        == len("CREATE TABLE t (a TEXT); -- db-a v1")
    )

    other = agent.retrieve_schema_context("db-b", "a", top_k=6)
    assert calls == ["db-a", "db-b"], "a different DSN must not share a cache entry"
    assert other.plain_ddl_chars == len("CREATE TABLE t (a TEXT); -- db-b v1")

    fingerprints["db-a"] = ("v2",)
    agent.retrieve_schema_context("db-a", "a", top_k=6)
    assert calls == ["db-a", "db-b", "db-a"], "a schema change must invalidate the DDL"
