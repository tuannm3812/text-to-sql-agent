"""Render the deck's single icon set (Material Symbols Rounded) and fetch product logos.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_icons.py
"""

from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ICONS = "verified_user target trending_up help construction monitoring flag chat schema code "
ICONS += "table_rows person fact_check science menu_book query_stats check_circle cancel timer"
COLOURS = {"white": "#FFFFFF", "blue": "#0F4BEB", "navy": "#17243B"}
WEAKNESS = {"amber": "#E6A23C"}  # only these two icons need amber
FONT = (
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD"
    "@24,400,0,0"
)
LOGOS = {
    "snowflake": "snowflakedb",
    "databricks": "databricks",
    "wren": "Canner",
    "vanna": "vanna-ai",
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": 96, "height": 96}, device_scale_factor=2)
    for icon in ICONS.split():
        for name, colour in (
            {**COLOURS, **WEAKNESS} if icon in ("cancel", "check_circle") else COLOURS
        ).items():
            style = (
                "font-family:'Material Symbols Rounded';font-size:96px;line-height:96px;"
                f"display:block;color:{colour}"
            )
            tab.set_content(
                f'<link rel="stylesheet" href="{FONT}"><body style="margin:0;'
                f'background:transparent"><span style="{style}">{icon}</span>',
                wait_until="networkidle",
            )
            tab.evaluate("document.fonts.ready")
            tab.wait_for_timeout(120)
            tab.screenshot(path=HERE / f"assets/icons/{icon}-{name}.png", omit_background=True)
    browser.close()

TECH = [
    "streamlit",
    "python",
    "pandas",
    "sqlite",
    "duckdb",
    "postgresql",
    "ollama",
    "googlegemini",
    "langchain",
]
with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": 128, "height": 128}, device_scale_factor=2)
    for name in TECH:
        request = Request(
            f"https://cdn.simpleicons.org/{name}", headers={"User-Agent": "Mozilla/5.0"}
        )
        with urlopen(request) as response:
            svg = response.read().decode()
        tab.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
        tab.evaluate("document.querySelector('svg').setAttribute('width', 128)")
        tab.evaluate("document.querySelector('svg').setAttribute('height', 128)")
        tab.screenshot(path=HERE / f"assets/logos/tech-{name}.png", omit_background=True)
    browser.close()

for name, org in LOGOS.items():
    with urlopen(f"https://github.com/{org}.png?size=160") as response:
        (HERE / f"assets/logos/{name}.png").write_bytes(response.read())
with urlopen("https://raw.githubusercontent.com/tobymao/sqlglot/main/sqlglot.png") as response:
    (HERE / "assets/logos/tech-sqlglot.png").write_bytes(response.read())
print("done")
