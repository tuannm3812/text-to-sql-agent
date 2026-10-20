"""Capture the README screenshots from the running app, reproducibly.

    uv run --group screenshots python scripts/capture_screenshots.py [--model qwen3.5:9b-q4_K_M]

Starts `streamlit run app.py` on a free local port, drives it with Playwright (the installed
Google Chrome by default) at 1440x1000 (and 390x844 for the narrow check), and writes PNGs to
`docs/screenshots/`. Every
answer is a real one: the app's own Ollama path with the given local model on the tracked
demo databases, so no paid provider is called. `docs/screenshots/capture.json` records the
commit, model, questions and capture time; the agent log repeats them.

A model answer is not deterministic in general, so a re-run can differ in wording or SQL;
the images are evidence of the interface, not of benchmark accuracy.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import Locator, Page, ViewportSize, expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
WIDE: ViewportSize = {"width": 1440, "height": 1000}
NARROW: ViewportSize = {"width": 390, "height": 844}
DEMO = "Retail Analytics"
QUESTION = "Which product categories generate the most revenue?"
REFUSAL = "Delete every order that was cancelled."
ANSWER_TIMEOUT_MS = 180_000


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_app(port: int) -> subprocess.Popen[bytes]:
    env = {k: v for k, v in os.environ.items() if "API_KEY" not in k}  # no cloud keys
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.port",
            str(port),
            "--server.address",
            "127.0.0.1",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _wait_for(url: str, page: Page) -> None:
    deadline = time.time() + 60
    while True:
        try:
            page.goto(url)
            expect(page.get_by_text("Text-to-SQL Agent").first).to_be_visible(timeout=15_000)
            return
        except Exception:
            if time.time() > deadline:
                raise
            time.sleep(1)


def _settle(page: Page) -> None:
    """Wait for Streamlit's rerun after an interaction to finish."""
    page.wait_for_timeout(500)
    expect(page.get_by_test_id("stStatusWidget")).to_have_count(0, timeout=30_000)
    page.wait_for_timeout(500)


def _choose(page: Page, label: str, option: str) -> None:
    sidebar = page.get_by_test_id("stSidebar")
    sidebar.get_by_label(label, exact=True).click()
    page.get_by_role("option", name=option, exact=True).click()
    _settle(page)


def _scroll_to_question(page: Page, question: str) -> None:
    """Put the question's bubble at the top, so its answer card is in view below it."""
    page.locator(".chat-user-bubble", has_text=question).last.evaluate(
        "e => e.scrollIntoView({block: 'start'})"
    )
    page.wait_for_timeout(500)


def _last_answer(page: Page) -> Locator:
    return page.get_by_test_id("stChatMessage").last


def _wait_for_answers(page: Page, count: int) -> None:
    expect(page.get_by_role("tab", name="Result")).to_have_count(count, timeout=ANSWER_TIMEOUT_MS)
    page.wait_for_timeout(1500)  # let the chart finish drawing


def capture(model: str, channel: str) -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    port = _free_port()
    app = _start_app(port)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=channel or None)
            page = browser.new_page(viewport=WIDE, device_scale_factor=1)
            _wait_for(f"http://127.0.0.1:{port}", page)
            _settle(page)
            _choose(page, "Demo", DEMO)
            _choose(page, "Provider", "Ollama (local)")
            _choose(page, "Model", model)

            page.get_by_text(QUESTION, exact=True).first.click()
            _wait_for_answers(page, 1)
            _scroll_to_question(page, QUESTION)
            page.screenshot(path=OUT / "01-answer-result.png")

            _last_answer(page).get_by_role("tab", name="SQL").click()
            page.screenshot(path=OUT / "02-answer-sql.png")
            _last_answer(page).get_by_role("tab", name="Context").click()
            page.screenshot(path=OUT / "03-answer-context.png")

            page.get_by_test_id("stChatInputTextArea").fill(REFUSAL)
            page.keyboard.press("Enter")
            _wait_for_answers(page, 2)
            _scroll_to_question(page, REFUSAL)
            page.screenshot(path=OUT / "04-read-only-refusal.png")

            page.set_viewport_size(NARROW)
            page.wait_for_timeout(1000)
            page.screenshot(path=OUT / "05-narrow.png")
            browser.close()
    finally:
        app.terminate()
        app.wait(timeout=20)

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    record = {
        "commit": commit,
        "dirty": dirty,
        "captured": datetime.now(UTC).isoformat(timespec="seconds"),
        "method": "scripts/capture_screenshots.py: streamlit + Playwright "
        f"({channel or 'chromium'})",
        "viewport": WIDE,
        "narrow_viewport": NARROW,
        "database": f"{DEMO} demo (data/retail_analytics.db)",
        "provider": "ollama",
        "model": model,
        "questions": [QUESTION, REFUSAL],
    }
    (OUT / "capture.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default="qwen3.5:9b-q4_K_M")
    parser.add_argument(
        "--channel",
        default="chrome",
        help="Playwright browser channel; 'chrome' uses the installed Google Chrome, '' "
        "Playwright's own Chromium (needs `playwright install chromium`).",
    )
    args = parser.parse_args()
    print(json.dumps(capture(args.model, args.channel), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
