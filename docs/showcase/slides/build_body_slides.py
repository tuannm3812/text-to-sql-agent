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


LINE_H = 12 * 1.1 * 1.2


def lines(runs, width=235.0):
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


def note(s, rest, x=43.5, y=458, w=606, prefix="Note:"):
    """A 9 pt note with its bold prefix."""
    text(s, x, y, w, 18, [[(prefix + " ", B), (rest, {})]], size=9, color=GREY)


def bar_row(s, label, value, width, color, y, x=43.5, label_w=128, h=16, shown=None):
    """A labelled bar drawn from zero, with its value at the end."""
    text(s, x, y, label_w, h, label, size=12, anchor=MSO_ANCHOR.MIDDLE)
    shape(s, MSO_SHAPE.RECTANGLE, x + label_w, y, width, h, fill=color)
    text(
        s,
        x + label_w + width + 6,
        y,
        50,
        h,
        [[(shown or value, B)]],
        size=12,
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
        "45 / 0",
        "read-only tests passed / skipped, on 3 database engines",
    ),
    (
        "target",
        "white",
        BLUE,
        WHITE,
        "64.6%",
        "of Spider dev answers matched, with a local 9B model",
    ),
    (
        "target",
        "white",
        BLUE,
        WHITE,
        "35.2%",
        "of the harder BIRD dev answers matched, with evidence",
    ),
    (
        "trending_up",
        "navy",
        AMBER,
        NAVY,
        "+3.6 pts",
        "on large databases [+1.4, +5.8], with 69% fewer prompt tokens",
    ),
]
for i, (ic, ic_col, fill, fg, value, label) in enumerate(tiles):
    x = 43.5 + i * 153
    card(
        s,
        x,
        130,
        147,
        124,
        [
            [(" ", {"size": 24})],
            [(value, {"bold": True, "size": 26, "color": fg})],
            [(label, {"size": 10, "color": fg})],
        ],
        fill=fill,
        after=2,
    )
    icon(s, ic, ic_col, x + 8, 136, 22)
marker(s, 1, 37, 124)
marker(s, 3, 190, 124)
text(
    s,
    43.5,
    268,
    606,
    20,
    [[("Large databases: more correct answers from less context", {"bold": True, "size": 16})]],
)
text(
    s,
    43.5,
    291,
    606,
    16,
    "Sending only the most relevant tables beat sending every table, and used far less prompt.",
    size=12,
    color=GREY,
)
marker(s, 2, 30, 271)
text(s, 43.5, 320, 280, 14, [[("Answers matched", B)]], size=12)
bar_row(s, "Every table + hints", "25.5%", 88, SLATE, 340, label_w=112)
bar_row(s, "Top 6 tables", "29.1%", 100, BLUE, 366, label_w=112)
text(s, 350, 320, 280, 14, [[("Prompt size, every table = 100", B)]], size=12)
bar_row(s, "Every table + hints", "100", 110, SLATE, 340, x=350, label_w=112)
bar_row(s, "Top 6 tables", "31", 34, AMBER, 366, x=350, label_w=112)
note(
    s,
    "accuracy uses this project's result comparison, not leaderboard "
    "scoring. Large databases: 1,222 questions, 4 databases of 21 to 65 tables, 19 October 2026.",
    y=404,
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
                ("The gain holds on the ", {}),
                ("tested large databases", BB),
                (". It is not a universal result.", {}),
            ],
        ),
        (
            "Judge the whole answer",
            [
                (
                    "About one in three Spider answers still did not match, and better "
                    "retrieval did not measurably help. ",
                    {},
                ),
                ("A person should review", BB),
                (" results.", {}),
            ],
        ),
    ],
)

# Slide 3: agenda icons
s = new_slide(
    "AGENDA",
    "From the problem to the evidence",
    "Why it is hard, what we built, what we measured and what comes next.",
    3,
)
for x, name, col, fill in (
    (43.5, "help", "white", BLUE),
    (267.5, "construction", "white", NAVY),
    (491.5, "monitoring", "navy", AMBER),
    (715.5, "flag", "white", SLATE),
):
    shape(s, MSO_SHAPE.OVAL, x, 122, 64, 64, fill=fill)
    icon(s, name, col, x + 16, 138, 32)

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
        "Words like “revenue” are not columns. Gross or net? The schema does not say.",
    ),
    (
        248.5,
        PALE_BLUE,
        "Scale",
        "Real schemas are large. The right tables must be found among hundreds of columns.",
    ),
    (
        453.5,
        "E8EAEE",
        "Risk",
        "Generated SQL runs on real data, so it must be stopped from changing it.",
    ),
]
for x, fill, h, b in problems:
    card(
        s,
        x,
        196,
        196,
        88,
        [[(h, {"bold": True, "size": 16, "color": NAVY})], [(b, {"size": 12})]],
        fill=fill,
        after=2,
    )
marker(s, 1, 37, 190)
marker(s, 2, 242, 190)
marker(s, 3, 447, 190)
text(
    s,
    43.5,
    296,
    606,
    20,
    [[("Published scores fall on enterprise tasks", {"bold": True, "size": 16})]],
)
for i, (lab, v, col) in enumerate(
    (("Spider 1.0", 91.2, SLATE), ("BIRD", 73.0, AMBER), ("Spider 2.0 enterprise", 21.3, BLUE))
):
    bar_row(s, lab, f"{v} %", v * 4.6, col, 322 + i * 24, label_w=128)
note(
    s,
    "share of tasks solved, o1-preview results reported in the Spider 2.0 "
    "paper (2024); not this project's results.",
    y=398,
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
                ("Scores fall sharply on real schemas, so ", {}),
                ("a good demo is not evidence", BB),
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

# Slide 5: other approaches, two rows
s = new_slide(
    "PROBLEM  >  OTHER APPROACHES",
    "Other tools add business meaning before the SQL",
    "Two families of approach, grouped by where the meaning comes from; not a ranking",
    5,
)
rows = [
    (
        130,
        NAVY,
        "People define the meaning",
        [
            (
                "snowflake",
                "Snowflake Cortex Analyst",
                "A semantic model describes business terms the schema lacks.",
            ),
            (
                "databricks",
                "Databricks Genie Agents",
                "Experts add descriptions, instructions and example SQL.",
            ),
            ("wren", "WrenAI", "Approved metric definitions are kept in a Git repository."),
        ],
    ),
    (
        296,
        AMBER,
        "Systems learn from examples",
        [
            (
                "vanna",
                "Vanna",
                "Retrieves schema, documents and earlier question and SQL pairs. "
                "Repository archived March 2026.",
            ),
            (None, "Research agents", "Multi-step pipelines tuned to benchmarks such as BIRD."),
        ],
    ),
]
for y, col, name, items in rows:
    fg = WHITE if col == NAVY else NAVY
    o = card(
        s,
        43.5,
        y,
        606,
        26,
        [[(name, {"bold": True, "size": 12, "color": fg})]],
        fill=col,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    for i, (lg, h, b) in enumerate(items):
        x = 43.5 + i * 205
        card(
            s,
            x,
            y + 32,
            196,
            118,
            [
                [(" ", {"size": 26})],
                [(h, {"bold": True, "size": 12})],
                [(b, {"size": 10, "color": GREY})],
            ],
            fill=CREAM,
            after=3,
        )
        if lg:
            logo(s, lg, x + 8, y + 40)
        else:
            icon(s, "science", "blue", x + 8, y + 40, 26)
card(
    s,
    453.5,
    328,
    196,
    118,
    [
        [(" ", {"size": 26})],
        [("What both need", {"bold": True, "size": 12})],
        [
            (
                "Setup first: someone must write the definitions or supply the examples.",
                {"size": 10, "color": NAVY},
            )
        ],
    ],
    fill=PALE_AMBER,
    after=3,
)
icon(s, "menu_book", "navy", 461.5, 336, 26)
marker(s, 1, 37, 124)
marker(s, 2, 37, 290)
marker(s, 3, 241, 322)
note(
    s,
    "product descriptions from public documentation, read 6 November 2026. "
    "Logos belong to their owners.",
    y=458,
)
takeaways(
    s,
    [
        (
            "Definitions give control",
            [
                ("Terms like revenue are decided once, but ", {}),
                ("someone must write and maintain", BB),
                (" them.", {}),
            ],
        ),
        (
            "Examples save effort",
            [
                ("Past queries carry meaning, but they ", {}),
                ("must stay current", BB),
                (" as the schema changes.", {}),
            ],
        ),
        (
            "Research is close, not done",
            [
                ("The top BIRD test score was ", {}),
                ("83.40 %, against 92.96 % for humans", BB),
                (" (read 6 November 2026).", {}),
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
for x, name, b in (
    (43.5, "Analyst", "knows the question, not the schema"),
    (349.5, "Reviewer", "decides if an LLM can be trusted near a database"),
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
    icon(s, "person", "blue", x + 8, 139, 24)
marker(s, 1, 37, 124)
MX, MY, MW, MH = 66, 182, 584, 254
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, MX, MY, MW, MH, fill=CREAM, radius=0.03)
line(s, MX + MW / 2, MY, MX + MW / 2, MY + MH)
line(s, MX, MY + MH / 2, MX + MW, MY + MH / 2)
axis = text(
    s, -56, 303, 230, 14, "Business meaning built in", size=10, color=GREY, align=PP_ALIGN.CENTER
)
axis.rotation = -90
text(
    s,
    MX,
    MY + MH + 3,
    MW,
    14,
    "Setup needed before the first useful answer",
    size=10,
    color=GREY,
    align=PP_ALIGN.CENTER,
)
for lg, name, x, y in (
    ("snowflake", "Semantic model", 420, 26),
    ("databricks", "Curated knowledge", 345, 76),
    ("wren", "Open semantic layer", 262, 118),
    ("vanna", "Retrieval over past work", 190, 158),
):
    logo(s, lg, MX + x, MY + y, 22)
    text(s, MX + x + 27, MY + y + 3, 140, 16, name, size=10)
card(
    s,
    MX + 14,
    MY + 186,
    196,
    56,
    [
        [("This project", {"bold": True, "size": 12, "color": WHITE})],
        [("Schema and bounded hints; a person checks the meaning", {"size": 10, "color": WHITE})],
    ],
    fill=BLUE,
    anchor=MSO_ANCHOR.MIDDLE,
)
marker(s, 2, MX + 8, MY + 180)
marker(s, 3, 50, 176)
note(s, "positions are our qualitative reading, not a measurement.", x=66, y=456, w=584)
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
                ("No model to build first. ", {}),
                ("SQL is always visible", BB),
                (", validated and run read-only, with a local model option.", {}),
            ],
        ),
        (
            "What we gave up",
            [
                ("No governed metric definitions, so ", {}),
                ("“revenue” stays ambiguous", BB),
                (" until a person checks it. The next slide shows this.", {}),
            ],
        ),
    ],
)

prs.save(OUT)
print("wrote", OUT.name)
