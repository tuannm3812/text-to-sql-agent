"""Schema extraction: raw DDL and cached, retrieval-ready schema chunks.

Both entry points delegate to the `Engine` resolved from the DSN by
`open_engine` - SQLite, DuckDB or PostgreSQL, by DSN scheme.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from .engines import open_engine
from .types import SchemaChunk

if TYPE_CHECKING:
    from functools import _CacheInfo


def get_schema(db_path: str) -> str:
    """Extract CREATE TABLE statements for all user tables.

    Args:
        db_path: Filesystem path (or DSN) to the database.

    Returns:
        The `CREATE TABLE` statements, one per table, semicolon-terminated
        and separated by blank lines, in table-name order.
    """
    return open_engine(db_path).raw_schema()


@lru_cache(maxsize=32)
def _cached_schema_chunks(dsn: str, _fingerprint: tuple[object, ...]) -> tuple[SchemaChunk, ...]:
    return tuple(open_engine(dsn).schema_chunks())


def get_schema_chunks(db_path: str) -> list[SchemaChunk]:
    """Return cached table-level schema chunks for retrieval.

    Results are cached by `(dsn, engine.schema_fingerprint())` via
    `lru_cache`, so the cache is invalidated automatically whenever the
    database's schema changes. The DSN is part of the key, not just the
    fingerprint: a fingerprint only promises to change when its own
    database's schema changes, not to be unique across databases, so two
    different databases could otherwise collide on one cache entry and leak
    one database's row-derived value hints into another's prompt.

    Args:
        db_path: Filesystem path (or DSN) to the database.

    Returns:
        One `SchemaChunk` per user table, each carrying its DDL, columns,
        foreign-table names, and sample value hints.
    """
    fingerprint = open_engine(db_path).schema_fingerprint()
    return list(_cached_schema_chunks(db_path, fingerprint))


@lru_cache(maxsize=32)
def _cached_raw_schema(dsn: str, _fingerprint: tuple[object, ...]) -> str:
    return open_engine(dsn).raw_schema()


def get_schema_chunks_and_plain_ddl(db_path: str) -> tuple[list[SchemaChunk], str]:
    """Return `get_schema_chunks(db_path)` and `get_schema(db_path)`, both cached.

    Retrieval needs plain full DDL only to measure what the RAG-off path would have
    sent. Both values are cached on the same `(dsn, engine.schema_fingerprint())`
    key, read from a single fingerprint, so measuring that baseline costs a question
    no catalogue query beyond the one it already made: the DDL is read once per
    schema version, exactly as the chunks are. `get_schema` itself stays uncached,
    so the RAG-off path is unchanged.

    Args:
        db_path: Filesystem path (or DSN) to the database.

    Returns:
        `(chunks, plain_ddl)`, where `plain_ddl` is the string `get_schema` returns.
    """
    fingerprint = open_engine(db_path).schema_fingerprint()
    return (
        list(_cached_schema_chunks(db_path, fingerprint)),
        _cached_raw_schema(db_path, fingerprint),
    )


def get_schema_chunk_cache_info() -> _CacheInfo:
    """Return `lru_cache` hit/miss statistics for the schema chunk cache."""
    return _cached_schema_chunks.cache_info()
