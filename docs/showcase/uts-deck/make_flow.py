"""Render the appendix flowchart (21 November 2026): one question's path as an executable flowchart.

Style after the owner's reference slide (rounded steps tagged code or model, a pass/fail branch with yes and no,
a dashed loop back, coloured end states), in the deck's colour key: yellow = the model, teal = enforced in code,
white = a plain app step, green = done, red = refused. HTML and inline SVG rendered with Playwright so the boxes
keep rounded corners, which the kit's native shapes do not support.

Run: uv run --no-project --with "playwright==1.60.0" python make_flow.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets/figures/flowchart.png"
W, H = 1000, 395   # CSS px; placed at 875.5 x 345.8 pt

INK, BODY, HAIR = "#1B2430", "#5A6370", "#C9CFD6"
STYLE = {   # fill, border, title colour
    "app": ("#FFFFFF", INK, INK),
    "code": ("#E4F2F1", "#21918C", INK),
    "model": ("#FDE725", "#FDE725", INK),
    "start": ("#EDF0F3", "#EDF0F3", INK),
    "stop": ("#FBE6E4", "#C0392B", "#8E2A1F"),
    "done": ("#DFF3E7", "#2E8B57", "#1F6B43"),
}


def node(x, y, w, h, kind, title, tag="", sub="", icon=""):
    fill, border, ink = STYLE[kind]
    inner = f'<div class="t" style="color:{ink}">{icon}{title}</div>'
    if sub:
        inner += f'<div class="s">{sub}</div>'
    if tag:
        inner += f'<div class="g">{tag}</div>'
    return (f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            f'border:2px solid {border}">{inner}</div>')


def label(x, y, text, colour=BODY, size=12, weight=400, align="left", w=200):
    return (f'<div class="l" style="left:{x}px;top:{y}px;width:{w}px;color:{colour};font-size:{size}px;'
            f'font-weight:{weight};text-align:{align}">{text}</div>')


ARROW = (f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
         f'<marker id="d" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#21918C"/></marker></defs>')


def path(d, dashed=False):
    colour = "#21918C" if dashed else INK
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    marker = "d" if dashed else "a"
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.8"{dash} marker-end="url(#{marker})"/>'


# Row 1: ask -> read schema -> select tables -> generate (model) -> validate (gate 1)
nodes = [
    node(0, 58, 118, 64, "start", "a plain question", sub="from the person"),
    node(140, 50, 128, 80, "app", "read schema", tag="code", sub="tables, keys, hints"),
    node(290, 50, 140, 80, "app", "select tables", tag="code", sub="top 6 + neighbours"),
    node(452, 20, 200, 140, "model", "generate", icon="&#10022;&#8201;", sub="the one model call"),
    node(674, 50, 140, 80, "code", "validate", tag="code: gate 1", sub="sqlglot"),
    node(836, 58, 72, 64, "app", "one read?"),
    # Row 2
    node(836, 210, 164, 80, "code", "run read-only", tag="code: gate 2", sub="budget, 1,000-row cap"),
    node(600, 222, 200, 64, "stop", "refused, explained", icon="&#10007;&#8201;", sub="nothing reaches the engine"),
    node(836, 322, 164, 60, "done", "answer shown", icon="&#10003;&#8201;", sub="with the SQL and tables"),
]
# the model's two providers, as chips inside the generate box
chips = ('<div class="c" style="left:470px;top:78px;width:76px">Ollama</div>'
         '<div class="c" style="left:558px;top:78px;width:76px">Gemini</div>'
         + label(452, 118, "writes one SQL statement,<br>or declines", INK, 12, 400, "center", 200))
arrows = [
    path("M118,90 L138,90"), path("M268,90 L288,90"), path("M430,90 L450,90"),
    path("M652,90 L672,90"), path("M814,90 L834,90"),
    path("M872,122 L872,208"),                         # yes: one read -> run
    path("M850,122 L850,168 L700,168 L700,220"),       # no: refused
    path("M918,290 L918,320"),                         # run -> answer
    path("M846,290 L846,304 L552,304 L552,162", True),  # query error: one repair try
]
labels = [
    label(880, 150, "yes", "#2E8B57", 12, 700),
    label(756, 150, "no", "#C0392B", 12, 700, "right", 90),
    label(566, 310, "query error: one repair try, then both gates again", "#21918C", 12, 400, "left", 262),
    label(330, 178, "a decline also ends<br>at <b>refused</b>", BODY, 11, 400, "right", 212),
]
# legend and reading notes in the empty lower left
legend = [
    ('<div class="k" style="background:#FFFFFF;border:2px solid ' + INK + '"></div>', "app step, plain code"),
    ('<div class="k" style="background:#E4F2F1;border:2px solid #21918C"></div>', "a gate enforced in code"),
    ('<div class="k" style="background:#FDE725;border:2px solid #FDE725"></div>', "the model: behaviour, not a guarantee"),
    ('<div class="k" style="background:#DFF3E7;border:2px solid #2E8B57"></div>', "end state: answer shown"),
    ('<div class="k" style="background:#FBE6E4;border:2px solid #C0392B"></div>', "end state: refused and explained"),
]
leg = "".join(f'<div class="r" style="left:0px;top:{218 + i * 26}px">{k}<span>{t}</span></div>'
              for i, (k, t) in enumerate(legend))
leg += label(300, 218, "Every question takes this path on its own.<br>Nothing checks meaning: the person reads<br>"
             "the SQL before trusting the answer.", BODY, 12, 400, "left", 280)

import base64
B64 = {w: base64.b64encode((HERE / f"assets/fonts/GoogleSans-{w}.ttf").read_bytes()).decode() for w in ("Regular", "Bold")}
html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Regular']}); font-weight: 400; }}
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Bold']}); font-weight: 700; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; position: relative; font-family: GS; background: transparent; }}
.n {{ position: absolute; border-radius: 16px; display: flex; flex-direction: column; justify-content: center;
     align-items: center; text-align: center; padding: 6px 8px; }}
.t {{ font-size: 17px; font-weight: 700; line-height: 1.15; }}
.s {{ font-size: 12px; color: {BODY}; line-height: 1.25; margin-top: 3px; }}
.g {{ font-size: 11px; color: {INK}; letter-spacing: .02em; margin-top: 3px; opacity: .8; }}
.c {{ position: absolute; height: 30px; border-radius: 10px; background: #FFFFFF; font-size: 13px; font-weight: 700;
     color: {INK}; display: flex; align-items: center; justify-content: center; }}
.l {{ position: absolute; line-height: 1.3; }}
.r {{ position: absolute; display: flex; align-items: center; gap: 10px; font-size: 12px; color: {INK}; }}
.k {{ width: 26px; height: 16px; border-radius: 5px; }}
svg {{ position: absolute; left: 0; top: 0; }}
</style><body>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{ARROW}{''.join(arrows)}</svg>
{''.join(nodes)}{chips}{''.join(labels)}{leg}
</body>"""
# the generate box's own title sits at its top
html = html.replace('class="n" style="left:452px;top:20px;width:200px;height:140px;',
                    'class="n" style="left:452px;top:20px;width:200px;height:140px;justify-content:flex-start;padding-top:12px;')

with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=3)
    tab.set_content(html)
    tab.wait_for_timeout(300)
    tab.screenshot(path=OUT, omit_background=True)
    browser.close()
print("wrote", OUT.name)
