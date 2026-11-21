"""Render the appendix flowchart (21 November 2026, round 3): one question's path, split into four stage lanes.

Lanes, left to right: 1 Prepare (app, no model), 2 Generate (the model), 3 Check and run (enforced in code),
4 Answer (the person). Each lane's header names its kind, so the header row is the legend. Steps are rounded cards
with an icon or the tool's logo; decisions branch yes and no; a dashed loop runs back for the one repair try;
end states are green (answer) or red (refused, stopped). Smaller type than round 2; the image starts just under
the title, using the space the dropped subtitle left.

Run: uv run --no-project --with "playwright==1.60.0" python make_flow.py
"""

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets/figures/flowchart.png"
W, H = 1000, 432   # CSS px; placed at 875.5 x 378 pt, from just under the title to the content floor

INK, BODY = "#1B2430", "#5A6370"
STYLE = {   # fill, border, title colour
    "app": ("#FFFFFF", INK, INK),
    "code": ("#FFFFFF", "#21918C", INK),
    "model": ("#FDE725", "#FDE725", INK),
    "stop": ("#FBE6E4", "#C0392B", "#8E2A1F"),
    "done": ("#DFF3E7", "#2E8B57", "#1F6B43"),
    "note": ("#FFFFFF", "#FFFFFF", INK),
}
LANES = [   # x, width, header, kind label, lane tint, header colour
    (0, 330, "1  Prepare", "app step, no model", "#F4F5F6", INK),
    (342, 196, "2  Generate", "the model: behaviour", "#FEF8D2", INK),
    (550, 258, "3  Check and run", "gates enforced in code", "#E9F4F3", "#14605C"),
    (820, 180, "4  Answer", "for the person", "#EAF5EE", "#1F6B43"),
]
I = "assets/icons/"


def uri(rel):
    data = (HERE / rel).read_bytes()
    kind = "svg+xml" if rel.endswith(".svg") else "png"
    return f"data:image/{kind};base64,{base64.b64encode(data).decode()}"


def img(rel, size=15):
    return f'<img src="{uri(rel)}" style="width:{size}px;height:{size}px;object-fit:contain;flex:none">'


def node(x, y, w, h, kind, title, sub="", tag="", art=(), radius=12, align="center", logos=()):
    fill, border, ink = STYLE[kind]
    icons = "".join(img(a) for a in art)
    head = f'<div class="h">{icons}<span style="color:{ink}">{title}</span></div>'
    body = f'<div class="s">{sub}</div>' if sub else ""
    marks = "".join(img(a, 13) for a in logos)
    foot = f'<div class="g">{marks}<span>{tag}</span></div>' if (tag or logos) else ""
    return (f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            f'border:1.6px solid {border};border-radius:{radius}px;justify-content:{align}">{head}{body}{foot}</div>')


def text(x, y, w, html, colour=BODY, size=10, weight=400, align="left"):
    return (f'<div class="l" style="left:{x}px;top:{y}px;width:{w}px;color:{colour};font-size:{size}px;'
            f'font-weight:{weight};text-align:{align}">{html}</div>')


DEFS = ('<defs>' + "".join(
    f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for k, c in (("a", INK), ("d", "#21918C"), ("r", "#C0392B"), ("g", "#2E8B57"))) + '</defs>')


def path(d, kind="a"):
    colour = {"a": INK, "d": "#21918C", "r": "#C0392B", "g": "#2E8B57"}[kind]
    dash = ' stroke-dasharray="5 4"' if kind == "d" else ""
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.5"{dash} marker-end="url(#{kind})"/>'


# Lanes: tinted columns with a header that doubles as the legend
lanes = ""
for x, w, head, kind, tint, colour in LANES:
    lanes += (f'<div class="lane" style="left:{x}px;width:{w}px;background:{tint}"></div>'
              f'<div class="lh" style="left:{x}px;width:{w}px;color:{colour}"><b>{head}</b><span>{kind}</span></div>')

Y = 40   # first row of steps, under the lane headers
nodes = [
    # 1 Prepare: ask, then a column down: read schema, select tables, build prompt
    node(10, Y, 150, 66, "app", "ask", "a plain question, a database and a model", art=(f"{I}person-ink.png",),
         align="flex-start"),
    node(172, Y, 148, 84, "app", "read schema", "tables, columns, keys; up to 6 values from small text columns",
         tag="code", art=(f"{I}schema-ink.png",), logos=("assets/logos/tech-python.png",), align="flex-start"),
    node(172, Y + 100, 148, 84, "app", "select tables", "score every table; keep the top 6 plus foreign-key neighbours",
         tag="code", art=(f"{I}table_rows-ink.png",), logos=("assets/logos/tech-python.png",), align="flex-start"),
    node(172, Y + 200, 148, 70, "app", "build prompt", "dialect rules, the schema and the question",
         tag="code", art=(f"{I}description-ink.png",), logos=("assets/logos/tech-langchain.png",), align="flex-start"),
    # 2 Generate
    node(352, Y + 162, 176, 138, "model", "generate", "the one model call", art=(f"{I}code-ink.png",),
         align="flex-start"),
    # 3 Check and run: down the lane, exits to the right
    node(560, Y, 132, 76, "code", "validate", "one SELECT or WITH; no writes or internals",
         tag="code: gate 1", logos=("assets/logos/tech-sqlglot.png",), align="flex-start"),
    node(578, Y + 96, 96, 44, "app", "one read?", radius=10),
    node(560, Y + 160, 132, 80, "code", "run read-only", "work budget; result cut at 1,000 rows", tag="code: gate 2",
         logos=("assets/logos/tech-sqlite.png", "assets/logos/tech-duckdb.png", "assets/logos/tech-postgresql.png"),
         align="flex-start"),
    node(572, Y + 262, 108, 44, "app", "query error?", radius=10),
    node(706, Y + 82, 94, 76, "stop", "&#10007; refused", "explained in plain words; nothing runs", align="flex-start"),
    node(706, Y + 172, 94, 76, "stop", "&#10007; stopped", "over the work budget; not retried", align="flex-start"),
    # 4 Answer
    node(830, Y, 160, 250, "app", "show", "", art=("assets/logos/tech-streamlit.png", "assets/logos/tech-pandas.png"),
         align="flex-start"),
    node(830, Y + 316, 160, 66, "done", "&#10003; the person inspects", "reads the SQL before trusting the answer",
         align="flex-start"),
]
# inside generate: providers as chips, then what it does
gen = (f'<div class="c" style="left:362px;top:{Y + 214}px;width:76px">{img("assets/logos/tech-ollama.png", 14)}Ollama</div>'
       f'<div class="c" style="left:442px;top:{Y + 214}px;width:76px">{img("assets/logos/tech-googlegemini.png", 14)}Gemini</div>'
       + text(362, Y + 250, 156, "writes one SQL statement, or <b>declines</b> a write or an unanswerable question",
              INK, 10, 400))
# a model note above generate, in the empty top of its lane
gen += node(352, Y, 176, 140, "note", "about the model",
            "Gemini is hosted; Ollama runs locally. A hosted model receives the whole prompt: the question, "
            "the schema and the hints. Thinking is off by default. Its declines are behaviour, not a guarantee.",
            art=(f"{I}help-ink.png",), align="flex-start")
# what the person sees, listed inside show
seen = [("description", "a one-line answer"), ("table_rows", "the result table"), ("monitoring", "a bar chart, when it suits"),
        ("code", "the SQL, highlighted"), ("schema", "tables chosen, and why"), ("chat", "errors in plain words")]
show = "".join(f'<div class="li" style="left:840px;top:{Y + 34 + i * 34}px">{img(f"{I}{a}-ink.png", 14)}<span>{t}</span></div>'
               for i, (a, t) in enumerate(seen))
# lower left of Prepare: what the flow guarantees
facts = [(f"{I}fact_check-ink.png", "Rows stay out", "the model sees the schema and a few hints, never result rows"),
         (f"{I}verified_user-ink.png", "Read-only twice", "sqlglot, then a read-only engine; 15 conformance tests each"),
         (f"{I}timer-ink.png", "Cached per schema", "the schema and its index are reused until the schema changes")]
cards = "".join(f'<div class="f" style="left:10px;top:{Y + 92 + i * 100}px;width:150px;height:90px">'
                f'<div class="h">{img(a)}<span>{h}</span></div><div class="s">{b}</div></div>'
                for i, (a, h, b) in enumerate(facts))
cards += node(172, Y + 290, 148, 92, "note", "one question at a time",
              "earlier questions are not sent; each answer is built from this path alone",
              art=(f"{I}chat-ink.png",), align="flex-start")

arrows = [
    path(f"M160,{Y + 33} L170,{Y + 33}"),                       # ask -> read schema
    path(f"M246,{Y + 84} L246,{Y + 98}"),                       # read schema -> select tables
    path(f"M246,{Y + 184} L246,{Y + 198}"),                     # select tables -> build prompt
    path(f"M320,{Y + 235} L350,{Y + 235}"),                     # build prompt -> generate
    path(f"M528,{Y + 235} L540,{Y + 235} L540,{Y + 33} L558,{Y + 33}"),   # generate -> validate
    path(f"M626,{Y + 76} L626,{Y + 94}"),                       # validate -> one read?
    path(f"M626,{Y + 140} L626,{Y + 158}", "g"),                # yes -> run
    path(f"M674,{Y + 118} L704,{Y + 118}", "r"),                # no -> refused
    path(f"M692,{Y + 210} L704,{Y + 210}", "r"),                # budget -> stopped
    path(f"M626,{Y + 240} L626,{Y + 260}"),                     # run -> query error?
    path(f"M684,{Y + 275} L760,{Y + 275} L760,{Y + 326} L828,{Y + 326}", "g"),   # no error -> answer lane
    path(f"M910,{Y + 250} L910,{Y + 314}"),                     # show -> person
    path(f"M572,{Y + 284} L556,{Y + 284} L556,{Y + 330} L440,{Y + 330} L440,{Y + 302}", "d"),   # repair
]
# show is reached from below: the green arrow ends at the show card's lower edge
arrows[-3] = path(f"M680,{Y + 284} L812,{Y + 284} L812,{Y + 230} L828,{Y + 230}", "g")
labels = [
    text(631, Y + 141, 30, "yes", "#2E8B57", 10, 700), text(678, Y + 103, 26, "no", "#C0392B", 10, 700),
    text(686, Y + 268, 40, "no", "#2E8B57", 10, 700),
    text(352, Y + 338, 176, "yes: one repair try, then both gates again", "#21918C", 10, 700, "center"),
]

B64 = {w: base64.b64encode((HERE / f"assets/fonts/GoogleSans-{w}.ttf").read_bytes()).decode()
       for w in ("Regular", "Bold")}
html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Regular']}); font-weight: 400; }}
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Bold']}); font-weight: 700; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; position: relative; font-family: GS; background: transparent; }}
.lane {{ position: absolute; top: 0; height: {H}px; border-radius: 12px; }}
.lh {{ position: absolute; top: 8px; padding: 0 10px; display: flex; align-items: baseline; gap: 8px; font-size: 13px; }}
.lh span {{ font-size: 10px; color: {BODY}; }}
.n {{ position: absolute; display: flex; flex-direction: column; align-items: flex-start; padding: 7px 9px; }}
.h {{ display: flex; align-items: center; gap: 5px; font-size: 13px; font-weight: 700; line-height: 1.1; }}
.s {{ font-size: 10px; color: {BODY}; line-height: 1.3; margin-top: 4px; }}
.g {{ font-size: 9px; color: {INK}; margin-top: auto; padding-top: 3px; letter-spacing: .02em; display: flex; align-items: center; gap: 4px; }}
.g span {{ opacity: .7; }}
.c {{ position: absolute; height: 26px; border-radius: 9px; background: #FFFFFF; font-size: 11px; font-weight: 700;
     color: {INK}; display: flex; align-items: center; justify-content: center; gap: 5px; }}
.l {{ position: absolute; line-height: 1.3; }}
.li {{ position: absolute; display: flex; align-items: center; gap: 7px; font-size: 11px; color: {INK}; }}
.f {{ position: absolute; background: #FFFFFF; border-radius: 12px; padding: 7px 9px; }}
.f .h {{ font-size: 12px; }}
svg {{ position: absolute; left: 0; top: 0; }}
</style><body>
{lanes}
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}{''.join(arrows)}</svg>
{''.join(nodes)}{gen}{show}{cards}{''.join(labels)}
</body>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=3)
    tab.set_content(html)
    tab.wait_for_timeout(400)
    tab.screenshot(path=OUT, omit_background=True)
    browser.close()
print("wrote", OUT.name)
