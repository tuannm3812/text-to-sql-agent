"""Render the deck's single icon set (Material Symbols Rounded) and fetch product logos.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_icons.py
"""

from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ICONS = "verified_user target trending_up help construction monitoring flag chat schema code "
ICONS += "table_rows person fact_check science menu_book"
COLOURS = {"white": "#FFFFFF", "blue": "#0F4BEB", "navy": "#17243B"}
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
        for name, colour in COLOURS.items():
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

for name, org in LOGOS.items():
    with urlopen(f"https://github.com/{org}.png?size=160") as response:
        (HERE / f"assets/logos/{name}.png").write_bytes(response.read())
print("done")
