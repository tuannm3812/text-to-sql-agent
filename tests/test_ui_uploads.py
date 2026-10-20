"""Tests for `ui.uploads.redact_dsn`.

The "Connection string" sidebar option must never echo a DSN's password back
to the page - not in the "Using `...`" caption, and not in an exception
message a driver raised that happened to embed the DSN it failed to reach.
No PostgreSQL engine exists yet (Phase 3b), but its DSN form is exactly the
credentials-bearing case this guards, so it is tested here even though
nothing in this repo can construct one today.
"""

from __future__ import annotations

import pytest

from ui.uploads import redact_dsn


def test_redact_dsn_masks_a_postgresql_password() -> None:
    dsn = "postgresql://user:password@host/db"
    assert redact_dsn(dsn) == "postgresql://user:***@host/db"


def test_redact_dsn_does_not_leak_the_password_substring() -> None:
    dsn = "postgresql://alice:hunter2@db.example.com:5432/prod"
    redacted = redact_dsn(dsn)
    assert "hunter2" not in redacted
    assert redacted == "postgresql://alice:***@db.example.com:5432/prod"


def test_redact_dsn_leaves_a_credential_free_dsn_unchanged() -> None:
    assert redact_dsn("sqlite:///path/to.db") == "sqlite:///path/to.db"
    assert redact_dsn("duckdb:///path/to.duckdb") == "duckdb:///path/to.duckdb"


def test_redact_dsn_leaves_plain_text_unchanged() -> None:
    assert redact_dsn("input database not found") == "input database not found"


def test_redact_dsn_masks_a_dsn_embedded_inside_a_longer_error_message() -> None:
    message = "could not connect to postgresql://user:s3cr3t@host:5432/db: timed out"
    redacted = redact_dsn(message)
    assert "s3cr3t" not in redacted
    assert redacted == "could not connect to postgresql://user:***@host:5432/db: timed out"


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://u:p@host/db",
        "mysql://u:p@host:3306/db",
        "postgres://u:p@127.0.0.1/db",
    ],
)
def test_redact_dsn_masks_credentials_for_any_scheme(dsn: str) -> None:
    assert ":p@" not in redact_dsn(dsn)
    assert ":***@" in redact_dsn(dsn)


@pytest.mark.parametrize(
    ("dsn", "secret"),
    [
        ("postgresql://:s3cret@host/db", "s3cret"),
        ("postgresql://u:pa/ss@host/db", "pa/ss"),
        ("postgresql://u:p@ss@host/db", "p@ss"),
        ("postgresql://u:s3cret@host:5432/db?sslmode=require", "s3cret"),
    ],
)
def test_redact_dsn_masks_the_whole_password_in_awkward_forms(dsn: str, secret: str) -> None:
    """An empty user, or an unescaped `/` or `@` in the password, must not leak any of it."""
    redacted = redact_dsn(dsn)
    assert secret not in redacted
    assert "ss@" not in redacted
    assert redacted.endswith("host/db") or "host:5432/db" in redacted


# --- Upload identity (Codex, 2026-10-20) ----------------------------------------------


class _FakeUpload:
    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self.size = len(data)
        self._data = data

    def getbuffer(self) -> memoryview:
        return memoryview(self._data)


def test_replacing_an_upload_with_same_name_and_size_uses_the_new_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path
    from types import SimpleNamespace

    import ui.uploads as uploads

    state: dict[str, object] = {"sb_source": "Upload `.db`"}
    monkeypatch.setattr(uploads, "st", SimpleNamespace(session_state=state))

    state["sb_upload_db"] = _FakeUpload("same.db", b"first")
    first = uploads.active_db_path()
    state["sb_upload_db"] = _FakeUpload("same.db", b"other")
    second = uploads.active_db_path()

    assert first is not None and second is not None
    assert Path(first).read_bytes() == b"first"
    assert Path(second).read_bytes() == b"other"


def test_replacing_a_csv_with_same_name_and_size_reingests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path
    from types import SimpleNamespace

    import ui.uploads as uploads

    state: dict[str, object] = {"sb_source": "Upload CSV(s)"}
    monkeypatch.setattr(uploads, "st", SimpleNamespace(session_state=state))
    ingested: list[list[str]] = []

    def fake_ingest(paths: list[str], output_db_path: str) -> str:
        ingested.append([Path(p).read_text(encoding="utf-8") for p in paths])
        return output_db_path

    monkeypatch.setattr(uploads.backend, "ingest_csvs_to_db", fake_ingest)
    state["sb_upload_csv"] = [_FakeUpload("t.csv", b"a\n1\n")]
    uploads.active_db_path()
    state["sb_upload_csv"] = [_FakeUpload("t.csv", b"a\n2\n")]
    uploads.active_db_path()

    assert ingested == [["a\n1\n"], ["a\n2\n"]]
