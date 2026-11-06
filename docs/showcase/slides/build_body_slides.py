"""Build the body objects of deck slides 2 to 16 as editable shapes in a PowerPoint.

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
from pptx.enum.dml import MSO_LINE
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
CODE = "Google Sans Code"
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


def line(s, x1, y1, x2, y2, color=RULE, width=1.0, arrow=False, dashed=False, both=False):
    """A flat native connector."""
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    if dashed:
        c.line.dash_style = MSO_LINE.DASH
    style = c._element.find(qn("p:style"))
    if style is not None:
        c._element.remove(style)
    if arrow:
        ln = c.line._get_or_add_ln()
        head = {"type": "triangle", "w": "med", "len": "med"}
        if both:
            ln.append(ln.makeelement(qn("a:headEnd"), head))
        ln.append(ln.makeelement(qn("a:tailEnd"), head))


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
    y=398,
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
TXX = 412
CARD_W = 238
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, TXX, 130, CARD_W, GIF_H, fill=NAVY, radius=0.03)
text(
    s,
    TXX + 12,
    139,
    CARD_W - 24,
    12,
    [[("THE SQL, AND WHAT COMPLETED REVENUE ADDS", {"bold": True, "color": WHITE})]],
    size=8,
)
SQL_LINES = (
    ("SELECT category, SUM(unit_price * quantity", False),
    ("+   * (1 - discount_pct)", True),
    ("  ) AS total_revenue", False),
    ("FROM order_items oi", False),
    ("JOIN products p", False),
    ("  ON oi.product_id = p.product_id", False),
    ("+ JOIN orders o ON oi.order_id = o.order_id", True),
    ("+ WHERE o.order_status = 'Completed'", True),
    ("GROUP BY category", False),
    ("ORDER BY total_revenue DESC;", False),
)
text(
    s,
    TXX + 12,
    160,
    CARD_W - 20,
    150,
    [
        [(code, {"font": CODE, "size": 8, "color": AMBER if added else WHITE, "bold": added})]
        for code, added in SQL_LINES
    ],
    size=8,
    after=4,
)
text(
    s,
    TXX + 12,
    324,
    CARD_W - 24,
    12,
    [[("Amber: added by the benchmark question", {"color": AMBER})]],
    size=8,
)
marker(s, 2, TXX - 6, 124)
text(
    s,
    43.5,
    352,
    606,
    16,
    [[("Same top category, two definitions of revenue", {"bold": True, "size": 12})]],
)
marker(s, 3, 28, 355)
REV_SCALE = 300 / 173366
bar_row(s, "All 220 orders, list price", "173,366", 300, SLATE, 374, label_w=168, h=18)
text(s, 43.5, 398, 168, 18, "179 completed, after discounts", size=10, anchor=MSO_ANCHOR.MIDDLE)
for x, w, fill, label, fg in (
    (211.5, 136984 * REV_SCALE, BLUE, "136,984", WHITE),
    (211.5 + 136984 * REV_SCALE, (173366 - 136984) * REV_SCALE, PALE_BLUE, "21 % lower", BLUE),
):
    bar = shape(s, MSO_SHAPE.RECTANGLE, x, 398, w, 18, fill=fill)
    tf = bar.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(tf, [[(label, {"bold": True, "size": 10, "color": fg})]], align=PP_ALIGN.CENTER)
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


# Slides 8 to 16 share these two helpers.
def box(s, x, y, w, h, label, fill, fg=NAVY, size=10, bold=True, kind=MSO_SHAPE.RECTANGLE):
    """A filled shape with one centred label."""
    o = shape(s, kind, x, y, w, h, fill=fill)
    tf = o.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    write(tf, [[(label, {"bold": bold, "size": size, "color": fg})]], align=PP_ALIGN.CENTER)
    return o


def step(s, x, y, w, h, head, body, fill=CREAM):
    """A card with a 12 pt heading and 10 pt body."""
    return card(
        s,
        x,
        y,
        w,
        h,
        [[(head, {"bold": True, "size": 12})], [(body, {"size": 10})]],
        fill=fill,
        after=2,
    )


# Slide 8: data boundary
s = new_slide(
    "SOLUTION  >  DATA BOUNDARY",
    "The model sees 79 stored values, not the 1,851 rows",
    "What the prompt held for the demo question on the Retail Analytics database",
    8,
)
text(
    s,
    43.5,
    130,
    606,
    16,
    [[("79 of the 608 stored text values reach the prompt", {"bold": True, "size": 12})]],
)
BARW = 606
SENT_W = BARW * 79 / 608
box(s, 43.5, 152, SENT_W, 18, "79 sent", AMBER)
box(s, 43.5 + SENT_W, 152, BARW - SENT_W, 18, "529 not sent", "E8EAEE", fg=GREY)
text(
    s,
    43.5,
    173,
    606,
    12,
    [
        [
            (
                "Distinct values across the database's 30 text columns, sent as lists "
                "and never linked to a row.",
                {},
            )
        ]
    ],
    size=8,
    color=GREY,
)
PW = 372
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, 190, PW, 176, fill=NAVY, radius=0.03)
text(
    s,
    55.5,
    198,
    PW - 24,
    12,
    [[("FROM THE REAL PROMPT (SHORTENED)", {"bold": True, "color": WHITE})]],
    size=8,
)
PROMPT_LINES = (
    ("CREATE TABLE orders (", WHITE),
    ("  order_id INTEGER PRIMARY KEY,", WHITE),
    ("  order_status TEXT NOT NULL ...", WHITE),
    (");", WHITE),
    ("-- order_status sample values:", AMBER),
    ("     Completed, Returned, Cancelled", AMBER),
    ("-- gender sample values: Female, Other, Male", AMBER),
    ("### User question", "9FB6F5"),
    ("Which product categories generate the most revenue?", "9FB6F5"),
)
text(
    s,
    55.5,
    216,
    PW - 20,
    146,
    [[(code, {"font": CODE, "size": 8, "color": colour})] for code, colour in PROMPT_LINES],
    size=8,
    after=3,
)
LX = 427
for k, (head, items, ic, colour) in enumerate(
    (
        (
            "IN THE PROMPT",
            ("Tables, columns, keys", "79 stored values as hints", "The question"),
            "check_circle",
            "blue",
        ),
        (
            "NOT IN THE PROMPT",
            ("Result rows", "Names and emails: over the limit", "All other stored values"),
            "cancel",
            "amber",
        ),
    )
):
    y = 190 + k * 90
    shape(
        s,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        LX,
        y,
        222.5,
        86,
        fill=PALE_BLUE if k == 0 else CREAM,
        radius=0.05,
    )
    text(s, LX + 10, y + 7, 200, 12, [[(head, B)]], size=8, color=GREY)
    for i, item in enumerate(items):
        icon(s, ic, colour, LX + 10, y + 24 + i * 19, 11)
        text(s, LX + 25, y + 22 + i * 19, 190, 15, item, size=10, anchor=MSO_ANCHOR.MIDDLE)
for x, ic, head, body, fill in (
    (43.5, "verified_user", "Local model", "The prompt stays on your machine", PALE_BLUE),
    (349.5, "chat", "Hosted model", "Question, schema and hints go to the provider", PALE_AMBER),
):
    card(
        s,
        x,
        376,
        300,
        48,
        [[(head, {"bold": True, "size": 12})], [(body, {"size": 10})]],
        fill=fill,
        anchor=MSO_ANCHOR.MIDDLE,
    ).text_frame.margin_left = Pt(38)
    icon(s, ic, "blue" if x < 100 else "navy", x + 8, 388, 24)
marker(s, 1, 37, 184)
marker(s, 2, 37, 262)
marker(s, 3, 37, 370)
marker(s, 4, LX - 6, 184)
note(
    s,
    "counted for this question on data/retail_analytics.db; it varies. "
    "Numeric columns send no values. A repair try also sends the failed query and its error.",
    y=432,
)
takeaways(
    s,
    [
        (
            "The prompt is mostly structure",
            [
                ("About ", {}),
                ("71 % of the schema text", BB),
                (" is table definitions. Hints are the other 29 %.", {}),
            ],
        ),
        (
            "Hints are real data",
            [
                ("The limit counts values, not sensitivity. Emails stay out ", {}),
                ("only because there are over 20", BB),
                (".", {}),
            ],
        ),
        (
            "The model choice moves the boundary",
            [
                ("With a local model nothing leaves your machine. A hosted model ", {}),
                ("receives the whole prompt", BB),
                (".", {}),
            ],
        ),
        (
            "Check before using real data",
            [
                ("Review which columns qualify as hints, or ", {}),
                ("turn table selection off", BB),
                (" to send no hints.", {}),
            ],
        ),
    ],
)

# Slide 9: architecture
s = new_slide(
    "SOLUTION  >  ARCHITECTURE",
    "The model proposes SQL; the application controls execution",
    "Five stages take one question to an answer, with the technology behind each step",
    9,
)
# Eight equal cards on a four-column grid, top row left to right, bottom row right to left.
W9, H9, G9 = 130.5, 76, 28
CX = [43.5 + i * (W9 + G9) for i in range(4)]
BAR1, ROW1, DBY, DBH, ROW2, BAR2 = 130, 153, 249, 38, 313, 394
BARH = 18


def stage9(x, y, w, label, output, fill=NAVY):
    """A stage bar: the stage on the left, what it hands on at the right."""
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, BARH, fill=fill, radius=0.2)
    text(s, x + 7, y + 4, 70, 11, [[(label, {"bold": True})]], size=8, color=WHITE)
    text(s, x + w - 117, y + 4, 110, 11, output, size=8, color=WHITE, align=PP_ALIGN.RIGHT)


def step9(n, x, y, name, body, module, marks=("tech-python",), fill=CREAM, badge=NAVY):
    """One step, always laid out the same way: number and name, body, module and logos."""
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, W9, H9, fill=fill, radius=0.07)
    box(s, x + 7, y + 7, 13, 13, str(n), badge, fg=WHITE, size=8, kind=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(s, x + 24, y + 7, W9 - 31, 13, [[(name, B)]], size=10, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 7, y + 24, W9 - 14, 32, [body], size=8)
    text(s, x + 7, y + H9 - 16, 70, 11, [[(module, {"font": CODE})]], size=8, color=GREY)
    right = x + W9 - 7
    for mark in reversed(marks):
        if mark == "tech-sqlglot":  # a wide wordmark, so it keeps its own shape
            shape(
                s,
                MSO_SHAPE.ROUNDED_RECTANGLE,
                right - 41,
                y + H9 - 19,
                41,
                13,
                fill=NAVY,
                radius=0.2,
            )
            s.shapes.add_picture(
                str(LOGOS / f"{mark}.png"), Pt(right - 39), Pt(y + H9 - 17), Pt(37), Pt(9)
            )
            right -= 45
        else:
            logo(s, mark, right - 13, y + H9 - 19, 13)
            right -= 17


stage9(CX[0], BAR1, W9, "ASK", "Output: question")
stage9(CX[1], BAR1, 3 * W9 + 2 * G9, "PREPARE", "Output: prompt")
stage9(CX[3], BAR2, W9, "GENERATE", "Output: SQL text", fill=BLUE)
stage9(CX[1], BAR2, 2 * W9 + G9, "CHECK AND RUN", "Output: rows, refusal or error")
stage9(CX[0], BAR2, W9, "ANSWER", "Output: answer")
step9(
    1,
    CX[0],
    ROW1,
    "Ask",
    [("Pick a demo, a file, a connection or CSV uploads, then ask in plain English", {})],
    "app.py, ui/",
    marks=("tech-streamlit",),
)
step9(
    2,
    CX[1],
    ROW1,
    "Read schema",
    [("Tables, keys and value hints", {}), ("1", {"sup": True})],
    "schema.py",
)
step9(
    3,
    CX[2],
    ROW1,
    "Select tables",
    [("Schema RAG: top 6 by hybrid score, plus neighbours", {}), ("2", {"sup": True})],
    "rag.py",
)
step9(4, CX[3], ROW1, "Build prompt", [("Dialect rules, schema and question", {})], "llm.py")
step9(
    5,
    CX[3],
    ROW2,
    "Generate",
    [
        ("Gemini or Ollama", {}),
        ("3", {"sup": True}),
        (" writes one SQL statement or declines. It never sees result rows", {}),
    ],
    "llm.py",
    marks=("tech-langchain", "tech-googlegemini", "tech-ollama"),
    fill=PALE_BLUE,
    badge=BLUE,
)
step9(
    6,
    CX[2],
    ROW2,
    "Validate",
    [("One SELECT or WITH, no engine internals. Unsafe SQL stops here", {})],
    "safety.py",
    marks=("tech-sqlglot",),
)
step9(
    7,
    CX[1],
    ROW2,
    "Run",
    [
        ("Read-only connection, work budget and row cap", {}),
        ("4", {"sup": True}),
        (". A query error gets one repair", {}),
    ],
    "execution.py",
)
step9(
    8,
    CX[0],
    ROW2,
    "Show",
    [("Answer, table, a chart when it fits, the SQL and why those tables were chosen", {})],
    "ui/results.py",
    marks=("tech-pandas", "tech-streamlit"),
)
# The person opens and closes the flow, in the space between steps 1 and 8.
icon(s, "person", "navy", CX[0] + 7, DBY + 8, 22)
text(
    s,
    CX[0] + 35,
    DBY + 8,
    W9 - 35,
    22,
    [[("The person", B)], [("Asks first, inspects last", {})]],
    size=8,
)
# The database layer between the rows, read by steps 2 and 7.
DBW = 2 * W9 + G9
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, CX[1], DBY, DBW, DBH, fill=PALE_AMBER, radius=0.1)
text(
    s,
    CX[1] + 7,
    DBY + 7,
    112,
    24,
    [[("Database engine", {"bold": True, "size": 10})], [("Set by the connection string", {})]],
    size=8,
)
for x, mark, label in (
    (CX[1] + 120, "tech-sqlite", "SQLite"),
    (CX[1] + 170, "tech-duckdb", "DuckDB"),
    (CX[1] + 220, "tech-postgresql", "PostgreSQL"),
):
    logo(s, mark, x, DBY + 12, 14)
    text(s, x + 17, DBY + 13, 46, 12, label, size=8)
# Arrows at card mid-height, and at each card's centre between the rows.
MID1, MID2 = ROW1 + H9 / 2, ROW2 + H9 / 2
C2, C4 = CX[1] + W9 / 2, CX[3] + W9 / 2
for x1, y1, x2, y2 in (
    (CX[0] + W9, MID1, CX[1], MID1),
    (CX[1] + W9, MID1, CX[2], MID1),
    (CX[2] + W9, MID1, CX[3], MID1),
    (C4, ROW1 + H9, C4, ROW2),
    (CX[3], MID2, CX[2] + W9, MID2),
    (CX[2], MID2, CX[1] + W9, MID2),
    (CX[1], MID2, CX[0] + W9, MID2),
    (C2, DBY, C2, ROW1 + H9),
):
    line(s, x1, y1, x2, y2, color=SLATE, width=1.5, arrow=True)
# The run sends the query and gets rows back.
line(s, C2, ROW2, C2, DBY + DBH, color=SLATE, width=1.5, arrow=True, both=True)
# The one repair, from the run back over step 6 to the model.
RX1, RX2, RY = CX[1] + W9 - 18, CX[3] + 18, DBY + DBH + 10
line(s, RX1, ROW2, RX1, RY, color=AMBER, width=1.5, dashed=True)
line(s, RX1, RY, RX2, RY, color=AMBER, width=1.5, dashed=True)
line(s, RX2, RY, RX2, ROW2, color=AMBER, width=1.5, arrow=True, dashed=True)
marker(s, 1, CX[3] - 6, ROW2 - 6)
marker(s, 2, CX[2] - 6, ROW2 - 6)
marker(s, 3, CX[1] - 6, DBY - 6)
marker(s, 4, CX[2] + W9 / 2 - 6, RY - 6)
# Legend, then the note that explains the content.
for x, fill, label in (
    (CX[0], CREAM, "Application"),
    (CX[0] + 72, PALE_BLUE, "Model"),
    (CX[0] + 124, PALE_AMBER, "Database"),
):
    shape(s, MSO_SHAPE.RECTANGLE, x, 417, 9, 9, fill=fill, line=RULE)
    text(s, x + 13, 416, 56, 11, label, size=8, color=GREY)
line(s, CX[0] + 186, 421.5, CX[0] + 206, 421.5, color=AMBER, width=1.5, dashed=True)
text(s, CX[0] + 211, 416, 100, 11, "One repair try", size=8, color=GREY)
text(
    s,
    43.5,
    429,
    606,
    48,
    [
        [("Note:", B)],
        [
            ("1", {"sup": True}),
            (
                " Value hints are up to 6 stored values from text columns with 20 or fewer "
                "distinct values.",
                {},
            ),
        ],
        [
            ("2", {"sup": True}),
            (
                " The hybrid score combines keyword (BM25), name, character-trigram and hashed "
                "n-gram scores; neighbours are tables one foreign key away.",
                {},
            ),
        ],
        [
            ("3", {"sup": True}),
            (
                " Gemini is hosted; Ollama runs locally through LangChain. The model declines "
                "a request that would change data or that the schema cannot answer.",
                {},
            ),
        ],
        [
            ("4", {"sup": True}),
            (
                " Work budget: 100,000 VM steps on SQLite, 5,000 ms on DuckDB and PostgreSQL. "
                "Row cap: 1,000 rows. A query stopped by the budget is not repaired.",
                {},
            ),
        ],
    ],
    size=8,
    color=GREY,
)
takeaways(
    s,
    [
        (
            "One step of eight uses a model",
            [
                ("It returns text. ", {}),
                ("The application decides", BB),
                (" whether that text runs at all. Retrieval, prompts and checks use no model.", {}),
            ],
        ),
        (
            "Two separate gates",
            [
                ("sqlglot checks the query, then the engine runs it read-only. ", {}),
                ("Neither checks meaning", BB),
                (", so a valid query can still be wrong.", {}),
            ],
        ),
        (
            "One flow, three engines",
            [
                ("The connection string picks the engine, and each passes ", {}),
                ("the same 15 tests", BB),
                (". Each engine enforces read-only in its own way.", {}),
            ],
        ),
        (
            "A query error gets one retry",
            [
                ("The error goes back to the model once, and ", {}),
                ("nothing skips the checks", BB),
                (". A failed repair ends the attempt.", {}),
            ],
        ),
    ],
)

# Slide 10: safety
s = new_slide(
    "SOLUTION  >  SAFETY",
    "Safety does not rest on the model",
    "Three lines of defence stop different threats, and each is tested on its own",
    10,
)
# Threats down the side, layers across, and how many lines each threat meets.
TW, CW, CG, DW = 140, 132, 6, 42
X10 = [43.5 + TW + CG + i * (CW + CG) for i in range(3)]
XD = X10[2] + CW + CG
text(s, 43.5, 142, TW, 12, [[("THREAT AND EXAMPLE", B)]], size=8, color=GREY)
for x, (name, sub, fill) in zip(
    X10,
    (
        ("1  MODEL", "Declines the request", BLUE),
        ("2  APPLICATION", "sqlglot check", NAVY),
        ("3  ENGINE", "Read-only connection", NAVY),
    ),
    strict=True,
):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 130, CW, 30, fill=fill, radius=0.12)
    text(s, x + 7, 134, CW - 14, 11, [[(name, B)]], size=8, color=WHITE)
    text(s, x + 7, 145, CW - 14, 11, sub, size=8, color=WHITE)
text(
    s,
    XD,
    136,
    DW,
    22,
    [[("LINES", B)], [("of defence", {})]],
    size=8,
    color=GREY,
    align=PP_ALIGN.CENTER,
)
TICK, SOFT, GAP = "check_circle-blue", "check_circle-amber", "cancel-amber"
ROWS10 = (
    (
        "Write or schema change",
        "Drop the students table",
        ((SOFT, "Declined 6 of 6"), (TICK, "Blocked"), (TICK, "Denied on 3 engines")),
    ),
    (
        "Reading engine internals",
        "Show me sqlite_master",
        ((SOFT, "Declined 3 of 3"), (TICK, "Blocked"), (GAP, "Would run")),
    ),
    (
        "Reading files on disk",
        "read_csv on a local file",
        (None, (TICK, "Blocked"), (TICK, "Denied")),
    ),
    (
        "Runaway query",
        "A cross join on large tables",
        (None, None, (TICK, "Stopped by work budget")),
    ),
    (
        "Oversized result",
        "More rows than the cap",
        (None, None, (TICK, "Cut at 1,000 rows")),
    ),
    (
        "Data the schema lacks",
        "Each patient's blood type",
        ((SOFT, "Declined 5 of 6"), None, None),
    ),
)
Y10, H10 = 165, 36
y = Y10
for label, example, cells in ROWS10:
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, y, 606, H10, fill=CREAM, radius=0.08)
    text(s, 51, y + 7, TW - 10, 11, [[(label, B)]], size=8)
    text(s, 51, y + 19, TW - 10, 11, example, size=8, color=GREY)
    for x, cell in zip(X10, cells, strict=True):
        if cell:
            name, words = cell
            s.shapes.add_picture(str(ICONS / f"{name}.png"), Pt(x + 7), Pt(y + 12), Pt(12), Pt(12))
            text(s, x + 23, y + 13, CW - 26, 11, words, size=8)
        else:
            line(s, x + 9, y + 18, x + 17, y + 18, color=GREY, width=1.25)
    depth = sum(1 for c in cells if c and c[0] != GAP)
    for k in range(3):
        shape(
            s,
            MSO_SHAPE.OVAL,
            XD + 6 + k * 11,
            y + 14,
            8,
            8,
            fill=BLUE if k < depth else RULE,
        )
    y += H10 + 3
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, y, 606, H10, fill=PALE_AMBER, radius=0.08)
text(s, 51, y + 7, TW - 10, 11, [[("Valid SQL, wrong meaning", B)]], size=8)
text(s, 51, y + 19, TW - 10, 11, "Shipping weight became unit cost", size=8, color=GREY)
icon(s, "person", "navy", X10[0] + 6, y + 11, 14)
text(
    s,
    X10[0] + 23,
    y + 13,
    3 * CW,
    11,
    "No layer checks this, so the person reads the answer and its SQL",
    size=8,
)
for k in range(3):
    shape(s, MSO_SHAPE.OVAL, XD + 6 + k * 11, y + 14, 8, 8, fill=RULE)
marker(s, 1, X10[0] - 6, 124)
marker(s, 2, X10[2] - 6, Y10 - 6)
marker(s, 3, XD - 2, Y10 + 5 * (H10 + 3) - 6)
marker(s, 4, 37.5, y - 6)
# Legend, then scope.
LY = y + H10 + 6
for x, name, label in (
    (43.5, TICK, "Enforced and tested"),
    (140, SOFT, "Model behaviour, measured in one run"),
    (300, GAP, "Not stopped by this layer"),
):
    s.shapes.add_picture(str(ICONS / f"{name}.png"), Pt(x), Pt(LY), Pt(10), Pt(10))
    text(s, x + 13, LY, 150, 11, label, size=8, color=GREY)
line(s, 420, LY + 5, 428, LY + 5, color=GREY, width=1.25)
text(s, 433, LY, 210, 11, "Not this layer's role, or not tested", size=8, color=GREY)
text(
    s,
    43.5,
    LY + 13,
    606,
    12,
    [
        [
            ("Scope: ", B),
            (
                "one model, 15 cases, safety accuracy 73.3 % [53.3, 93.3]. Declining internals as "
                "unanswerable is safe but not counted as correct.",
                {},
            ),
        ],
    ],
    size=8,
    color=GREY,
)
takeaways(
    s,
    [
        (
            "The model is only the first line",
            [
                ("14 of 15 safety cases ended in its own decline. ", {}),
                ("That is behaviour", BB),
                (", and it can change with the model or prompt.", {}),
            ],
        ),
        (
            "Each layer is tested alone",
            [
                ("Writes run straight at each engine, bypassing the application check, and ", {}),
                ("all 3 engines refuse them", BB),
                (".", {}),
            ],
        ),
        (
            "Cover differs by threat",
            [
                ("Writes meet all three lines, but ", {}),
                ("missing data meets only the model", BB),
                (", which declined 5 of 6.", {}),
            ],
        ),
        (
            "No layer checks meaning",
            [
                (
                    "Asked for shipping weight, the model returned unit cost, and every "
                    "check passed. ",
                    {},
                ),
                ("The person is the last check", BB),
                (".", {}),
            ],
        ),
    ],
)

# Slide 11: method
s = new_slide(
    "EVIDENCE  >  METHOD",
    "Every result can be traced and compared fairly",
    "3,817 questions in five suites, every run recorded and every comparison paired",
    11,
)
text(s, 43.5, 130, 286, 15, [[("Each suite answers one question", {"bold": True, "size": 12})]])
for i, (name, n, ask, col) in enumerate(
    (
        ("Spider 1.0 dev", 1034, "Can it write SQL across many domains?", SLATE),
        ("BIRD dev", 1534, "Can it handle messy values, with or without evidence?", SLATE),
        ("Large schemas", 1222, "Does table selection work at 21 to 65 tables?", BLUE),
        ("Demo", 12, "Does it work on the demo's own databases?", AMBER),
        ("Safety", 15, "Does it refuse and decline when it should?", AMBER),
    )
):
    y = 150 + i * 39
    text(s, 43.5, y, 200, 12, [[(name, {"bold": True})]], size=10)
    text(s, 43.5, y + 12, 286, 11, ask, size=8, color=GREY)
    w = max(n / 1534 * 240, 3)
    shape(s, MSO_SHAPE.RECTANGLE, 43.5, y + 24, w, 8, fill=col)
    text(s, 43.5 + w + 5, y + 22, 40, 11, [[(f"{n:,}", B)]], size=8)
for i, (ic, head, body) in enumerate(
    (
        (
            "fact_check",
            "Typed comparison",
            "Results are compared by value and type, so SQL wording does not matter",
        ),
        ("target", "95 % intervals", "10,000 bootstrap resamples over the cases, on every rate"),
        (
            "menu_book",
            "A manifest per run",
            "37 runs recorded, each pinning commit, data, prompt and model",
        ),
        (
            "query_stats",
            "Paired comparisons",
            "Same questions, a named baseline, flagged when not controlled",
        ),
    )
):
    y = 130 + i * 52
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 345, y, 305, 46, fill=CREAM, radius=0.09)
    icon(s, ic, "blue", 354, y + 12, 22)
    text(s, 386, y + 7, 256, 13, [[(head, B)]], size=10)
    text(s, 386, y + 21, 256, 22, body, size=8)
# How to read a paired change, the skill slides 12 to 15 rely on.
PY0, PH = 346, 90
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, PY0, 606.5, PH, fill=PALE_BLUE, radius=0.05)
text(s, 51, PY0 + 7, 300, 13, [[("How to read a paired change", B)]], size=10)
AX0, AX1, V0, V1 = 330.0, 630.0, -2.0, 6.0


def px11(v):
    """A change in points, placed on the axis."""
    return AX0 + (v - V0) / (V1 - V0) * (AX1 - AX0)


for v in (-2, 2, 4, 6):
    line(s, px11(v), PY0 + PH - 20, px11(v), PY0 + PH - 16, color=GREY, width=0.75)
    label = f"+{v}" if v > 0 else str(v).replace("-", "\u2212")
    text(s, px11(v) - 15, PY0 + PH - 14, 30, 11, label, size=8, color=GREY, align=PP_ALIGN.CENTER)
line(s, px11(0), PY0 + 24, px11(0), PY0 + PH - 16, color=NAVY, width=1.25)
text(
    s,
    222,
    PY0 + 9,
    420,
    11,
    "The 0 line means no change. A whole interval to its right is a measurable gain.",
    size=8,
)
text(
    s,
    px11(0) - 30,
    PY0 + PH - 14,
    60,
    11,
    [[("0 no change", B)]],
    size=8,
    align=PP_ALIGN.CENTER,
)
text(s, 222, PY0 + PH - 14, 100, 11, "Change in accuracy points", size=8, color=GREY)
for y, head, sub, mid, lo, hi, col, tag in (
    (
        PY0 + 26,
        "Top 6 against every table with hints",
        "Large schemas, 1,222 questions",
        3.6,
        1.4,
        5.8,
        BLUE,
        "+3.6 [+1.4, +5.8]  measurable",
    ),
    (
        PY0 + 56,
        "One prompt layout against another",
        "Large schemas, 1,222 questions",
        0.2,
        -1.5,
        2.0,
        SLATE,
        "+0.2 [-1.5, +2.0]  not measurable",
    ),
):
    text(s, 51, y, 270, 11, [[(head, {"bold": True})]], size=8)
    text(s, 51, y + 11, 270, 11, sub, size=8, color=GREY)
    line(s, px11(lo), y + 13, px11(hi), y + 13, color=col, width=2.5)
    shape(s, MSO_SHAPE.OVAL, px11(mid) - 4, y + 9, 8, 8, fill=col)
    tx, ty = (px11(lo), y - 2) if lo > 0 else (px11(hi) + 7, y + 8)
    text(s, tx, ty, 170, 11, [[(tag, {"bold": True, "color": col})]], size=8)
marker(s, 1, 339, 124 + 3 * 52)
marker(s, 2, 29, 150 + 2 * 39)
marker(s, 3, 29, 150 + 3 * 39)
marker(s, 4, 37.5, PY0 - 6)
for x, fill, label in (
    (43.5, SLATE, "Accuracy"),
    (98, BLUE, "Table selection"),
    (178, AMBER, "Diagnostics"),
):
    shape(s, MSO_SHAPE.RECTANGLE, x, 442, 9, 9, fill=fill)
    text(s, x + 13, 441, 70, 11, label, size=8, color=GREY)
note(s, "accuracy uses this project's typed comparison, not the benchmark scorers.", y=455)
takeaways(
    s,
    [
        (
            "Compare the same questions",
            [
                ("A change counts only against a named baseline, with a ", {}),
                ("paired interval", BB),
                (" on the same questions.", {}),
            ],
        ),
        (
            "Test where selection matters",
            [
                ("Dev databases have at most 14 tables, so a separate suite tests ", {}),
                ("21 to 65 tables", BB),
                (".", {}),
            ],
        ),
        (
            "Small suites are diagnostics",
            [
                ("With 12 and 15 cases, these suites ", {}),
                ("show behaviour, not accuracy", BB),
                (": their intervals are wide.", {}),
            ],
        ),
        (
            "Read the interval, not the point",
            [
                ("A change is measurable only when ", {}),
                ("its interval clears zero", BB),
                (". Slides 12 to 15 use this rule.", {}),
            ],
        ),
    ],
)

# Slide 12: benchmarks
s = new_slide(
    "EVIDENCE  >  BENCHMARKS",
    "Local model: 64.6 % on Spider, 35.2 % on BIRD with evidence",
    "Answers matched, with 95 % intervals; one local 9B model, thinking off, 10 October 2026",
    12,
)
AX0, AXW = 190, 440
px = lambda v: AX0 + v / 80 * AXW  # noqa: E731
for v in (0, 20, 40, 60, 80):
    line(s, px(v), 136, px(v), 268, color=RULE, width=0.5)
    text(s, px(v) - 20, 270, 40, 11, [[(f"{v} %", {})]], size=8, color=GREY, align=PP_ALIGN.CENTER)
for i, (name, sub, v, lo, hi, col) in enumerate(
    (
        ("Spider 1.0 dev", "1,034 questions", 64.6, 61.6, 67.5, BLUE),
        ("BIRD dev, with evidence", "1,534 questions", 35.2, 32.9, 37.6, BLUE),
        ("BIRD dev, no evidence", "1,534 questions", 25.1, 22.9, 27.3, SLATE),
        ("Demo suite", "12 questions, 4 matched", 33.3, 8.3, 58.3, AMBER),
    )
):
    y = 142 + i * 32
    text(s, 43.5, y - 3, 140, 26, [[(name, B)], [(sub, {"size": 8, "color": GREY})]], size=10)
    line(s, px(lo), y + 8, px(hi), y + 8, color=col, width=2.5)
    shape(s, MSO_SHAPE.OVAL, px(v) - 5, y + 3, 10, 10, fill=col)
    shape(s, MSO_SHAPE.RECTANGLE, px(hi) + 4, y + 1, 40, 14, fill=WHITE)
    text(s, px(hi) + 6, y + 1, 40, 14, [[(f"{v} %", B)]], size=10)
text(s, 43.5, 270, 140, 11, "Dot: score. Line: 95 % interval.", size=8, color=GREY)
# Spider: what each level means, and how it scored.
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, 290, 300, 136, fill=CREAM, radius=0.04)
text(s, 53, 296, 280, 13, [[("Spider by difficulty", B)]], size=10)
text(
    s,
    53,
    309,
    280,
    11,
    "Levels follow Spider's own rule: how many SQL parts a query needs",
    size=8,
    color=GREY,
)
for k, (lab, n, means, v) in enumerate(
    (
        ("Easy", 248, "One table, a count or a maximum", 84.3),
        ("Medium", 446, "A join, or grouping", 65.9),
        ("Hard", 174, "A subquery or EXCEPT", 58.6),
        ("Extra", 166, "Joins with grouping and ordering", 38.0),
    )
):
    y = 324 + k * 25
    text(
        s,
        53,
        y,
        160,
        12,
        [[(lab, {"bold": True, "size": 10}), (f"  {n} questions", {"color": GREY})]],
        size=8,
    )
    text(s, 53, y + 12, 160, 11, means, size=8, color=GREY)
    shape(s, MSO_SHAPE.RECTANGLE, 200, y + 5, v * 1.25, 13, fill=BLUE)
    text(s, 200 + v * 1.25 + 4, y + 6, 40, 12, [[(f"{v} %", B)]], size=8)
# BIRD: each level with and without the benchmark's evidence.
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 349.5, 290, 300, 136, fill=CREAM, radius=0.04)
text(s, 359, 296, 280, 13, [[("BIRD by difficulty", B)]], size=10)
text(
    s,
    359,
    309,
    284,
    11,
    "Evidence is a hint, such as: promotional name refers to flavorName",
    size=8,
    color=GREY,
)
for k, (lab, n, on, off) in enumerate(
    (("Simple", 860, 43.1, 34.2), ("Moderate", 443, 29.1, 16.3), ("Challenging", 231, 17.3, 8.2))
):
    y = 325 + k * 28
    text(s, 359, y + 2, 90, 12, [[(lab, {"bold": True, "size": 10})]], size=8)
    text(s, 359, y + 14, 90, 11, f"{n} questions", size=8, color=GREY)
    for dy, v, col in ((0, on, BLUE), (13, off, SLATE)):
        shape(s, MSO_SHAPE.RECTANGLE, 440, y + dy, v * 1.25, 11, fill=col)
        text(s, 440 + v * 1.25 + 4, y + dy, 40, 11, [[(f"{v} %", B)]], size=8)
shape(s, MSO_SHAPE.RECTANGLE, 572, 393, 9, 9, fill=BLUE)
text(s, 585, 392, 62, 11, "With evidence", size=8, color=GREY)
shape(s, MSO_SHAPE.RECTANGLE, 572, 406, 9, 9, fill=SLATE)
text(s, 585, 405, 62, 11, "No evidence", size=8, color=GREY)
marker(s, 1, 28, 286)
marker(s, 2, 28, 174)
marker(s, 3, 28, 238)
note(
    s,
    "matched means the result set equals the reference answer. This project's scorer, so these "
    "are not leaderboard scores.",
    y=434,
)
takeaways(
    s,
    [
        (
            "Harder questions score lower",
            [
                ("Spider falls from 84.3 % to ", {}),
                ("38.0 %", BB),
                (" across its difficulty levels.", {}),
            ],
        ),
        (
            "BIRD evidence adds 10.1 points",
            [
                ("Hints supplied by the benchmark lift the same questions by ", {}),
                ("10.1 points [8.1, 12.1]", BB),
                (".", {}),
            ],
        ),
        (
            "The demo suite is small",
            [
                ("4 of 12 matched, and its interval is ", {}),
                ("50 points wide", BB),
                (", so a good demo proves little.", {}),
            ],
        ),
        (
            "Thinking needs an output budget",
            [
                ("Turning thinking off avoided empty SQL: ", {}),
                ("+8.5 points [5.8, 11.3]", BB),
                (" on Spider.", {}),
            ],
        ),
    ],
)

# Slide 13: large schemas
s = new_slide(
    "EVIDENCE  >  LARGE SCHEMAS",
    "On large databases, sending fewer tables scored 3.6 points higher",
    "1,222 BIRD train questions on 4 databases of 21 to 65 tables; 19 October 2026",
    13,
)
# One colour per way of sending the schema, used across the slide.
TOP6, HINTS, PLAIN = BLUE, AMBER, SLATE


def bar13(x, y, w, h, label, fill):
    """A bar with its value inside when it fits, and beside it when it does not."""
    shape(s, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=fill)
    if w >= 30:
        ink = NAVY if fill == AMBER else WHITE
        text(
            s, x + 5, y + (h - 11) / 2, w - 8, 11, [[(label, {"bold": True, "color": ink})]], size=8
        )
    else:
        text(s, x + w + 4, y + (h - 11) / 2, 40, 11, [[(label, B)]], size=8)


COLS13 = (
    (178, "fact_check", "Answers matched", 130 / 30),
    (338, "chat", "Prompt tokens", 130 / 8501),
    (498, "timer", "Time per question", 130 / 6),
)
text(s, 43.5, 133, 130, 12, [[("Schema sent", B)]], size=8, color=GREY)
for x, ic, head, _ in COLS13:
    icon(s, ic, "navy", x, 130, 14)
    text(s, x + 18, 132, 130, 12, [[(head, B)]], size=8)
for i, (name, acc, tok, sec, col) in enumerate(
    (
        ("Every table + hints", 25.5, 8501, 4.0, HINTS),
        ("Every table, no hints", 26.8, 6221, 4.2, PLAIN),
        ("Top 6 + neighbours", 29.1, 2670, 6.0, TOP6),
    )
):
    y = 148 + i * 21
    text(s, 43.5, y + 2, 130, 13, [[(name, {"bold": col == TOP6})]], size=10)
    for (x, _, _, k), v, label in zip(
        COLS13, (acc, tok, sec), (f"{acc} %", f"{tok:,}", f"{sec} s"), strict=True
    ):
        bar13(x, y, v * k, 16, label, col)
# Left: the gain by database, on a labelled axis.
PANEL13 = 216
PH13 = 170
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, PANEL13, 300, PH13, fill=CREAM, radius=0.04)
icon(s, "query_stats", "blue", 52, PANEL13 + 7, 22)
text(s, 80, PANEL13 + 7, 258, 13, [[("Gain from top 6, by database", B)]], size=10)
text(
    s,
    80,
    PANEL13 + 19,
    258,
    11,
    "Against every table + hints, paired 95 % interval",
    size=8,
    color=GREY,
)
D0, DW = 150, 180
pd = lambda v: D0 + (v + 8) / 20 * DW  # noqa: E731
YD = PANEL13 + 36
line(s, pd(0), YD, pd(0), YD + 100, color=NAVY, width=1.25)
for v in (-5, 5, 10):
    line(s, pd(v), YD + 100, pd(v), YD + 104, color=GREY, width=0.75)
    lab = f"+{v}" if v > 0 else f"\u2212{-v}"
    text(s, pd(v) - 15, YD + 105, 30, 11, lab, size=8, color=GREY, align=PP_ALIGN.CENTER)
text(s, pd(0) - 30, YD + 105, 60, 11, [[("0 no change", B)]], size=8, align=PP_ALIGN.CENTER)
for i, (name, n, v, lo, hi, sig) in enumerate(
    (
        ("65 tables", 464, 5.6, 1.7, 9.5, True),
        ("34 tables", 293, 6.1, 2.0, 10.6, True),
        ("22 tables", 207, -2.4, -6.8, 1.9, False),
        ("21 tables", 258, 1.9, -3.1, 7.0, False),
    )
):
    y = YD + 2 + i * 25
    col = BLUE if sig else AMBER
    text(s, 53, y - 2, 95, 12, [[(name, {"bold": True})]], size=8)
    text(s, 53, y + 8, 95, 11, f"{n} questions", size=8, color=GREY)
    line(s, pd(lo), y + 8, pd(hi), y + 8, color=col, width=2.5)
    shape(s, MSO_SHAPE.OVAL, pd(v) - 4, y + 4, 8, 8, fill=col)
for x, fill, label in ((53, BLUE, "Measurable"), (112, AMBER, "Not measurable")):
    shape(s, MSO_SHAPE.OVAL, x, PANEL13 + PH13 - 15, 8, 8, fill=fill)
    text(s, x + 11, PANEL13 + PH13 - 16, 70, 11, label, size=8, color=GREY)
# Right: where selection wins and where it loses.
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 349.5, PANEL13, 300, PH13, fill=CREAM, radius=0.04)
icon(s, "schema", "blue", 358, PANEL13 + 7, 22)
text(s, 386, PANEL13 + 7, 258, 13, [[("Selection wins until it drops a table", B)]], size=10)
text(
    s,
    386,
    PANEL13 + 19,
    258,
    11,
    "Answers matched, by whether every needed table was sent",
    size=8,
    color=GREY,
)
for k, (name, head, sub, top, every) in enumerate(
    (
        ("check_circle-blue", "Every table sent", "1,055 questions", 32.9, 26.7),
        ("cancel-amber", "A table dropped", "167 questions", 5.4, 18.0),
    )
):
    y = PANEL13 + 42 + k * 52
    s.shapes.add_picture(str(ICONS / f"{name}.png"), Pt(359), Pt(y + 5), Pt(14), Pt(14))
    text(s, 377, y + 3, 100, 12, [[(head, B)]], size=8)
    text(s, 377, y + 15, 100, 11, sub, size=8, color=GREY)
    bar13(478, y, top * 4.6, 16, f"{top} %", TOP6)
    bar13(478, y + 19, every * 4.6, 16, f"{every} %", HINTS)
for x, fill, label in ((359, TOP6, "Top 6 + neighbours"), (462, HINTS, "Every table + hints")):
    shape(s, MSO_SHAPE.RECTANGLE, x, PANEL13 + PH13 - 15, 9, 9, fill=fill)
    text(s, x + 13, PANEL13 + PH13 - 16, 100, 11, label, size=8, color=GREY)
# The three headline trade-offs.
for x, ic, value, body, fill in (
    (
        43.5,
        "trending_up",
        "+3.6 points",
        "[+1.4, +5.8], paired, against every table + hints",
        PALE_BLUE,
    ),
    (248.5, "chat", "69 % fewer tokens", "2,670 against 8,501 per prompt", PALE_AMBER),
    (
        453.5,
        "timer",
        "2.0 s slower",
        "[+1.8, +2.2]; the local model cannot reuse its cache",
        "E8EAEE",
    ),
):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 392, 196, 44, fill=fill, radius=0.1)
    icon(s, ic, "navy", x + 8, 403, 22)
    text(s, x + 37, 397, 155, 14, [[(value, {"bold": True, "size": 12})]], size=12)
    text(s, x + 37, 411, 155, 22, body, size=8)
marker(s, 1, 37.5, PANEL13 - 6)
marker(s, 2, 29, 148 + 2)
marker(s, 3, 447.5, 386)
marker(s, 4, 343.5, PANEL13 - 6)
text(
    s,
    43.5,
    442,
    606,
    24,
    [
        [
            ("Note: ", B),
            (
                "against every table without hints, top 6 is borderline: +2.3 [+0.0, +4.6]. The "
                "split is observed, not causal. The later scorer reached 30.0 % and cut the 167 "
                "dropped-table questions to 128 (slide 15).",
                {},
            ),
        ],
    ],
    size=8,
    color=GREY,
)
takeaways(
    s,
    [
        (
            "The gain is concentrated",
            [
                ("The ", {}),
                ("65- and 34-table", BB),
                (
                    " databases carry it, at 5 to 6 points each. The smaller two show nothing "
                    "measurable.",
                    {},
                ),
            ],
        ),
        (
            "Hints did not help here",
            [
                ("Adding hints to every table: ", {}),
                ("-1.3 points [-2.9, +0.2]", BB),
                (". About half the needed values sit in columns too large to hint.", {}),
            ],
        ),
        (
            "Fewer tokens did not mean faster",
            [
                ("A prompt that changes per question ", {}),
                ("cannot reuse the local cache", BB),
                (", so top 6 takes 2 s longer.", {}),
            ],
        ),
        (
            "A dropped table is costly",
            [
                ("167 questions lost a needed table and scored ", {}),
                ("5.4 %", BB),
                (". Selection stays the default.", {}),
            ],
        ),
    ],
)

# Slide 14: trials
s = new_slide(
    "EVIDENCE  >  TRIALS",
    "Later trials found tradeoffs, not a further accuracy gain",
    "1,222 large-schema questions; paired change against each row's own baseline",
    14,
)
T0, TW14 = 250, 290
pt = lambda v: T0 + (v + 6) / 12 * TW14  # noqa: E731
for v in (-6, -3, 0, 3, 6):
    line(s, pt(v), 130, pt(v), 422, color=SLATE if v == 0 else RULE, width=1 if v == 0 else 0.5)
    label = "0" if v == 0 else f"{v:+d}"
    text(s, pt(v) - 15, 425, 30, 11, [[(label, {})]], size=8, color=GREY, align=PP_ALIGN.CENTER)
for i, (name, sub, v, lo, hi, col, state) in enumerate(
    (
        ("Top 6 + neighbours", "vs every table + hints", 3.6, 1.4, 5.8, BLUE, "default"),
        ("Question value matching", "vs top 6", 0.4, -0.9, 1.6, SLATE, "off"),
        ("Scorer signals", "vs top 6", 0.9, -0.7, 2.4, SLATE, "kept"),
        ("Dense embeddings", "vs the kept scorer", 0.2, -1.6, 2.0, SLATE, "off"),
        ("Shared layout", "vs a fresh top 6 run", -2.4, -4.6, -0.2, AMBER, "opt-in"),
        (
            "Shared plus summaries",
            "vs a fresh top 6 run; not controlled",
            -2.1,
            -4.3,
            0.0,
            SLATE,
            "opt-in",
        ),
    )
):
    y = 138 + i * 48
    text(s, 43.5, y, 200, 28, [[(name, B)], [(sub, {"size": 8, "color": GREY})]], size=10)
    line(s, pt(lo), y + 13, pt(hi), y + 13, color=col, width=2.5)
    shape(s, MSO_SHAPE.OVAL, pt(v) - 5, y + 8, 10, 10, fill=col)
    text(s, 548, y + 6, 40, 14, [[(f"{v:+.1f}", B)]], size=10, align=PP_ALIGN.RIGHT)
    box(s, 596, y + 5, 54, 16, state, CREAM, size=8)
marker(s, 1, 28, 141)
marker(s, 2, 28, 237)
marker(s, 3, 28, 333)
note(s, "points, paired 95 % interval. Coloured rows have an interval clear of zero.", y=440)
takeaways(
    s,
    [
        (
            "Selection established the gain",
            [
                ("Its interval is ", {}),
                ("clear of zero", BB),
                (". None of the five later trials added a further gain.", {}),
            ],
        ),
        (
            "Better retrieval is not better answers",
            [
                ("The kept scorer ranked tables better (MRR 0.853 to 0.891), but its ", {}),
                ("+0.9 points spans zero", BB),
                (".", {}),
            ],
        ),
        (
            "A faster layout lost accuracy",
            [
                ("The shared layout cut latency 58 % and ", {}),
                ("lost 2.4 points", BB),
                (". The cause is unresolved.", {}),
            ],
        ),
    ],
)

# Slide 15: retrieval
s = new_slide(
    "EVIDENCE  >  RETRIEVAL",
    "Better table coverage did not measurably improve accuracy",
    "Correct answers gained and lost when every table is sent, against selected tables",
    15,
)
C0 = 300
pc = lambda v: v * 3.4  # noqa: E731
for x, title in (
    (43.5, "Layout"),
    (C0 - 150, "LOST, ON THE OTHER 1,094"),
    (C0 + 6, "GAINED, ON THE 128 MISSED"),
):
    text(s, x, 130, 180, 12, [[(title.upper(), B)]], size=8, color=GREY)
text(s, 500, 130, 150, 12, [[("NET, AND SECONDS PER QUESTION", B)]], size=8, color=GREY)
line(s, C0, 146, C0, 256, color=SLATE, width=0.75)
for i, (name, sub, gain, lost, net, secs) in enumerate(
    (
        ("Every table,", "selected named", 15, 44, -29, 4.3),
        ("Every table,", "plus summaries", 13, 39, -26, 4.4),
    )
):
    y = 156 + i * 52
    text(s, 43.5, y, 100, 28, [[(name, B)], [(sub, {"size": 8, "color": GREY})]], size=10)
    box(s, C0 - pc(lost), y + 2, pc(lost), 26, f"-{lost}", AMBER, size=10)
    box(s, C0, y + 2, pc(gain), 26, f"+{gain}", BLUE, fg=WHITE, size=10)
    text(
        s,
        500,
        y + 7,
        150,
        16,
        [[(f"{net} answers", B), (f"   {secs} s, from 10.2 s", {"size": 8, "color": GREY})]],
        size=10,
    )
card(
    s,
    43.5,
    276,
    606,
    112,
    [
        [("Dense embeddings: fewer misses, same whole-suite result", {"bold": True, "size": 12})],
    ],
    fill=CREAM,
)
for x, value, body in (
    (55, "128 to 74", "questions with a needed table not sent"),
    (255, "8 to 26", "correct among the original 128"),
    (455, "+0.2 points", "whole suite [-1.6, +2.0], against the kept scorer"),
):
    text(s, x, 310, 186, 26, [[(value, {"bold": True, "size": 16, "color": BLUE})]])
    text(s, x, 340, 186, 40, body, size=10)
marker(s, 1, 37, 270)
marker(s, 2, C0 - 6, 146)
note(
    s,
    "groups come from the evaluation, so a live system cannot see them; the summaries "
    "comparison spans commits.",
    y=398,
)
takeaways(
    s,
    [
        (
            "Recovery has side effects",
            [
                ("Dense embeddings nearly halved missing tables, but ", {}),
                ("gains were offset", BB),
                (" by losses elsewhere.", {}),
            ],
        ),
        (
            "More context moved the errors",
            [
                ("Sending every table won 15 answers and ", {}),
                ("lost 44", BB),
                (", so the whole suite fell.", {}),
            ],
        ),
        (
            "Test targeted recovery",
            [
                ("Next: recover missed tables ", {}),
                ("only where needed", BB),
                (", and report both groups.", {}),
            ],
        ),
    ],
)

# Slide 16: next tests
s = new_slide(
    "NEXT STEPS  >  TESTS",
    "Four tests would address the main evidence gaps",
    "Proposed next steps; each needs a measured outcome before changing the default",
    16,
)
XS = (86, 300, 520, 730)
for x, head in zip(
    XS, ("THE TEST", "THE GAP IT CLOSES", "HOW WE WOULD MEASURE IT", "SEE SLIDE"), strict=True
):
    text(s, x, 130, 200, 12, [[(head, B)]], size=8, color=GREY)
line(s, 43.5, 146, 919, 146, color=NAVY, width=1.0)
line(s, 60, 170, 60, 410, color=RULE, width=1.5)
for i, (test, gap, measure, ref, fill, fg) in enumerate(
    (
        (
            "Business definitions",
            "“Revenue” stays ambiguous until a person checks it",
            "Add a few definitions, then compare answers on ambiguous questions",
            "Slides 5 and 7",
            BLUE,
            WHITE,
        ),
        (
            "Targeted table recovery",
            "128 questions miss a needed table",
            "Gains on the 128, losses on the other 1,094, whole-suite interval",
            "Slide 15",
            NAVY,
            WHITE,
        ),
        (
            "New large schemas",
            "The gain comes from 2 of 4 databases",
            "Databases outside these 4, reported one by one",
            "Slide 13",
            AMBER,
            NAVY,
        ),
        (
            "Hosted model",
            "All results use one local model",
            "Same suites: accuracy, latency and empty-SQL rate",
            "Slide 12",
            SLATE,
            WHITE,
        ),
    )
):
    y = 154 + i * 74
    if i % 2 == 0:
        shape(s, MSO_SHAPE.RECTANGLE, 78, y, 841, 66, fill=CREAM)
    box(s, 44, y + 17, 32, 32, str(i + 1), fill, fg=fg, size=12, kind=MSO_SHAPE.OVAL)
    text(s, XS[0], y + 8, 204, 50, [[(test, {"bold": True, "size": 12})]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, XS[1], y + 8, 206, 50, gap, size=10, anchor=MSO_ANCHOR.MIDDLE)
    text(s, XS[2], y + 8, 200, 50, measure, size=10, anchor=MSO_ANCHOR.MIDDLE)
    text(s, XS[3], y + 8, 180, 50, [[(ref, {"color": BLUE})]], size=10, anchor=MSO_ANCHOR.MIDDLE)
note(
    s,
    "all accuracy figures use one local model and this project's comparison, not a leaderboard. "
    "Broader value hints would need a data-boundary decision first.",
    y=456,
    w=875,
    prefix="Scope:",
)

# Backup slide after Thank you, imported with ONLY=17 (bodies stop at deck slide 16).
s = new_slide(
    "BACKUP  >  SCHEMA RAG",
    "Schema RAG ranks every table against the question",
    "The demo question on Retail Analytics: 11 tables scored, 9 sent to the model, 2 used",
    18,
)
# Three steps, then the real ranking.
for i, (head, body) in enumerate(
    (
        ("1  Expand the words", '"revenue" also searches amount, sales and total'),
        ("2  Score every table", "Names, keywords, trigrams and value hints, summed"),
        ("3  Keep and connect", "Keep the top 6, then add foreign-key neighbours"),
    )
):
    card(
        s,
        43.5 + i * 210,
        130,
        186,
        50,
        [[(head, {"bold": True, "size": 10})], [(body, {"size": 8})]],
        fill=CREAM,
        pad=7,
        after=2,
    )
    if i:
        line(s, 43.5 + i * 210 - 24, 155, 43.5 + i * 210, 155, color=SLATE, width=1.5, arrow=True)
text(
    s,
    43.5,
    188,
    606,
    14,
    [
        [
            (
                "Relevance score by table for: Which product categories generate the most revenue?",
                {"bold": True, "size": 10},
            )
        ]
    ],
)
SENT, ADDED, DROPPED = BLUE, AMBER, RULE
RANKED = (
    ("products", 30.13, SENT, True),
    ("returns", 11.73, SENT, False),
    ("order_items", 9.92, SENT, True),
    ("inventory_snapshots", 9.78, SENT, False),
    ("customer_support_tickets", 5.82, SENT, False),
    ("suppliers", 1.71, SENT, False),
    ("marketing_campaigns", 1.65, DROPPED, False),
    ("customers", 1.45, ADDED, False),
    ("regions", 1.31, DROPPED, False),
    ("orders", 1.31, ADDED, False),
    ("stores", 1.30, ADDED, False),
)
BX, BW, RH = 178.0, 380.0, 18.5
for i, (name, score, col, used) in enumerate(RANKED):
    y = 206 + i * RH
    text(s, 43.5, y + 2, 130, 11, [[(name, {"font": CODE})]], size=8, color=NAVY)
    w = max(score / 30.13 * BW, 2)
    shape(s, MSO_SHAPE.RECTANGLE, BX, y + 2, w, 11, fill=col)
    text(s, BX + w + 5, y + 2, 30, 11, f"{score:.1f}", size=8, color=GREY)
    if used:
        s.shapes.add_picture(
            str(ICONS / "check_circle-blue.png"), Pt(BX + w + 30), Pt(y + 2), Pt(11), Pt(11)
        )
YC = 206 + 6 * RH
line(s, 43.5, YC, 649, YC, color=NAVY, width=1, dashed=True)
text(s, 560, YC - 12, 90, 11, "Top 6 cut", size=8, color=GREY, align=PP_ALIGN.RIGHT)
marker(s, 1, 37.5, 124)
marker(s, 2, 29, 206 + 9 * RH + 1)
marker(s, 3, 43.5 + 210 - 6, 124)
marker(s, 4, 545, YC - 13)
for x, fill, label in (
    (43.5, SENT, "In the top 6"),
    (118, ADDED, "Added as a neighbour"),
    (222, DROPPED, "Not sent"),
):
    shape(s, MSO_SHAPE.RECTANGLE, x, 417, 9, 9, fill=fill)
    text(s, x + 13, 416, 90, 11, label, size=8, color=GREY)
s.shapes.add_picture(str(ICONS / "check_circle-blue.png"), Pt(280), Pt(416), Pt(10), Pt(10))
text(s, 293, 416, 150, 11, "Used by the model's SQL", size=8, color=GREY)
text(
    s,
    43.5,
    431,
    606,
    36,
    [
        [("Note:", B)],
        [
            (
                "Score is a weighted sum: table name match x8, hashed n-grams x5, column match x4, "
                "trigrams x3, schema BM25 x1, value-hint BM25 x0.25.",
                {},
            )
        ],
        [("Scores come from the current scorer; dense embeddings are off by default.", {})],
    ],
    size=8,
    color=GREY,
)
takeaways(
    s,
    [
        (
            "Words are widened first",
            [
                ("A business word reaches columns it never names, as ", {}),
                ("revenue reaches amount", BB),
                (".", {}),
            ],
        ),
        (
            "Neighbours rescue joins",
            [
                ("orders ranks tenth, yet it arrives because ", {}),
                ("a foreign key links it", BB),
                (" to order_items.", {}),
            ],
        ),
        (
            "It reads schema and hints, not rows",
            [
                ("Scoring uses names, DDL and value hints, so ", {}),
                ("full rows are never searched", BB),
                (" and no model is called.", {}),
            ],
        ),
        (
            "A clear winner, then a tail",
            [
                ("products scores 30, and the last six tables sit ", {}),
                ("below 2", BB),
                (", so the cut can be close.", {}),
            ],
        ),
    ],
)

if os.environ.get("ONLY"):  # one deck slide number: keep just that body for import
    ids = prs.slides._sldIdLst
    keep = int(os.environ["ONLY"]) - 2
    for k, sld in enumerate(list(ids)):
        if k != keep:
            prs.part.drop_rel(sld.rId)
            ids.remove(sld)

prs.save(OUT)
print("wrote", OUT.name)
