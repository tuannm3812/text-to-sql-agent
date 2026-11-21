"""Render the appendix flowchart (21 November 2026, round 5): one question's path in four stage lanes.

Layout: lanes run left to right (Prepare, Generate, Check and run, Answer); inside each lane the steps run top to
bottom on a shared row grid; a band across the bottom holds what the whole flow guarantees. Its own smaller type.
Round 5: card text as short bullets, steps numbered 1 to 8 in circles, an icon on every block, arrows rechecked and
drawn with rounded corners; refused and stopped now lead to the answer card's plain-language error.

Block colour rules (one meaning per style):
- lane tint and header colour = the stage
- step card = white with a border in its lane's colour (Prepare ink, Check and run teal, Answer green)
- the one model call = the only solid yellow card
- decision = white pill with its lane's border
- end state = tinted card: green for the answer, red for refused or stopped
- note = white with no border (context, not a step)

Run: uv run --no-project --with "playwright==1.60.0" python make_flow.py
"""

import base64
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets/figures/flowchart.png"
W, H = 1000, 432   # CSS px; placed at 875.5 x 378 pt, from just under the title to the content floor

INK, BODY = "#1B2430", "#5A6370"
TEAL, GREEN, RED, YELLOW = "#21918C", "#2E8B57", "#C0392B", "#FDE725"
I = "assets/icons/"

LANES = {   # x, width, title, kind, tint, lane colour
    "prep": (0, 178, "Prepare", "app steps, no model", "#F1F3F5", INK),
    "gen": (188, 232, "Generate", "the model", "#FEF8D2", "#7A6A00"),
    "check": (430, 330, "Check and run", "gates enforced in code", "#E7F3F2", TEAL),
    "ans": (770, 230, "Answer", "for the person", "#E8F4EC", GREEN),
}
ROWS = [34, 112, 190, 268]   # tops of the four step rows
RH = 70                      # row card height
BAND = (346, 84)             # guarantee band: top, height


def uri(rel):
    data = (HERE / rel).read_bytes()
    kind = "svg+xml" if rel.endswith(".svg") else "png"
    return f"data:image/{kind};base64,{base64.b64encode(data).decode()}"


def img(rel, size=13):
    return f'<img src="{uri(rel)}" style="width:{size}px;height:{size}px;object-fit:contain;flex:none">'


def bullets(items, numbered=False):
    """Short bullets. Under a numbered title the dots sit under the number and the text under the title."""
    cls = "b bn" if numbered else "b"
    return f'<ul class="{cls}">' + "".join(f"<li>{t}</li>" for t in items) + "</ul>"


def card(x, y, w, h, style, title, items=(), tag="", icon=None, logos=(), lane="prep", n=None):
    colour = LANES[lane][5]
    fill, border, ink, radius = {
        "step": ("#FFFFFF", colour, INK, 10),
        "model": (YELLOW, YELLOW, INK, 10),
        "decision": ("#FFFFFF", colour, INK, 30),
        "done": ("#DFF3E7", GREEN, "#1F6B43", 10),
        "stop": ("#FBE6E4", RED, "#8E2A1F", 10),
        "note": ("#FFFFFF", "#FFFFFF", INK, 10),
    }[style]
    num = (f'<span class="num" style="background:{colour if style != "model" else INK}">{n}</span>'
           if n is not None else "")
    art = "".join(img(a, 13) for a in logos) if logos else (img(icon, 14) if icon else "")
    head = f'<div class="h">{num}<span style="color:{ink}">{title}</span><span class="ic">{art}</span></div>'
    body = bullets(items, n is not None) if items else ""
    foot = f'<div class="g"><span>{tag}</span></div>' if tag else ""
    decision = style == "decision"
    return (f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            f'border:1.5px solid {border};border-radius:{radius}px;'
            f'justify-content:{"center" if decision else "flex-start"};'
            f'align-items:{"center" if decision else "stretch"}">{head}{body}{foot}</div>')


def text(x, y, w, html, colour=BODY, size=9, weight=400, align="left"):
    return (f'<div class="l" style="left:{x}px;top:{y}px;width:{w}px;color:{colour};font-size:{size}px;'
            f'font-weight:{weight};text-align:{align}">{html}</div>')


COLOURS = {"a": INK, "d": TEAL, "r": RED, "g": GREEN}
DEFS = '<defs>' + "".join(
    f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for k, c in COLOURS.items()) + '</defs>'


def route(points, kind="a", r=7):
    """An orthogonal connector through the points, with rounded corners and an arrowhead at the end."""
    d = f"M{points[0][0]},{points[0][1]}"
    for (x0, y0), (x1, y1), (x2, y2) in zip(points, points[1:], points[2:]):
        ax = x1 - r * ((x1 > x0) - (x1 < x0))
        ay = y1 - r * ((y1 > y0) - (y1 < y0))
        bx = x1 + r * ((x2 > x1) - (x2 < x1))
        by = y1 + r * ((y2 > y1) - (y2 < y1))
        d += f" L{ax},{ay} Q{x1},{y1} {bx},{by}"
    d += f" L{points[-1][0]},{points[-1][1]}"
    dash = ' stroke-dasharray="5 4"' if kind == "d" else ""
    return (f'<path d="{d}" fill="none" stroke="{COLOURS[kind]}" stroke-width="1.4" stroke-linejoin="round"'
            f'{dash} marker-end="url(#{kind})"/>')


def mid(row):
    return ROWS[row] + RH / 2


lanes = "".join(
    f'<div class="lane" style="left:{x}px;width:{w}px;background:{tint}"></div>'
    f'<div class="lh" style="left:{x}px;width:{w}px;color:{col}"><b>{t}</b><span>{k}</span></div>'
    for x, w, t, k, tint, col in LANES.values())

# 1 Prepare
px, pw = 10, 158
cards = [
    card(px, ROWS[0], pw, RH, "step", "ask", ["a plain question", "a database or CSV files", "Gemini or Ollama"],
         logos=(f"{I}person-ink.png", "assets/logos/tech-streamlit.png"), n=1),
    card(px, ROWS[1], pw, RH, "step", "read schema", ["tables, columns and keys", "up to 6 sample values", "cached per schema"],
         logos=(f"{I}schema-ink.png", "assets/logos/tech-python.png"), n=2),
    card(px, ROWS[2], pw, RH, "step", "select tables", ["score every table", "keep the top 6", "add foreign-key neighbours"],
         logos=(f"{I}table_rows-ink.png", "assets/logos/tech-python.png"), n=3),
    card(px, ROWS[3], pw, RH, "step", "build prompt", ["dialect rules", "the schema and the question", "never result rows"],
         logos=(f"{I}description-ink.png", "assets/logos/tech-langchain.png"), n=4),
]
# 2 Generate
gx, gw = 198, 168   # leaves a strip on the right of the lane for the repair loop's label
cards += [
    card(gx, ROWS[0], gw, ROWS[1] + RH - ROWS[0], "note", "about the model",
         ["Gemini is hosted; Ollama runs locally", "a hosted model receives the whole prompt",
          "thinking is off by default", "a decline is behaviour, not a guarantee"], icon=f"{I}help-ink.png", lane="gen"),
    card(gx, ROWS[2], gw, ROWS[3] + RH - ROWS[2], "model", "generate", tag="the one model call",
         icon=f"{I}code-ink.png", lane="gen", n=5),
]
chips = (f'<div class="c" style="left:{gx + 10}px;top:{ROWS[2] + 30}px;width:71px">'
         f'{img("assets/logos/tech-ollama.png", 13)}Ollama</div>'
         f'<div class="c" style="left:{gx + 87}px;top:{ROWS[2] + 30}px;width:71px">'
         f'{img("assets/logos/tech-googlegemini.png", 13)}Gemini</div>'
         f'<div style="position:absolute;left:{gx + 10}px;top:{ROWS[2] + 64}px;width:{gw - 20}px">'
         + bullets(["writes one SQL statement", "or <b>declines</b> a write", "or a question the schema cannot answer"])
         + "</div>")
# 3 Check and run
cx, cw = 440, 160
ex, ew = 636, 114
cards += [
    card(cx, ROWS[0], cw, RH, "step", "validate", ["gate 1: one SELECT or WITH", "no writes, no engine internals", "parsed by sqlglot"],
         logos=(f"{I}verified_user-teal.png", "assets/logos/tech-sqlglot.png"), lane="check", n=6),
    card(cx + 24, ROWS[1] + 12, cw - 48, RH - 24, "decision", "one read?", icon=f"{I}help-teal.png", lane="check"),
    card(cx, ROWS[2], cw, RH, "step", "run", ["gate 2: read-only connection", "work budget", "result cut at 1,000 rows"],
         logos=("assets/logos/tech-sqlite.png", "assets/logos/tech-duckdb.png", "assets/logos/tech-postgresql.png"),
         lane="check", n=7),
    card(cx + 24, ROWS[3] + 12, cw - 48, RH - 24, "decision", "query error?", icon=f"{I}help-teal.png", lane="check"),
    card(ex, ROWS[1], ew, RH, "stop", "refused", ["nothing runs", "explained in plain words"], icon=f"{I}cancel-red.png"),
    card(ex, ROWS[2], ew, RH, "stop", "stopped", ["over the work budget", "not retried"], icon=f"{I}timer-red.png"),
]
# 4 Answer
ax, aw = 780, 210
cards += [
    card(ax, ROWS[0], aw, ROWS[2] + RH - ROWS[0], "step", "show",
         logos=("assets/logos/tech-streamlit.png", "assets/logos/tech-pandas.png"), tag="what the person sees",
         lane="ans", n=8),
    card(ax, ROWS[3], aw, RH, "done", "the person inspects",
         ["reads the SQL before trusting the answer", "nothing else checks meaning"], icon=f"{I}check_circle-green.png"),
]
seen = [("description", "a one-line answer"), ("table_rows", "the result table"),
        ("trending_up", "a bar chart, when it suits"), ("code", "the SQL, highlighted"),
        ("schema", "the tables chosen, and why"), ("chat", "errors in plain words")]
show = "".join(f'<div class="li" style="left:{ax + 14}px;top:{ROWS[0] + 32 + i * 30}px">'
               f'{img(f"{I}{a}-ink.png", 13)}<span>{t}</span></div>' for i, (a, t) in enumerate(seen))

# guarantee band
by, bh = BAND
facts = [(f"{I}fact_check-ink.png", "Rows stay out", ["the schema and a few hints only", "never result rows"]),
         (f"{I}verified_user-ink.png", "Read-only twice",
          ["sqlglot, then a read-only engine", "15 conformance tests per engine"]),
         (f"{I}timer-ink.png", "Cached per schema", ["schema and index reused", "until the schema changes"]),
         (f"{I}chat-ink.png", "One question at a time", ["earlier questions are not sent", "each answer stands alone"])]
fw = (W - 20 - 3 * 10) / 4
band = (f'<div class="band" style="top:{by}px;height:{bh}px"></div>'
        + text(10, by + 6, 300, "<b>What the whole flow guarantees</b>", INK, 10))
band += "".join(f'<div class="f" style="left:{10 + i * (fw + 10)}px;top:{by + 24}px;width:{fw}px;height:{bh - 32}px">'
                f'<div class="h">{img(a, 14)}<span>{h}</span></div>{bullets(b)}</div>'
                for i, (a, h, b) in enumerate(facts))

pc = px + pw / 2          # Prepare column centre
cc = cx + cw / 2          # Check column centre
arrows = [
    route([(pc, ROWS[0] + RH), (pc, ROWS[1] - 2)]),                         # ask -> read schema
    route([(pc, ROWS[1] + RH), (pc, ROWS[2] - 2)]),                         # read schema -> select tables
    route([(pc, ROWS[2] + RH), (pc, ROWS[3] - 2)]),                         # select tables -> build prompt
    route([(px + pw, mid(3)), (gx - 2, mid(3))]),                           # build prompt -> generate
    route([(gx + gw, ROWS[2] + 14), (cx - 14, ROWS[2] + 14), (cx - 14, mid(0)), (cx - 2, mid(0))]),  # -> validate
    route([(cc, ROWS[0] + RH), (cc, ROWS[1] + 10)]),                        # validate -> one read?
    route([(cc, ROWS[1] + RH - 12), (cc, ROWS[2] - 2)], "g"),               # yes -> run
    route([(cx + cw - 24, mid(1)), (ex - 2, mid(1))], "r"),                 # no -> refused
    route([(cx + cw, mid(2)), (ex - 2, mid(2))], "r"),                      # over budget -> stopped
    route([(cc, ROWS[2] + RH), (cc, ROWS[3] + 10)]),                        # run -> query error?
    route([(cx + cw - 24, mid(3)), (ax - 16, mid(3)), (ax - 16, ROWS[2] + RH - 14),
           (ax - 2, ROWS[2] + RH - 14)], "g"),                              # no error -> show
    route([(ex + ew, mid(1)), (ax - 2, mid(1))], "r"),                      # refused -> shown as a plain error
    route([(ex + ew, mid(2) - 10), (ax - 2, mid(2) - 10)], "r"),            # stopped -> shown as a plain error
    route([(ax + aw / 2, ROWS[2] + RH), (ax + aw / 2, ROWS[3] - 2)]),       # show -> the person
    route([(cx + 24, mid(3)), (gx + gw + 2, mid(3))], "d"),                 # yes: repair, back to generate
]
labels = [
    text(cc + 5, ROWS[1] + RH - 12, 30, "yes", GREEN, 9, 700),
    text(cx + cw - 20, mid(1) - 13, 30, "no", RED, 9, 700),
    text(cx + cw + 2, mid(2) - 13, 34, "budget", RED, 8.5, 700),
    text(cx + cw - 20, mid(3) - 13, 30, "no", GREEN, 9, 700),
    text(gx + gw + 4, ROWS[2] + 26, 50, "<b>yes:</b> one repair try, then both gates again", TEAL, 8.5, 400),
]

B64 = {w: base64.b64encode((HERE / f"assets/fonts/GoogleSans-{w}.ttf").read_bytes()).decode()
       for w in ("Regular", "Bold")}
html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Regular']}); font-weight: 400; }}
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Bold']}); font-weight: 700; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; position: relative; font-family: GS; background: transparent; }}
.lane {{ position: absolute; top: 0; height: {BAND[0] - 8}px; border-radius: 10px; }}
.lh {{ position: absolute; top: 8px; padding: 0 10px; display: flex; align-items: baseline; gap: 7px; font-size: 12px; }}
.lh span {{ font-size: 9px; color: {BODY}; }}
.n {{ position: absolute; display: flex; flex-direction: column; padding: 6px 9px; }}
.h {{ display: flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 700; line-height: 1.1; }}
.h .ic {{ margin-left: auto; display: flex; }}
.num {{ width: 15px; height: 15px; border-radius: 50%; color: #FFFFFF; font-size: 9px; font-weight: 700;
       display: inline-flex; align-items: center; justify-content: center; flex: none; }}
ul.b {{ list-style: none; padding: 0; margin-top: 4px; }}
ul.b li {{ font-size: 9px; color: {BODY}; line-height: 1.25; padding-left: 9px; position: relative; }}
ul.b li::before {{ content: ""; position: absolute; left: 1px; top: 3.9px; width: 3.4px; height: 3.4px;
                   border-radius: 50%; background: {BODY}; }}
ul.b.bn li {{ padding-left: 20px; }}
ul.b.bn li::before {{ left: 5.8px; }}
.g {{ font-size: 8.5px; color: {INK}; margin-top: auto; display: flex; align-items: center; gap: 4px; }}
.g span {{ opacity: .7; }}
.c {{ position: absolute; height: 26px; border-radius: 8px; background: #FFFFFF; font-size: 10.5px; font-weight: 700;
     color: {INK}; display: flex; align-items: center; justify-content: center; gap: 5px; }}
.l {{ position: absolute; line-height: 1.3; }}
.li {{ position: absolute; display: flex; align-items: center; gap: 7px; font-size: 10px; color: {INK}; }}
.band {{ position: absolute; left: 0; width: {W}px; background: #F4F5F6; border-radius: 10px; }}
.f {{ position: absolute; background: #FFFFFF; border-radius: 8px; padding: 6px 9px; }}
.f .h {{ font-size: 10.5px; }}
svg {{ position: absolute; left: 0; top: 0; }}
</style><body>
{lanes}{band}
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}{''.join(arrows)}</svg>
{''.join(cards)}{chips}{show}{''.join(labels)}
</body>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    tab = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=3)
    tab.set_content(html)
    tab.wait_for_timeout(400)
    tab.screenshot(path=OUT, omit_background=True)
    browser.close()
print("wrote", OUT.name)
