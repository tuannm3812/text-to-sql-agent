"""Browser acceptance pass for the answer UI: overflow, focus, fonts and edge states.

    uv run --group screenshots python scripts/ui_acceptance.py

Serves `scripts/ui_fixtures/states_page.py` (the real `render_answer` over fixture turns:
signed values, a missing value, long names and many categories, empty, unsupported
type, provider failure) and the real `app.py`, then in Chrome at 1440x1000 and 390x844:

- records the page's scroll width against the viewport (no horizontal page scroll);
- tabs through the app's controls and records each focused element and whether it shows
  a visible outline;
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


def _focus_walk(page: Page, steps: int = 14) -> list[dict[str, object]]:
    walk = []
    page.evaluate("document.activeElement && document.activeElement.blur()")
    for _ in range(steps):
        page.keyboard.press("Tab")
        page.wait_for_timeout(120)
        walk.append(
            page.evaluate(
                """() => { const e = document.activeElement; if (!e) return null;
            const s = getComputedStyle(e);
            const visible = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0)
                || s.boxShadow !== 'none';
            return {tag: e.tagName.toLowerCase(),
                    label: (e.getAttribute('aria-label') || e.innerText || e.value || '')
                        .trim().slice(0, 40),
                    visible}; }"""
            )
        )
    return walk


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
                for state in ("signed", "long names", "unsupported", "provider"):
                    _load(page, f"http://127.0.0.1:{states_port}/?state={state}", "UI states")
                    report[f"{state}_{name}_overflow_px"] = _overflow(page)
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
            report["app_focus_walk"] = _focus_walk(app)
            app.keyboard.press("Shift+Tab")
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
