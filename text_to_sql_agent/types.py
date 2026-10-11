"""Dataclasses shared across the agent package: query results and schema retrieval."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueryResult:
    """The outcome of executing (or attempting to execute) a SQL query.

    Attributes:
        columns: Result-set column names, in order. Empty if no rows.
        rows: Result-set rows, each a tuple of column values.
        sql: The SQL text that was executed, when execution was attempted.
        error: A machine-readable error code or message, or `None` on
            success. See `execute_query` and `text_to_sql_agent.pipeline` for
            the specific values used.
    """

    columns: list[str]
    rows: list[tuple[Any, ...]]
    sql: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        """Whether the query completed without an error."""
        return self.error is None


@dataclass(frozen=True)
class SchemaChunk:
    """A single table's schema, plus retrieval metadata for RAG scoring.

    Attributes:
        table_name: The table's name, bare.
        ddl: Its `CREATE TABLE` statement.
        columns: Column names.
        foreign_tables: Names of tables referenced by foreign keys, spelled
            the same way `qualified_name` spells this one - bare for a table
            in the engine's default schema, `schema.table` otherwise - so a
            foreign-key edge and a chunk's own identity are the same kind of
            key (`rag.py`'s neighbour graph joins on exactly that).
        search_text: Concatenated text used for lexical/semantic scoring.
        schema_name: The schema this table lives in, **only when the table
            cannot be spelled bare** - outside the engine's default schema on
            SQLite/DuckDB, or (PostgreSQL, 2026-09-27) whenever the bare name
            does not resolve to this table on the role's search path; `""`
            otherwise. Empty is therefore both "spelled bare" and "no schema
            recorded", which is what lets it default and keeps every
            pre-Phase-3b construction (and `rag.py`, Phase 4's file) correct
            unchanged. The engine that built the chunk is the one that knows
            how its own bare names resolve, so it decides before setting this.
        home_schema: For a chunk spelled bare (`schema_name == ""`), the schema
            it actually lives in, when that is not simply the engine's
            `default_schema`; `""` otherwise. Only PostgreSQL sets it: its bare
            names resolve across the whole search path (2026-09-27), so a bare
            table may live in any path schema, and `engines/base.py::
            table_name_spellings` needs the real one to build the table's
            qualified spelling. SQLite and DuckDB leave it empty, meaning
            `default_schema`, exactly as before.
        value_hints: Sample distinct values per low-cardinality text column.
        score: Relevance score assigned during retrieval; `0.0` until scored.
        matched_terms: Query terms that matched this chunk, once scored.
        match_reasons: Human-readable explanations of why this chunk matched.
    """

    table_name: str
    ddl: str
    columns: list[str]
    foreign_tables: list[str]
    search_text: str
    schema_name: str = ""
    home_schema: str = ""
    value_hints: dict[str, list[str]] | None = None
    score: float = 0.0
    matched_terms: list[str] | None = None
    match_reasons: list[str] | None = None

    @property
    def qualified_name(self) -> str:
        """`schema.table` outside the engine's default schema, else the bare name.

        This is exactly the spelling that is valid to write in SQL against the
        engine this chunk came from, and exactly the spelling that engine's
        `table_names()` advertises to `safety.is_safe_query` - one identity,
        not one per layer, which is what the 2026-09-25 decision
        (`docs/3_decisions.md`) found the three layers disagreeing about.
        """
        return f"{self.schema_name}.{self.table_name}" if self.schema_name else self.table_name


def render_schema_text(chunks: Sequence[SchemaChunk]) -> str:
    """Render chunks as the schema text a RAG-on prompt carries: DDL, then value hints.

    The single rendering behind `SchemaRetrievalResult.schema_text` and its
    `ddl_with_hints_chars` baseline, so a size and the text it measures cannot drift.
    This is what the model receives; changing a byte of it changes every RAG-on prompt.
    """
    parts: list[str] = []
    for chunk in chunks:
        parts.append(chunk.ddl)
        if chunk.value_hints:
            parts.append(
                "\n".join(
                    f"-- {column} sample values: {', '.join(values)}"
                    for column, values in sorted(chunk.value_hints.items())
                )
            )
    return "\n\n".join(parts)


def _signed_pct(change: int, baseline: int) -> float | None:
    """`change` as a percent of `baseline`, one decimal place; `None` for an empty baseline."""
    if baseline <= 0:
        return None
    return round(change / baseline * 100, 1)


def _size_change(baseline: int, change: int) -> str:
    """`"<baseline> chars; change <+n> chars (<+p>%)"` for the retrieval report."""
    pct = _signed_pct(change, baseline)
    pct_text = "n/a" if pct is None else f"{pct:+.1f}%"
    return f"{baseline} chars; change {change:+d} chars ({pct_text})"


@dataclass(frozen=True)
class SchemaRetrievalResult:
    """The chunks retrieved for a question, plus the terms and stats behind them.

    Attributes:
        chunks: The selected `SchemaChunk`s, most relevant first.
        query_tokens: Tokens extracted from the question.
        expanded_tokens: `query_tokens` plus synonym expansions.
        top_k: The requested chunk limit that produced this result.
        decomposed_terms: The question broken into aggregations, filters,
            and comparisons, as returned by `decompose_question`.
        plain_ddl_chars: `len()` of plain full DDL, `schema.get_schema(dsn)` - exactly
            the schema text the RAG-off path sends.
        ddl_with_hints_chars: `len()` of `render_schema_text` over every chunk - full
            DDL plus value hints, exactly what RAG on sends with `top_k=0`.
        cache_hit: Whether the underlying schema-chunk cache was hit.
        strategy: Name of the retrieval strategy that produced this result.
    """

    chunks: list[SchemaChunk]
    query_tokens: list[str]
    expanded_tokens: list[str]
    top_k: int
    decomposed_terms: dict[str, list[str]] | None = None
    plain_ddl_chars: int = 0
    ddl_with_hints_chars: int = 0
    cache_hit: bool = False
    strategy: str = "hybrid-bm25-embedding-semantic-values-graph"

    @property
    def schema_text(self) -> str:
        """DDL and value hints for the retrieved chunks, formatted for a prompt."""
        return render_schema_text(self.chunks)

    @property
    def sent_schema_chars(self) -> int:
        """`len(schema_text)`: characters of schema text the RAG-on path sends."""
        return len(self.schema_text)

    @property
    def change_vs_plain_ddl_chars(self) -> int:
        """Signed change of the sent text against plain full DDL; positive is growth.

        This is the change from the shipped RAG-off path, which sends plain full DDL.
        """
        return self.sent_schema_chars - self.plain_ddl_chars

    @property
    def change_vs_plain_ddl_pct(self) -> float | None:
        """`change_vs_plain_ddl_chars` as a percent of plain full DDL; `None` if empty."""
        return _signed_pct(self.change_vs_plain_ddl_chars, self.plain_ddl_chars)

    @property
    def change_vs_ddl_with_hints_chars(self) -> int:
        """Signed change of the sent text against full DDL plus hints; positive is growth.

        Both sides carry value hints, so this isolates the effect of table selection.
        """
        return self.sent_schema_chars - self.ddl_with_hints_chars

    @property
    def change_vs_ddl_with_hints_pct(self) -> float | None:
        """`change_vs_ddl_with_hints_chars` as a percent of that baseline; `None` if empty."""
        return _signed_pct(self.change_vs_ddl_with_hints_chars, self.ddl_with_hints_chars)

    @property
    def report(self) -> str:
        """A human-readable summary of the retrieval: strategy, terms, and tables."""
        if not self.chunks:
            return "No schema chunks were retrieved."
        lines = [
            f"Schema RAG strategy: {self.strategy}",
            f"Query tokens: {', '.join(self.query_tokens) or '(none)'}",
            f"Expanded tokens: {', '.join(self.expanded_tokens) or '(none)'}",
            "Schema text size (characters of schema text, not provider tokens; "
            "a positive change is growth):",
            f"- sent: {self.sent_schema_chars} chars",
            "- vs plain full DDL, what RAG off sends: "
            + _size_change(self.plain_ddl_chars, self.change_vs_plain_ddl_chars),
            "- vs full DDL plus value hints, all tables: "
            + _size_change(self.ddl_with_hints_chars, self.change_vs_ddl_with_hints_chars)
            + "; isolates table selection",
            f"Cache hit: {self.cache_hit}",
            "",
            "Query decomposition:",
        ]
        for key, values in (self.decomposed_terms or {}).items():
            lines.append(f"- {key}: {', '.join(values) or '(none)'}")
        lines += [
            "",
            "Retrieved tables:",
        ]
        for chunk in self.chunks:
            terms = ", ".join(chunk.matched_terms or []) or "fallback"
            reasons = "; ".join(chunk.match_reasons or [])
            lines.append(f"- {chunk.qualified_name} (score={chunk.score:.2f}; terms={terms})")
            if reasons:
                lines.append(f"  {reasons}")
            if chunk.value_hints:
                for column, values in sorted(chunk.value_hints.items()):
                    lines.append(f"  value hints {column}: {', '.join(values)}")
        return "\n".join(lines)
