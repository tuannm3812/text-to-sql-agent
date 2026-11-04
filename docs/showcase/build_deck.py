"""Build the editable showcase deck (16:9 PowerPoint) from native shapes.

Layout, type roles, colours, takeaway columns and markers follow the Project 15
presentation standard (project-15-strategy/deliverables/portfolio-showcase/DESIGN.md).
Every figure is copied from the README's Evaluation Results and AGENTS.md's current
state; sources sit in each slide's speaker notes, not on the slide face. Run from the
repo root:

    uv run --no-project --with python-pptx python docs/showcase/build_deck.py

The deck uses Google Sans, as the standard asks, for import into Google Slides. Markers sit
beside each takeaway heading's first rendered line, measured with MEASURE_FONT (DM Sans,
metrically close; the TTFs are in project-15-strategy's oral-presentation/figures/fonts).
text-to-sql-agent-deck-preview.pdf is the same deck with DECK_FONT="DM Sans", rendered by
LibreOffice (soffice --headless --convert-to pdf) with a fontconfig file pointing at those
TTFs; Google Sans is not installed locally.
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
ROOT = HERE.parent.parent
OUT = HERE / os.environ.get("DECK_OUT", "text-to-sql-agent-deck.pptx")
FONT = os.environ.get("DECK_FONT", "Google Sans")
PROJECT = "Text-to-SQL agent"

INK, MUTED = "20242C", "59636E"
BLUE, TEAL, SLATE, RED = "0F4BEB", "147D79", "46576C", "C64040"
LINE, PALE_BLUE, NEUTRAL = "E6E9ED", "EEF3FF", "F5F7FA"
PALE_TEAL, PALE_SLATE, BADGE = "EAF6F3", "F1F4F8", "EEF0F4"
TAGS = {  # project-fit tags: strength, constraint, evidence limit
    "default": (TEAL, "E5F4F2"),
    "kept": (TEAL, "E5F4F2"),
    "off": (SLATE, BADGE),
    "opt-in": ("875A12", "FFF2D9"),
}


def rgb(hex_: str) -> RGBColor:
    """Colour from a hex string."""
    return RGBColor.from_string(hex_)


prs = Presentation()
prs.slide_width, prs.slide_height = Pt(960), Pt(540)
BLANK = prs.slide_layouts[6]


def text(
    slide,
    x,
    y,
    w,
    h,
    runs,
    size=12,
    color=INK,
    bold=False,
    align=None,
    anchor=None,
    pad=0.0,
    spacing=None,
    after=0,
):
    """A text box. runs: a string, or paragraphs of [(text, {bold, color, size})]."""
    box = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = box.text_frame
    tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Pt(pad))
    if anchor:
        tf.vertical_anchor = anchor
    paras = [[(runs, {})]] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align:
            p.alignment = align
        if spacing:
            p.line_spacing = spacing
        p.space_after = Pt(after)
        for chunk, opt in para:
            r = p.add_run()
            r.text = chunk
            f = r.font
            f.name = FONT
            f.size = Pt(opt.get("size", size))
            f.bold = opt.get("bold", bold)
            f.color.rgb = rgb(opt.get("color", color))
    return box


def shape(slide, kind, x, y, w, h, fill=None, line=None, width=0.75, radius=None):
    """A native shape with explicit fill and outline and no theme style."""
    s = slide.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(width)
    else:
        s.line.fill.background()
    style = s._element.find(qn("p:style"))
    if style is not None:  # the theme style adds a shadow; colours are set explicitly
        s._element.remove(style)
    if radius is not None:
        s.adjustments[0] = radius
    return s


def card(slide, x, y, w, h, heading, body, fill=NEUTRAL, accent=INK, pad=8):
    """A shaded card whose heading and description live in the shape's own text."""
    s = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=LINE, radius=0.06)
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Pt(pad))
    paras = [[(heading, {"bold": True, "size": 16, "color": accent})]]
    paras += [[(body, {})]] if isinstance(body, str) else body
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(4)
        for chunk, opt in para:
            r = p.add_run()
            r.text = chunk
            r.font.name = FONT
            r.font.size = Pt(opt.get("size", 12))
            r.font.bold = opt.get("bold", False)
            r.font.color.rgb = rgb(opt.get("color", INK))
    return s


def marker(slide, n, x, y, d=12):
    """One editable ellipse with its number inside, centred, zero padding."""
    s = shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=RED)
    tf = s.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(n)
    r.font.name, r.font.size, r.font.bold = FONT, Pt(8), True
    r.font.color.rgb = rgb("FFFFFF")
    return s


def badge(slide, letter, x, y):
    """A lettered reference badge for a figure qualification."""
    s = shape(
        slide,
        MSO_SHAPE.ROUNDED_RECTANGLE,
        x,
        y,
        13,
        12,
        fill=BADGE,
        line=SLATE,
        width=0.5,
        radius=0.3,
    )
    tf = s.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = letter
    r.font.name, r.font.size, r.font.bold = FONT, Pt(8), True
    r.font.color.rgb = rgb(SLATE)


def tag(slide, label, x, y, w=44):
    """A small decision tag (default, kept, off, opt-in)."""
    fg, bg = TAGS[label]
    s = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 15, fill=bg, radius=0.3)
    tf = s.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.name, r.font.size, r.font.bold = FONT, Pt(8), True
    r.font.color.rgb = rgb(fg)


def line(slide, x1, y1, x2, y2, color=LINE, width=1.0, arrow=False):
    """A native straight connector, optionally with one destination arrowhead."""
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    if arrow:
        ln = c.line._get_or_add_ln()
        tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
        ln.append(tail)
    return c


def slide_number(slide):
    """Footer: rounded blue bar, project name, automatic slide number."""
    bar = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, 48, 492, 864, 37.2, fill=BLUE, radius=0.5)
    bar.name = "footer"
    text(
        slide,
        72,
        501.8,
        600,
        19.5,
        PROJECT,
        size=10,
        color="FFFFFF",
        bold=True,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    box = text(
        slide,
        792,
        501.8,
        96,
        19.5,
        "",
        size=10,
        color="FFFFFF",
        align=PP_ALIGN.RIGHT,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    p = box.text_frame.paragraphs[0]._p
    fld = p.makeelement(
        qn("a:fld"), {"id": "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}", "type": "slidenum"}
    )
    rpr = fld.makeelement(qn("a:rPr"), {"lang": "en-AU", "sz": "1000", "b": "0"})
    fill = rpr.makeelement(qn("a:solidFill"), {})
    fill.append(fill.makeelement(qn("a:srgbClr"), {"val": "FFFFFF"}))
    rpr.append(fill)
    rpr.append(rpr.makeelement(qn("a:latin"), {"typeface": FONT}))
    fld.append(rpr)
    t = fld.makeelement(qn("a:t"), {})
    t.text = "‹#›"
    fld.append(t)
    p.insert(len(p) - 1 if p[-1].tag == qn("a:endParaRPr") else len(p), fld)


def header(slide, section, title, subtitle, sub=None):
    """Section label, title and subtitle at the standard positions."""
    runs = [(section, {"bold": True, "size": 10, "color": INK})]
    if sub:
        runs += [
            ("  >  ", {"bold": True, "size": 10, "color": "999999"}),
            (sub, {"bold": True, "size": 10, "color": "999999"}),
        ]
    text(slide, 43.5, 21.744, 870, 16, [runs])
    text(slide, 43.5, 48.413, 870, 36, title, size=24, bold=True, color=BLUE)
    text(slide, 43.5, 90.921, 870, 18, subtitle, size=12, color=MUTED)


def takeaways(slide, groups, note=None):
    """Add the standard takeaway column and its markers.

    One text box at x 684, y 156, 235 x 324, zero padding; a marker at x 668 beside each
    heading's first line. groups: [(heading, body)], body a string or a list of rich runs.
    """
    box = slide.shapes.add_textbox(Pt(684), Pt(156), Pt(235), Pt(324))
    tf = box.text_frame
    tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    first = True
    y = 156.0
    for i, (heading, body) in enumerate(groups, start=1):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.line_spacing = 1.1
        p.space_before = Pt(0 if first else 14)
        p.space_after = Pt(6)
        if not first:
            y += 14
        r = p.add_run()
        r.text = heading
        r.font.name, r.font.size, r.font.bold = FONT, Pt(12), True
        r.font.color.rgb = rgb(INK)
        marker(slide, i, 668, y + 2.5)
        y += _lines([(heading, {"bold": True})]) * LINE_H + 6
        q = tf.add_paragraph()
        q.line_spacing = 1.1
        q.space_after = Pt(6)
        runs = [(body, {})] if isinstance(body, str) else body
        for chunk, opt in runs:
            r = q.add_run()
            r.text = chunk
            r.font.name, r.font.size = FONT, Pt(12)
            r.font.bold = opt.get("bold", False)
            r.font.color.rgb = rgb(opt.get("color", INK))
        y += _lines(runs) * LINE_H + 6
        first = False
    if note:
        q = tf.add_paragraph()
        q.space_before = Pt(8)
        prefix, rest = note
        for chunk, bold in ((prefix + " ", True), (rest, False)):
            r = q.add_run()
            r.text = chunk
            r.font.name, r.font.size, r.font.bold = FONT, Pt(8), bold
            r.font.color.rgb = rgb(MUTED)


LINE_H = 12 * 1.1 * 1.2  # 12 pt type at 110 % line spacing
# Marker placement needs the rendered wrap. MEASURE_FONT is a TTF with metrics close to the
# deck font (DM Sans for Google Sans); without one, a character count stands in.
_MEASURE = os.environ.get("MEASURE_FONT")


def _lines(runs, width: float = 235.0) -> int:
    """Rendered line count of rich text: runs is a string or [(text, opts)] at 12 pt."""
    if isinstance(runs, str):
        runs = [(runs, {})]
    words = []  # (word, bold, starts_after_space)
    for chunk, opt in runs:
        for k, w in enumerate(chunk.split(" ")):
            if w:
                words.append((w, opt.get("bold", False), k > 0 or chunk.startswith(" ")))
    if _MEASURE:
        from PIL import ImageFont

        reg = ImageFont.truetype(_MEASURE, 120)
        bold_font = ImageFont.truetype(_MEASURE.replace("400", "700"), 120)

        def size(w: str, bold: bool) -> float:
            return (bold_font if bold else reg).getlength(w) / 10

        space = reg.getlength(" ") / 10
    else:

        def size(w: str, bold: bool) -> float:
            return len(w) * 6.0

        space = 6.0
    lines, cur = 1, 0.0
    for i, (w, bold, spaced) in enumerate(words):
        add = size(w, bold) + (space if spaced and i and cur else 0)
        if cur and cur + add > width and spaced:
            lines, cur = lines + 1, size(w, bold)
        else:
            cur += add
    return lines


def note(slide, prefix, rest, x=43.5, y=470, w=610):
    """An 8 pt note with a bold prefix."""
    text(slide, x, y, w, 14, [[(prefix + " ", {"bold": True}), (rest, {})]], size=8, color=MUTED)


SPOKEN = [
    # 1 cover
    "This is a text-to-SQL agent: you ask a database a question in plain English, and it "
    "answers with SQL you can read and a result you can check.\n"
    "[Point: Text-to-SQL agent]\n"
    "It works with SQLite, DuckDB and PostgreSQL, with a local or hosted model, and I have "
    "evaluated it on two public benchmarks and a large-schema suite I built.",
    # 2 executive summary
    "Here is the whole story on one slide before the detail.\n"
    "[Point: What it is]\n"
    "The model only proposes one read-only query; the application decides whether it runs.\n"
    "[Point: How well it answers]\n"
    "With a small local model it answers about two in three Spider questions, and every figure "
    "carries an interval.\n"
    "[Point: What October established]\n"
    "The October work found where choosing tables pays, and tested five more ideas honestly: "
    "none of them was a measurable accuracy gain.\n"
    "[Point: What is next]\n"
    "Next is the hosted model under the same rules, and the questions whose tables we miss.",
    # 3 context
    "This slide is about the problem and, just as important, what the model is allowed to see.\n"
    "[Point: Schema metadata]\n"
    "The model gets the structure of the database: names, types, keys and the table "
    "definitions.\n"
    "[Point: Value hints]\n"
    "It also gets a few common category values, so it can spell a filter correctly.\n"
    "[Point: Result rows — never sent]\n"
    "It never sees the rows of an answer, and a feature that would send matching stored values "
    "stays switched off, because it did not measurably help.",
    # 4 architecture
    "Now how one question becomes an answer, left to right.\n"
    "[Point: Select]\n"
    "The only choice that shapes what the model sees is which tables to send: the top six plus "
    "their neighbours.\n"
    "[Point: Generate]\n"
    "The model writes one statement.\n"
    "[Point: Check]\n"
    "Then the application, not the model, decides: a parser check first, then the engine's own "
    "read-only mode.\n"
    "[Point: One repair try]\n"
    "If a safe query fails, the error goes back once for a repair.",
    # 5 safety
    "Safety rests on two guarantees that each hold by themselves.\n"
    "[Point: Application check]\n"
    "The application parses the SQL in the engine's dialect and refuses anything but a single "
    "read.\n"
    "[Point: Engine guarantee]\n"
    "Each engine is also opened so it cannot write, whatever the SQL says.\n"
    "[Point: 45 / 0]\n"
    "One conformance suite runs on all three engines, with no skips allowed, and it passed "
    "against a live PostgreSQL server on the fourth of November.\n"
    "[Point: 6 / 6]\n"
    "On the safety suite the model declined every request to change data. The overall safety "
    "score is 11 of 15, so this is a small suite.",
    # 6 method
    "Before the results, how they were measured.\n"
    "[Point: Suite]\n"
    "Two public benchmarks, Spider and BIRD, and a large-schema suite built from BIRD's training "
    "set, because the public dev sets have too few tables to test table selection.\n"
    "[Point: Typed result comparison]\n"
    "An answer counts as right when its result matches the reference result, not its SQL text.\n"
    "[Point: Paired comparisons]\n"
    "And every change is compared on the same questions against a named baseline, so small "
    "differences are not read off two separate intervals.",
    # 7 standard benchmarks
    "Results on the public benchmarks, with a local nine-billion-parameter model.\n"
    "[Point: Spider 1.0 dev — 64.6 %]\n"
    "About two in three Spider questions are answered correctly.\n"
    "[Point: BIRD dev, with evidence — 35.2 %]\n"
    "BIRD is much harder. Its hints are worth about ten points on the same questions.\n"
    "The biggest single fix was turning the model's thinking off: with thinking on, it often "
    "ran out of tokens before writing any SQL. These are not leaderboard numbers, because the "
    "scoring is this project's own.",
    # 8 large schemas
    "This is the result the October work was built around.\n"
    "[Point: Top 6 tables plus neighbours — 29.1 %]\n"
    "On databases with 21 to 65 tables, sending the top six tables beats sending them all by "
    "3.6 points, with 69 percent fewer prompt tokens.\n"
    "[Point: Full DDL plus value hints]\n"
    "The category hints that helped on Spider show no measurable effect here.\n"
    "[Point: About 2 s slower]\n"
    "The price is time: each question gets a different schema, so the local model cannot "
    "reuse its cache.",
    # 9 what was tried
    "After that, five ideas were tested, each against a named baseline.\n"
    "[Point: Top 6 plus neighbours]\n"
    "Only table selection has an interval entirely above zero.\n"
    "[Point: Scorer signals — kept]\n"
    "A scorer change was kept because it found the right tables more often; its effect on "
    "answers is inside its interval.\n"
    "[Point: Shared layout]\n"
    "Sending every table made answers 58 percent faster but cost 2.4 points. Why is not "
    "settled, because those layouts changed several things at once.",
    # 10 retrieval and answers
    "This slide explains why better retrieval did not mean better answers.\n"
    "[Point: Dense embeddings, against the kept scorer]\n"
    "Embeddings cut the questions missing a needed table from 128 to 74, and fixed many of "
    "them, but flipped about as many other answers the wrong way.\n"
    "[Point: 128 with a needed table not sent]\n"
    "Sending every table helps those 128 questions,\n"
    "[Point: The other 1,094]\n"
    "and costs the other 1,094 more. That is what these layouts did, not a limit on what "
    "better retrieval could reach. The next test is to recover the 128 without changing what "
    "the others receive.",
    # 11 interface
    "Finally the product itself, redesigned so the answer comes first.\n"
    "[Point: Answer screenshot]\n"
    "The answer states what the rows say, with a chart when it fits and the table.\n"
    "[Point: How this was answered]\n"
    "Beside it, the evidence: which tables were picked and why, the SQL and the read-only "
    "check, all recorded when the question was answered. A request to change data is declined "
    "and nothing runs.",
    # 12 next steps
    "What the results do not yet show, in priority order.\n"
    "[Point: 1 Measure Gemini]\n"
    "First, the hosted model has not been measured under these rules.\n"
    "[Point: 2 Recover the 128]\n"
    "Second, the questions whose tables are missed.\n"
    "[Point: 3 and 4]\n"
    "Then hint coverage, which needs a privacy decision, and more large schemas, since the "
    "gain comes from two databases. All of this uses one local model.",
    # 13 close
    "To close: the agent is grounded, its work is visible, it cannot write, and it is "
    "measured, including the ideas that did not work.\n"
    "[Point: Live demo]\n"
    "The demo and the full record of runs and decisions are public. It began as a group "
    "project in May with Huy Duc Vu, Ngoc Bao Tran Nguyen and Nguyen Nghia Doan Dang, and I have "
    "refined it since. Thank you.",
]


NOTES: list[str] = []


def new_slide(reference: str, numbered=True):
    """A blank slide with speaker notes and, unless the cover, the footer.

    The notes are the spoken script for the slide (SPOKEN, in deck order) followed by the
    sources under "Reference — not read aloud", as the standard's speaker-note pattern asks.
    """
    spoken = SPOKEN[len(prs.slides)]
    s = prs.slides.add_slide(BLANK)
    notes = f"{spoken}\n\nReference — not read aloud\n{reference}"
    s.notes_slide.notes_text_frame.text = notes
    NOTES.append(notes)
    if numbered:
        slide_number(s)
    return s


def axis(slide, x0, x1, y, lo, hi, ticks, fmt):
    """A horizontal axis with labelled ticks."""
    line(slide, x0, y, x1, y, color="BFC5CC", width=0.75)
    for t in ticks:
        x = x0 + (t - lo) / (hi - lo) * (x1 - x0)
        line(slide, x, y, x, y + 4, color="BFC5CC", width=0.75)
        text(slide, x - 20, y + 5, 40, 12, fmt(t), size=8, color=MUTED, align=PP_ALIGN.CENTER)


B = {"bold": True}
BB = {"bold": True, "color": BLUE}


# 1 — cover (unnumbered)
s = new_slide(
    "Cover. A portfolio prototype, refined since the May 2026 UTS group project. Numbers in "
    "this deck are from the README's Evaluation Results at f3a4e93 and AGENTS.md's current "
    "state (2026-11-05).",
    numbered=False,
)
shape(s, MSO_SHAPE.RECTANGLE, 0, 0, 960, 8, fill=BLUE)
text(s, 80, 120, 800, 20, "PORTFOLIO PROTOTYPE", size=10, bold=True, color=MUTED)
text(s, 80, 150, 800, 110, [[("Text-to-SQL agent", {"color": BLUE, "size": 44, "bold": True})]])
text(
    s,
    80,
    220,
    760,
    70,
    "Ask a database a question in plain English, get read-only SQL you can check, "
    "and see exactly what the model was given.",
    size=20,
    color=INK,
)
text(
    s,
    80,
    330,
    760,
    60,
    [
        [
            ("SQLite, DuckDB and PostgreSQL", {"bold": True}),
            ("   local Ollama or hosted Gemini", {}),
        ],
        [("Evaluated on Spider, BIRD and a 1,222-question large-schema suite", {})],
    ],
    size=14,
    color=MUTED,
    after=6,
)
text(s, 80, 460, 800, 20, "Manh Tuan Nguyen    November 2026", size=12, color=MUTED)

# 2 — executive summary
s = new_slide(
    "Executive summary. Sources: README (What It Does, Evaluation Results, Large schemas); "
    "AGENTS.md 2026-11-04 and 2026-11-05 entries."
)
header(
    s,
    "EXECUTIVE SUMMARY",
    "Accurate enough to demo, measured enough to trust the numbers",
    "Where the agent stands on 5 November 2026, and what the October work established",
)
cards = [
    (
        "What it is",
        [
            [
                ("A question becomes ", {}),
                ("one read-only SELECT", B),
                (
                    ", checked by the application and run under each engine's own "
                    "read-only mode. Answers show the rows, the SQL and the schema text "
                    "sent. Result rows never reach the model.",
                    {},
                ),
            ]
        ],
    ),
    (
        "How well it answers",
        [
            [
                ("64.6 %", BB),
                (" on Spider dev and ", {}),
                ("35.2 %", BB),
                (
                    " on BIRD dev with evidence, with a local 9B model and "
                    "95 % intervals on every figure.",
                    {},
                ),
            ]
        ],
    ),
    (
        "What October established",
        [
            [
                ("On 21- to 65-table databases, sending the top 6 tables scored ", {}),
                ("+3.6 points", BB),
                (" over full DDL plus hints, with ", {}),
                ("69 % fewer prompt tokens", B),
                (". Five later ideas were measured; none was a measurable accuracy gain.", {}),
            ]
        ],
    ),
    (
        "What is next",
        [
            [
                (
                    "Gemini under the same contract, hint coverage beyond the 20-value "
                    "ceiling, and recovering the ",
                    {},
                ),
                ("128 questions", B),
                (" whose needed table is not sent.", {}),
            ]
        ],
    ),
]
for i, (h, b) in enumerate(cards):
    x = 43.5 + (i % 2) * 440
    y = 150 + (i // 2) * 130
    card(s, x, y, 428, 116, h, b, accent=BLUE, pad=12)

# 3 — context
s = new_slide(
    "Problem and what the model sees. Source: README, What It Does. Value hints are row-derived "
    "but bounded: up to six of the most frequent values of text columns with at most 20 "
    "distinct values, labelled when the list is cut (fe90991). Question value matching is "
    "built, measured on bird_train_large (+0.4 [-0.9, +1.6]) and off by the owner's decision "
    "of 2026-10-19."
)
header(
    s,
    "CONTEXT",
    "Useful answers need checkable SQL and a database that cannot change",
    "The problem, and exactly what is sent to the model",
    sub="PROBLEM",
)
rows = [
    ("Schema metadata", "Table and column names, types, keys, CREATE TABLE DDL", "sent", PALE_BLUE),
    (
        "Value hints",
        "Up to 6 frequent values of text columns with at most 20 distinct values; "
        "a cut list says so",
        "sent, bounded",
        PALE_BLUE,
    ),
    (
        "Question value matching",
        "Stored values matching words in the question, from any text column",
        "built, off",
        PALE_SLATE,
    ),
    ("Result rows", "The answer's rows", "never sent", PALE_SLATE),
]
text(s, 43.5, 150, 610, 16, [[("WHAT THE MODEL SEES", {"bold": True, "size": 10, "color": MUTED})]])
for i, (k, v, status, fill) in enumerate(rows):
    y = 172 + i * 70
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 43.5, y, 610, 60, fill=fill, line=LINE, radius=0.08)
    text(s, 55.5, y + 8, 170, 44, k, size=12, bold=True)
    text(s, 230, y + 8, 300, 44, v, size=12, color=INK)
    text(
        s,
        540,
        y + 8,
        105,
        44,
        status,
        size=12,
        bold=True,
        color=BLUE if fill == PALE_BLUE else SLATE,
        align=PP_ALIGN.RIGHT,
    )
marker(s, 1, 30, 196)
marker(s, 1, 30, 266)
marker(s, 2, 30, 336)
marker(s, 2, 30, 406)
takeaways(
    s,
    [
        (
            "The model sees structure",
            "Names, types, keys and DDL, plus a few category values so it can spell a filter. "
            "That is enough to write SQL without reading the data.",
        ),
        (
            "Metadata, not data",
            [
                ("Rows stay local", BB),
                (
                    ". The one feature that would send stored values matching "
                    "the question was measured and kept off.",
                    {},
                ),
            ],
        ),
    ],
)

# 4 — architecture
s = new_slide(
    "Architecture. Source: README, Architecture and Schema RAG; docs/2_architecture.md. "
    "Scorer weights chosen 2026-10-21 on bird_train_large (text_to_sql_agent/config.py). A "
    "dense-embedding signal exists but is off by default."
)
header(
    s,
    "SYSTEM",
    "The model proposes the SQL; the application decides whether it runs",
    "One question, five steps, from schema to answer",
    sub="ARCHITECTURE",
)
steps = [
    ("Schema", "One chunk per table: DDL, keys, value hints", NEUTRAL, INK),
    ("Select", "BM25, name matches, trigrams; top 6 plus foreign-key neighbours", NEUTRAL, INK),
    (
        "Generate",
        "Question and that schema to Ollama or Gemini; one statement back",
        PALE_BLUE,
        BLUE,
    ),
    (
        "Check",
        "AST check in the dialect, then the engine's read-only mode, a work budget and a row cap",
        PALE_TEAL,
        TEAL,
    ),
    ("Show", "Rows, a chart where it fits, the SQL, the selection report", NEUTRAL, INK),
]
for i, (h, b, fill, acc) in enumerate(steps):
    x = 43.5 + i * 124
    card(s, x, 175, 110, 170, h, b, fill=fill, accent=acc)
    if i < 4:
        line(s, x + 110, 260, x + 124, 260, color=SLATE, arrow=True)
line(s, 470.5, 345, 470.5, 380, color=SLATE, arrow=True)
card(
    s,
    415.5,
    380,
    238,
    66,
    "One repair try",
    "If a safe query fails to run, the error goes back to the model once",
    fill=NEUTRAL,
)
marker(s, 1, 167.5 + 55 - 6, 158)
marker(s, 2, 415.5 + 55 - 6, 158)
takeaways(
    s,
    [
        (
            "Selection is the only model-facing choice",
            "Which tables the model sees is decided before generation, and the app reports which "
            "were picked and why.",
        ),
        (
            "Execution authority stays in Python",
            [
                ("Unsafe SQL is ", {}),
                ("refused before any database call", BB),
                ("; a failed safe query gets one repair attempt.", {}),
            ],
        ),
    ],
)

# 5 — safety
s = new_slide(
    "Safety. Sources: README Safety Model; docs/0_coding_standards.md section 3 and 4; "
    "engines/duckdb.py (read_only plus enable_external_access=False). Live PostgreSQL 16 in "
    "Docker on 2026-11-04: 1,870 passed / 6 skipped with the DSN; conformance 45 / 0 skipped, "
    "15 per engine (AGENTS.md). Safety suite 2026-10-10: 11 of 15 correct, 73.3 % [53.3, 93.3]; "
    "all 6 data-change requests refused; 3 internals requests declined as unanswerable, not "
    "counted correct."
)
header(
    s,
    "SYSTEM",
    "Two independent read-only guarantees on every engine",
    "What the application checks, what each engine enforces, and how it is tested",
    sub="SAFETY",
)
cols = [("Engine", 100), ("Application check", 220), ("Engine guarantee", 290)]
x = 43.5
for name, w in cols:
    text(s, x + 8, 150, w - 16, 14, name, size=12, bold=True, color=MUTED)
    x += w
line(s, 43.5, 168, 653.5, 168)
eng = [
    ("SQLite", "read-only URI, query_only, an authorizer denying writes, attach and pragmas"),
    ("DuckDB", "opened read_only with external access off"),
    (
        "PostgreSQL",
        "least-privilege role in a read-only transaction; refuses to connect as a superuser",
    ),
]
for i, (e, g) in enumerate(eng):
    y = 174 + i * 46
    text(s, 51.5, y, 84, 40, e, size=12, bold=True)
    text(
        s,
        151.5,
        y,
        204,
        40,
        "one SELECT or WITH, parsed in this dialect; internals blocked",
        size=12,
    )
    text(s, 371.5, y, 274, 40, g, size=12)
    line(s, 43.5, y + 42, 653.5, y + 42)
metrics = [
    ("45 / 0", "conformance tests passed / skipped, 15 per engine"),
    ("1,870", "tests passed against live PostgreSQL 16, 4 Nov"),
    ("6 / 6", "data-change requests refused on the safety suite"),
]
for i, (v, label) in enumerate(metrics):
    x = 43.5 + i * 206
    card(s, x, 330, 196, 86, v, label, fill=PALE_TEAL, accent=TEAL)
marker(s, 1, 30, 214)
marker(s, 1, 30, 366)
marker(s, 2, 467.5, 316)
takeaways(
    s,
    [
        (
            "Each guarantee holds alone",
            [
                ("The same conformance suite runs on every engine with ", {}),
                ("no skips allowed", BB),
                ("; neither the parser nor the engine is trusted by itself.", {}),
            ],
        ),
        (
            "Refusing is measured too",
            "The model declined every write request. Internals requests came back as unanswerable "
            "rather than refused, and the gate still blocked them.",
        ),
    ],
    note=("Scope:", "safety accuracy 73.3 % [53.3, 93.3] on 15 cases."),
)

# 6 — evaluation method
s = new_slide(
    "Evaluation method. Source: docs/superpowers/specs/2026-10-08-evaluation-contract-v2-"
    "design.md; README Evaluation Results; evaluation/results/bird_train_large/README.md. "
    "scripts/evaluate_v2.py --compare pairs runs that differ in one setting."
)
header(
    s,
    "EVALUATION",
    "Every reported number comes from a citable, paired run",
    "The contract behind the results, and the suites it runs on",
    sub="METHOD",
)
suites = [
    ("Spider 1.0 dev", "1,034", "≤ 14 tables per database"),
    ("BIRD dev", "1,534", "with and without evidence hints"),
    ("bird_train_large", "1,222", "4 databases of 21 to 65 tables"),
    ("demo", "12", "the 3 demo databases"),
    ("safety", "15", "refusals and unanswerables"),
]
text(s, 43.5, 150, 300, 14, "Suite", size=12, bold=True, color=MUTED)
text(s, 190, 150, 70, 14, "Questions", size=12, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)
line(s, 43.5, 168, 330, 168)
for i, (n, q, d) in enumerate(suites):
    y = 174 + i * 46
    text(s, 43.5, y, 150, 40, [[(n, B)], [(d, {"size": 8, "color": MUTED})]], size=12)
    text(s, 190, y, 70, 20, q, size=12, align=PP_ALIGN.RIGHT)
    line(s, 43.5, y + 42, 330, y + 42)
contract = [
    ("Typed result comparison", "EX compares result sets by type, not SQL text"),
    ("95 % bootstrap intervals", "over cases, on every rate"),
    ("A manifest per run", "commit, suite and database hashes, prompt hash, model, settings"),
    ("Paired comparisons", "two runs differing in one setting, same questions"),
]
for i, (h, b) in enumerate(contract):
    card(s, 350, 150 + i * 80, 303.5, 72, h, b, fill=PALE_BLUE, accent=BLUE)
marker(s, 1, 336, 155)
marker(s, 2, 30, 270)
takeaways(
    s,
    [
        (
            "Comparisons, not single scores",
            [
                ("Each change is judged ", {}),
                ("paired on the same questions", BB),
                (
                    " against a named baseline, so small effects are not read from "
                    "separate intervals.",
                    {},
                ),
            ],
        ),
        (
            "A suite built for the question",
            "Spider and BIRD dev have too few tables to show whether choosing tables helps, so a "
            "large-schema suite was built from BIRD train.",
        ),
    ],
    note=("Note:", "EX here is this contract's typed comparison, not each benchmark's scorer."),
)

# 7 — standard benchmarks
s = new_slide(
    "Standard benchmarks. Release runs 2026-10-10 at 7708295, qwen3.5:9b-q4_K_M, thinking off, "
    "RAG on k=6. Re-run after the hint label (fe90991): Spider 64.0, BIRD with evidence 35.7, "
    "without 25.4; none a measurable change. BIRD evidence hints +10.1 [8.1, 12.1] paired. "
    "Thinking off +8.5 [5.8, 11.3] on Spider against the default-thinking full run. Mean time "
    "per question 2.9 s Spider, 6.2 s BIRD. RAG ablation (gate G8): +3.0 [+1.1, +4.9] on Spider, "
    "nothing measurable on BIRD."
)
header(
    s,
    "RESULTS",
    "A local 9B model answers about two in three Spider questions",
    "Execution accuracy on full dev sets, Ollama qwen3.5:9b, thinking off, 10 Oct 2026",
    sub="STANDARD BENCHMARKS",
)
X0, X1, LO, HI = 230, 630, 0, 80
axis(s, X0, X1, 400, LO, HI, [0, 20, 40, 60, 80], lambda t: f"{t} %")
bench = [
    ("Spider 1.0 dev", "1,034 questions", 64.6, 61.6, 67.5),
    ("BIRD dev, with evidence", "1,534 questions", 35.2, 32.9, 37.6),
    ("BIRD dev, without evidence", "1,534 questions", 25.1, 22.9, 27.3),
]


def px(v):
    """Value to x position on the benchmark axis."""
    return X0 + (v - LO) / (HI - LO) * (X1 - X0)


for i, (n, q, est, lo, hi) in enumerate(bench):
    y = 190 + i * 70
    text(s, 43.5, y - 14, 180, 30, [[(n, B)], [(q, {"size": 8, "color": MUTED})]], size=12)
    line(s, px(lo), y, px(hi), y, color=BLUE, width=2)
    shape(s, MSO_SHAPE.OVAL, px(est) - 5, y - 5, 10, 10, fill=BLUE)
    text(s, px(hi) + 6, y - 16, 120, 14, f"{est} %", size=16, bold=True)
    text(s, px(hi) + 6, y + 2, 120, 12, f"[{lo}, {hi}]", size=8, color=MUTED)
text(
    s,
    X0,
    420,
    400,
    12,
    "Execution accuracy, point and 95 % bootstrap interval",
    size=8,
    color=MUTED,
)
marker(s, 1, 30, 254)
marker(s, 2, 30, 184)
takeaways(
    s,
    [
        (
            "Evidence hints are worth 10 points",
            [
                ("On the same BIRD questions, the benchmark's hints add ", {}),
                ("10.1 points [8.1, 12.1]", BB),
                (".", {}),
            ],
        ),
        (
            "Thinking off was the largest fix",
            [
                (
                    "With thinking on, long thoughts used the output cap and no SQL came "
                    "back. Off: ",
                    {},
                ),
                ("+8.5 points [5.8, 11.3]", BB),
                (" on Spider, paired.", {}),
            ],
        ),
    ],
    note=("Note:", "not comparable with leaderboard figures, which use each benchmark's scorer."),
)

# 8 — large schemas
s = new_slide(
    "Large schemas. bird_train_large full suite, three arms at 47284f5, 2026-10-19; evidence "
    "hints on. Top 6 vs full DDL plus hints +3.6 [+1.4, +5.8], 69 % fewer prompt tokens; "
    "carried by the 65- and 34-table databases (+5 to +6 each). Full DDL plus hints vs plain "
    "DDL -1.3 [-2.9, +0.2]. Top 6 is about 2 s slower: Ollama prefills each question's schema "
    "(the 19 Oct profiling, AGENTS.md). Source: evaluation/results/bird_train_large/README.md."
)
header(
    s,
    "RESULTS",
    "On large schemas, choosing tables beats sending them all",
    "Execution accuracy on bird_train_large: 1,222 BIRD train questions, 4 databases of "
    "21 to 65 tables",
    sub="LARGE SCHEMAS",
)
arms = [
    ("Full DDL plus value hints", 25.5, "BFC5CC"),
    ("Plain full DDL (RAG off)", 26.8, "BFC5CC"),
    ("Top 6 tables plus neighbours", 29.1, BLUE),
]
BX0, BX1 = 230, 540
for i, (n, v, c) in enumerate(arms):
    y = 165 + i * 48
    text(s, 43.5, y + 2, 180, 20, n, size=12, bold=(c == BLUE))
    w = v / 35 * (BX1 - BX0)
    shape(s, MSO_SHAPE.RECTANGLE, BX0, y, w, 24, fill=c)
    text(
        s,
        BX0 + w + 6,
        y + 2,
        70,
        20,
        f"{v} %",
        size=16,
        bold=True,
        color=BLUE if c == BLUE else INK,
    )
line(s, BX0, 158, BX0, 315, color="BFC5CC", width=0.75)
text(s, BX0, 318, 400, 12, "Execution accuracy, 0 to 35 % scale, 19 Oct 2026", size=8, color=MUTED)
card(
    s,
    43.5,
    350,
    196,
    86,
    "+3.6 points",
    "[+1.4, +5.8] over full DDL plus hints, paired",
    fill=PALE_BLUE,
    accent=BLUE,
)
card(
    s,
    249.5,
    350,
    196,
    86,
    "69 % fewer",
    "prompt tokens than full DDL plus hints",
    fill=PALE_BLUE,
    accent=BLUE,
)
card(
    s,
    455.5,
    350,
    198,
    86,
    "About 2 s slower",
    "per question: each prompt's schema differs, so Ollama cannot reuse its cache",
    fill=NEUTRAL,
)
marker(s, 1, 30, 270)
marker(s, 2, 30, 172)
marker(s, 3, 642, 344)
takeaways(
    s,
    [
        (
            "Selection pays where there is choice",
            [
                ("The 65- and 34-table databases carry the gain, ", {}),
                ("about 5 to 6 points each", BB),
                (". On Spider and BIRD dev it added nothing measurable.", {}),
            ],
        ),
        (
            "No measurable effect from hints here",
            "Full DDL plus hints against plain DDL: -1.3 points [-2.9, +0.2]. Half the needed "
            "literals sit in columns over the 20-value ceiling.",
        ),
        (
            "The cost is time",
            "The default is slower but smaller and more accurate; the fast layouts "
            "on the next slide "
            "trade accuracy back.",
        ),
    ],
)

# 9 — what was tried
s = new_slide(
    "What was tried, 19 Oct to 4 Nov. README table at f3a4e93. Baselines are not a chain: top 6 "
    "ran three times (29.1 % at 47284f5, 30.0 % with the kept scorer at 28f21bc, 30.0 % again "
    "at 20ee05f). Value matching 29.5 %; scorer 30.0 %; dense 30.2 %; shared 27.7 %; "
    "shared-summary 27.9 %. Shared latency 4.3 s vs 10.2 s for the fresh selected run. "
    "Summary's comparisons are across commits (5ec3893 vs 20ee05f), so not controlled."
)
header(
    s,
    "RESULTS",
    "Only selection delivered a measurable accuracy gain",
    "Paired change in execution accuracy on the 1,222 questions, each against its named baseline",
    sub="WHAT WAS TRIED",
)
DX0, DX1, DLO, DHI = 300, 560, -6, 7


def dx(v):
    """Points to x position on the paired-change axis."""
    return DX0 + (v - DLO) / (DHI - DLO) * (DX1 - DX0)


tried = [
    ("Top 6 plus neighbours", "vs full DDL plus hints", 3.6, 1.4, 5.8, "default"),
    ("Question value matching", "vs top 6, 47284f5", 0.4, -0.9, 1.6, "off"),
    ("Scorer signals", "vs top 6, 47284f5", 0.9, -0.7, 2.4, "kept"),
    ("Dense embeddings", "vs the kept scorer", 0.2, -1.6, 2.0, "off"),
    ("Shared layout", "vs fresh top 6, 20ee05f", -2.4, -4.6, -0.2, "opt-in"),
    ("Shared plus summaries", "vs fresh top 6, 20ee05f", -2.1, -4.3, 0.0, "opt-in"),
]
line(s, dx(0), 150, dx(0), 412, color="BFC5CC", width=0.75)
for i, (n, base, est, lo, hi, t) in enumerate(tried):
    y = 162 + i * 42
    text(s, 43.5, y - 11, 245, 30, [[(n, B)], [(base, {"size": 8, "color": MUTED})]], size=12)
    col = BLUE if lo > 0 else SLATE
    line(s, dx(lo), y, dx(hi), y, color=col, width=2)
    shape(s, MSO_SHAPE.OVAL, dx(est) - 4.5, y - 4.5, 9, 9, fill=col)
    text(s, 566, y - 8, 45, 16, f"{est:+.1f}", size=12, bold=True, align=PP_ALIGN.RIGHT)
    tag(s, t, 614, y - 7.5, w=40)
axis(s, DX0, DX1, 414, DLO, DHI, [-6, -3, 0, 3, 6], lambda t: f"{t:+d}" if t else "0")
text(s, DX0, 432, 300, 12, "Points, paired 95 % interval", size=8, color=MUTED)
badge(s, "A", 290 - 16, 366)
marker(s, 1, 30, 157)
marker(s, 2, 30, 241)
marker(s, 3, 30, 325)
takeaways(
    s,
    [
        (
            "Only selection is a measured gain",
            [("Its interval is the only one ", {}), ("entirely above zero", BB), (".", {})],
        ),
        (
            "Kept for retrieval, not for accuracy",
            "The scorer change raised retrieval MRR from 0.853 to 0.891; its +0.9 on answers is "
            "inside its interval.",
        ),
        (
            "Faster prompts cost accuracy",
            "Sending every table lets Ollama reuse its cache: 58 % faster, 2.4 "
            "points lower. Why is "
            "not settled; length, content and placement changed together.",
        ),
    ],
    note=("Note A:", "compared across commits, so not a controlled comparison."),
)

# 10 — retrieval versus answers
s = new_slide(
    "Retrieval versus answers. README 'What this says'; evaluation/results/dense_embeddings and "
    "shared_layout READMEs; evaluation/results/retrieval/README.md (MRR 0.891, every needed "
    "table sent in 89.5 % at top 6). 'Selected tables plus neighbours' is 6 to 20 tables, "
    "exactly six in 127 cases. Subgroup counts are observations, not a bound on better "
    "retrieval."
)
header(
    s,
    "RESULTS",
    "Sending the right tables more often did not mean more right answers",
    "Correct answers by subgroup on bird_train_large, under the default and two full-schema "
    "layouts",
    sub="RETRIEVAL AND ANSWERS",
)
hdr = [
    ("Prompt layout", 190, PP_ALIGN.LEFT),
    ("128 with a needed table not sent", 150, PP_ALIGN.RIGHT),
    ("The other 1,094", 130, PP_ALIGN.RIGHT),
    ("Seconds per question", 140, PP_ALIGN.RIGHT),
]
x = 43.5
for h, w, a in hdr:
    text(s, x + 6, 150, w - 12, 30, h, size=12, bold=True, color=MUTED, align=a)
    x += w
line(s, 43.5, 182, 653.5, 182)
mat = [
    ("Selected tables (default)", "8", "359", "10.2", PALE_BLUE),
    ("Every table, selected named", "23", "315", "4.3", None),
    ("Every table, plus summaries", "21", "320", "4.4", None),
]
for i, (n, a, b, c, fill) in enumerate(mat):
    y = 188 + i * 40
    if fill:
        shape(s, MSO_SHAPE.RECTANGLE, 43.5, y - 4, 610, 36, fill=fill)
    x = 43.5
    for v, (_h, w, al) in zip((n, a, b, c), hdr, strict=True):
        text(
            s,
            x + 6,
            y + 4,
            w - 12,
            20,
            v,
            size=12 if al == PP_ALIGN.LEFT else 16,
            bold=al != PP_ALIGN.LEFT or fill is not None,
            align=al,
        )
        x += w
    line(s, 43.5, y + 34, 653.5, y + 34)
card(
    s,
    43.5,
    330,
    610,
    92,
    "Dense embeddings, against the kept scorer",
    [
        [
            ("Questions with a needed table not sent: ", {}),
            ("128 to 74", BB),
            (". Correct among the original 128: ", {}),
            ("8 to 26", BB),
            (". Whole suite: ", {}),
            ("+0.2 points [-1.6, +2.0]", B),
            (".", {}),
        ]
    ],
    fill=NEUTRAL,
)
marker(s, 1, 30, 360)
marker(s, 2, 30, 230)
marker(s, 3, 245, 156)
takeaways(
    s,
    [
        (
            "Recall is not accuracy",
            "Embeddings fixed many missing-table questions, but changed table sets "
            "flipped about as "
            "many other answers the wrong way. Both are reported, separately.",
        ),
        (
            "The few gain, the many lose",
            [
                ("Sending every table helps the 128 and costs the 1,094 more. ", {}),
                ("That is what these layouts did", BB),
                (", not a limit on better retrieval.", {}),
            ],
        ),
        (
            "Next test",
            "Recover the missing tables for the 128 without changing what the other 1,094 receive.",
        ),
    ],
)

# 11 — interface
s = new_slide(
    "Interface. Real captures from scripts/capture_screenshots.py (local Ollama "
    "qwen3.5:9b-q4_K_M, Retail Analytics demo); provenance in docs/screenshots/capture.json. "
    "Teal and IBM Plex direction approved 2026-10-21, docs/design/design.md. Screens show the "
    "interface, not benchmark accuracy."
)
header(
    s,
    "PRODUCT",
    "The answer comes first; the evidence is one glance away",
    "Redesigned Streamlit interface, real captures from a local model on the demo database",
    sub="INTERFACE",
)
for i, (img, cap) in enumerate(
    (
        ("01-answer.png", "Answer: headline from the rows, chart, table"),
        (
            "02-how-it-was-answered.png",
            "How this was answered: tables and why, SQL, the check, the run",
        ),
    )
):
    x = 43.5 + i * 310
    pic = s.shapes.add_picture(
        str(ROOT / "docs" / "screenshots" / img), Pt(x), Pt(150), width=Pt(300)
    )
    pic.line.color.rgb = rgb(LINE)
    pic.line.width = Pt(0.75)
    text(s, x, 150 + 300 * 1000 / 1440 + 6, 300, 30, cap, size=8, color=MUTED)
marker(s, 1, 30, 150)
marker(s, 2, 640, 150)
takeaways(
    s,
    [
        (
            "Answers state what the rows say",
            "A headline from the result, a bar chart when the result is one "
            "category and one number, "
            "and the table.",
        ),
        (
            "Evidence is recorded, not rebuilt",
            [
                (
                    "Tables picked and why, the schema size sent, the SQL and the "
                    "read-only check are ",
                    {},
                ),
                ("kept from the moment of answering", BB),
                (".", {}),
            ],
        ),
    ],
)

# 12 — next steps (main content carries the findings; no takeaway column)
s = new_slide(
    "Next steps. Source: docs/4_next_steps.md (Evaluation v2 item 3, Phase 4); README Evaluation "
    "Results. Gemini: thinking tokens count against max_output_tokens=512 and no thinking budget "
    "is set; no key is configured locally, so the empty-answer rate is unmeasured."
)
header(
    s,
    "NEXT STEPS",
    "What the results do not yet show, in priority order",
    "Limits to keep beside the numbers, and the tests that would address them",
)
nexts = [
    (
        "1",
        "Measure Gemini under the same contract",
        "Supported but unmeasured since May. Its thinking shares the 512-token output cap; set a "
        "thinking budget and record it in the run identity once a key is available.",
    ),
    (
        "2",
        "Recover the 128 missing-table questions",
        "Find their tables without lengthening the prompt for the other 1,094.",
    ),
    (
        "3",
        "Widen hint coverage",
        "Half the needed literals sit in columns over the 20-value ceiling. Listing more values "
        "needs a privacy decision first.",
    ),
    (
        "4",
        "Test more large schemas",
        "The selection gain comes from two of four BIRD train databases; other schemas are "
        "untested.",
    ),
]
for i, (n, h, b) in enumerate(nexts):
    x = 43.5 + (i % 2) * 440
    y = 150 + (i // 2) * 130
    card(s, x, y, 428, 116, f"{n}   {h}", b, fill=NEUTRAL, accent=BLUE, pad=12)
note(
    s,
    "Scope:",
    "all v2 accuracy figures use one local model, qwen3.5:9b-q4_K_M via Ollama; "
    "EX is this project's typed comparison, not a leaderboard score.",
    y=420,
    w=870,
)

# 13 — close
s = new_slide(
    "Close. Origin: UTS AT3 group project, May 2026 (docs/academic/). Refinement since then on "
    "tuannm3812/main-refinement."
)
text(s, 43.5, 120, 870, 20, "THANK YOU", size=10, bold=True, color=MUTED)
text(
    s,
    43.5,
    145,
    870,
    90,
    "Grounded, visible, read-only and measured, including the ideas that did not work.",
    size=28,
    bold=True,
    color=BLUE,
)
text(
    s,
    43.5,
    260,
    870,
    50,
    [
        [("Live demo  ", B), ("aipa-text-to-sql-agent.streamlit.app", {})],
        [("Code, runs and decision log  ", B), ("github.com/tuannm3812/text-to-sql-agent", {})],
    ],
    size=14,
    after=6,
)
text(
    s,
    43.5,
    350,
    870,
    60,
    [
        [
            (
                "Began as a UTS group project in May 2026 with Huy Duc Vu, Ngoc Bao Tran Nguyen, "
                "Manh Tuan Nguyen and Nguyen Nghia Doan Dang; refined since by Manh Tuan Nguyen.",
                {},
            )
        ],
    ],
    size=12,
    color=MUTED,
)

prs.core_properties.title = "Text-to-SQL agent"
prs.core_properties.author = "Manh Tuan Nguyen"
prs.save(OUT)
if OUT.name == "text-to-sql-agent-deck.pptx":
    md = [
        "# Speaker notes — Text-to-SQL agent deck",
        "",
        "Generated by build_deck.py with the deck; edit SPOKEN there, not here.",
        "",
    ]
    for i, n in enumerate(NOTES, start=1):
        md += [f"## Slide {i}", ""] + [f"{ln}\n" for ln in n.split("\n") if ln]
    (HERE / "speaker-notes.md").write_text("\n".join(md), encoding="utf-8")
print("wrote", OUT.name)
