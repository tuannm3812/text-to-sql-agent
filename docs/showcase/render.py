"""Render the showcase poster (PNG and PDF) from its HTML. The deck is build_deck.py.

Every figure in poster.html is copied from the README's
Evaluation Results and the results READMEs it links; update those first.
Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/render.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
POSTER = ("poster.html", "text-to-sql-agent-poster", 1200, 1700)

with sync_playwright() as p:
    browser = p.chromium.launch()

    src, stem, width, height = POSTER
    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
    page.goto((HERE / src).as_uri())
    page.evaluate("document.fonts.ready")
    page.screenshot(path=HERE / f"{stem}.png")
    page.pdf(
        path=HERE / f"{stem}.pdf", width=f"{width}px", height=f"{height}px", print_background=True
    )
    print("wrote", f"{stem}.png", f"{stem}.pdf")

    browser.close()
