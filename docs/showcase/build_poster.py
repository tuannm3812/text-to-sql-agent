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
    420,
    12,
    [[("TEXT-TO-SQL AGENT  ·  UTS CAPSTONE  ·  NOVEMBER 2026", B)]],
    size=9,
    color=WHITE,
)
text(
    L,
    32,
    460,
    80,
    [[("Ask in English.", {"bold": True})], [("Inspect the SQL.", {"bold": True})]],
    size=33,
    color=WHITE,
)
text(
    L,
    113,
    440,
    28,
    "A read-only agent that turns a plain-English question into SQL a person can check, "
    "on SQLite, DuckDB or PostgreSQL.",
    size=10.5,
    color=WHITE,
)
for i, (value, body) in enumerate(
    (
        ("64.6 %", "of Spider answers matched, local 9B model"),
        ("35.2 %", "of BIRD answers matched, with evidence"),
        ("+3.6 pts", "from choosing tables on large databases"),
        ("45 of 45", "engine conformance tests, none skipped"),
    )
):
    x, y = 500 + (i % 2) * 185, 14 + (i // 2) * 62
    panel(x, y, 179, 57, WHITE)
    text(x + 10, y + 7, 160, 24, [[(value, {"bold": True, "size": 19, "color": BLUE})]], size=19)
    text(x + 10, y + 31, 162, 24, body, size=8.5, color=GREY)

# 1 The problem.
Y = 158
section(Y, 1, "THE PROBLEM", "A fluent answer can still be the wrong answer")
Y1 = Y + 25
panel(L, Y1, 400, 92)
text(L + 10, Y1 + 7, 380, 12, [[("Published scores fall on enterprise tasks", B)]], size=10)
for i, (name, v, col) in enumerate(
    (("Spider 1.0", 91.2, SLATE), ("BIRD", 73.0, SLATE), ("Spider 2.0 enterprise", 21.3, AMBER))
):
    y = Y1 + 23 + i * 17
    text(L + 10, y + 2, 110, 12, name, size=9)
    bar(L + 122, y, v * 2.9, 14, f"{v} %", col)
text(
    L + 10,
    Y1 + 77,
    382,
    11,
    "Share of tasks solved, o1-preview, Spider 2.0 paper (2024); not this project.",
    size=8,
    color=GREY,
)
for i, (ic, head, body) in enumerate(
    (
        ("help", "Meaning", "“Revenue” is not a column. Gross or net? The schema does not say."),
        (
            "table_rows",
            "Scale",
            "Real schemas are large. Spider 2.0 databases often exceed 1,000 columns.",
        ),
        (
            "verified_user",
            "Risk",
            "Generated SQL runs on real data, so it must be stopped from changing it.",
        ),
    )
):
    x = L + 408 + i * 142
    panel(x, Y1, 136, 92, PALE_BLUE)
    d.icon(s, ic, "blue", x + 9, Y1 + 8, 20)
    text(x + 34, Y1 + 11, 96, 14, [[(head, B)]], size=11)
    text(x + 9, Y1 + 34, 120, 62, body, size=9.5)

# 2 The demo.
Y = Y1 + 105
section(Y, 2, "THE DEMO", "The SQL shows what the answer includes")
Y2 = Y + 25
H2 = 160
scr = s.shapes.add_picture(str(SCREEN), Pt(L), Pt(Y2), Pt(270), Pt(H2))
scr.line.color.rgb = d.rgb(RULE)
scr.line.width = Pt(0.75)
X2 = L + 278
panel(X2, Y2, 262, H2, NAVY)
text(
    X2 + 11,
    Y2 + 9,
    240,
    12,
    [[("THE SQL, AND WHAT COMPLETED REVENUE ADDS", {"bold": True, "color": WHITE})]],
    size=8,
)
text(
    X2 + 11,
    Y2 + 26,
    244,
    130,
    [
        [(code, {"font": CODE, "size": 8.5, "color": AMBER if added else WHITE, "bold": added})]
        for code, added in d.SQL_LINES
    ],
    size=8.5,
    after=1.5,
)
X3 = X2 + 270
panel(X3, Y2, R - X3, H2)
text(X3 + 10, Y2 + 9, 262, 14, [[("Same top category, two definitions of revenue", B)]], size=10)
text(X3 + 10, Y2 + 34, 260, 11, "All 220 orders, list price", size=9)
bar(X3 + 10, Y2 + 47, 260, 17, "173,366", SLATE)
text(X3 + 10, Y2 + 70, 260, 11, "179 completed orders, after discounts", size=9)
bar(X3 + 10, Y2 + 83, 260 * 136984 / 173366, 17, "136,984", BLUE)
text(
    X3 + 10,
    Y2 + 108,
    262,
    48,
    [
        [
            ("21 % lower", {"bold": True, "color": BLUE}),
            (
                ". Neither figure is wrong by itself. A person decides which revenue the business means.",
                {},
            ),
        ]
    ],
    size=9.5,
)

# 3 How it works.
Y = Y2 + H2 + 15
section(Y, 3, "HOW IT WORKS", "One step of eight uses a model; the application controls execution")
Y3 = Y + 25
STAGES = (
    ("ASK", 118, NAVY, ("1  Ask in plain English",), ("tech-streamlit",)),
    (
        "PREPARE",
        186,
        NAVY,
        ("2  Read schema", "3  Schema RAG: top 6 tables", "4  Build prompt"),
        ("tech-python",),
    ),
    (
        "GENERATE",
        150,
        BLUE,
        ("5  Write SQL or decline", "Never sees result rows"),
        ("tech-langchain", "tech-googlegemini", "tech-ollama"),
    ),
    (
        "CHECK AND RUN",
        186,
        NAVY,
        ("6  Validate: one read only", "7  Run read-only, budget, row cap"),
        ("tech-python",),
    ),
    (
        "ANSWER",
        124,
        NAVY,
        ("8  Show table, chart, SQL", "and why tables were chosen"),
        ("tech-pandas", "tech-streamlit"),
    ),
)
x = L
GAP = 16
for i, (name, w, fill, rows, marks) in enumerate(STAGES):
    d.box(s, x, Y3, w, 18, name, fill, fg=WHITE, size=8.5, kind=MSO_SHAPE.ROUNDED_RECTANGLE)
    panel(x, Y3 + 21, w, 66, PALE_BLUE if fill == BLUE else CREAM)
    text(x + 8, Y3 + 27, w - 12, 44, [[(r, {})] for r in rows], size=9, after=2)
    mx = x + w - 20
    for m in reversed(marks):
        pic(m, mx, Y3 + 69, 14)
        mx -= 18
    if i < 4:
        line(x + w + 1, Y3 + 54, x + w + GAP - 1, Y3 + 54, color=SLATE, width=1.5, arrow=True)
    x += w + GAP
XG = L + 118 + GAP + 186 + GAP
XC = XG + 150 + GAP
YDB = Y3 + 94
line(XC + 80, Y3 + 87, XC + 80, YDB + 11, color=AMBER, width=1.5, dashed=True)
line(XC + 80, YDB + 11, XG + 75, YDB + 11, color=AMBER, width=1.5, dashed=True)
line(XG + 75, YDB + 11, XG + 75, Y3 + 87, color=AMBER, width=1.5, arrow=True, dashed=True)
text(XG + 80, YDB, 120, 11, [[("A query error gets one repair", {"color": GREY})]], size=8)
panel(L + 134, YDB, 186, 24, PALE_AMBER)
for off, m, label in (
    (6, "tech-sqlite", "SQLite"),
    (62, "tech-duckdb", "DuckDB"),
    (120, "tech-postgresql", "PostgreSQL"),
):
    pic(m, L + 134 + off, YDB + 6, 12)
    text(L + 134 + off + 15, YDB + 7, 45, 11, label, size=8)
text(XC + 90, YDB + 6, 200, 12, "The same 15 tests pass on every engine", size=8.5, color=GREY)

# 4 Safety and data.
Y = YDB + 37
section(
    Y,
    4,
    "SAFETY AND DATA",
    "Safety does not rest on the model, and row data stays out of the prompt",
)
Y4 = Y + 25
H4 = 164
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
    (L + 112, SOFT, "Model behaviour, one run"),
    (L + 252, GAPI, "Not stopped here"),
):
    pic(n, x, Y4 + 152, 10)
    text(x + 13, Y4 + 152, 130, 11, label, size=8, color=GREY)
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
Y = Y4 + H4 + 15
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
                ": Spider falls from 84.3 % on easy questions to 38.0 % on extra hard ones. Project scorer, not leaderboard scores.",
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
                " [+1.4, +5.8] against every table + hints on 1,222 questions, from the 65- and 34-table databases.",
                {},
            ),
        ]
    ],
    size=8.5,
)

# 6 What we learned.
Y = Y5 + H5 + 15
section(Y, 6, "WHAT WE LEARNED", "Better retrieval is not better answers; four tests come next")
Y6 = Y + 25
panel(L, Y6, 330, 118)
text(L + 10, Y6 + 8, 310, 12, [[("Each fix helps where it aims, and the rest pay", B)]], size=10)
C0 = L + 190
for i, (name, gain, lost, net) in enumerate(
    (
        ("Dense embeddings", 18, 16, "+2"),
        ("Send every table", 15, 44, "−29"),
        ("+ table summaries", 13, 39, "−26"),
    )
):
    y = Y6 + 42 + i * 24
    text(L + 10, y + 4, 92, 11, [[(name, B)]], size=8.5)
    d.box(s, C0 - lost * 1.9, y, lost * 1.9, 20, f"−{lost}", AMBER, size=8.5)
    d.box(s, C0, y, max(gain * 1.9, 26), 20, f"+{gain}", BLUE, fg=WHITE, size=8.5)
    text(L + 262, y + 4, 60, 12, [[(f"{net} net", B)]], size=9)
text(C0 - 92, Y6 + 26, 88, 11, "Lost on 1,094", size=8, color=GREY, align=PP_ALIGN.RIGHT)
text(C0 + 4, Y6 + 26, 80, 11, "Gained on 128", size=8, color=GREY)
line(C0, Y6 + 38, C0, Y6 + 114, color=NAVY, width=1.25)
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
    y = Y6 + (i // 2) * 60
    panel(x, y, WN / 2 - 2, 56, PALE_BLUE)
    d.icon(s, ic, "blue", x + 8, y + 8, 18)
    text(x + 32, y + 8, WN / 2 - 40, 12, [[(head, B)]], size=9.5)
    text(x + 32, y + 22, WN / 2 - 40, 30, body, size=8.5)

# Footer.
FY = Y6 + 128
rect(0, FY, 900, 1275 - FY, BLUE)
text(
    L,
    FY + 10,
    500,
    12,
    [[("Live demo  ", {"bold": True}), ("aipa-text-to-sql-agent.streamlit.app", {})]],
    size=9,
    color=WHITE,
)
text(
    L,
    FY + 24,
    500,
    12,
    [
        [
            ("Code, runs and decision log  ", {"bold": True}),
            ("github.com/tuannm3812/text-to-sql-agent", {}),
        ]
    ],
    size=9,
    color=WHITE,
)
text(
    500,
    FY + 10,
    364,
    26,
    "Began as a UTS group project in May 2026 with Huy Duc Vu, Ngoc Bao Tran Nguyen, Manh Tuan Nguyen and Nguyen Nghia Doan Dang; refined since by Manh Tuan Nguyen. Results: local qwen3.5:9b, runs of 10 and 19 October 2026.",
    size=8,
    color=WHITE,
    align=PP_ALIGN.RIGHT,
)
print("footer top", FY)
prs.save(OUT)
print("wrote", OUT.name)
