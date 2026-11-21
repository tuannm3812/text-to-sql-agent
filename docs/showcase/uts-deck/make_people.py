"""Render two flat illustrations (22 November 2026), palette A, no real person or data:

- persona.png: the store manager (an illustrative persona) at a counter with a laptop, a question bubble above.
- close-answer.png: an answer card with a tick, a small bar chart and a SQL strip, for the closing slide.

Run: uv run --no-project --with "playwright==1.60.0" python make_people.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent / "assets/figures"
NAVY, BLUE, PALE, GOLD, SKIN, HAIR, WHITE = "#1B2430", "#32658A", "#C9D6E3", "#B89245", "#E8B98F", "#3A2A22", "#FFFFFF"

PERSONA = f"""
<rect width="600" height="560" fill="#EDF0F3"/>
<circle cx="470" cy="110" r="70" fill="#EAF0F6"/>
<!-- shelves behind -->
<rect x="40" y="120" width="190" height="10" rx="4" fill="{PALE}"/>
<rect x="40" y="200" width="190" height="10" rx="4" fill="{PALE}"/>
<rect x="56" y="78" width="34" height="42" rx="5" fill="{GOLD}"/><rect x="98" y="90" width="28" height="30" rx="5" fill="{BLUE}"/>
<rect x="134" y="70" width="40" height="50" rx="5" fill="#8FA9C0"/><rect x="182" y="96" width="30" height="24" rx="5" fill="{GOLD}"/>
<rect x="60" y="158" width="44" height="42" rx="5" fill="#8FA9C0"/><rect x="112" y="166" width="30" height="34" rx="5" fill="{GOLD}"/>
<rect x="150" y="150" width="36" height="50" rx="5" fill="{BLUE}"/>
<!-- person -->
<path d="M230 560 C230 420 290 370 330 370 C370 370 430 420 430 560 Z" fill="{BLUE}"/>
<path d="M300 372 L330 420 L360 372 Z" fill="{WHITE}"/>
<rect x="316" y="330" width="28" height="42" rx="10" fill="{SKIN}"/>
<ellipse cx="330" cy="290" rx="52" ry="58" fill="{SKIN}"/>
<path d="M276 292 C268 220 330 205 368 228 C392 244 392 280 384 300 C376 268 350 250 318 252 C296 254 284 272 276 292 Z" fill="{HAIR}"/>
<circle cx="312" cy="296" r="4.5" fill="{NAVY}"/><circle cx="350" cy="296" r="4.5" fill="{NAVY}"/>
<path d="M318 322 Q331 330 344 322" stroke="{NAVY}" stroke-width="4" fill="none" stroke-linecap="round"/>
<!-- name badge -->
<rect x="372" y="430" width="38" height="24" rx="4" fill="{GOLD}"/>
<!-- counter and laptop -->
<rect x="150" y="470" width="420" height="90" rx="10" fill="{NAVY}"/>
<path d="M235 470 L262 395 L420 395 L400 470 Z" fill="#2A3543"/>
<rect x="210" y="466" width="240" height="10" rx="5" fill="#8FA9C0"/>
<circle cx="330" cy="432" r="9" fill="{PALE}"/>
<!-- question bubble -->
<rect x="390" y="150" width="190" height="104" rx="22" fill="{WHITE}" stroke="{NAVY}" stroke-width="4"/>
<path d="M410 250 L392 290 L440 252 Z" fill="{WHITE}" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/>
<rect x="408" y="248" width="40" height="8" fill="{WHITE}"/>
<text x="485" y="228" font-family="Georgia, serif" font-size="78" font-weight="700" fill="{GOLD}" text-anchor="middle">?</text>
<rect x="412" y="172" width="44" height="10" rx="5" fill="{PALE}"/><rect x="516" y="172" width="44" height="10" rx="5" fill="{PALE}"/>
"""

CLOSE = f"""
<rect width="600" height="700" fill="{NAVY}"/>
<g fill="#2A3543">{''.join(f'<circle cx="{x}" cy="{y}" r="3"/>' for x in range(20, 600, 40) for y in range(20, 700, 40))}</g>
<rect x="90" y="150" width="420" height="400" rx="34" fill="{WHITE}"/>
<circle cx="150" cy="215" r="30" fill="#2E8B57"/>
<path d="M136 215 L147 227 L166 203" stroke="{WHITE}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="198" y="198" width="220" height="16" rx="8" fill="{NAVY}"/><rect x="198" y="224" width="140" height="12" rx="6" fill="{PALE}"/>
<rect x="130" y="280" width="300" height="34" rx="10" fill="{BLUE}"/>
<rect x="130" y="326" width="120" height="34" rx="10" fill="{GOLD}"/>
<rect x="130" y="372" width="96" height="34" rx="10" fill="{GOLD}"/>
<rect x="130" y="418" width="64" height="34" rx="10" fill="{GOLD}"/>
<rect x="130" y="478" width="340" height="44" rx="12" fill="#EDF0F3"/>
<rect x="146" y="494" width="70" height="12" rx="6" fill="{BLUE}"/><rect x="226" y="494" width="110" height="12" rx="6" fill="#8FA9C0"/>
<rect x="346" y="494" width="60" height="12" rx="6" fill="{GOLD}"/>
"""


def page(svg, w, h):
    return ("<!doctype html><style>*{margin:0}body{background:transparent}</style>"
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{svg}</svg>')


with sync_playwright() as p:
    browser = p.chromium.launch()
    for name, svg, w, h in (("persona.png", PERSONA, 600, 560), ("close-answer.png", CLOSE, 600, 700)):
        tab = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        tab.set_content(page(svg, w, h))
        tab.screenshot(path=HERE / name, omit_background=True)
        print("wrote", name)
    browser.close()
