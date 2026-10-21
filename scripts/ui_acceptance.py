"""Browser acceptance pass for the answer UI: overflow, focus, fonts and edge states.

    uv run --group screenshots python scripts/ui_acceptance.py

Serves `scripts/ui_fixtures/states_page.py` (the real `render_answer` over fixture turns:
signed values, a missing value, long names and many categories, empty, unsupported
type, provider failure) and the real `app.py`, then in Chrome at 1440x1000 and 390x844:

- records the page's scroll width against the viewport (no horizontal page scroll);
- drives the app by keyboard alone: open Change, switch to Ollama, ask a sample question,
  then reach Ask, CSV, the table disclosure and the schema expander, with outline state;
- records text clipped inside an answer card or its chart, which page width misses;
- checks the locally served Plex files load, then renders with them blocked to check
  the system fallback.

Writes PNGs and `report.json` to `docs/design/acceptance/`. Fixtures, not model answers.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import Page, ViewportSize, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "design" / "acceptance"
VIEWPORTS: dict[str, ViewportSize] = {
    "desktop": {"width": 1440, "height": 1000},
    "narrow": {"width": 390, "height": 844},
}


def _port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _serve(script: str, port: int) -> subprocess.Popen[bytes]:
    env = {k: v for k, v in os.environ.items() if "API_KEY" not in k}
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            script,
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


def _load(page: Page, url: str, text: str) -> None:
    deadline = time.time() + 60
    while True:
        try:
            page.goto(url)
            page.get_by_text(text).first.wait_for(timeout=15_000)
            page.wait_for_timeout(2500)
            return
        except Exception:
            if time.time() > deadline:
                raise
            time.sleep(1)


def _overflow(page: Page) -> int:
    return int(page.evaluate("document.documentElement.scrollWidth - window.innerWidth"))


_CLIPPED = """() => {
  // Text inside an answer card that does not fit: an element wider than the card, or a
  // chart label drawn past its own SVG's edge. Page width alone misses both.
  const out = [];
  for (const card of document.querySelectorAll('[class*="st-key-answer_"]')) {
    const box = card.getBoundingClientRect();
    for (const el of card.querySelectorAll('span, p, h2, h3, code, pre, td')) {
      const r = el.getBoundingClientRect();
      if (r.width && (r.right > box.right + 1 || r.left < box.left - 1))
        out.push('element: ' + el.textContent.trim().slice(0, 40));
    }
    for (const svg of card.querySelectorAll('svg')) {
      const sb = svg.getBoundingClientRect();
      for (const t of svg.querySelectorAll('text')) {
        const r = t.getBoundingClientRect();
        if (r.width && (r.right > sb.right + 1 || r.left < sb.left - 1))
          out.push('chart text: ' + t.textContent.trim().slice(0, 40));
      }
    }
  }
  return out;
}"""


def _clipped(page: Page) -> list[str]:
    return list(page.evaluate(_CLIPPED))


def _focused(page: Page) -> dict[str, object]:
    return dict(
        page.evaluate(
            """() => { const e = document.activeElement; const s = getComputedStyle(e);
            return {tag: e.tagName.toLowerCase(),
                    label: (e.getAttribute('aria-label') || e.innerText || e.value || '')
                        .trim().slice(0, 40),
                    outline: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0}; }"""
        )
    )


def _tab_until(
    page: Page, label: str, limit: int = 40, *, exact: bool = False
) -> dict[str, object] | None:
    """Press Tab until the focused element's label contains (or, `exact`, is) `label`."""
    for _ in range(limit):
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
        focused = _focused(page)
        text = str(focused["label"]).strip().lower()
        if (text == label.lower()) if exact else (label.lower() in text):
            return focused
    return None


def _keyboard_path(page: Page) -> dict[str, object]:
    """Keyboard only: open Change, switch to Ollama, ask a sample, reach the answer's controls.

    Every step is a key press; nothing is clicked. A step that cannot be reached is
    recorded as None. The answer comes from local Ollama, so this needs it running.
    """
    path: dict[str, object] = {}
    page.evaluate("document.activeElement && document.activeElement.blur()")
    path["change"] = _tab_until(page, "Change")
    page.keyboard.press("Enter")
    page.wait_for_timeout(800)
    path["provider"] = _tab_until(page, "Provider")
    page.keyboard.press("ArrowDown")  # open the list on the current option
    page.wait_for_timeout(400)
    page.keyboard.press("ArrowDown")  # move to Ollama (local)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1500)
    path["ollama_selected"] = bool(
        page.evaluate("document.body.innerText.includes('Runs on this machine')")
    )
    path["model"] = _tab_until(page, "Model")
    page.keyboard.press("ArrowDown")  # opens the list on the next option, qwen3.5:9b-q4_K_M
    page.wait_for_timeout(400)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)
    page.evaluate("document.activeElement && document.activeElement.blur()")
    path["summary"] = page.evaluate(
        "document.querySelector('.conn') && document.querySelector('.conn').innerText"
    )
    # The pills are one tab stop (the first); arrow keys move between them.
    path["sample_pill"] = _tab_until(page, "Students per major")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("ArrowRight")  # to "Top students", a ranked list: a table and CSV
    path["sample_pill_chosen"] = _focused(page)
    page.keyboard.press("Enter")
    page.get_by_text("How this was answered").first.wait_for(timeout=180_000)
    page.wait_for_timeout(2000)
    page.evaluate("document.activeElement && document.activeElement.blur()")
    path["ask_button"] = _tab_until(page, "Ask", exact=True)
    path["csv"] = _tab_until(page, "Download CSV")
    path["all_tables"] = _tab_until(page, "All selected tables")
    path["full_schema"] = _tab_until(page, "Full schema sent")
    page.keyboard.press("Enter")
    page.wait_for_timeout(500)
    path["full_schema_opened"] = bool(
        page.evaluate(
            "[...document.querySelectorAll('details')].some(d => d.open && "
            "d.innerText.includes('Full schema sent'))"
        )
    )
    return path


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    states_port, app_port = _port(), _port()
    servers = [
        _serve("scripts/ui_fixtures/states_page.py", states_port),
        _serve("app.py", app_port),
    ]
    report: dict[str, object] = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome")
            for name, viewport in VIEWPORTS.items():
                page = browser.new_page(viewport=viewport)
                _load(page, f"http://127.0.0.1:{states_port}", "UI states")
                report[f"states_{name}_overflow_px"] = _overflow(page)
                report[f"states_{name}_plex_loaded"] = page.evaluate(
                    "document.fonts.check('16px \"IBM Plex Sans\"') && "
                    "document.fonts.check('13px \"IBM Plex Mono\"')"
                )
                report[f"states_{name}_fonts"] = page.evaluate(
                    "[...['h1.hero', 'h2.headline', '.trace h3', '.trace pre']].map("
                    "q => getComputedStyle(document.querySelector(q)).fontFamily)"
                )
                page.screenshot(path=OUT / f"states-{name}.png", full_page=False)
                for state in (
                    "signed",
                    "missing value",
                    "long names",
                    "empty",
                    "unsupported",
                    "provider",
                ):
                    _load(page, f"http://127.0.0.1:{states_port}/?state={state}", "UI states")
                    report[f"{state}_{name}_overflow_px"] = _overflow(page)
                    report[f"{state}_{name}_clipped"] = _clipped(page)
                    page.screenshot(path=OUT / f"{state.replace(' ', '-')}-{name}.png")
                page.close()

                fallback = browser.new_page(viewport=viewport)
                fallback.route("**/app/static/fonts/**", lambda route: route.abort())
                _load(fallback, f"http://127.0.0.1:{states_port}/?state=signed", "UI states")
                report[f"fallback_{name}_overflow_px"] = _overflow(fallback)
                report[f"fallback_{name}_plex_loaded"] = fallback.evaluate(
                    "document.fonts.check('16px \"IBM Plex Sans\"')"
                )
                fallback.screenshot(path=OUT / f"fallback-fonts-{name}.png")
                fallback.close()

            app = browser.new_page(viewport=VIEWPORTS["desktop"])
            _load(app, f"http://127.0.0.1:{app_port}", "Ask your data")
            report["keyboard"] = _keyboard_path(app)
            app.screenshot(path=OUT / "app-focus.png")
            browser.close()
    finally:
        for server in servers:
            server.terminate()
            server.wait(timeout=20)
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
