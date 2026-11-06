"""Build the body objects of deck slides 2 to 6 as editable shapes in a PowerPoint.

The objects are imported into the live Google Slides deck, which stays the source of truth;
rerun this only to rebuild those bodies. Follows DESIGN.md: content levels, red takeaway
markers, one icon set. PREVIEW=1 adds stand-in headers and a footer for a local render.

    MEASURE_FONT=<DMSans-400.ttf> uv run --no-project --with python-pptx --with pillow \
        python docs/showcase/slides/build_body_slides.py
"""

import os
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

HERE = Path(__file__).resolve().parent
ICONS = HERE / "assets" / "icons"
LOGOS = HERE / "assets" / "logos"
OUT = Path(os.environ.get("DECK_OUT", HERE / "body-slides.pptx"))
FONT = os.environ.get("DECK_FONT", "Google Sans")
PREVIEW = bool(os.environ.get("PREVIEW"))
MEASURE = os.environ.get("MEASURE_FONT")

BLUE, AMBER, NAVY, CREAM = "0F4BEB", "E6A23C", "17243B", "FAF7F0"
GREY, SLATE, RED, RULE, WHITE = "59636E", "46576C", "C64040", "D8DCE3", "FFFFFF"
PALE_BLUE, PALE_AMBER = "E7EDFD", "FBEFD9"
B = {"bold": True}
BB = {"bold": True, "color": BLUE}

prs = Presentation()
prs.slide_width, prs.slide_height = Pt(960), Pt(540)


def rgb(value: str) -> RGBColor:
    """Colour from a hex string."""
    return RGBColor.from_string(value)


def write(frame, paras, size=12, color=NAVY, align=None, spacing=None, after=0):
    """Fill a text frame. paras: a string, or paragraphs of [(text, options)]."""
    frame.word_wrap = True
    paras = [[(paras, {})]] if isinstance(paras, str) else paras
    for i, para in enumerate(paras):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        if align:
            p.alignment = align
        if spacing:
            p.line_spacing = spacing
        p.space_after = Pt(after)
        for chunk, opt in para:
            r = p.add_run()
            r.text = chunk
            r.font.name = opt.get("font", FONT)
            r.font.size = Pt(opt.get("size", size))
            r.font.bold = opt.get("bold", False)
            r.font.color.rgb = rgb(opt.get("color", color))
            if opt.get("url"):
                r.hyperlink.address = opt["url"]
            if opt.get("sup"):
                r.font._element.set("baseline", "30000")


def text(s, x, y, w, h, paras, anchor=None, **kw):
    """A text box with zero padding."""
    box = s.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = box.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    if anchor:
        tf.vertical_anchor = anchor
    write(tf, paras, **kw)
    return box


def shape(s, kind, x, y, w, h, fill=None, radius=None, line=None):
    """A native shape with explicit fill and no theme style."""
    o = s.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
    if fill:
        o.fill.solid()
        o.fill.fore_color.rgb = rgb(fill)
    else:
        o.fill.background()
    if line:
        o.line.color.rgb = rgb(line)
        o.line.width = Pt(1)
    else:
        o.line.fill.background()
    style = o._element.find(qn("p:style"))
    if style is not None:
        o._element.remove(style)
    if radius is not None:
        o.adjustments[0] = radius
    return o


def card(s, x, y, w, h, paras, fill=CREAM, pad=8, anchor=MSO_ANCHOR.TOP, **kw):
    """A rounded card whose text lives in the shape."""
    o = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, radius=0.07)
    tf = o.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Pt(pad))
    tf.vertical_anchor = anchor
    write(tf, paras, align=kw.pop("align", PP_ALIGN.LEFT), **kw)
    return o


def icon(s, name, colour, x, y, size=24):
    """One icon from the deck's single set."""
    return s.shapes.add_picture(
        str(ICONS / f"{name}-{colour}.png"), Pt(x), Pt(y), Pt(size), Pt(size)
    )


def logo(s, name, x, y, size=26):
    """A product logo, in its own colours."""
    return s.shapes.add_picture(str(LOGOS / f"{name}.png"), Pt(x), Pt(y), Pt(size), Pt(size))


def line(s, x1, y1, x2, y2, color=RULE, width=1.0, arrow=False):
    """A flat native connector."""
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    style = c._element.find(qn("p:style"))
    if style is not None:
        c._element.remove(style)
    if arrow:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))


def marker(s, n, x, y):
    """One red numbered ellipse, 12 pt, number centred inside."""
    o = shape(s, MSO_SHAPE.OVAL, x, y, 12, 12, fill=RED)
    tf = o.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
    write(tf, [[(str(n), {"bold": True, "size": 8, "color": WHITE})]], align=PP_ALIGN.CENTER)


LINE_H = 17.2


def lines(runs, width=250.0):
    """Rendered line count of rich 12 pt text."""
    runs = [(runs, {})] if isinstance(runs, str) else runs
    if MEASURE:
        from PIL import ImageFont

        reg = ImageFont.truetype(MEASURE, 120)
        bold = ImageFont.truetype(MEASURE.replace("400", "700"), 120)

        def size(word, is_bold):
            return (bold if is_bold else reg).getlength(word) / 10

        space = reg.getlength(" ") / 10
    else:

        def size(word, is_bold):
            return len(word) * 6.0

        space = 6.0
    total, cur, gap = 1, 0.0, False
    for chunk, opt in runs:
        for k, word in enumerate(chunk.split(" ")):
            if not word:
                gap = True
                continue
            spaced = k > 0 or gap
            gap = False
            add = size(word, opt.get("bold", False)) + (space if spaced and cur else 0)
            if cur and cur + add > width and spaced:
                total, cur = total + 1, size(word, opt.get("bold", False))
            else:
                cur += add
    return total


def takeaways(s, groups, top=136.0):
    """The standard column: one box at x684, 235 wide, red marker at x668 per heading."""
    divider(s)
    box = s.shapes.add_textbox(Pt(684), Pt(top), Pt(235), Pt(324))
    tf = box.text_frame
    tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    y = top
    for i, (heading, body) in enumerate(groups, start=1):
        p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
        p.line_spacing = 1.1
        p.space_before = Pt(0 if i == 1 else 14)
        p.space_after = Pt(6)
        y += 0 if i == 1 else 14
        r = p.add_run()
        r.text = heading
        r.font.name, r.font.size, r.font.bold = FONT, Pt(12), True
        r.font.color.rgb = rgb(NAVY)
        marker(s, i, 668, y + 2.5)
        y += lines([(heading, B)]) * LINE_H + 6
        q = tf.add_paragraph()
        q.line_spacing = 1.1
        q.space_after = Pt(6)
        runs = [(body, {})] if isinstance(body, str) else body
        for chunk, opt in runs:
            r = q.add_run()
            r.text = chunk
            r.font.name, r.font.size = FONT, Pt(12)
            r.font.bold = opt.get("bold", False)
            r.font.color.rgb = rgb(opt.get("color", NAVY))
        y += lines(runs) * LINE_H + 6


def divider(s):
    """The rule between evidence and takeaways, on every takeaway slide."""
    line(s, 658, 130, 658, 476, color=RULE, width=1.0)


def note(s, rest, x=43.5, y=458, w=606, prefix="Note:"):
    """A 9 pt note with its bold prefix."""
    text(s, x, y, w, 18, [[(prefix + " ", B), (rest, {})]], size=8, color=GREY)


def bar_row(s, label, value, width, color, y, x=43.5, label_w=128, h=16, shown=None):
    """A labelled bar drawn from zero, with its value at the end."""
    text(s, x, y, label_w, h, label, size=10, anchor=MSO_ANCHOR.MIDDLE)
    shape(s, MSO_SHAPE.RECTANGLE, x + label_w, y, width, h, fill=color)
    text(
        s,
        x + label_w + width + 6,
        y,
        50,
        h,
        [[(shown or value, B)]],
        size=10,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def new_slide(label, title, subtitle, number):
    """A blank slide; in preview, with stand-in header and footer."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if PREVIEW:
        text(s, 43.5, 29.5, 600, 14, [[(label, {"bold": True, "size": 10})]])
        text(s, 43.5, 48.4, 800, 34, [[(title, {"bold": True, "size": 24, "color": BLUE})]])
        text(s, 43.5, 90.9, 860, 16, subtitle, size=12, color=GREY)
        shape(s, MSO_SHAPE.RECTANGLE, 43.5, 492, 917, 28, fill=BLUE)
        text(s, 880, 498, 40, 14, str(number), size=10, color=WHITE)
    return s


# Slide 2: executive summary
s = new_slide(
    "EXECUTIVE SUMMARY",
    "Inspectable SQL, with measured limits",
    "What the agent does, how well it did, and what to keep in mind",
    2,
)
tiles = [
    (
        "verified_user",
        "white",
        NAVY,
        WHITE,
        "Read-only checks",
        "45 of 45",
        "tests passed, none skipped, on 3 database engines",
    ),
    (
        "target",
        "white",
        BLUE,
        WHITE,
        "Spider benchmark",
        "64.6%",
        "of answers matched: common test, local 9B model",
    ),
    (
        "target",
        "white",
        BLUE,
        WHITE,
        "BIRD benchmark",
        "35.2%",
        "of answers matched: harder test, with evidence hints",
    ),
    (
        "trending_up",
        "navy",
        AMBER,
        NAVY,
        "Large databases",
        "+3.6 pts",
        "from choosing tables [+1.4, +5.8]",
    ),
]
for i, (ic, ic_col, fill, fg, head, value, label) in enumerate(tiles):
    x = 43.5 + i * 153
    card(
        s,
        x,
        130,
        147,
        112,
        [
            [(head, {"bold": True, "size": 12, "color": fg})],
            [(value, {"bold": True, "size": 26, "color": fg})],
            [(label, {"size": 10, "color": fg})],
        ],
        fill=fill,
        after=2,
    ).text_frame.margin_right = Pt(8)
    icon(s, ic, ic_col, x + 119, 136, 20)
marker(s, 1, 37, 124)
marker(s, 3, 190, 124)
text(
    s,
    43.5,
    252,
    606,
    20,
    [[("Large databases: more correct answers from less context", {"bold": True, "size": 12})]],
)
marker(s, 2, 30, 255)
for x, head, rows, reading in (
    (
        43.5,
        "Answers matched",
        (("Every table + hints", "25.5%", 80, SLATE), ("Top 6 tables", "29.1%", 91, BLUE)),
        "Sending only the most relevant tables scored 3.6 points higher.",
    ),
    (
        349.5,
        "Prompt size, every table = 100",
        (("Every table + hints", "100", 92, SLATE), ("Top 6 tables", "31", 29, AMBER)),
        "The prompt was 69% smaller, but each answer took about 2 s longer.",
    ),
):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 278, 300, 148, fill=CREAM, radius=0.05)
    text(s, x + 12, 288, 276, 16, [[(head, B)]], size=12)
    for k, (lab, val, w, col) in enumerate(rows):
        bar_row(s, lab, val, w, col, 311 + k * 26, x=x + 12, label_w=118)
    text(s, x + 12, 369, 276, 48, reading, size=10)
marker(s, 4, 343, 272)
note(
    s,
    "accuracy uses this project's result comparison, not leaderboard scoring. Large databases: "
    "1,222 questions on 4 databases of 21 to 65 tables.",
    y=436,
)
takeaways(
    s,
    [
        (
            "Read-only is not the same as right",
            [
                ("The controls limit what can run. They do not show the answer is ", {}),
                ("analytically correct", BB),
                (".", {}),
            ],
        ),
        (
            "Selection helps at scale",
            [
                ("The gain comes from the ", {}),
                ("65- and 34-table databases", BB),
                (". It is not a universal result.", {}),
            ],
        ),
        (
            "Judge the whole answer",
            [
                (
                    "About one in three Spider answers still did not match, and better retrieval "
                    "did not measurably help. ",
                    {},
                ),
                ("A person should review", BB),
                (" results.", {}),
            ],
        ),
        (
            "Smaller prompts are not faster here",
            [
                ("Each question gets a different schema, so the local model ", {}),
                ("cannot reuse its cache", BB),
                (".", {}),
            ],
        ),
    ],
)

# Slide 3: agenda
s = new_slide(
    "AGENDA",
    "From the problem to the evidence",
    "Why it is hard, what we built, what we measured and what comes next.",
    3,
)
line(s, 75, 162, 780, 162, color=RULE, width=1.5)
for x, n, fill, fg, head, question, items in (
    (
        43.5,
        "01",
        BLUE,
        WHITE,
        "Problem",
        "What are we solving?",
        (("Why it is hard", 4), ("Other tools", 5), ("Our aim", 6)),
    ),
    (
        267.5,
        "02",
        NAVY,
        WHITE,
        "Solution",
        "What did we build?",
        (("Demo", 7), ("Data boundary", 8), ("Architecture", 9), ("Safety", 10)),
    ),
    (
        491.5,
        "03",
        AMBER,
        NAVY,
        "Evidence",
        "What did we learn?",
        (
            ("Method", 11),
            ("Benchmarks", 12),
            ("Large schemas", 13),
            ("Trials", 14),
            ("Retrieval", 15),
        ),
    ),
    (
        715.5,
        "04",
        SLATE,
        WHITE,
        "Next steps",
        "What should we test next?",
        (("Tests", 16), ("Close", 17)),
    ),
):
    o = shape(s, MSO_SHAPE.OVAL, x, 130, 64, 64, fill=fill)
    tf = o.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(tf, [[(n, {"bold": True, "size": 24, "color": fg})]], align=PP_ALIGN.CENTER)
    text(s, x, 208, 200, 26, [[(head, {"bold": True, "size": 16})]])
    text(s, x, 238, 200, 18, [[(question, {"color": GREY})]], size=10)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 264, 200, 160, fill=CREAM, radius=0.05)
    for i, (item, page) in enumerate(items):
        y = 270 + i * 30
        text(s, x + 12, y + 2, 140, 20, [[(item, {})]], size=10)
        chip = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 164, y + 3, 24, 18, fill=fill, radius=0.3)
        tf = chip.text_frame
        for side in ("left", "right", "top", "bottom"):
            setattr(tf, f"margin_{side}", 0)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        write(tf, [[(str(page), {"bold": True, "size": 10, "color": fg})]], align=PP_ALIGN.CENTER)
        if i < len(items) - 1:
            line(s, x + 12, y + 27, x + 188, y + 27, color=RULE, width=0.75)

# Slide 4: why it is hard
s = new_slide(
    "PROBLEM  >  WHY IT IS HARD",
    "A fluent answer can still be the wrong answer",
    "Text-to-SQL turns a question into SQL over a schema, then returns "
    "rows; each step can go wrong",
    4,
)
steps = [
    ("chat", "Question", "What the person asks"),
    ("schema", "Schema", "Tables and columns"),
    ("code", "SQL", "The generated query"),
    ("table_rows", "Rows", "The answer returned"),
]
for i, (ic, h, b) in enumerate(steps):
    x = 43.5 + i * 155
    card(
        s,
        x,
        130,
        141,
        56,
        [[(h, {"bold": True, "size": 12})], [(b, {"size": 10, "color": GREY})]],
        fill=CREAM,
        anchor=MSO_ANCHOR.MIDDLE,
        pad=8,
    ).text_frame.margin_left = Pt(40)
    icon(s, ic, "blue", x + 9, 146, 24)
    if i < 3:
        line(s, x + 141, 158, x + 155, 158, color=SLATE, arrow=True)
problems = [
    (
        43.5,
        PALE_AMBER,
        "Meaning",
        [
            ("Words like ", {}),
            ("“revenue”", BB),
            (" are not columns. Gross or net? The schema does not say.", {}),
        ],
    ),
    (
        248.5,
        PALE_BLUE,
        "Scale",
        [
            ("Real schemas are large. Spider 2.0 databases often exceed ", {}),
            ("1,000 columns", BB),
            (".", {}),
        ],
    ),
    (
        453.5,
        "E8EAEE",
        "Risk",
        [
            ("Generated SQL runs on ", {}),
            ("real data", BB),
            (", so it must be stopped from changing it.", {}),
        ],
    ),
]
for x, fill, h, b in problems:
    card(
        s,
        x,
        196,
        196,
        76,
        [[(h, {"bold": True, "size": 12, "color": NAVY})], b],
        fill=fill,
        after=2,
        size=10,
    )
marker(s, 1, 37, 190)
marker(s, 2, 28, 287)
marker(s, 3, 333, 398)
marker(s, 4, 447, 190)
text(
    s,
    43.5,
    284,
    606,
    20,
    [[("Published scores fall on enterprise tasks", {"bold": True, "size": 12})]],
)
SCALE = 4.6
BAR_X = 171.5
for i, (lab, v, col) in enumerate((("Spider 1.0", 91.2, SLATE), ("BIRD", 73.0, AMBER))):
    bar_row(s, lab, f"{v} %", v * SCALE, col, 308 + i * 24, label_w=128, h=18)
text(s, 43.5, 356, 128, 18, "Spider 2.0 enterprise", size=10, anchor=MSO_ANCHOR.MIDDLE)
for x, w, fill, label, fg in (
    (BAR_X, 21.3 * SCALE, BLUE, "21.3 %", WHITE),
    (BAR_X + 21.3 * SCALE, 69.9 * SCALE, PALE_BLUE, "69.9 points below Spider 1.0", BLUE),
):
    bar = shape(s, MSO_SHAPE.RECTANGLE, x, 356, w, 18, fill=fill)
    tf = bar.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(tf, [[(label, {"bold": True, "size": 10, "color": fg})]], align=PP_ALIGN.CENTER)
for x, w, runs in (
    (
        43.5,
        285,
        [
            ("Why scores fall: ", B),
            ("tasks need metadata, ", {}),
            ("several SQL dialects", BB),
            (" and project code, and queries often pass ", {}),
            ("100 lines", BB),
            (".", {}),
        ],
    ),
    (
        350.5,
        299,
        [
            ("In this project: ", B),
            ("64.6 %", BB),
            (" on Spider and ", {}),
            ("35.2 %", BB),
            (" on BIRD with evidence, using our own scorer, so not comparable with the chart.", {}),
        ],
    ),
):
    card(s, x, 386, w, 56, [runs], fill=CREAM, size=10)
note(
    s,
    "share of tasks solved, o1-preview results reported in the Spider 2.0 "
    "paper (2024); not this project's results.",
    y=450,
)
takeaways(
    s,
    [
        (
            "SQL is the easy part",
            [
                ("The hard part is knowing ", {}),
                ("what the question means", BB),
                (" in this database.", {}),
            ],
        ),
        (
            "Demos flatter; enterprise data does not",
            [
                ("Published scores fall about 70 points on enterprise tasks, so ", {}),
                ("a good demo is not evidence", BB),
                (".", {}),
            ],
        ),
        (
            "We see the same direction",
            [
                ("Our scores also fall on the harder test, from ", {}),
                ("64.6 % to 35.2 %", BB),
                (".", {}),
            ],
        ),
        (
            "Keep a person in the loop",
            [
                (
                    "A valid query can still answer the wrong question. Dashboards and "
                    "analyst SQL remain best for ",
                    {},
                ),
                ("defined, recurring metrics", BB),
                (".", {}),
            ],
        ),
    ],
)

# Slide 5: other approaches, one comparison table
s = new_slide(
    "PROBLEM  >  OTHER TOOLS",
    "Other tools get business meaning through setup",
    "Two routes to meaning, compared on the same criteria",
    5,
)
HEAD = ("APPROACH", "SOURCE", "SETUP", "UPKEEP", "BEST FOR", "RISK")
WIDTHS = (118, 100, 96, 96, 98, 98)
BANDS = (
    ("PEOPLE DEFINE THE MEANING", 1),
    ("SYSTEMS WORK IT OUT", 3),
    ("THIS PROJECT", 4),
)
rows = [
    (
        0,
        "snowflake",
        "Snowflake Cortex Analyst",
        "1",
        "Semantic view",
        (2, "Define view"),
        (2, "Refine with evaluations"),
        "Agreed metrics",
        "Stale definitions",
    ),
    (
        0,
        "databricks",
        "Databricks Genie Agents",
        "2",
        "SQL expressions, example SQL",
        (3, "Expert curation"),
        (2, "Iterate with feedback"),
        "One topic and audience",
        "Curator-dependent",
    ),
    (
        0,
        "wren",
        "WrenAI",
        "3",
        "Semantic layer in Git",
        (2, "Define MDL model"),
        (2, "Review in Git"),
        "Versioned definitions",
        "Unmodelled data",
    ),
    (
        1,
        "vanna",
        "Vanna",
        "4",
        "Saved past queries",
        (1, "Learns from use"),
        (2, "Self-maintained"),
        "Repeated questions",
        "Repeats past errors",
    ),
    (
        1,
        None,
        "BIRD leaderboard systems",
        "5",
        "Mostly not listed",
        (None, "Not listed"),
        (None, "Not listed"),
        "Benchmark scores",
        "Transfer unproven",
    ),
    (
        2,
        "project",
        "This project",
        "",
        "Schema, bounded hints",
        (0, "Connect only"),
        (0, "None"),
        "First look",
        "Person checks meaning",
    ),
]
TX, TY, HEAD_H, BAND_H, ROW_H = 43.5, 130, 18, 16, 35


def dots(level):
    """Effort as three dots; None means the effort is not listed."""
    if level is None:
        return [("–", {"size": 8, "color": GREY})]
    return [
        ("●" * level, {"size": 8, "color": BLUE}),
        ("●" * (3 - level), {"size": 8, "color": RULE}),
    ]


n_rows = 1 + len(BANDS) + len(rows)
table = s.shapes.add_table(
    n_rows, 6, Pt(TX), Pt(TY), Pt(sum(WIDTHS)), Pt(HEAD_H + BAND_H * 3 + ROW_H * len(rows))
).table
for c, w in enumerate(WIDTHS):
    table.columns[c].width = Pt(w)


def cell(r, c, value, fill, **opt):
    """Fill one table cell."""
    target = table.cell(r, c)
    target.fill.solid()
    target.fill.fore_color.rgb = rgb(fill)
    target.margin_left = target.margin_right = Pt(5)
    target.margin_top = target.margin_bottom = Pt(2)
    target.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(target.text_frame, [[(value, {"size": 8, **opt})]])


table.rows[0].height = Pt(HEAD_H)
for c, head in enumerate(HEAD):
    cell(0, c, head, WHITE, bold=True, color=NAVY)
r, y, band = 1, TY + HEAD_H, -1
for group, lg, name, mark, *values in rows:
    if group != band:
        band = group
        label, number = BANDS[group]
        table.rows[r].height = Pt(BAND_H)
        table.cell(r, 0).merge(table.cell(r, 5))
        for c in range(6):
            table.cell(r, c).fill.solid()
            table.cell(r, c).fill.fore_color.rgb = rgb(CREAM)
        cell(r, 0, label, CREAM, bold=True, color=SLATE)
        marker(s, number, 28, y + 2)
        r, y = r + 1, y + BAND_H
    table.rows[r].height = Pt(ROW_H)
    fill = PALE_BLUE if lg == "project" else WHITE
    cell(r, 0, name, fill, bold=True)
    if mark:
        run = table.cell(r, 0).text_frame.paragraphs[0].add_run()
        run.text = mark
        run.font.name, run.font.size, run.font.bold = FONT, Pt(8), True
        run.font.color.rgb = rgb(BLUE)
        run.font._element.set("baseline", "30000")
    table.cell(r, 0).margin_left = Pt(30)
    source, setup, upkeep, best, risk = values
    project = lg == "project"
    cell(r, 1, source, fill)
    for c, (level, label) in ((2, setup), (3, upkeep)):
        target = table.cell(r, c)
        target.fill.solid()
        target.fill.fore_color.rgb = rgb(fill)
        target.margin_left = target.margin_right = Pt(5)
        target.margin_top = target.margin_bottom = Pt(2)
        target.vertical_anchor = MSO_ANCHOR.MIDDLE
        write(
            target.text_frame,
            [
                dots(level),
                [(label, {"size": 8, **(BB if project else {})})],
            ],
        )
    cell(r, 4, best, fill)
    cell(r, 5, risk, fill, **(BB if project else {}))
    for c, name_icon, colour in ((4, "check_circle", "blue"), (5, "cancel", "amber")):
        table.cell(r, c).margin_left = Pt(19)
        icon(s, name_icon, colour, TX + sum(WIDTHS[:c]) + 5, y + ROW_H / 2 - 5, 10)
    if lg == "project":
        icon(s, "fact_check", "blue", TX + 6, y + 8, 19)
    elif lg:
        logo(s, lg, TX + 6, y + 8, 19)
    else:
        icon(s, "science", "blue", TX + 6, y + 8, 19)
    line(s, TX, y + ROW_H, TX + sum(WIDTHS), y + ROW_H, color=RULE, width=0.5)
    r, y = r + 1, y + ROW_H
line(s, TX, TY + HEAD_H, TX + sum(WIDTHS), TY + HEAD_H, color=NAVY, width=1.0)
marker(s, 2, TX + 118 + 100 + 96 - 9, TY + 3)
text(
    s,
    43.5,
    114,
    606,
    12,
    [
        [
            ("EFFORT  ", B),
            *dots(3),
            (" High    ", {}),
            *dots(2),
            (" Moderate    ", {}),
            *dots(1),
            (" Low    ", {}),
            *dots(0),
            (" None", {}),
        ]
    ],
    size=8,
    color=GREY,
    align=PP_ALIGN.RIGHT,
)
SOURCES = (
    (
        "1",
        "Recommends moving to Cortex Agents; Autopilot can draft a view. ",
        "Snowflake docs",
        "https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst",
    ),
    (
        "2",
        "Formerly Genie Spaces; advises five or fewer tables. ",
        "Databricks docs",
        "https://docs.databricks.com/aws/en/genie/best-practices",
    ),
    (
        "3",
        "Engine is Apache-2.0; some features are commercial. ",
        "WrenAI repository",
        "https://github.com/Canner/WrenAI",
    ),
    (
        "4",
        "Archived 29 March 2026; version 2.0 learns from saved queries. ",
        "Vanna repository",
        "https://github.com/vanna-ai/vanna",
    ),
    (
        "5",
        "Top test entry, AskData, 83.40 %; most entries list no method. ",
        "BIRD leaderboard",
        "https://bird-bench.github.io/",
    ),
)
text(
    s,
    43.5,
    409,
    606,
    66,
    [
        [
            ("Note: ", B),
            (
                "Effort is our qualitative assessment, not a ranking. "
                "Sources read 6 November 2026.",
                {},
            ),
        ],
        *[
            [(n, {"sup": True}), (" " + fact, {}), (label, {"url": url, "color": BLUE})]
            for n, fact, label, url in SOURCES
        ],
    ],
    size=8,
    color=GREY,
    spacing=1.0,
)
takeaways(
    s,
    [
        (
            "Setup is the price of meaning",
            [
                ("Vendors add what schemas lack: ", {}),
                ("business definitions and metrics", BB),
                (", written down before the first answer.", {}),
            ],
        ),
        (
            "That work does not end",
            [
                ("Snowflake and Databricks both expect teams to ", {}),
                ("test and refine", BB),
                (" over time.", {}),
            ],
        ),
        (
            "Systems are close, not done",
            [
                ("The top BIRD test score, ", {}),
                ("83.40 %", BB),
                (", is still below 92.96 % for humans.", {}),
            ],
        ),
        (
            "We pay in review, not setup",
            [
                ("With no model to build, ", {}),
                ("a person must check", BB),
                (" what each answer means.", {}),
            ],
        ),
    ],
)

# Slide 6: our aim
s = new_slide(
    "PROBLEM  >  OUR AIM",
    "Our aim: useful without setup, and checkable by default",
    "A narrower tool: no curated semantic model, with the checking in the user's hands",
    6,
)
for x, ic, name, b in (
    (43.5, "query_stats", "Useful without setup", "connect a database and ask a question"),
    (349.5, "fact_check", "Checkable by default", "SQL shown, validated and run read-only"),
):
    card(
        s,
        x,
        130,
        300,
        42,
        [[(name, {"bold": True, "size": 12})], [(b, {"size": 10, "color": GREY})]],
        fill=PALE_BLUE,
        anchor=MSO_ANCHOR.MIDDLE,
    ).text_frame.margin_left = Pt(38)
    icon(s, ic, "blue", x + 8, 139, 24)
marker(s, 1, 37, 124)
MX, MY, MW, MH = 66, 182, 584, 254
HALF_W, HALF_H = MW / 2, MH / 2
for qx, qy, fill, label in (
    (MX, MY, PALE_AMBER, "MEANING WITHOUT SETUP: THE IDEAL, NOT YET AVAILABLE"),
    (MX + HALF_W, MY, PALE_BLUE, "MEANING THROUGH SETUP: CURATED TOOLS"),
    (MX, MY + HALF_H, CREAM, "QUICK START: PEOPLE CHECK THE MEANING"),
    (MX + HALF_W, MY + HALF_H, "F1F2F4", "SETUP WITHOUT MEANING: TO AVOID"),
):
    shape(s, MSO_SHAPE.RECTANGLE, qx, qy, HALF_W, HALF_H, fill=fill)
    inset = 20 if label.startswith("MEANING THROUGH") else 8
    text(s, qx + inset, qy + 7, HALF_W - 28, 12, [[(label, B)]], size=8, color=GREY)
line(s, MX - 4, MY + MH + 4, MX - 4, MY, color=NAVY, width=1.25, arrow=True)
line(s, MX - 4, MY + MH + 4, MX + MW, MY + MH + 4, color=NAVY, width=1.25, arrow=True)
axis = text(
    s,
    -67,
    302,
    230,
    12,
    [[("BUSINESS MEANING BUILT IN", B)]],
    size=8,
    align=PP_ALIGN.CENTER,
)
axis.rotation = -90
text(s, 34, MY, 24, 12, [[("HIGH", B)]], size=8, color=GREY, align=PP_ALIGN.RIGHT)
text(s, 34, MY + MH - 12, 24, 12, [[("LOW", B)]], size=8, color=GREY, align=PP_ALIGN.RIGHT)
text(
    s,
    MX,
    MY + MH + 7,
    MW,
    12,
    [[("SETUP BEFORE THE FIRST USEFUL ANSWER", B)]],
    size=8,
    align=PP_ALIGN.CENTER,
)
text(s, MX, MY + MH + 7, 40, 12, [[("NONE", B)]], size=8, color=GREY)
text(
    s, MX + MW - 40, MY + MH + 7, 40, 12, [[("HIGH", B)]], size=8, color=GREY, align=PP_ALIGN.RIGHT
)
for name, mark, x, y, right in (
    ("BI dashboards", "monitoring", 500, 28, True),
    ("Snowflake Cortex Analyst", "snowflake", 320, 54, False),
    ("Databricks Genie Agents", "databricks", 470, 80, True),
    ("WrenAI", "wren", 320, 104, False),
    ("Vanna", "vanna", 170, 160, False),
    ("This project", "fact_check", 40, 176, False),
    ("General chatbot", "chat", 40, 222, False),
):
    if mark in ("monitoring", "chat"):
        icon(s, mark, "navy", MX + x, MY + y - 2, 16)
    elif mark == "fact_check":
        icon(s, mark, "blue", MX + x, MY + y - 2, 16)
    else:
        logo(s, mark, MX + x, MY + y - 2, 16)
    project = name == "This project"
    text(
        s,
        MX + x + (-135 if right else 21),
        MY + y,
        130,
        14,
        [[(name, {"bold": project, "size": 10, "color": BLUE if project else NAVY})]],
        align=PP_ALIGN.RIGHT if right else None,
    )
marker(s, 2, MX + 25, MY + 178)
marker(s, 3, 44, 228)
marker(s, 4, MX + HALF_W + 5, MY + 5)
note(
    s,
    "Product positions reflect the Setup ratings on slide 5; other placements are our "
    "qualitative assessment. BIRD systems are excluded: setup not published.",
    x=66,
    y=457,
    w=584,
)
takeaways(
    s,
    [
        (
            "Who it helps",
            [
                ("An analyst who knows the ", {}),
                ("question but not the schema", BB),
                (", and a reviewer judging whether to trust the answer.", {}),
            ],
        ),
        (
            "What we chose",
            [
                ("A quick start with ", {}),
                ("tested checks", BB),
                (": no model to build, and all 45 conformance tests passed.", {}),
            ],
        ),
        (
            "What we gave up",
            [
                ("No governed metric definitions, so ", {}),
                ("“revenue” stays ambiguous", BB),
                (" until a person checks it.", {}),
            ],
        ),
        (
            "When a curated tool fits better",
            [
                ("If metrics must match across teams, ", {}),
                ("choose a governed tool", BB),
                (". This project suits a first look.", {}),
            ],
        ),
    ],
)

# Slide 7: demo
s = new_slide(
    "SOLUTION  >  DEMO",
    "The SQL shows what the answer includes",
    "One revenue question on the Retail Analytics demo, answered by the local model",
    7,
)
GIF_W, GIF_H = 360, 214
demo = s.shapes.add_picture(
    str(HERE / "captures" / "2026-11-06-retail-demo.gif"), Pt(43.5), Pt(130), Pt(GIF_W), Pt(GIF_H)
)
demo.line.color.rgb = rgb(RULE)
demo.line.width = Pt(0.75)
marker(s, 1, 37, 124)
TW = (58, 90, 90)
TXX = 412
compare = s.shapes.add_table(4, 3, Pt(TXX), Pt(130), Pt(sum(TW)), Pt(214)).table
for c, w in enumerate(TW):
    compare.columns[c].width = Pt(w)
for r, h in enumerate((24, 70, 60, 60)):
    compare.rows[r].height = Pt(h)
COMPARE = (
    ("", "DEMO QUESTION", "BENCHMARK QUESTION"),
    ("Wording", "“...the most revenue?”", "“...the most completed order revenue?”"),
    ("Orders", "All 220, with cancelled and returned", "179 completed"),
    ("Discounts", "Ignored", "Applied"),
)
for r, row in enumerate(COMPARE):
    for c, value in enumerate(row):
        target = compare.cell(r, c)
        target.fill.solid()
        target.fill.fore_color.rgb = rgb(WHITE if r == 0 else (CREAM if r % 2 else WHITE))
        target.margin_left = target.margin_right = Pt(5)
        target.margin_top = target.margin_bottom = Pt(2)
        target.vertical_anchor = MSO_ANCHOR.MIDDLE
        write(target.text_frame, [[(value, {"size": 8, "bold": r == 0 or c == 0})]])
line(s, TXX, 154, TXX + sum(TW), 154, color=NAVY, width=1.0)
marker(s, 2, TXX - 11, 134)
text(
    s,
    43.5,
    352,
    606,
    16,
    [[("Same top category, two definitions of revenue", {"bold": True, "size": 12})]],
)
marker(s, 3, 28, 355)
REV_SCALE = 340 / 173366
bar_row(s, "Demo question", "173,366", 340, SLATE, 374, label_w=128, h=18)
text(s, 43.5, 398, 128, 18, "Benchmark question", size=10, anchor=MSO_ANCHOR.MIDDLE)
for x, w, fill, label, fg in (
    (171.5, 136984 * REV_SCALE, BLUE, "136,984", WHITE),
    (171.5 + 136984 * REV_SCALE, (173366 - 136984) * REV_SCALE, PALE_BLUE, "21 % lower", BLUE),
):
    bar = shape(s, MSO_SHAPE.RECTANGLE, x, 398, w, 18, fill=fill)
    tf = bar.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(tf, [[(label, {"bold": True, "size": 10, "color": fg})]], align=PP_ALIGN.CENTER)
marker(s, 4, 28, 430)
note(
    s,
    "Electronics revenue. This illustrates inspection, not a benchmark failure: the two "
    "questions are worded differently. Recomputed on data/retail_analytics.db.",
    y=428,
)
takeaways(
    s,
    [
        (
            "The answer looks finished",
            [
                ("Electronics leads with ", {}),
                ("173,366", BB),
                (", yet the chart does not say which orders it counted.", {}),
            ],
        ),
        (
            "The SQL shows the choice",
            [
                ("It sums price × quantity with ", {}),
                ("no status filter and no discounts", BB),
                (", so all 220 orders count.", {}),
            ],
        ),
        (
            "Wording changes the number",
            [
                ("Asking for completed order revenue gives 136,984, about ", {}),
                ("21 % lower", BB),
                (", with the same top category.", {}),
            ],
        ),
        (
            "This is why inspection matters",
            [
                ("Neither figure is wrong by itself. ", {}),
                ("A person decides", BB),
                (" which revenue the business means.", {}),
            ],
        ),
    ],
)

prs.save(OUT)
print("wrote", OUT.name)
