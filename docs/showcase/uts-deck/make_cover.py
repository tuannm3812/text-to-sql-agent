"""Render the wordless cover illustration: schema tables and an inspected result.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_cover_art.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent / "assets/figures"
TABLES = [(70, 70), (290, 40), (520, 90), (40, 300), (560, 340), (90, 520), (320, 560),
          (150, -190), (420, -160), (130, 790), (450, 800)]
LINKS = [(0, 1), (1, 2), (0, 3), (2, 4), (3, 5), (5, 6), (7, 8), (7, 0), (8, 2), (9, 10), (9, 5), (10, 6)]
BARS = [250, 150, 136, 92, 50]
CX, CY, R = 372, 330, 178


def card(x: int, y: int) -> str:
    """One schema table: a header bar and three column rows."""
    rows = "".join(
        f'<rect x="{x + 14}" y="{y + 40 + i * 22}" width="{122 - (i % 2) * 24}" height="9" '
        'rx="4.5" fill="#8FA9C0"/>'
        for i in range(3)
    )
    return (
        f'<rect x="{x}" y="{y}" width="150" height="118" rx="14" fill="#32658A"/>'
        f'<rect x="{x + 14}" y="{y + 14}" width="90" height="12" rx="6" fill="#C9D6E3"/>{rows}'
    )


def art() -> str:
    """The 900 x 900 scene: linked tables, then the magnifier over a result."""
    links = "".join(
        f'<line x1="{TABLES[a][0] + 75}" y1="{TABLES[a][1] + 59}" x2="{TABLES[b][0] + 75}" '
        f'y2="{TABLES[b][1] + 59}" stroke="#8FA9C0" stroke-width="4"/>'
        for a, b in LINKS
    )
    cards = "".join(card(x, y) for x, y in TABLES)
    bars = "".join(
        f'<rect x="{CX - 125}" y="{CY - 100 + i * 42}" width="{w}" height="26" rx="8" '
        f'fill="{"#32658A" if i == 0 else "#B89245"}"/>'
        for i, w in enumerate(BARS)
    )
    lens = (
        f'<line x1="{CX + 128}" y1="{CY + 128}" x2="{CX + 236}" y2="{CY + 236}" stroke="#8FA9C0" '
        'stroke-width="30" stroke-linecap="round"/>'
        f'<line x1="{CX + 128}" y1="{CY + 128}" x2="{CX + 160}" y2="{CY + 160}" stroke="#B89245" '
        'stroke-width="30"/>'
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="#fff" stroke="#1B2430" stroke-width="18"/>'
        f"{bars}"
    )
    grid = "".join(
        f'<circle cx="{x}" cy="{y}" r="2.2" fill="#2A3543"/>'
        for x in range(-200, 1100, 36) for y in range(-200, 1100, 36)
    )
    return f'<rect x="-400" y="-400" width="1700" height="1700" fill="#1B2430"/>{grid}{links}{cards}{lens}'


def page(view: str, radius: int, size: int, height: int | None = None) -> str:
    """A page holding the scene, clipped to rounded corners when radius is set."""
    h = height or size
    return (
        "<!doctype html><style>*{margin:0}body{background:transparent}</style>"
        f'<div style="width:{size}px;height:{h}px;border-radius:{radius}px;overflow:hidden">'
        f'<svg width="{size}" height="{h}" viewBox="{view}">{art()}</svg></div>'
    )


with sync_playwright() as p:
    browser = p.chromium.launch()
    for name, view, radius in (
        ("cover-art.png", "0 0 900 900", 0),
        ("cover-art-close.png", "20 20 720 720", 56),
    ):
        tab = browser.new_page(viewport={"width": 900, "height": 900}, device_scale_factor=2)
        tab.set_content(page(view, radius, 900))
        tab.screenshot(path=HERE / name, omit_background=True)
        print("wrote", name)
    # Portrait panels for the cover (400 x 540 pt) and the close (455 x 540 pt), centred on the lens.
    for name, w, h in (("cover-portrait.png", 800, 1080), ("close-portrait.png", 910, 1080)):
        vw = 760
        vh = vw * h / w
        view = f"{375 - vw / 2} {CY + 40 - vh / 2} {vw} {vh}"
        tab = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        tab.set_content(page(view, 0, w, h))
        tab.screenshot(path=HERE / name, omit_background=True)
        print("wrote", name)
    browser.close()
