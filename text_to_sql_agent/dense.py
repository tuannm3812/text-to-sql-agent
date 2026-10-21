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

import json
import math
import os
import re
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


def embed(texts: Sequence[str], model: str = DEFAULT_RAG_DENSE_MODEL) -> list[Vector] | None:
    """Embeddings for `texts` in order, or `None` if Ollama or the model is unavailable."""
    vectors: list[Vector] = []
    for start in range(0, len(texts), _BATCH):
        body = json.dumps({"model": model, "input": list(texts[start : start + _BATCH])})
        request = urllib.request.Request(
            f"{_host()}/api/embed",
            data=body.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
                payload = json.load(response)
        except (urllib.error.URLError, OSError, ValueError):
            return None
        batch = payload.get("embeddings")
        if not isinstance(batch, list):
            return None
        vectors.extend(tuple(float(x) for x in vector) for vector in batch)
    return vectors if len(vectors) == len(texts) else None


@lru_cache(maxsize=32)
def chunk_vectors(version: tuple[object, ...], model: str) -> tuple[Vector, ...] | None:
    """One embedding per chunk of a schema version, in chunk order; cached on that key."""
    chunks = get_schema_chunks_at(version)
    vectors = embed([chunk_text(chunk) for chunk in chunks], model)
    return tuple(vectors) if vectors is not None else None


@lru_cache(maxsize=512)
def question_vector(question: str, model: str) -> Vector | None:
    """The question's embedding, cached by text; `None` if Ollama is unavailable."""
    vectors = embed([question], model)
    return vectors[0] if vectors else None


def cosine(left: Vector, right: Vector) -> float:
    """Cosine similarity; 0 for a zero vector."""
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    norm = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return dot / norm if norm else 0.0
