"""`text_to_sql_agent.dense` at its HTTP boundary, with `urlopen` stubbed (Codex, 2026-10-22).

No test reaches Ollama: responses are fakes, so these run the real `embed`, its response
validation, its failure caching and its recovery.
"""

from __future__ import annotations

import http.client
import json
import urllib.error
from typing import Any

import pytest

from text_to_sql_agent import dense, rag

pytestmark = pytest.mark.dense


class _Response:
    def __init__(self, body: bytes | Exception) -> None:
        self.body = body

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        if isinstance(self.body, Exception):
            raise self.body
        return self.body


class _Server:
    """A stand-in `urlopen`: `/api/tags` reports `digest`; each embed call takes the next
    scripted reply, else `vector_for` of each text."""

    def __init__(self, replies: list[Any], digest: str = "a" * 64) -> None:
        self.replies = replies
        self.calls = 0
        self.digest = digest
        self.vector_for = lambda text: [1.0, 0.0] if "course" in text else [0.0, 1.0]

    def __call__(self, request: Any, timeout: float = 0) -> _Response:
        if isinstance(request, str) and request.endswith("/api/tags"):
            tags = {"models": [{"name": "all-minilm:latest", "digest": self.digest}]}
            return _Response(json.dumps(tags).encode())
        self.calls += 1
        reply = self.replies.pop(0) if self.replies else self.default(request)
        if callable(reply):
            reply = reply(request)
        if isinstance(reply, urllib.error.URLError):
            raise reply
        return _Response(
            reply if isinstance(reply, bytes | Exception) else json.dumps(reply).encode()
        )

    def default(self, request: Any) -> dict[str, Any]:
        texts = json.loads(request.data)["input"]
        return {"embeddings": [self.vector_for(t) for t in texts]}


@pytest.mark.parametrize(
    "reply",
    [
        http.client.IncompleteRead(b"{"),
        [],
        {"embeddings": [[None]]},
        {"embeddings": [["bad"]]},
        {"embeddings": [[1.0], [1.0, 2.0]]},
        {"embeddings": [[float("nan")]]},
        urllib.error.URLError("refused"),
    ],
)
def test_a_broken_reply_gives_no_vectors_instead_of_an_exception(
    monkeypatch: pytest.MonkeyPatch, reply: Any
) -> None:
    texts = ["a"] if not (isinstance(reply, dict) and len(reply["embeddings"]) == 2) else ["a", "b"]
    monkeypatch.setattr("urllib.request.urlopen", _Server([reply]))
    assert dense.embed(texts) is None


def test_a_failure_is_not_cached_and_the_signal_comes_back(
    customers_courses_db: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server = _Server([urllib.error.URLError("down")])
    monkeypatch.setattr("urllib.request.urlopen", server)
    question = "list every course"

    down = rag.rank_schema_chunks(customers_courses_db, question)
    assert not any("dense" in r for c in down for r in c.match_reasons or [])
    assert server.calls == 1  # the schema failed, so no question vector was requested

    monkeypatch.setattr(dense, "RETRY_AFTER_SECONDS", 0.0)  # the cool-down has passed
    up = rag.rank_schema_chunks(customers_courses_db, question)
    assert up[0].table_name == "courses"
    assert any("dense similarity" in r for r in up[0].match_reasons or [])


def test_after_a_failure_no_request_is_made_during_the_cool_down(
    customers_courses_db: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server = _Server([urllib.error.URLError("down")])
    monkeypatch.setattr("urllib.request.urlopen", server)
    for question in ("one", "two", "three"):
        rag.rank_schema_chunks(customers_courses_db, question)
    assert server.calls == 1


def _version(db: str) -> tuple[object, ...]:
    from text_to_sql_agent.schema import get_schema_chunks_plain_ddl_and_version

    return get_schema_chunks_plain_ddl_and_version(db)[2]


def test_a_replaced_model_never_mixes_with_cached_vectors(
    customers_courses_db: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex, 2026-10-25: vectors cached under digest A were labelled with digest B."""
    server = _Server([])
    monkeypatch.setattr("urllib.request.urlopen", server)
    version = _version(customers_courses_db)
    first = dense.vectors_for(version, "list every course")
    assert first is not None and first[1] == (1.0, 0.0)

    server.digest = "b" * 64  # replaced in place: same name, new weights
    server.vector_for = lambda text: [0.0, 1.0] if "course" in text else [1.0, 0.0]
    again = dense.vectors_for(version, "list every course")  # no cache clearing
    assert again is not None and again[1] == (0.0, 1.0)  # re-embedded under the new key

    # A run that recorded digest A refuses vectors from B instead of mixing them.
    pinned_a = "all-minilm:latest@" + "a" * 12
    assert dense.vectors_for(version, "list every course", expected_identity=pinned_a) is None


def test_a_replacement_during_embedding_is_refused(
    customers_courses_db: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server = _Server([])

    def swap_then_answer(request: Any) -> dict[str, Any]:
        server.digest = "c" * 64  # the model changes while this request is served
        return server.default(request)

    server.replies = [swap_then_answer]
    monkeypatch.setattr("urllib.request.urlopen", server)
    assert dense.vectors_for(_version(customers_courses_db), "anything") is None


def test_vectors_of_different_lengths_across_batches_are_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    texts = [f"t{i}" for i in range(65)]  # two batches: 64, then 1
    server = _Server([{"embeddings": [[1.0, 0.0]] * 64}, {"embeddings": [[1.0, 0.0, 0.0]]}])
    monkeypatch.setattr("urllib.request.urlopen", server)
    assert dense.embed(texts) is None


def test_a_schema_and_question_size_mismatch_is_dropped_then_recovers(
    customers_courses_db: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server = _Server([])
    # Schema vectors are 2-d; the first question vector comes back 3-d.
    server.replies = [server.default, {"embeddings": [[1.0, 0.0, 0.0]]}]
    monkeypatch.setattr("urllib.request.urlopen", server)
    question = "list every course"

    broken = rag.rank_schema_chunks(customers_courses_db, question)  # no exception
    assert not any("dense" in r for c in broken for r in c.match_reasons or [])

    healed = rag.rank_schema_chunks(customers_courses_db, question)  # no cache clearing
    assert healed[0].table_name == "courses"
    assert any("dense similarity" in r for r in healed[0].match_reasons or [])
