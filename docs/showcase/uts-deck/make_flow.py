"""Render the appendix flowchart (21 November 2026, round 2): one question's path, in detail, filling the page.

Style after the owner's reference slide: rounded steps tagged code or model, decisions with yes and no branches,
a dashed loop back, coloured end states. Legend on top. Each card carries its icon or the tool's logo.
Colour key as the rest of the deck: yellow = the model, teal = enforced in code, white = a plain app step,
green = answer shown, red = stopped and explained.

Run: uv run --no-project --with "playwright==1.60.0" python make_flow.py
"""

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets/figures/flowchart.png"
W, H = 1000, 393   # CSS px; placed at 875.5 x 344 pt (the whole content area)

INK, BODY = "#1B2430", "#5A6370"
STYLE = {   # fill, border, title colour
    "app": ("#FFFFFF", INK, INK),
    "code": ("#E4F2F1", "#21918C", INK),
    "model": ("#FDE725", "#FDE725", INK),
    "start": ("#EDF0F3", "#EDF0F3", INK),
    "stop": ("#FBE6E4", "#C0392B", "#8E2A1F"),
    "done": ("#DFF3E7", "#2E8B57", "#1F6B43"),
}


def uri(rel):
    data = (HERE / rel).read_bytes()
    kind = "svg+xml" if rel.endswith(".svg") else "png"
    return f"data:image/{kind};base64,{base64.b64encode(data).decode()}"


def img(rel, size=18):
    return f'<img src="{uri(rel)}" style="width:{size}px;height:{size}px;object-fit:contain">'


def node(x, y, w, h, kind, title, sub="", tag="", art=(), shape="16px", top=False):
    fill, border, ink = STYLE[kind]
    icons = "".join(img(a, 17) for a in art)
    head = f'<div class="h">{icons}<span style="color:{ink}">{title}</span></div>'
    body = f'<div class="s">{sub}</div>' if sub else ""
    foot = f'<div class="g">{tag}</div>' if tag else ""
    align = "flex-start" if top else "center"
    return (f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            f'border:2px solid {border};border-radius:{shape};justify-content:{align}">{head}{body}{foot}</div>')


def text(x, y, w, html, colour=BODY, size=11, weight=400, align="left"):
    return (f'<div class="l" style="left:{x}px;top:{y}px;width:{w}px;color:{colour};font-size:{size}px;'
            f'font-weight:{weight};text-align:{align}">{html}</div>')


DEFS = ('<defs>'
        + "".join(f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                  f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                  for k, c in (("a", INK), ("d", "#21918C"), ("r", "#C0392B")))
        + '</defs>')


def path(d, kind="a"):
    colour = {"a": INK, "d": "#21918C", "r": "#C0392B"}[kind]
    dash = ' stroke-dasharray="6 5"' if kind == "d" else ""
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.8"{dash} marker-end="url(#{kind})"/>'


I = "assets/icons/"

# Legend on top
legend = [("app", "app step, plain code"), ("code", "gate enforced in code"), ("model", "the model: behaviour"),
          ("done", "answer shown"), ("stop", "stopped and explained")]
leg, x = "", 0
for kind, lab in legend:
    fill, border, _ = STYLE[kind]
    leg += (f'<div class="r" style="left:{x}px;top:0px"><div class="k" style="background:{fill};'
            f'border:2px solid {border}"></div><span>{lab}</span></div>')
    x += 40 + len(lab) * 5.6
leg += text(x + 4, 2, 1000 - x - 4, "Each question takes this path on its own.", BODY, 11, 400, "right")

R1, R1H = 36, 104          # top row
R2, R2H = 186, 88          # lower row
nodes = [
    node(0, R1, 130, R1H, "start", "ask", "a plain question, a database and a model",
         art=(f"{I}person-ink.png",), tag="Streamlit"),
    node(148, R1, 140, R1H, "app", "read schema", "tables, columns, keys; up to 6 values from small text columns",
         art=(f"{I}schema-ink.png",), tag="code"),
    node(306, R1, 140, R1H, "app", "select tables", "score every table; keep the top 6 plus foreign-key neighbours",
         art=(f"{I}table_rows-ink.png",), tag="code"),
    node(464, R1, 140, R1H, "app", "build prompt", "dialect rules, schema and question; never result rows",
         art=(f"{I}description-ink.png",), tag="code"),
    node(622, R1 - 10, 200, R1H + 30, "model", "generate", "the one model call", top=True,
         art=(f"{I}code-ink.png",)),
    node(842, R1, 158, R1H, "code", "validate", "sqlglot: one SELECT or WITH; no writes, no engine internals",
         art=("assets/logos/tech-sqlglot.png",), tag="code: gate 1"),
    # lower row, right to left
    node(882, R2 + 8, 78, 70, "app", "one read?", shape="12px"),
    node(650, R2, 196, R2H, "code", "run read-only", "work budget; result cut at 1,000 rows",
         art=("assets/logos/tech-sqlite.png", "assets/logos/tech-duckdb.png", "assets/logos/tech-postgresql.png"),
         tag="code: gate 2"),
    node(524, R2 + 8, 90, 70, "app", "query error?", shape="12px"),
    node(300, R2, 190, R2H, "app", "show", "answer, table, a chart when it suits, the SQL and the tables chosen",
         art=("assets/logos/tech-streamlit.png", "assets/logos/tech-pandas.png"), tag="code"),
    node(0, R2, 262, R2H, "done", "&#10003; the person inspects",
         "reads the SQL before trusting the answer; nothing else checks meaning", art=(f"{I}person-ink.png",)),
    # end states below
    node(842, 312, 158, 74, "stop", "&#10007; refused", "explained in plain words; nothing reaches the engine"),
    node(650, 312, 172, 74, "stop", "&#10007; stopped", "over the work budget; not retried"),
]
# inside the generate card: providers as chips with logos, then what it does
gen = ('<div class="c" style="left:636px;top:80px;width:82px">' + img("assets/logos/tech-ollama.png", 16) + 'Ollama</div>'
       '<div class="c" style="left:726px;top:80px;width:82px">' + img("assets/logos/tech-googlegemini.png", 16) + 'Gemini</div>'
       + text(630, 118, 184, "writes one SQL statement,<br>or <b>declines</b> a write or an<br>unanswerable question", INK, 11, 400, "center"))
arrows = [
    path("M130,88 L146,88"), path("M288,88 L304,88"), path("M446,88 L462,88"), path("M604,88 L620,88"),
    path("M822,88 L840,88"),
    path("M921,140 L921,192"),                              # validate -> one read?
    path("M882,230 L848,230"),                              # yes -> run
    path("M960,230 L974,230 L974,310", "r"),                # no -> refused
    path("M650,230 L616,230"),                              # run -> query error?
    path("M736,274 L736,310", "r"),                         # budget stop -> stopped
    path("M524,230 L492,230"),                              # no error -> show
    path("M300,230 L264,230"),                              # show -> person
    path("M569,186 L569,178 L700,178 L700,166", "d"),       # error: one repair try, back to generate
]
labels = [
    text(852, 212, 30, "yes", "#2E8B57", 11, 700), text(980, 250, 20, "no", "#C0392B", 11, 700),
    text(494, 212, 30, "no", "#2E8B57", 11, 700), text(742, 286, 90, "budget", "#C0392B", 11, 700),
    text(470, 160, 160, "yes: one repair try", "#21918C", 11, 700, "right"),
    text(708, 168, 130, "then both gates again", "#21918C", 11, 400),
]
# lower left: what the flow guarantees, as three small cards
facts = [
    (f"{I}verified_user-ink.png", "Read-only twice", "sqlglot, then a read-only engine; 15 conformance tests per engine"),
    (f"{I}fact_check-ink.png", "Rows stay out", "the model sees the schema and a few hints, never result rows"),
    (f"{I}chat-ink.png", "Declines end safely", "a model decline is explained like a refusal"),
]
fx = 0
for art, head, body in facts:
    nodes.append(f'<div class="f" style="left:{fx}px;top:312px;width:196px;height:74px">'
                 f'<div class="h">{img(art, 16)}<span>{head}</span></div><div class="s">{body}</div></div>')
    fx += 210

B64 = {w: base64.b64encode((HERE / f"assets/fonts/GoogleSans-{w}.ttf").read_bytes()).decode()
       for w in ("Regular", "Bold")}
html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Regular']}); font-weight: 400; }}
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Bold']}); font-weight: 700; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; position: relative; font-family: GS; background: transparent; }}
.n {{ position: absolute; display: flex; flex-direction: column; align-items: flex-start; padding: 8px 10px; }}
.h {{ display: flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 700; line-height: 1.1; }}
.s {{ font-size: 11px; color: {BODY}; line-height: 1.3; margin-top: 5px; }}
.g {{ font-size: 10px; color: {INK}; opacity: .75; margin-top: auto; padding-top: 4px; letter-spacing: .02em; }}
.c {{ position: absolute; height: 30px; border-radius: 10px; background: #FFFFFF; font-size: 12px; font-weight: 700;
     color: {INK}; display: flex; align-items: center; justify-content: center; gap: 5px; }}
.l {{ position: absolute; line-height: 1.3; }}
.r {{ position: absolute; display: flex; align-items: center; gap: 7px; font-size: 11px; color: {INK}; }}
.k {{ width: 24px; height: 14px; border-radius: 5px; }}
.f {{ position: absolute; background: #F4F5F6; border-radius: 12px; padding: 8px 10px; }}
.f .h {{ font-size: 13px; }}
svg {{ position: absolute; left: 0; top: 0; }}
</style><body>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}{''.join(arrows)}</svg>
{leg}{''.join(nodes)}{gen}{''.join(labels)}
</body>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=3)
    tab.set_content(html)
    tab.wait_for_timeout(400)
    tab.screenshot(path=OUT, omit_background=True)
    browser.close()
print("wrote", OUT.name)
