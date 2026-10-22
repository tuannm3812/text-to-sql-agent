"""Dense sentence embeddings for schema retrieval, from a local Ollama embedding model.

An optional signal beside the lexical ones in `rag` (`ScoringWeights.dense`). Each table
is embedded once per schema version as its name, its columns and its value-hint values,
with identifiers split into words (`SalesPerson` -> `sales person`); the question is
embedded per call. Ollama's `/api/embed` is called directly with the standard library, so
no dependency is added. When the server or the model is unavailable, every function
returns `None` and retrieval scores without this signal, as before (the hosted demo has
no Ollama). Nothing leaves the machine unless `OLLAMA_HOST` points elsewhere; the text
sent is the schema text the prompt already carries.
"""

from __future__ import annotations

import http.client
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from functools import lru_cache

from .config import DEFAULT_RAG_DENSE_MODEL
from .schema import get_schema_chunks_at
from .types import SchemaChunk

_TIMEOUT_SECONDS = 20
_BATCH = 64
_MAX_CHARS = 1000

Vector = tuple[float, ...]


def _host() -> str:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    return host if "://" in host else f"http://{host}"


def _words(identifier: str) -> str:
    """`SalesPerson` / `sales_person` -> `sales person`."""
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", identifier).replace("_", " ").lower()


def chunk_text(chunk: SchemaChunk) -> str:
    """What a table is embedded as: name, columns and value-hint values, as words."""
    values = " ".join(v for vals in (chunk.value_hints or {}).values() for v in vals)
    columns = ", ".join(_words(column) for column in chunk.columns)
    return f"{_words(chunk.table_name)}: {columns}. {values}"[:_MAX_CHARS]


class DenseUnavailable(Exception):
    """Ollama or the embedding model could not supply usable vectors."""


# After a failure, no request is made for this long: a dead server would otherwise cost a
# full timeout on every question. Then the next question tries again (Codex, 2026-10-22).
RETRY_AFTER_SECONDS = 30.0
_last_failure = -math.inf


def _vectors(payload: object, count: int) -> list[Vector]:
    """The validated `embeddings` of an `/api/embed` response, or `DenseUnavailable`."""
    if not isinstance(payload, dict):
        raise DenseUnavailable("response is not a JSON object")
    batch = payload.get("embeddings")
    if not isinstance(batch, list) or len(batch) != count:
        raise DenseUnavailable("response has no embedding per input")
    vectors: list[Vector] = []
    for vector in batch:
        if (
            not isinstance(vector, list)
            or not vector
            or not all(isinstance(x, int | float) and not isinstance(x, bool) for x in vector)
            or not all(math.isfinite(x) for x in vector)
        ):
            raise DenseUnavailable("an embedding is not a list of finite numbers")
        vectors.append(tuple(float(x) for x in vector))
    if len({len(v) for v in vectors}) > 1:
        raise DenseUnavailable("embeddings have different lengths")
    return vectors


def _embed_or_raise(texts: Sequence[str], model: str) -> list[Vector]:
    global _last_failure
    if time.monotonic() - _last_failure < RETRY_AFTER_SECONDS:
        raise DenseUnavailable("recent failure; waiting before the next attempt")
    vectors: list[Vector] = []
    try:
        for start in range(0, len(texts), _BATCH):
            batch = list(texts[start : start + _BATCH])
            request = urllib.request.Request(
                f"{_host()}/api/embed",
                data=json.dumps({"model": model, "input": batch}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
                    payload = json.loads(response.read())
            except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
                raise DenseUnavailable(f"{type(exc).__name__}: {exc}") from exc
            vectors.extend(_vectors(payload, len(batch)))
    except DenseUnavailable:
        _last_failure = time.monotonic()
        raise
    return vectors


def embed(texts: Sequence[str], model: str = DEFAULT_RAG_DENSE_MODEL) -> list[Vector] | None:
    """Embeddings for `texts` in order, or `None` if Ollama or the model is unavailable.

    Transport failures (refused, timed out, truncated) and malformed responses all give
    `None`; anything else is a bug and is raised.
    """
    try:
        return _embed_or_raise(texts, model)
    except DenseUnavailable:
        return None


@lru_cache(maxsize=32)
def _chunk_vectors_cached(version: tuple[object, ...], model: str) -> tuple[Vector, ...]:
    chunks = get_schema_chunks_at(version)
    vectors = embed([chunk_text(chunk) for chunk in chunks], model)
    if vectors is None:
        raise DenseUnavailable("no chunk vectors")  # not cached: the next call retries
    return tuple(vectors)


def chunk_vectors(version: tuple[object, ...], model: str) -> tuple[Vector, ...] | None:
    """One embedding per chunk of a schema version, in chunk order, or `None`.

    Only successes are cached (on the chunks' `(dsn, fingerprint)` key); a failure is not,
    so the schema regains the signal once Ollama answers again.
    """
    try:
        return _chunk_vectors_cached(version, model)
    except DenseUnavailable:
        return None


@lru_cache(maxsize=512)
def _question_vector_cached(question: str, model: str) -> Vector:
    vectors = embed([question], model)
    if not vectors:
        raise DenseUnavailable("no question vector")
    return vectors[0]


def question_vector(question: str, model: str) -> Vector | None:
    """The question's embedding, cached by text on success; `None` if unavailable."""
    try:
        return _question_vector_cached(question, model)
    except DenseUnavailable:
        return None


_enabled = True


def set_enabled(enabled: bool) -> None:
    """Turn the signal on or off for this process; the evaluation runner pins it per run."""
    global _enabled
    _enabled = enabled


def is_enabled() -> bool:
    """Whether retrieval may use this signal at all (`set_enabled`)."""
    return _enabled


def model_identity(model: str = DEFAULT_RAG_DENSE_MODEL) -> str | None:
    """`name@digest12` of the installed embedding model, from `/api/tags`; `None` if absent.

    The digest pins the exact weights, so a run records which model it used.
    """
    try:
        with urllib.request.urlopen(f"{_host()}/api/tags", timeout=_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError):
        return None
    wanted = {model, f"{model}:latest"} if ":" not in model else {model}
    for entry in payload.get("models", []) if isinstance(payload, dict) else []:
        name = entry.get("name") if isinstance(entry, dict) else None
        digest = entry.get("digest") if isinstance(entry, dict) else None
        if name in wanted and isinstance(digest, str) and digest:
            return f"{name}@{digest[:12]}"
    return None


def clear_caches() -> None:
    """Forget cached vectors and any recent failure (tests, and after a model change)."""
    global _last_failure
    _chunk_vectors_cached.cache_clear()
    _question_vector_cached.cache_clear()
    _last_failure = -math.inf


def cosine(left: Vector, right: Vector) -> float:
    """Cosine similarity; 0 for a zero vector."""
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    norm = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return dot / norm if norm else 0.0
