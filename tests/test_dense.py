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
    """A stand-in `urlopen`: each call takes the next scripted reply."""

    def __init__(self, replies: list[Any]) -> None:
        self.replies = replies
        self.calls = 0

    def __call__(self, request: Any, timeout: float = 0) -> _Response:
        self.calls += 1
        reply = self.replies.pop(0) if self.replies else self.default(request)
        if isinstance(reply, urllib.error.URLError):
            raise reply
        return _Response(
            reply if isinstance(reply, bytes | Exception) else json.dumps(reply).encode()
        )

    @staticmethod
    def default(request: Any) -> dict[str, Any]:
        texts = json.loads(request.data)["input"]
        return {"embeddings": [[1.0, 0.0] if "course" in t else [0.0, 1.0] for t in texts]}


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
