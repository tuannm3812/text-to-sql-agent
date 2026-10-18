"""Hybrid schema retrieval: BM25, char-ngram, and embedding scoring with a graph boost."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from hashlib import blake2b
from typing import TYPE_CHECKING

from .config import (
    DEFAULT_RAG_EMBEDDING_WEIGHT,
    DEFAULT_RAG_NEIGHBORS,
    DEFAULT_RAG_SEMANTIC_WEIGHT,
    DEFAULT_RAG_TOP_K,
    RAG_SYNONYMS,
    STOPWORDS,
)
from .schema import (
    get_schema_chunk_cache_info,
    get_schema_chunks_at,
    get_schema_chunks_plain_ddl_and_version,
)
from .types import SchemaChunk, SchemaRetrievalResult, render_schema_text

if TYPE_CHECKING:
    from functools import _CacheInfo


def _tokenize_for_rag(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    expanded: list[str] = []
    for token in tokens:
        if token not in STOPWORDS:
            expanded.append(token)
        for part in token.split("_"):
            if part and part not in STOPWORDS:
                expanded.append(part)
    return expanded


def _expand_query_tokens(tokens: list[str]) -> list[str]:
    expanded = list(tokens)
    for token in tokens:
        expanded.extend(RAG_SYNONYMS.get(token, []))
    return expanded


def _char_ngrams(text: str, *, n: int = 3) -> Counter[str]:
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    compact = f" {normalized} "
    if len(compact) <= n:
        return Counter([compact])
    return Counter(compact[i : i + n] for i in range(len(compact) - n + 1))


def _cosine_counter_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _hashed_embedding(text: str, *, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    tokens = _tokenize_for_rag(text)
    tokens.extend(_char_ngrams(text).keys())
    for token in tokens:
        digest = blake2b(token.encode("utf-8"), digest_size=4).digest()
        raw = int.from_bytes(digest, "little")
        index = raw % dimensions
        sign = 1.0 if raw & 1 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def _cosine_vector_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=False))


@dataclass(frozen=True)
class _ChunkIndex:
    """What scoring one chunk needs that does not depend on the question."""

    token_counts: Counter[str]
    doc_len: int
    table_tokens: frozenset[str]
    column_tokens: frozenset[str]
    text_tokens: frozenset[str]
    ngrams: Counter[str]
    embedding: list[float]


@dataclass(frozen=True)
class _CorpusIndex:
    """The question-independent half of scoring, one entry per chunk in chunk order."""

    entries: tuple[_ChunkIndex, ...]
    doc_freq: Counter[str]
    avg_doc_len: float


@lru_cache(maxsize=32)
def _cached_corpus_index(version: tuple[object, ...]) -> _CorpusIndex:
    """Build the scoring index for one schema version, cached on the chunks' own key.

    Before 2026-10-19 every question re-tokenised, re-counted n-grams and re-hashed the
    embedding of every chunk in the database. None of that depends on the question, so
    it is computed once per `(dsn, fingerprint)` here and reused until the schema
    changes - the same key and the same invalidation as `schema._cached_schema_chunks`.
    Each value is built by exactly the call the per-question loop used to make, so the
    scores, ranks and prompt bytes are unchanged (checked on every question of the
    three committed suites; see `docs/6_agent_log.md`).
    """
    chunks = get_schema_chunks_at(version)
    doc_tokens = [_tokenize_for_rag(chunk.search_text) for chunk in chunks]
    doc_lengths = [len(tokens) or 1 for tokens in doc_tokens]
    avg_doc_len = sum(doc_lengths) / len(doc_lengths)
    doc_freq: Counter[str] = Counter()
    for tokens in doc_tokens:
        doc_freq.update(set(tokens))
    entries = tuple(
        _ChunkIndex(
            token_counts=Counter(tokens),
            doc_len=doc_len,
            table_tokens=frozenset(_tokenize_for_rag(chunk.table_name)),
            column_tokens=frozenset(_tokenize_for_rag(" ".join(chunk.columns))),
            text_tokens=frozenset(tokens),
            ngrams=_char_ngrams(chunk.search_text),
            embedding=_hashed_embedding(chunk.search_text),
        )
        for chunk, tokens, doc_len in zip(chunks, doc_tokens, doc_lengths, strict=True)
    )
    return _CorpusIndex(entries=entries, doc_freq=doc_freq, avg_doc_len=avg_doc_len)


def get_retrieval_index_cache_info() -> _CacheInfo:
    """Return `lru_cache` hit/miss statistics for the scoring index cache."""
    return _cached_corpus_index.cache_info()


def decompose_question(question: str) -> dict[str, list[str]]:
    """Break a question into entities, aggregations, filters, and comparisons.

    A lightweight, keyword-based decomposition used both for schema-retrieval
    scoring and for the retrieval report shown in the UI.

    Args:
        question: The user's natural-language question.

    Returns:
        A dict with keys `"entities_or_metrics"`, `"aggregations"`,
        `"filters_or_dimensions"`, and `"comparisons"`, each a sorted list of
        matched tokens (empty if none matched).
    """
    tokens = _tokenize_for_rag(question)
    aggregations = []
    if any(token in tokens for token in ("count", "many", "number")):
        aggregations.append("count")
    if any(token in tokens for token in ("average", "avg", "mean")):
        aggregations.append("average")
    if any(token in tokens for token in ("sum", "total", "revenue", "sales")):
        aggregations.append("sum")
    if any(token in tokens for token in ("highest", "top", "most", "best")):
        aggregations.append("top")
    if any(token in tokens for token in ("lowest", "least", "bottom")):
        aggregations.append("bottom")

    filters = [
        token
        for token in tokens
        if token
        in {
            "completed",
            "cancelled",
            "pending",
            "region",
            "city",
            "status",
            "grade",
            "priority",
            "category",
        }
    ]
    comparison = [
        token
        for token in tokens
        if token in {"than", "versus", "vs", "compare", "difference", "higher", "lower"}
    ]
    return {
        "entities_or_metrics": sorted(set(tokens)),
        "aggregations": sorted(set(aggregations)),
        "filters_or_dimensions": sorted(set(filters)),
        "comparisons": sorted(set(comparison)),
    }


def retrieve_schema_chunks(
    db_path: str,
    question: str,
    *,
    top_k: int = DEFAULT_RAG_TOP_K,
    include_neighbors: int = DEFAULT_RAG_NEIGHBORS,
) -> list[SchemaChunk]:
    """Return the schema chunks selected by `retrieve_schema_context`.

    Args:
        db_path: Filesystem path to the SQLite database.
        question: The user's natural-language question.
        top_k: Maximum number of top-scored chunks to select before
            neighbor expansion.
        include_neighbors: Number of foreign-key hops to expand the
            selection by.

    Returns:
        The retrieved `SchemaChunk`s, most relevant first. See
        `retrieve_schema_context` for the full retrieval result.
    """
    return retrieve_schema_context(
        db_path,
        question,
        top_k=top_k,
        include_neighbors=include_neighbors,
    ).chunks


def retrieve_schema_context(
    db_path: str,
    question: str,
    *,
    top_k: int = DEFAULT_RAG_TOP_K,
    include_neighbors: int = DEFAULT_RAG_NEIGHBORS,
    semantic_weight: float = DEFAULT_RAG_SEMANTIC_WEIGHT,
    embedding_weight: float = DEFAULT_RAG_EMBEDDING_WEIGHT,
) -> SchemaRetrievalResult:
    """Score and select the schema chunks most relevant to a question.

    Combines BM25-style lexical scoring, table/column name matches, a
    char-ngram cosine similarity, and a hashed-embedding cosine similarity,
    then expands the top-scored chunks with their foreign-key neighbors.

    Args:
        db_path: Filesystem path to the SQLite database.
        question: The user's natural-language question.
        top_k: Maximum number of top-scored chunks to select before
            neighbor expansion. `0` or negative returns all chunks unscored.
        include_neighbors: Number of foreign-key hops to expand the
            selection by, adding each unselected neighbor at most once.
        semantic_weight: Weight applied to the char-ngram similarity score.
        embedding_weight: Weight applied to the hashed-embedding similarity
            score.

    Returns:
        A `SchemaRetrievalResult` with the selected chunks, the tokens
        derived from the question, and retrieval statistics.
    """
    before_cache = get_schema_chunk_cache_info()
    chunks, plain_ddl, version = get_schema_chunks_plain_ddl_and_version(db_path)
    after_cache = get_schema_chunk_cache_info()
    cache_hit = after_cache.hits > before_cache.hits
    query_tokens = _tokenize_for_rag(question)
    expanded_tokens = _expand_query_tokens(query_tokens)
    decomposed_terms = decompose_question(question)
    # Both baselines are `len()` of a string a pipeline path really sends: plain full
    # DDL is the RAG-off prompt's schema text, and the full rendering is RAG on with
    # `top_k <= 0`. The sent size is `len(result.schema_text)` itself.
    plain_ddl_chars = len(plain_ddl)
    ddl_with_hints_chars = len(render_schema_text(chunks))

    if not chunks:
        return SchemaRetrievalResult(
            [],
            query_tokens,
            expanded_tokens,
            top_k,
            decomposed_terms=decomposed_terms,
            plain_ddl_chars=plain_ddl_chars,
            ddl_with_hints_chars=ddl_with_hints_chars,
            cache_hit=cache_hit,
        )
    if top_k <= 0:
        return SchemaRetrievalResult(
            chunks,
            query_tokens,
            expanded_tokens,
            top_k,
            decomposed_terms=decomposed_terms,
            plain_ddl_chars=plain_ddl_chars,
            ddl_with_hints_chars=ddl_with_hints_chars,
            cache_hit=cache_hit,
        )

    index = _cached_corpus_index(version)
    doc_freq = index.doc_freq
    avg_doc_len = index.avg_doc_len
    query_ngrams = _char_ngrams(" ".join(expanded_tokens) or question)

    query_counter = Counter(expanded_tokens)
    query_embedding = _hashed_embedding(" ".join(expanded_tokens) or question)
    scored: list[SchemaChunk] = []
    for chunk, entry in zip(chunks, index.entries, strict=True):
        token_counts = entry.token_counts
        doc_len = entry.doc_len

        score = 0.0
        matched_terms: set[str] = set()
        reasons: list[str] = []

        for token, query_weight in query_counter.items():
            if token not in token_counts:
                continue
            matched_terms.add(token)
            idf = math.log(1 + (len(chunks) - doc_freq[token] + 0.5) / (doc_freq[token] + 0.5))
            tf = token_counts[token]
            denominator = tf + 1.5 * (1 - 0.75 + 0.75 * doc_len / avg_doc_len)
            score += idf * ((tf * 2.5) / denominator) * max(1, query_weight)

        table_matches = sorted(set(expanded_tokens) & entry.table_tokens)
        column_matches = sorted(set(expanded_tokens) & entry.column_tokens)
        weak_matches = sorted(set(expanded_tokens) & entry.text_tokens)
        if table_matches:
            score += 8.0 * len(table_matches)
            reasons.append(f"table match: {', '.join(table_matches)}")
            matched_terms.update(table_matches)
        if column_matches:
            score += 4.0 * len(column_matches)
            reasons.append(f"column match: {', '.join(column_matches)}")
            matched_terms.update(column_matches)
        if weak_matches and not (table_matches or column_matches):
            reasons.append(f"schema text match: {', '.join(weak_matches[:6])}")

        semantic_score = _cosine_counter_similarity(query_ngrams, entry.ngrams)
        if semantic_score > 0:
            score += semantic_weight * semantic_score
            reasons.append(f"semantic similarity: {semantic_score:.2f}")

        embedding_score = _cosine_vector_similarity(query_embedding, entry.embedding)
        if embedding_score > 0:
            score += embedding_weight * embedding_score
            reasons.append(f"embedding similarity: {embedding_score:.2f}")

        scored.append(
            SchemaChunk(
                table_name=chunk.table_name,
                ddl=chunk.ddl,
                columns=chunk.columns,
                foreign_tables=chunk.foreign_tables,
                search_text=chunk.search_text,
                # Phase 3b Task 6: a rescored copy must keep the identity of
                # the chunk it copies. Dropping `schema_name` here would give
                # a table outside the engine's default schema the identity of
                # a same-named table inside it.
                schema_name=chunk.schema_name,
                home_schema=chunk.home_schema,
                value_hints=chunk.value_hints,
                value_hint_totals=chunk.value_hint_totals,
                score=score,
                matched_terms=sorted(matched_terms),
                match_reasons=reasons,
            )
        )

    selected = sorted(scored, key=lambda c: (-c.score, c.table_name))[:top_k]
    if all(chunk.score == 0 for chunk in selected):
        selected = sorted(scored, key=lambda c: c.table_name)[:top_k]

    # Keyed by `qualified_name`, not `table_name`, for the same reason
    # `foreign_tables` now holds qualified names (Phase 3b Task 6): two
    # schemas may hold a table of the same name, and a bare-name key would
    # make one chunk's foreign-key edges resolve to the other's chunk. For a
    # single-schema database the two keys are the same string, so this is a
    # no-op there.
    selected_names = {chunk.qualified_name for chunk in selected}
    if include_neighbors > 0:
        chunk_by_name = {chunk.qualified_name: chunk for chunk in scored}
        frontier = list(selected)
        for depth in range(include_neighbors):
            next_frontier: list[SchemaChunk] = []
            for chunk in frontier:
                for neighbor in chunk.foreign_tables:
                    if neighbor in chunk_by_name and neighbor not in selected_names:
                        selected_names.add(neighbor)
                        neighbor_chunk = chunk_by_name[neighbor]
                        next_frontier.append(
                            SchemaChunk(
                                table_name=neighbor_chunk.table_name,
                                ddl=neighbor_chunk.ddl,
                                columns=neighbor_chunk.columns,
                                foreign_tables=neighbor_chunk.foreign_tables,
                                search_text=neighbor_chunk.search_text,
                                schema_name=neighbor_chunk.schema_name,
                                home_schema=neighbor_chunk.home_schema,
                                value_hints=neighbor_chunk.value_hints,
                                value_hint_totals=neighbor_chunk.value_hint_totals,
                                score=max(neighbor_chunk.score, chunk.score * (0.35 / (depth + 1))),
                                matched_terms=neighbor_chunk.matched_terms or [],
                                match_reasons=[
                                    *(neighbor_chunk.match_reasons or []),
                                    f"foreign-key neighbor of {chunk.table_name}",
                                ],
                            )
                        )
            selected.extend(next_frontier)
            frontier = next_frontier

    selected = sorted(selected, key=lambda c: (-c.score, c.table_name))
    return SchemaRetrievalResult(
        selected,
        query_tokens,
        expanded_tokens,
        top_k,
        decomposed_terms=decomposed_terms,
        plain_ddl_chars=plain_ddl_chars,
        ddl_with_hints_chars=ddl_with_hints_chars,
        cache_hit=cache_hit,
    )


def retrieve_relevant_schema(
    db_path: str,
    question: str,
    *,
    top_k: int = DEFAULT_RAG_TOP_K,
) -> str:
    """Return prompt-ready schema text for the chunks most relevant to a question.

    Args:
        db_path: Filesystem path to the SQLite database.
        question: The user's natural-language question.
        top_k: Maximum number of top-scored chunks to select; see
            `retrieve_schema_context`.

    Returns:
        DDL and value hints for the retrieved chunks, formatted for
        inclusion in an LLM prompt (see `SchemaRetrievalResult.schema_text`).
    """
    return retrieve_schema_context(db_path, question, top_k=top_k).schema_text
