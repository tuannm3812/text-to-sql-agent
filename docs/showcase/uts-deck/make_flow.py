"""Render the appendix flowchart (21 November 2026, round 4): one question's path in four stage lanes.

Layout: lanes run left to right (Prepare, Generate, Check and run, Answer); inside each lane the steps run top to
bottom on a shared row grid, so cards in different lanes line up; a band across the bottom holds what the whole
flow guarantees. The diagram uses its own smaller type, not the slide scale.

Block colour rules (one meaning per style):
- lane tint and header colour = the stage
- step card = white with a border in its lane's colour (Prepare ink, Check and run teal, Answer green)
- the one model call = the only solid yellow card
- decision = white pill with its lane's border
- end state = tinted card: green for the answer, red for refused or stopped
- note = white with no border and grey text (context, not a step)

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

# lanes: x, width, title, kind label, tint, lane colour (borders and header)
LANES = {
    "prep": (0, 178, "1  Prepare", "app steps, no model", "#F1F3F5", INK),
    "gen": (188, 232, "2  Generate", "the model", "#FEF8D2", "#7A6A00"),
    "check": (430, 330, "3  Check and run", "gates enforced in code", "#E7F3F2", TEAL),
    "ans": (770, 230, "4  Answer", "for the person", "#E8F4EC", GREEN),
}
ROWS = [36, 112, 188, 264]   # tops of the four step rows
RH = 62                      # row card height
BAND = (342, 86)             # guarantee band: top, height


def uri(rel):
    data = (HERE / rel).read_bytes()
    kind = "svg+xml" if rel.endswith(".svg") else "png"
    return f"data:image/{kind};base64,{base64.b64encode(data).decode()}"


def img(rel, size=13):
    return f'<img src="{uri(rel)}" style="width:{size}px;height:{size}px;object-fit:contain;flex:none">'


def card(x, y, w, h, style, title, sub="", tag="", art=(), logos=(), lane="prep"):
    colour = LANES[lane][5]
    fill, border, ink, radius = {
        "step": ("#FFFFFF", colour, INK, 10),
        "model": (YELLOW, YELLOW, INK, 10),
        "decision": ("#FFFFFF", colour, INK, 30),
        "done": ("#DFF3E7", GREEN, "#1F6B43", 10),
        "stop": ("#FBE6E4", RED, "#8E2A1F", 10),
        "note": ("#FFFFFF", "#FFFFFF", INK, 10),
    }[style]
    icons = "".join(img(a) for a in art)
    head = f'<div class="h">{icons}<span style="color:{ink}">{title}</span></div>'
    body = f'<div class="s">{sub}</div>' if sub else ""
    marks = "".join(img(a, 12) for a in logos)
    foot = f'<div class="g">{marks}<span>{tag}</span></div>' if (tag or logos) else ""
    centre = "center" if style == "decision" else "flex-start"
    return (f'<div class="n" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            f'border:1.5px solid {border};border-radius:{radius}px;justify-content:{centre};'
            f'align-items:{"center" if style == "decision" else "flex-start"}">{head}{body}{foot}</div>')


def text(x, y, w, html, colour=BODY, size=9, weight=400, align="left"):
    return (f'<div class="l" style="left:{x}px;top:{y}px;width:{w}px;color:{colour};font-size:{size}px;'
            f'font-weight:{weight};text-align:{align}">{html}</div>')


DEFS = '<defs>' + "".join(
    f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for k, c in (("a", INK), ("d", TEAL), ("r", RED), ("g", GREEN))) + '</defs>'


def arrow(d, kind="a"):
    colour = {"a": INK, "d": TEAL, "r": RED, "g": GREEN}[kind]
    dash = ' stroke-dasharray="5 4"' if kind == "d" else ""
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.4"{dash} marker-end="url(#{kind})"/>'


def mid(row):
    return ROWS[row] + RH / 2


lanes = "".join(
    f'<div class="lane" style="left:{x}px;width:{w}px;background:{tint}"></div>'
    f'<div class="lh" style="left:{x}px;width:{w}px;color:{col}"><b>{t}</b><span>{k}</span></div>'
    for x, w, t, k, tint, col in LANES.values())

# 1 Prepare: one column, top to bottom
px, pw = 10, 158
cards = [
    card(px, ROWS[0], pw, RH, "step", "ask", "a plain question, a database and a model",
         art=(f"{I}person-ink.png",), logos=("assets/logos/tech-streamlit.png",), tag="Streamlit"),
    card(px, ROWS[1], pw, RH, "step", "read schema", "tables, columns, keys; up to 6 values from small text columns",
         art=(f"{I}schema-ink.png",), logos=("assets/logos/tech-python.png",), tag="code"),
    card(px, ROWS[2], pw, RH, "step", "select tables", "keep the top 6 tables plus foreign-key neighbours",
         art=(f"{I}table_rows-ink.png",), logos=("assets/logos/tech-python.png",), tag="code"),
    card(px, ROWS[3], pw, RH, "step", "build prompt", "dialect rules, the schema and the question",
         art=(f"{I}description-ink.png",), logos=("assets/logos/tech-langchain.png",), tag="code"),
]
# 2 Generate: a note over rows 0-1, the model card over rows 2-3
gx, gw = 198, 168   # leaves a strip on the right of the lane for the repair loop's label
cards += [
    card(gx, ROWS[0], gw, ROWS[1] + RH - ROWS[0], "note", "about the model",
         "Gemini is hosted; Ollama runs on the machine. A hosted model receives the whole prompt: the question, "
         "the schema and the hints. Thinking is off by default. A decline is behaviour, not a guarantee.",
         art=(f"{I}help-ink.png",)),
    card(gx, ROWS[2], gw, ROWS[3] + RH - ROWS[2], "model", "generate", "the one model call",
         art=(f"{I}code-ink.png",)),
]
chips = (f'<div class="c" style="left:{gx + 10}px;top:{ROWS[2] + 46}px;width:72px">'
         f'{img("assets/logos/tech-ollama.png", 13)}Ollama</div>'
         f'<div class="c" style="left:{gx + 86}px;top:{ROWS[2] + 46}px;width:72px">'
         f'{img("assets/logos/tech-googlegemini.png", 13)}Gemini</div>'
         + text(gx + 10, ROWS[2] + 82, gw - 20, "writes one SQL statement, or <b>declines</b> a write or a question "
                "the schema cannot answer", INK, 9.5))
# 3 Check and run: main column, exits to the right
cx, cw = 440, 160
ex, ew = 636, 114
cards += [
    card(cx, ROWS[0], cw, RH, "step", "validate", "one SELECT or WITH; no writes, no engine internals",
         logos=("assets/logos/tech-sqlglot.png",), tag="code: gate 1", lane="check"),
    card(cx + 28, ROWS[1] + 8, cw - 56, RH - 16, "decision", "one read?", lane="check"),
    card(cx, ROWS[2], cw, RH, "step", "run read-only", "work budget; the result is cut at 1,000 rows",
         logos=("assets/logos/tech-sqlite.png", "assets/logos/tech-duckdb.png", "assets/logos/tech-postgresql.png"),
         tag="code: gate 2", lane="check"),
    card(cx + 28, ROWS[3] + 8, cw - 56, RH - 16, "decision", "query error?", lane="check"),
    card(ex, ROWS[1], ew, RH, "stop", "&#10007; refused", "explained in plain words; nothing runs"),
    card(ex, ROWS[2], ew, RH, "stop", "&#10007; stopped", "over the work budget; not retried"),
]
# 4 Answer: what the person sees over rows 0-2, the end state in row 3
ax, aw = 780, 210
cards += [
    card(ax, ROWS[0], aw, ROWS[2] + RH - ROWS[0], "step", "show",
         logos=("assets/logos/tech-streamlit.png", "assets/logos/tech-pandas.png"), lane="ans"),
    card(ax, ROWS[3], aw, RH, "done", "&#10003; the person inspects", "reads the SQL before trusting the answer"),
]
seen = [("description", "a one-line answer"), ("table_rows", "the result table"),
        ("monitoring", "a bar chart, when it suits"), ("code", "the SQL, highlighted"),
        ("schema", "the tables chosen, and why"), ("chat", "errors in plain words")]
show = "".join(f'<div class="li" style="left:{ax + 12}px;top:{ROWS[0] + 30 + i * 28}px">'
               f'{img(f"{I}{a}-ink.png", 13)}<span>{t}</span></div>' for i, (a, t) in enumerate(seen))

# guarantee band across all lanes
by, bh = BAND
facts = [(f"{I}fact_check-ink.png", "Rows stay out", "the model sees the schema and a few hints, never result rows"),
         (f"{I}verified_user-ink.png", "Read-only twice", "sqlglot, then a read-only engine; 15 conformance tests each"),
         (f"{I}timer-ink.png", "Cached per schema", "the schema and its index are reused until the schema changes"),
         (f"{I}chat-ink.png", "One question at a time", "earlier questions are not sent; each answer stands alone")]
fw = (W - 20 - 3 * 10) / 4
band = (f'<div class="band" style="top:{by}px;height:{bh}px"></div>'
        + text(10, by + 6, 300, "<b>What the whole flow guarantees</b>", INK, 10))
band += "".join(f'<div class="f" style="left:{10 + i * (fw + 10)}px;top:{by + 24}px;width:{fw}px;height:{bh - 32}px">'
                f'<div class="h">{img(a)}<span>{h}</span></div><div class="s">{b}</div></div>'
                for i, (a, h, b) in enumerate(facts))

arrows = [
    arrow(f"M{px + pw / 2},{ROWS[0] + RH} L{px + pw / 2},{ROWS[1] - 2}"),
    arrow(f"M{px + pw / 2},{ROWS[1] + RH} L{px + pw / 2},{ROWS[2] - 2}"),
    arrow(f"M{px + pw / 2},{ROWS[2] + RH} L{px + pw / 2},{ROWS[3] - 2}"),
    arrow(f"M{px + pw},{mid(3)} L{gx - 2},{mid(3)}"),                                     # build prompt -> generate
    arrow(f"M{gx + gw},{mid(2)} L{cx - 14},{mid(2)} L{cx - 14},{mid(0)} L{cx - 2},{mid(0)}"),  # generate -> validate
    arrow(f"M{cx + cw / 2},{ROWS[0] + RH} L{cx + cw / 2},{ROWS[1] + 6}"),                # validate -> one read?
    arrow(f"M{cx + cw / 2},{ROWS[1] + RH - 8} L{cx + cw / 2},{ROWS[2] - 2}", "g"),       # yes -> run
    arrow(f"M{cx + cw - 28},{mid(1)} L{ex - 2},{mid(1)}", "r"),                          # no -> refused
    arrow(f"M{cx + cw},{mid(2)} L{ex - 2},{mid(2)}", "r"),                               # over budget -> stopped
    arrow(f"M{cx + cw / 2},{ROWS[2] + RH} L{cx + cw / 2},{ROWS[3] + 6}"),                # run -> query error?
    arrow(f"M{cx + cw - 28},{mid(3)} L{ax - 20},{mid(3)} L{ax - 20},{mid(1)} L{ax - 2},{mid(1)}", "g"),  # no -> show
    arrow(f"M{ax + aw / 2},{ROWS[2] + RH} L{ax + aw / 2},{ROWS[3] - 2}"),                # show -> person
    arrow(f"M{cx + 28},{mid(3)} L{gx + gw + 2},{mid(3)}", "d"),                          # yes: repair
]
labels = [
    text(cx + cw / 2 + 5, ROWS[1] + RH - 7, 30, "yes", GREEN, 9, 700),
    text(cx + cw - 24, mid(1) - 13, 30, "no", RED, 9, 700),
    text(cx + cw + 2, mid(2) - 13, 34, "budget", RED, 8.5, 700),
    text(cx + cw - 24, mid(3) - 13, 30, "no", GREEN, 9, 700),
    text(gx + gw + 4, ROWS[2] + 46, 50, "<b>yes:</b> one repair try, then both gates again", TEAL, 8.5, 400),
]

B64 = {w: base64.b64encode((HERE / f"assets/fonts/GoogleSans-{w}.ttf").read_bytes()).decode()
       for w in ("Regular", "Bold")}
html = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Regular']}); font-weight: 400; }}
@font-face {{ font-family: GS; src: url(data:font/ttf;base64,{B64['Bold']}); font-weight: 700; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: {W}px; height: {H}px; position: relative; font-family: GS; background: transparent; }}
.lane {{ position: absolute; top: 0; height: {BAND[0] - 8}px; border-radius: 10px; }}
.lh {{ position: absolute; top: 9px; padding: 0 10px; display: flex; align-items: baseline; gap: 7px; font-size: 12px; }}
.lh span {{ font-size: 9px; color: {BODY}; }}
.n {{ position: absolute; display: flex; flex-direction: column; padding: 6px 9px; }}
.h {{ display: flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 700; line-height: 1.1; }}
.s {{ font-size: 9px; color: {BODY}; line-height: 1.3; margin-top: 3px; }}
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
