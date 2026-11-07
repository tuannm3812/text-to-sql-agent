# ruff: noqa: E501
"""Build the portrait poster as editable shapes, from the deck's evidence and visuals.

The result is imported into the live Google Slides poster, which stays the source of truth.

    MEASURE_FONT=<DMSans-400.ttf> POSTER_OUT=<file.pptx> uv run --no-project \
        --with python-pptx --with pillow python docs/showcase/build_poster.py
"""

import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["DECK_OUT"] = str(Path(tempfile.gettempdir()) / "unused-body-slides.pptx")
os.environ.pop("ONLY", None)
sys.path.insert(0, str(HERE / "slides"))
import build_body_slides as d  # noqa: E402
from build_body_slides import (  # noqa: E402
    AMBER,
    BB,
    BLUE,
    CODE,
    CREAM,
    GREY,
    ICONS,
    LOGOS,
    MSO_SHAPE,
    NAVY,
    PALE_AMBER,
    PALE_BLUE,
    PP_ALIGN,
    RULE,
    SLATE,
    WHITE,
    B,
    Presentation,
    Pt,
)

OUT = Path(os.environ.get("POSTER_OUT", HERE / "poster-body.pptx"))
SCREEN = Path(os.environ.get("POSTER_SCREEN", HERE / "slides/captures/2026-11-06-retail-frame.png"))
prs = Presentation()
prs.slide_width, prs.slide_height = Pt(900), Pt(1275)
s = prs.slides.add_slide(prs.slide_layouts[6])
L, W = 36, 828
R = L + W


def text(x, y, w, h, paras, **kw):
    """A text box on the poster."""
    return d.text(s, x, y, w, h, paras, **kw)


def shape(kind, x, y, w, h, **kw):
    """A shape on the poster."""
    return d.shape(s, kind, x, y, w, h, **kw)


def rect(x, y, w, h, fill):
    """A flat rectangle."""
    return shape(MSO_SHAPE.RECTANGLE, x, y, w, h, fill=fill)


def panel(x, y, w, h, fill=CREAM):
    """A rounded panel."""
    return shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, radius=min(0.05, 7 / min(w, h))
    )


def line(x1, y1, x2, y2, **kw):
    """A line on the poster."""
    return d.line(s, x1, y1, x2, y2, **kw)


def pic(name, x, y, size):
    """An icon or a technology logo."""
    folder = LOGOS if name.startswith("tech-") else ICONS
    return s.shapes.add_picture(str(folder / f"{name}.png"), Pt(x), Pt(y), Pt(size), Pt(size))


def section(y, n, label, message):
    """A numbered section head that states the finding."""
    d.box(s, L, y, 18, 18, str(n), BLUE, fg=WHITE, size=10, kind=MSO_SHAPE.OVAL)
    text(
        L + 25,
        y + 1,
        W - 25,
        18,
        [[(label + "   ", {"bold": True, "color": BLUE, "size": 9}), (message, {"bold": True})]],
        size=14,
    )


def bar(x, y, w, h, label, fill):
    """A bar with its value inside when it fits, beside it when it does not."""
    rect(x, y, w, h, fill)
    if w >= 34:
        ink = NAVY if fill == AMBER else WHITE
        text(x + 5, y + (h - 11) / 2, w - 8, 11, [[(label, {"bold": True, "color": ink})]], size=9)
    else:
        text(x + w + 4, y + (h - 11) / 2, 50, 11, [[(label, B)]], size=9)


# Hero.
HERO = 148
rect(0, 0, 900, HERO, BLUE)
text(
    L,
    16,
    450,
    12,
    [[("36121  ARTIFICIAL INTELLIGENCE PRINCIPLES AND APPLICATIONS", B)]],
    size=9,
    color=WHITE,
)
text(
    L,
    32,
    460,
    80,
    [
        [("Ask in English.", {"bold": True})],
        [("Inspect the SQL.", {"bold": True, "color": AMBER})],
    ],
    size=33,
    color=WHITE,
)
text(
    L,
    113,
    446,
    28,
    [
        [
            ("Text-to-SQL Agent", {"bold": True, "color": AMBER}),
            (" turns a plain-English question into ", {}),
            ("read-only SQL", B),
            (" a person can check, on SQLite, DuckDB or PostgreSQL.", {}),
        ]
    ],
    size=10.5,
    color=WHITE,
)
for i, (value, body) in enumerate(
    (
        ("1 of 8", "steps uses a model, and it never sees result rows"),
        ("45 of 45", "engine tests passed on 3 read-only engines"),
        ("64.6 %", "of Spider answers matched by a local 9B model"),
        ("+3.6 pts", "from sending fewer tables on large databases"),
    )
):
    x, y = 500 + (i % 2) * 185, 14 + (i // 2) * 62
    panel(x, y, 179, 57, NAVY)
    text(x + 10, y + 6, 160, 24, [[(value, {"bold": True, "size": 19, "color": AMBER})]], size=19)
    text(x + 10, y + 31, 162, 24, body, size=8.5, color=WHITE)

# 1 The problem.
Y = 158
section(Y, 1, "THE PROBLEM", "A fluent answer can still be the wrong answer")
Y1 = Y + 25
panel(L, Y1, 400, 86)
text(L + 10, Y1 + 7, 380, 12, [[("Published scores fall on enterprise tasks", B)]], size=10)
for i, (name, v, col) in enumerate(
    (("Spider 1.0", 91.2, SLATE), ("BIRD", 73.0, SLATE), ("Spider 2.0 enterprise", 21.3, AMBER))
):
    y = Y1 + 22 + i * 16
    text(L + 10, y + 2, 110, 12, name, size=9)
    bar(L + 122, y, v * 2.9, 14, f"{v} %", col)
text(
    L + 122 + 21.3 * 2.9 + 6,
    Y1 + 22 + 2 * 16 + 2,
    190,
    11,
    [[("69.9 points below Spider 1.0", BB)]],
    size=9,
)
text(
    L + 10,
    Y1 + 73,
    382,
    11,
    "Share of tasks solved, o1-preview, Spider 2.0 paper (2024); not this project.",
    size=8,
    color=GREY,
)
for i, (ic, head, body) in enumerate(
    (
        (
            "help",
            "Meaning",
            [
                ("\u201cRevenue\u201d is not a column", BB),
                (". Gross or net? The schema does not say.", {}),
            ],
        ),
        (
            "table_rows",
            "Scale",
            [
                ("Real schemas are large: Spider 2.0 databases often exceed ", {}),
                ("1,000 columns", BB),
                (".", {}),
            ],
        ),
        (
            "verified_user",
            "Risk",
            [
                ("Generated SQL runs on ", {}),
                ("real data", BB),
                (", so it must be stopped from changing it.", {}),
            ],
        ),
    )
):
    x = L + 408 + i * 142
    panel(x, Y1, 136, 86, PALE_BLUE)
    d.icon(s, ic, "blue", x + 9, Y1 + 8, 20)
    text(x + 34, Y1 + 11, 96, 14, [[(head, B)]], size=11)
    text(x + 9, Y1 + 32, 120, 56, [body], size=9.5)

# 2 The demo.
Y = Y1 + 96
section(Y, 2, "THE DEMO", "The SQL shows what the answer includes")
Y2 = Y + 25
H2 = 152
WA, WB, GP = 256, 268, 16
XB = L + WA + GP
XC3 = XB + WB + GP
WC = R - XC3
for x, w, n, head, fill in (
    (L, WA, "1", "THE APP ANSWERS", NAVY),
    (XB, WB, "2", "THE SQL SHOWS HOW", NAVY),
    (XC3, WC, "3", "A PERSON DECIDES", BLUE),
):
    d.box(
        s, x, Y2, w, 17, f"{n}   {head}", fill, fg=WHITE, size=8.5, kind=MSO_SHAPE.ROUNDED_RECTANGLE
    )
for x in (L + WA, XB + WB):
    line(x + 1, Y2 + 90, x + GP - 1, Y2 + 90, color=SLATE, width=1.5, arrow=True)
YD = Y2 + 21
scr = s.shapes.add_picture(str(SCREEN), Pt(L), Pt(YD), Pt(WA), Pt(H2))
scr.line.color.rgb = d.rgb(RULE)
scr.line.width = Pt(0.75)
panel(XB, YD, WB, H2, NAVY)
text(
    XB + 10,
    YD + 8,
    WB - 16,
    118,
    [
        [(code, {"font": CODE, "size": 8.5, "color": AMBER if added else WHITE, "bold": added})]
        for code, added in d.SQL_LINES
    ],
    size=8.5,
    after=1,
)
text(
    XB + 10,
    YD + H2 - 18,
    WB - 16,
    11,
    [[("Amber: what completed revenue would add", {"color": AMBER})]],
    size=8.5,
)
panel(XC3, YD, WC, H2)
text(XC3 + 10, YD + 8, WC - 18, 13, [[("Electronics revenue, two definitions", B)]], size=10)
BW3 = WC - 20
text(XC3 + 10, YD + 28, BW3, 11, "All 220 orders, list price", size=9)
bar(XC3 + 10, YD + 41, BW3, 18, "173,366", SLATE)
text(XC3 + 10, YD + 66, BW3, 11, "179 completed orders, after discounts", size=9)
W3 = BW3 * 136984 / 173366
bar(XC3 + 10, YD + 79, W3, 18, "136,984", BLUE)
d.box(s, XC3 + 10 + W3, YD + 79, BW3 - W3, 18, "\u221221 %", AMBER, size=9)
text(
    XC3 + 10,
    YD + 106,
    BW3,
    40,
    [
        [
            ("Neither figure is wrong by itself. ", {}),
            ("A person decides", {"bold": True, "color": BLUE}),
            (" which revenue the business means.", {}),
        ]
    ],
    size=9.5,
)
Y2 = YD

# 3 How it works.
Y = Y2 + H2 + 10
section(Y, 3, "HOW IT WORKS", "One step of eight uses a model; the application controls execution")
Y3 = Y + 25
STAGES = (
    ("ASK", 124, NAVY, ((1, "Ask in plain English"),), ("tech-streamlit",)),
    (
        "PREPARE",
        196,
        NAVY,
        ((2, "Read schema"), (3, "Schema RAG: top 6 tables"), (4, "Build prompt")),
        ("tech-python",),
    ),
    (
        "GENERATE",
        156,
        BLUE,
        ((5, "Write SQL or decline; never sees result rows"),),
        ("tech-langchain", "tech-googlegemini", "tech-ollama"),
    ),
    (
        "CHECK AND RUN",
        196,
        NAVY,
        ((6, "Validate: one read-only query"), (7, "Run with work budget and row cap")),
        ("tech-sqlglot", "tech-python"),
    ),
    (
        "ANSWER",
        156,
        NAVY,
        ((8, "Show the answer, SQL and why those tables"),),
        ("tech-pandas", "tech-streamlit"),
    ),
)
x = L
XS = []
CH = 70
scale = W / sum(st[1] for st in STAGES)
for i, (name, w, fill, rows, marks) in enumerate(STAGES):
    w *= scale
    XS.append((x, w))
    kind = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
    over = 7 if i < 4 else 0
    d.box(s, x, Y3, w + over, 20, name, fill, fg=WHITE, size=8.5, kind=kind)
    panel(x, Y3 + 24, w - 5, CH, PALE_BLUE if fill == BLUE else CREAM)
    for j, (n, label) in enumerate(rows):
        y = Y3 + 31 + j * 16
        d.box(s, x + 7, y, 12, 12, str(n), fill, fg=WHITE, size=8, kind=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(x + 23, y + 1, w - 32, 24, label, size=8.5)
    mx = x + w - 5 - 20
    for m in reversed(marks):
        if m == "tech-sqlglot":
            shape(MSO_SHAPE.ROUNDED_RECTANGLE, mx - 26, Y3 + 75, 40, 13, fill=NAVY, radius=0.2)
            s.shapes.add_picture(str(LOGOS / f"{m}.png"), Pt(mx - 24), Pt(Y3 + 77), Pt(36), Pt(9))
            mx -= 44
        else:
            pic(m, mx, Y3 + 75, 14)
            mx -= 18
    x += w
(XP, WP), (XG, WG), (XC, WCK) = XS[1], XS[2], XS[3]
YR = Y3 + 24 + CH
YDB = YR + 16
# The repair loop, then the engines both ends of the flow rely on.
line(XC + 40, YR, XC + 40, YR + 8, color=AMBER, width=1.5, dashed=True)
line(XC + 40, YR + 8, XG + 60, YR + 8, color=AMBER, width=1.5, dashed=True)
line(XG + 60, YR + 8, XG + 60, YR, color=AMBER, width=1.5, arrow=True, dashed=True)
text(XC + 46, YR + 3, 120, 11, [[("A query error gets one repair", {"bold": True})]], size=8)
DBX, DBW = XP, XC + WCK - 5 - XP
panel(DBX, YDB, DBW, 24, PALE_AMBER)
text(
    DBX + 9,
    YDB + 6,
    170,
    12,
    [[("Database engine", B), ("  by connection string", {"color": GREY, "size": 8})]],
    size=9,
)
for off, m, label in (
    (186, "tech-sqlite", "SQLite"),
    (240, "tech-duckdb", "DuckDB"),
    (298, "tech-postgresql", "PostgreSQL"),
):
    pic(m, DBX + off, YDB + 5, 13)
    text(DBX + off + 16, YDB + 7, 50, 11, label, size=8.5)
text(
    DBX + DBW - 118,
    YDB + 7,
    110,
    11,
    "Same 15 tests on each",
    size=8.5,
    color=GREY,
    align=PP_ALIGN.RIGHT,
)
line(XP + 40, YDB, XP + 40, YR, color=SLATE, width=1.5, arrow=True)
line(XC + WCK - 16, YR, XC + WCK - 16, YDB, color=SLATE, width=1.5, arrow=True, both=True)

# 4 Safety and data.
Y = YDB + 32
section(
    Y,
    4,
    "SAFETY AND DATA",
    "Safety does not rest on the model, and result rows stay out of the prompt",
)
Y4 = Y + 25
H4 = 166
WM = 500
TW, CW = 150, 112
for i, (head, fill) in enumerate((("1 MODEL", BLUE), ("2 APPLICATION", NAVY), ("3 ENGINE", NAVY))):
    d.box(
        s,
        L + TW + i * (CW + 4),
        Y4,
        CW,
        17,
        head,
        fill,
        fg=WHITE,
        size=8.5,
        kind=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
TICK, SOFT, GAPI = "check_circle-blue", "check_circle-amber", "cancel-amber"
for i, (label, cells) in enumerate(
    (
        (
            "Write or schema change",
            ((SOFT, "Declined 6 of 6"), (TICK, "Blocked"), (TICK, "Denied")),
        ),
        (
            "Reading engine internals",
            ((SOFT, "Declined 3 of 3"), (TICK, "Blocked"), (GAPI, "Would run")),
        ),
        ("Reading files on disk", (None, (TICK, "Blocked"), (TICK, "Denied"))),
        ("Runaway or oversized query", (None, None, (TICK, "Budget, row cap"))),
        ("Data the schema lacks", ((SOFT, "Declined 5 of 6"), None, None)),
    )
):
    y = Y4 + 20 + i * 22
    panel(L, y, WM, 20)
    text(L + 7, y + 5, TW - 8, 11, [[(label, B)]], size=8.5)
    for k, cell in enumerate(cells):
        x = L + TW + k * (CW + 4)
        if cell:
            pic(cell[0], x + 6, y + 4, 12)
            text(x + 22, y + 5, CW - 22, 11, cell[1], size=8.5)
        else:
            line(x + 8, y + 10, x + 16, y + 10, color=GREY, width=1.25)
y = Y4 + 20 + 5 * 22
panel(L, y, WM, 20, PALE_AMBER)
text(L + 7, y + 5, TW - 8, 11, [[("Valid SQL, wrong meaning", B)]], size=8.5)
d.icon(s, "person", "navy", L + TW + 6, y + 3, 14)
text(
    L + TW + 24,
    y + 5,
    320,
    11,
    "No layer checks this, so the person reads the answer and its SQL",
    size=8.5,
)
for x, n, label in (
    (L, TICK, "Enforced and tested"),
    (L + 104, SOFT, "Model behaviour, one run"),
    (L + 226, GAPI, "Not stopped here"),
):
    pic(n, x, Y4 + 153, 10)
    text(x + 13, Y4 + 153, 120, 11, label, size=8, color=GREY)
line(L + 322, Y4 + 158, L + 330, Y4 + 158, color=GREY, width=1.25)
text(L + 335, Y4 + 153, 165, 11, "Not this layer's role, or not tested", size=8, color=GREY)
XD = L + WM + 8
WD = R - XD
panel(XD, Y4, WD, H4, PALE_BLUE)
text(
    XD + 10, Y4 + 8, WD - 18, 12, [[("79 of 608 stored text values reach the prompt", B)]], size=10
)
BW = WD - 20
rect(XD + 10, Y4 + 28, BW, 18, "E8EAEE")
bar(XD + 10, Y4 + 28, max(BW * 79 / 608, 34), 18, "79", AMBER)
text(XD + 10 + BW - 60, Y4 + 32, 54, 11, "529 not sent", size=8.5, color=GREY, align=PP_ALIGN.RIGHT)
for k, (head, rows, name) in enumerate(
    (
        ("In the prompt", ("Tables, columns, keys", "79 values as hints", "The question"), TICK),
        ("Not in the prompt", ("Result rows", "Names, emails", "Other values"), GAPI),
    )
):
    x = XD + 10 + k * (BW / 2)
    text(x, Y4 + 54, BW / 2, 12, [[(head, B)]], size=9)
    for j, r in enumerate(rows):
        pic(name, x, Y4 + 70 + j * 16, 11)
        text(x + 15, Y4 + 70 + j * 16, BW / 2 - 16, 11, r, size=8.5)
text(
    XD + 10,
    Y4 + 124,
    BW,
    36,
    "Hints are real stored values. A local model keeps the prompt on your machine; a hosted one receives it.",
    size=8.5,
)

# 5 Evidence.
Y = Y4 + H4 + 10
section(Y, 5, "THE EVIDENCE", "On large databases, sending fewer tables scored 3.6 points higher")
Y5 = Y + 25
H5 = 188
panel(L, Y5, 330, H5)
text(L + 10, Y5 + 8, 300, 12, [[("Answers matched, with 95 % intervals", B)]], size=10)
A0, AW = L + 128, 180
ax = lambda v: A0 + v / 80 * AW  # noqa: E731
for v in (0, 20, 40, 60, 80):
    line(ax(v), Y5 + 26, ax(v), Y5 + 128, color=RULE, width=0.5)
    text(ax(v) - 15, Y5 + 130, 30, 11, f"{v} %", size=8, color=GREY, align=PP_ALIGN.CENTER)
for i, (name, sub, v, lo, hi, col) in enumerate(
    (
        ("Spider 1.0 dev", "1,034 questions", 64.6, 61.6, 67.5, BLUE),
        ("BIRD + evidence", "1,534 questions", 35.2, 32.9, 37.6, BLUE),
        ("BIRD, no evidence", "1,534 questions", 25.1, 22.9, 27.3, SLATE),
        ("Demo suite", "4 of 12 matched", 33.3, 8.3, 58.3, AMBER),
    )
):
    y = Y5 + 26 + i * 26
    text(L + 10, y, 116, 11, [[(name, B)]], size=8.5)
    text(L + 10, y + 11, 116, 11, sub, size=8, color=GREY)
    line(ax(lo), y + 11, ax(hi), y + 11, color=col, width=2.5)
    shape(MSO_SHAPE.OVAL, ax(v) - 4, y + 7, 8, 8, fill=col)
    rect(ax(hi) + 3, y + 5, 34, 12, CREAM)
    text(ax(hi) + 4, y + 5, 40, 11, [[(f"{v} %", B)]], size=8.5)
text(
    L + 10,
    Y5 + 146,
    310,
    38,
    [
        [
            ("Harder questions score lower", B),
            (
                ": Spider falls from 84.3 % on easy questions to 38.0 % on extra hard ones. Project scorer, not leaderboard scores; local qwen3.5:9b, runs of 10 and 19 October 2026.",
                {},
            ),
        ]
    ],
    size=8.5,
)
XE = L + 338
WE = R - XE
panel(XE, Y5, WE, H5)
COLS = (
    (XE + 124, "fact_check", "Answers matched", 118 / 30),
    (XE + 250, "chat", "Prompt tokens", 110 / 8501),
    (XE + 370, "timer", "Time", 92 / 6),
)
text(XE + 10, Y5 + 8, 110, 11, [[("Schema sent", B)]], size=8.5, color=GREY)
for x, ic, head, _ in COLS:
    d.icon(s, ic, "navy", x, Y5 + 7, 12)
    text(x + 15, Y5 + 8, 96, 11, [[(head, B)]], size=8.5)
for i, (name, acc, tok, sec, col) in enumerate(
    (
        ("Every table + hints", 25.5, 8501, 4.0, AMBER),
        ("Every table, no hints", 26.8, 6221, 4.2, SLATE),
        ("Top 6 + neighbours", 29.1, 2670, 6.0, BLUE),
    )
):
    y = Y5 + 24 + i * 19
    text(XE + 10, y + 3, 112, 11, [[(name, {"bold": col == BLUE})]], size=8.5)
    for (x, _, _, k), v, lab in zip(
        COLS, (acc, tok, sec), (f"{acc} %", f"{tok:,}", f"{sec} s"), strict=True
    ):
        bar(x, y, v * k, 16, lab, col)
line(XE + 10, Y5 + 86, XE + WE - 10, Y5 + 86, color=RULE, width=0.75)
text(XE + 10, Y5 + 92, 240, 12, [[("Selection wins until it drops a table", B)]], size=10)
for k, (name, head, sub, top, every) in enumerate(
    (
        (TICK, "Every table sent", "1,055 questions", 32.9, 26.7),
        (GAPI, "A table dropped", "167 questions", 5.4, 18.0),
    )
):
    y = Y5 + 110 + k * 37
    pic(name, XE + 10, y + 5, 13)
    text(XE + 27, y + 2, 95, 11, [[(head, B)]], size=8.5)
    text(XE + 27, y + 13, 95, 11, sub, size=8, color=GREY)
    bar(XE + 124, y, top * 5.4, 16, f"{top} %", BLUE)
    bar(XE + 124, y + 17, every * 5.4, 16, f"{every} %", AMBER)
text(
    XE + 322,
    Y5 + 110,
    WE - 330,
    72,
    [
        [
            ("+3.6 points", {"bold": True, "color": BLUE}),
            (
                " [+1.4, +5.8] against every table + hints on 1,222 questions, from the 65- and 34-table databases. Blue is top 6; amber is every table + hints.",
                {},
            ),
        ]
    ],
    size=8.5,
)

# 6 What we learned.
Y = Y5 + H5 + 10
section(Y, 6, "WHAT WE LEARNED", "Better retrieval is not better answers; four tests come next")
Y6 = Y + 25
panel(L, Y6, 330, 112)
text(L + 10, Y6 + 7, 310, 12, [[("Each fix helps where it aims, and the rest pay", B)]], size=10)
text(
    L + 10,
    Y6 + 20,
    312,
    11,
    "Correct answers vs selected tables; the later scorer left 128 misses",
    size=8,
    color=GREY,
)
C0 = L + 190
for i, (name, gain, lost, net) in enumerate(
    (
        ("Dense embeddings", 18, 16, "+2"),
        ("Send every table", 15, 44, "−29"),
        ("+ table summaries", 13, 39, "−26"),
    )
):
    y = Y6 + 43 + i * 22
    text(L + 10, y + 4, 92, 11, [[(name, B)]], size=8.5)
    d.box(s, C0 - lost * 1.9, y, lost * 1.9, 19, f"−{lost}", AMBER, size=8.5)
    d.box(s, C0, y, max(gain * 1.9, 26), 19, f"+{gain}", BLUE, fg=WHITE, size=8.5)
    text(L + 262, y + 4, 60, 12, [[(f"{net} net", B)]], size=9)
text(C0 - 92, Y6 + 30, 88, 11, "Lost on 1,094", size=8, color=GREY, align=PP_ALIGN.RIGHT)
text(C0 + 4, Y6 + 30, 80, 11, "Gained on 128", size=8, color=GREY)
line(C0, Y6 + 41, C0, Y6 + 109, color=NAVY, width=1.25)
XN = L + 338
WN = R - XN
for i, (ic, head, body) in enumerate(
    (
        ("menu_book", "Business definitions", "Does a few definitions settle “revenue”?"),
        ("schema", "Targeted table recovery", "Keep the gains without losing other answers"),
        ("table_rows", "New large schemas", "Does top 6 hold beyond these 4 databases?"),
        ("science", "Hosted model", "Same suites: accuracy, latency, empty SQL"),
    )
):
    x = XN + (i % 2) * (WN / 2 + 2)
    y = Y6 + (i // 2) * 57
    panel(x, y, WN / 2 - 2, 55, PALE_BLUE)
    d.icon(s, ic, "blue", x + 8, y + 8, 18)
    text(x + 32, y + 8, WN / 2 - 40, 12, [[(head, B)]], size=9.5)
    text(x + 32, y + 22, WN / 2 - 40, 30, body, size=8.5)

# Footer.
FY = Y6 + 120
rect(0, FY, 900, 1275 - FY, BLUE)
s.shapes.add_picture(str(LOGOS / "uts-white.png"), Pt(L), Pt(FY + 9), height=Pt(22))
text(L + 70, FY + 14, 200, 13, [[("November 2026", B)]], size=10, color=WHITE)
GH = "github.com/tuannm3812/text-to-sql-agent"
DEMO = "aipa-text-to-sql-agent.streamlit.app"
text(
    470,
    FY + 7,
    394,
    28,
    [
        [("Code  ", B), (GH, {"url": "https://" + GH, "color": WHITE})],
        [("Live demo  ", B), (DEMO, {"url": "https://" + DEMO, "color": WHITE})],
    ],
    size=9.5,
    color=WHITE,
    align=PP_ALIGN.RIGHT,
    after=2,
)
print("footer top", FY)
prs.save(OUT)
print("wrote", OUT.name)
