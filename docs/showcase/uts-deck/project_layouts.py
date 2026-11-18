"""Project-owned layouts for the Text-to-SQL Agent deck on the UTS kit (port started 18 November 2026).

Loaded through brief-content.json "project_layouts": "project_layouts.py" (the kit's opt-in hook, v0.6.0).
The helpers below the divider are copied from deck-kit projects/fire-occurrence-talk-uts/project_layouts.py
(deck-kit 96bf255 worktree, 18 November 2026) so both ports draw columns, markers and legends the same way.
Wording comes from the slide fields; this file adds geometry and colours only.
"""
import json
from pathlib import Path

from uts_kit.typography import plain_text
from uts_kit.supporting_text import labelled
from uts_kit.takeaway import draw as draw_takeaway

HERE = Path(__file__).resolve().parent
LEFT, RIGHT, TOP, END = 43.5, 919.0, 132.0, 476.0
FIG_RIGHT = 650.0   # figure column of the kit's figure_evidence (43.5 + 606.5)



# -- small helpers -------------------------------------------------------------------------
def need(L, raw, w, size, bold=False):
    return L.metrics.wrap(str(raw), w, size, bold=bold)[2] * size * 1.35


def put(L, p, raw, x, y, w, size=10, role='body', bold=False, align=None, h=None):
    """Kit text in a frame measured to its own height; returns the height used."""
    h = need(L, raw, w, size, bold) if h is None else h
    L.text(p, raw, x, y, w, h, size, role, bold, align)
    return h


def paint(L, p, raw, x, y, w, size, colour, bold=False, align=None):
    """Text in a data colour that is not a theme role (a series colour)."""
    text, spans, lines = L.metrics.wrap(str(raw), w, size, bold=bold)
    h = lines * size * 1.35
    p.text(text, x, y, w, h, size=size, color=colour, bold=bold, spans=spans, spacing=135, align=align)
    return h


def width_of(L, text, size, bold=False):
    return L.metrics.fonts[(bold, False)].getlength(text) / 120 * size


def cap(L, p, text, x, y, w, role='accent'):
    """8 pt bold capitals: the old deck's small navigation label."""
    return put(L, p, text.upper(), x, y, w, 8, role, True)


def note(L, p, text, x, y, w):
    first = len(p.ops)
    h = put(L, p, labelled(text, 'Note'), x, y, w, L.size('caption'))
    for op in p.ops[first:]:
        if op['op'] == 'style-text' and op.get('bold'):
            op['color'] = L.t.color('ink')
    return h


def icon(L, p, path, alt, x, y, size):
    L.image(p, {'path': path, 'alt': alt}, x, y, size, size)


def card(L, p, x, y, w, h, bar='accent', weight=3):
    p.rect(x, y, w, h, L.t.color('card'))
    p.rect(x, y, w, weight, L.t.color(bar))


def legend(L, p, items, x, y, width, height=25):
    """Native legend keys above a figure, in the kit's geometry (caption size, 24 pt key + label, 16 pt gaps),
    with the point shapes the kit key lacks: square, triangle, diamond, a range bar and a colour ramp."""
    size = L.size('caption')
    lh = size * 1.35
    cursor, top = x, y
    for item in items:
        kind, colour, label = item['kind'], item.get('color'), item['label']
        key_w = item.get('key_width', 18)
        tw = width_of(L, label, size)
        entry = key_w + 6 + tw + (6 + width_of(L, item['after'], size) if item.get('after') else 0)
        if cursor > x and cursor + entry > x + width:
            cursor, top = x, top + lh + 2
        if top + lh > y + height + .1:
            raise ValueError(f'{p.id}: legend needs more height')
        cx, cy = cursor + 9, top + 5
        if kind == 'swatch':
            p.rect(cursor + 2, top + 2, 14, 6, colour)
        elif kind == 'dashed':
            p.line(cursor, cy, cursor + 18, cy, colour, 1.5, dash='DASH')
        elif kind == 'circle':
            p.rect(cx - 3.5, cy - 3.5, 7, 7, colour, 'ELLIPSE')
        elif kind == 'square':
            p.rect(cx - 3, cy - 3, 6, 6, colour)
        elif kind in ('triangle', 'diamond'):
            icon(L, p, item['path'], '', cx - 4, cy - 4, 8)
        elif kind == 'range':
            p.rect(cursor + 1, cy - 2, 16, 4, item['tint'])
            p.rect(cursor, cy - 5, 1.5, 10, colour)
            p.rect(cursor + 16.5, cy - 5, 1.5, 10, colour)
        elif kind == 'ramp':
            pass
        else:
            raise ValueError(f'{p.id}: unknown legend key {kind}')
        if kind == 'ramp':   # label first, then the ramp, then the far-end label
            L.text(p, label, cursor, top, tw + .1, lh, size, 'body')
            L.image(p, {'path': item['path'], 'alt': item['alt']}, cursor + tw + 6, top + 2, key_w, 6)
            after = item['after']
            L.text(p, after, cursor + tw + 12 + key_w, top, width_of(L, after, size) + .1, lh, size, 'body')
        else:
            L.text(p, label, cursor + key_w + 6, top, tw + .1, lh, size, 'body')
        cursor += entry + 16
    return top + lh - y


def figure_marker(L, p, slide, number, cx, cy, halo=True):
    if halo:
        p.rect(cx - 7, cy - 7, 14, 14, L.t.color('ground'), 'ELLIPSE')
    L.marker(p, number, cx - 6, cy - 6)
    slide.setdefault('figure_marks', []).append({'number': number, 'cx': cx, 'cy': cy})


def right_column(L, p, slide, marks, halo=False):
    """The kit's figure_evidence right column: hairline, optional takeaway, numbered headings and texts,
    with the paired markers placed on the figure at marks[number]."""
    p.line(658, 131, 658, END, L.t.color('hair'))
    L.band(p, slide.get('takeaway', ''), 668, 131, 251, 94)
    y = 237
    slide['figure_marks'] = []
    for number, item in enumerate(slide['annotations'], 1):
        if number not in marks:
            raise ValueError(f'{p.id}: no figure marker {number}')
        cx, cy = marks[number]
        figure_marker(L, p, slide, number, cx, cy, halo)
        L.marker(p, number, 668, y)
        hh = L.text(p, item['title'], 688, y, 231, min(47, END - y), 12, 'ink', True)
        body_y = y + hh + 4
        bh = L.text(p, item['text'], 688, body_y, 231, END - body_y, L.size('body'))
        first_line = L.metrics.wrap(item['title'], 231, 12, bold=True)[0].split('\n')[0]
        slide['marker_pairs'].append({'number': number, 'insight_heading': plain_text(item['title']),
                                      'insight_anchor': {'text': first_line, 'y': y}})
        y = body_y + bh + 12


def caption(L, p, slide, y=418, w=606.5):
    return put(L, p, slide['caption'], LEFT, y, w, L.size('caption'))




# Colour key (Viridis, one meaning per colour, used the same way on every figure; see DESIGN.project.md):
#   teal    #21918C  this project: its measured result, its default setting, what it sends
#   indigo  #3B528B  published or reference results: other papers, the benchmark's own answer
#   green   #5EC962  gained or added: answers won, tables added, lines a better question adds
#   purple  #440154  lost, dropped or not stopped
#   yellow  #FDE725  the model and its gaps: the one model step, a gap still to close (pale #FDF3A6 as a fill)
#   grey    #ADB5BD  baseline or comparison arm, not sent, behaviour-only suites
#   difficulty runs green to purple: easy #5EC962, medium #21918C, hard #3B528B, extra hard #440154
VIRIDIS = {'ours': '#21918C', 'published': '#3B528B', 'gap': '#FDF3A6'}


# -- problem ---------------------------------------------------------------------------------
def hard_page(L, p, slide):
    """Why it is hard: the four-step chain, published scores by benchmark, and the three causes."""
    slide.setdefault('marker_pairs', [])
    chain = slide['chain']
    gap = 14
    w = (FIG_RIGHT - LEFT - gap * (len(chain) - 1)) / len(chain)
    for i, (head, body, *art) in enumerate(chain):
        x = LEFT + i * (w + gap)
        card(L, p, x, TOP, w, 46)
        tx = x + 8
        if art:
            icon(L, p, f'assets/icons/{art[0]}-ink.png', head, x + 8, TOP + 13, 22)
            tx = x + 38
        put(L, p, head, tx, TOP + 9, x + w - 8 - tx, 12, 'ink', True)
        put(L, p, body, tx, TOP + 26, x + w - 8 - tx, 8, 'body')
        if i < len(chain) - 1:
            p.connector(x + w + 2, TOP + 23, x + w + gap - 2, TOP + 23, color=L.t.color('rule'))
    fig = slide['figure']
    causes = slide['causes']
    cw = (FIG_RIGHT - LEFT - 20 * (len(causes) - 1)) / len(causes)
    ch = max(need(L, c['text'], cw - 24, 10) for c in causes) + 52
    causes_y = END - ch
    y = TOP + 62
    step = (causes_y - 18 - (y + 22) - 26) / len(fig['bars'])   # bars share the height left above the causes
    put(L, p, fig['title'], LEFT, y, FIG_RIGHT - LEFT, 12, 'ink', True)
    y += 22
    lw, bw = 150, FIG_RIGHT - LEFT - 150 - 120
    marks = {}
    top = fig['bars'][0]['value']
    for bar in fig['bars']:
        put(L, p, bar['label'], LEFT, y + 5, lw - 8, 10, 'ink')
        bwid = bw * bar['value'] / 100
        p.rect(LEFT + lw, y, bwid, 24, VIRIDIS[bar['series']])
        paint(L, p, f"{bar['value']}\u00a0%", LEFT + lw + bwid + 6, y + 5, 60, 10, L.t.color('ink'), True)
        end = LEFT + lw + bwid + 60
        if bar.get('gap'):
            gx, gw = LEFT + lw + bwid + 56, bw * (top - bar['value']) / 100 - 56
            p.rect(gx, y, gw, 24, VIRIDIS['gap'])
            paint(L, p, bar['gap'], gx + 8, y + 5, gw - 16, 10, L.t.color('ink'), True)
            end = gx + gw
        if bar.get('marker'):
            marks[bar['marker']] = (end + 14, y + 12)
        y += step
    y += 2
    put(L, p, fig['caption'], LEFT, y, FIG_RIGHT - LEFT, L.size('caption'))
    y = causes_y
    for i, c in enumerate(causes):
        x = LEFT + i * (cw + 20)
        card(L, p, x, y, cw, ch)
        put(L, p, c['title'], x + 12, y + 12, cw - 24, 12, 'ink', True)
        put(L, p, c['text'], x + 12, y + 32, cw - 24, 10)
        if c.get('marker'):
            marks[c['marker']] = (x + cw - 10, y + 10)
    if y + ch > END:
        raise ValueError(f'{p.id}: causes run past the content area')
    right_column(L, p, slide, marks)


SERIES = {'primary': '#21918C', 'published': '#3B528B', 'secondary': '#5EC962', 'muted': '#ADB5BD', 'loss': '#440154',
          'pale': '#FDF3A6', 'model': '#FDE725', 'd1': '#5EC962', 'd2': '#21918C', 'd3': '#3B528B', 'd4': '#440154'}


def _fmt(v, unit):
    sign = '+' if unit == 'points' and v > 0 else ''
    text = f"{v:.1f}" if isinstance(v, float) else f"{v}"
    text = text.replace('-', '\u2212')
    return sign + text + (' %' if unit == '%' else '')


# -- evidence --------------------------------------------------------------------------------
def bars_page(L, p, slide):
    """Stacked bar or interval panels in the figure column, a legend above, markers paired with the right column.
    panel: title, scale [lo, hi], unit ('%', 'points' or ''), kind 'bar' or 'dot', rows of
    {label, value, lo, hi, series, marker, mono}. Numbers come from the slide fields unchanged."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    y = TOP
    if slide.get('legend'):
        y += legend(L, p, slide['legend'], LEFT, y, FIG_RIGHT - LEFT) + 10
    panels = slide['panels']
    cap_h = need(L, slide['caption'], FIG_RIGHT - LEFT, L.size('caption')) + 8 if slide.get('caption') else 0
    rows = sum(len(pn['rows']) for pn in panels)
    titles = 20 * len(panels) + 14 * (len(panels) - 1)
    step = min(slide.get('max_step', 30), (END - cap_h - y - titles) / rows)
    bh = min(18, step - 6)
    lw = slide.get('label_width', 150)
    labels = []
    for pi, pn in enumerate(panels):
        put(L, p, pn['title'], LEFT, y, FIG_RIGHT - LEFT, 10, 'ink', True)
        y += 20
        lo, hi = pn['scale']
        x0, x1 = LEFT + lw, FIG_RIGHT - 64
        X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
        top_y = y
        for r in pn['rows']:
            mono = r.get('mono')
            put(L, p, r['label'], LEFT, y + (step - 13.5) / 2, lw - 8, 10 if not mono else 8, 'ink', bool(r.get('bold')))
            colour = SERIES[r.get('series', 'primary')]
            cy = y + step / 2
            if pn.get('kind', 'bar') == 'bar':
                a, b = sorted((X(max(lo, 0)), X(r['value'])))
                p.rect(a, cy - bh / 2, max(b - a, 1.5), bh, colour)
                end = b
            else:
                p.rect(X(r['lo']), cy - 1.25, X(r['hi']) - X(r['lo']), 2.5, colour)
                for v in (r['lo'], r['hi']):
                    p.rect(X(v) - .75, cy - 5, 1.5, 10, colour)
                p.rect(X(r['value']) - 4.5, cy - 4.5, 9, 9, colour, 'ELLIPSE')
                end = X(r['hi'])
            label = r.get('text') or _fmt(r['value'], pn.get('unit', ''))
            if r.get('lo') is not None and pn.get('kind', 'bar') == 'dot' and not r.get('text'):
                label += f"  [{_fmt(r['lo'], pn.get('unit',''))}, {_fmt(r['hi'], pn.get('unit',''))}]"
            size = 8 if pn.get('kind') == 'dot' else 10
            tw = width_of(L, label, size, True) + 2
            labels.append([end + 6, cy - 6.5, tw, size, label, r.get('marker'), cy])
            y += step
        if lo < 0 < hi:
            p.rect(X(0) - .5, top_y - 2, 1, y - top_y + 2, L.t.color('rule'))
        if pn.get('marker'):
            marks[pn['marker']] = (LEFT + width_of(L, pn['title'], 10, True) + 14, top_y - 13)
        y += 14
    xs = sorted({round(lab[0], 2) for lab in labels})   # snap label columns that nearly align (audit near-miss)
    snap, groups = {}, []
    for x in xs:   # chain neighbours closer than 4 pt into one column, placed at the group's right edge
        if groups and x - groups[-1][-1] < 4:
            groups[-1].append(x)
        else:
            groups.append([x])
    for g in groups:
        for x in g:
            snap[x] = g[-1]
    for x, y0, tw, size, label, marker, cy in labels:
        x = snap[round(x, 2)]
        paint(L, p, label, x, y0, tw, size, L.t.color('ink'), True)
        if marker:
            marks[marker] = (x + tw + 12, cy)
    if slide.get('caption'):
        put(L, p, slide['caption'], LEFT, END - cap_h + 8, FIG_RIGHT - LEFT, L.size('caption'))
    right_column(L, p, slide, marks)


# -- problem ---------------------------------------------------------------------------------
def aim_page(L, p, slide):
    """Our aim: two promise cards, then the setup-against-meaning matrix with the tools placed on it."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    gap = 14
    w = (FIG_RIGHT - LEFT - gap) / 2
    for i, c in enumerate(slide['promises']):
        x = LEFT + i * (w + gap)
        card(L, p, x, TOP, w, 44)
        tx = x + 10
        if c.get('icon'):
            icon(L, p, f"assets/icons/{c['icon']}-ink.png", c['title'], x + 10, TOP + 12, 22)
            tx = x + 40
        put(L, p, c['title'], tx, TOP + 9, x + w - 10 - tx, 12, 'ink', True)
        put(L, p, c['text'], tx, TOP + 26, x + w - 10 - tx, 10)
        if c.get('marker'):
            marks[c['marker']] = (x + w - 10, TOP + 10)
    mx, my = LEFT, TOP + 66
    mw, mh = FIG_RIGHT - mx, END - 22 - my
    hw, hh = mw / 2, mh / 2
    acc = L.t.data['accents']
    fills = [acc['ochre']['fill'], acc['blue']['fill'], acc['slate']['fill'], L.t.color('card')]
    for k, q in enumerate(slide['quadrants']):
        qx, qy = mx + (k % 2) * hw, my + (k // 2) * hh
        p.rect(qx + 1, qy + 1, hw - 2, hh - 2, fills[k])
        if isinstance(q, list):
            q, sub = q
            put(L, p, sub, qx + 8, qy + 22, hw - 16, 8, 'body')
        cap(L, p, q, qx + 8, qy + 7, hw - 16, 'ink')
    p.line(mx, my, mx, my + mh, L.t.color('rule'), 1)
    p.line(mx, my + mh, mx + mw, my + mh, L.t.color('rule'), 1)
    put(L, p, slide['x_axis'], mx, my + mh + 6, mw, 8, 'body', True)
    put(L, p, slide['y_axis'], mx, my - 14, mw, 8, 'body', True)
    for pt in slide['points']:
        cx, cy = mx + pt['x'] * mw, my + (1 - pt['y']) * mh
        colour = SERIES['primary'] if pt.get('ours') else L.t.color('ink')
        if pt.get('art'):
            icon(L, p, pt['art'], pt['label'], cx - 8, cy - 8, 16)
        else:
            p.rect(cx - 4, cy - 4, 8, 8, colour, 'ELLIPSE')
        tw = width_of(L, pt['label'], 10, bool(pt.get('ours'))) + 2
        paint(L, p, pt['label'], cx + 12, cy - 7, tw, 10, colour, bool(pt.get('ours')))
        if pt.get('marker'):
            marks[pt['marker']] = (cx + 12 + tw + 12, cy)
    right_column(L, p, slide, marks)


def tools_page(L, p, slide):
    """Other tools: one row per approach with its logo, grouped in bands, effort as three dots."""
    cols = slide['columns']   # [(header, width)]
    xs, x = [], LEFT
    for _, w in cols:
        xs.append(x)
        x += w
    y = TOP
    kx = RIGHT - 250
    cap(L, p, 'Effort', kx, y, 40, 'body')
    kx += 36
    for n, lab in ((3, 'High'), (2, 'Moderate'), (1, 'Low'), (0, 'None')):
        dots(L, p, n, kx, y + 2.5)
        tw = width_of(L, lab, 8) + 2
        put(L, p, lab, kx + 20, y, tw, 8, 'body')
        kx += 20 + tw + 12
    y += 18
    for (head, _), x0, (_, w) in zip(cols, xs, cols):
        cap(L, p, head, x0, y, w - 8, 'body')
    y += 14
    p.rect(LEFT, y, RIGHT - LEFT, 1, L.t.color('ink'))
    acc = L.t.data['accents']
    for row in slide['rows']:
        if 'band' in row:
            a = acc[row['accent']]
            p.rect(LEFT, y + 1, RIGHT - LEFT, 17, a['fill'])
            p.rect(LEFT, y + 1, 2.5, 17, a['ink'])
            cap(L, p, row['band'], LEFT + 8, y + 5, 400, 'ink')
            y += 18
            continue
        h = slide.get('row_height', 34)
        if row.get('ours'):
            p.rect(LEFT, y, RIGHT - LEFT, h, acc['ochre']['fill'])
        if row.get('logo'):
            icon(L, p, row['logo'], row['cells'][0], LEFT + 4, y + (h - 18) / 2, 18)
        for j, (cell, x0, (_, w)) in enumerate(zip(row['cells'], xs, cols)):
            if isinstance(cell, list):   # [dots, text]
                if cell[0] is not None:
                    dots(L, p, cell[0], x0, y + h / 2 - 9)
                put(L, p, cell[1], x0, y + h / 2 - 1, w - 8, 8, 'body')
                continue
            tx = x0 + (28 if j == 0 else 0)
            th = need(L, cell, x0 + w - 8 - tx, 10, j == 0)
            put(L, p, cell, tx, y + (h - th) / 2, x0 + w - 8 - tx, 10, 'ink' if j == 0 else 'body', j == 0)
        y += h
        p.rect(LEFT, y, RIGHT - LEFT, 0.5, L.t.color('hair'))
    y += 8
    if slide.get('note'):
        note(L, p, slide['note'], LEFT, y, RIGHT - LEFT)
    L.band(p, slide.get('takeaway'))


def dots(L, p, n, x, y):
    for k in range(3):
        p.rect(x + k * 6, y, 4.5, 4.5, L.t.color('ink') if k < n else L.t.color('hair'), 'ELLIPSE')


def close_page(L, p, slide):
    """Closing page, modelled on the old deck's: UTS logo, the claim on a pale band, live demo and code links,
    byline, and the cover illustration at the right. Cover-like: no header or footer."""
    p.ops.clear()
    slide.pop('chapter_badges', None)
    if L.content.get('identity') == 'uts':
        L.image(p, {'path': 'assets/brand/uts-logo.svg', 'alt': 'University of Technology Sydney'}, 43.5, 39, 64, 64)
    y = 150
    p.rect(0, y, 505, 160, L.t.color('accent_pale'))
    p.rect(0, y, 8, 160, L.t.color('accent'))
    cap(L, p, slide['kicker'], LEFT, y + 18, 420, 'accent')
    th = put(L, p, slide['title'], LEFT, y + 36, 440, 24, 'ink', True)
    put(L, p, slide['subtitle'], LEFT, y + 36 + th + 8, 440, 12, 'body')
    yy = 334
    for lab, text, url, art in slide['links']:
        icon(L, p, f'assets/icons/{art}-ink.png', lab, LEFT, yy + 1, 14)
        put(L, p, lab, LEFT + 22, yy, 90, 10, 'ink', True)
        L.text(p, text, LEFT + 112, yy, 340, 14, 10, 'body')
        next(op for op in reversed(p.ops) if op['op'] == 'add-textbox')['href'] = url
        yy += 22
    put(L, p, L.content['author'], LEFT, 410, 420, 12, 'ink', True)
    put(L, p, f"{L.content['affiliation']}  \u00b7  {L.content['date']}", LEFT, 428, 420, 10, 'body')
    L.image(p, slide['image'], 505, 0, 455, 540)


CODE_BG, CODE_INK, CODE_ADD = '#1B2430', '#FFFFFF', '#5EC962'   # added lines in Viridis green (added), never amber on navy


def code_panel(L, p, x, y, w, h, title, lines):
    """A dark code panel: small caps title, then code lines; an added line is bold pale blue."""
    p.rect(x, y, w, h, CODE_BG)
    paint(L, p, title.upper(), x + 10, y + 8, w - 20, 8, '#FFFFFF', True)
    yy = y + 26
    for text, added in lines:
        paint(L, p, f'`{text}`', x + 10, yy, w - 20, 8, CODE_ADD if added else CODE_INK, added)
        yy += 12
    return yy


def hbar(L, p, x, y, w, h, colour, label, ink='#FFFFFF'):
    p.rect(x, y, w, h, colour)
    if label:
        paint(L, p, label, x + 6, y + (h - 13.5) / 2, w - 8, 10, ink, True)


def demo_page(L, p, slide):
    """Demo: the app screenshot, the SQL with what completed revenue adds, and the two revenue figures."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    iw = 300
    ih = iw * 880 / 1190
    L.image(p, slide['image'], LEFT, TOP, iw, ih)
    marks[1] = (LEFT + iw * 0.37, TOP + ih * 0.34)
    cx = LEFT + iw + 14
    code_panel(L, p, cx, TOP, FIG_RIGHT - cx, ih, slide['code_title'], slide['code'])
    marks[2] = (FIG_RIGHT - 12, TOP + 12)
    y = TOP + ih + 16
    put(L, p, slide['bars_title'], LEFT, y, FIG_RIGHT - LEFT, 12, 'ink', True)
    y += 22
    lw, bw = 170, FIG_RIGHT - LEFT - 170
    top = slide['bars'][0]['value']
    for k, b in enumerate(slide['bars']):
        put(L, p, b['label'], LEFT, y + 4, lw - 8, 10, 'ink')
        w = bw * b['value'] / top
        hbar(L, p, LEFT + lw, y, w, 22, SERIES['primary' if k == 0 else 'published'], b['text'])
        if b.get('gap'):
            hbar(L, p, LEFT + lw + w, y, bw - w, 22, SERIES['pale'], b['gap'], L.t.color('ink'))
            marks[3] = (FIG_RIGHT - 12, y + 11)
        y += 28
    note(L, p, slide['note'], LEFT, y + 4, FIG_RIGHT - LEFT)
    right_column(L, p, slide, marks, halo=True)


def boundary_page(L, p, slide):
    """Data boundary: share of stored values sent, the real prompt shortened, what is in and out, local or hosted."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    y = TOP
    put(L, p, slide['bar_title'], LEFT, y, FIG_RIGHT - LEFT, 12, 'ink', True)
    y += 20
    sent, total = slide['sent'], slide['total']
    W = FIG_RIGHT - LEFT
    sw = max(W * sent / total, 60)
    hbar(L, p, LEFT, y, sw, 18, SERIES['primary'], f'{sent} sent')
    hbar(L, p, LEFT + sw, y, W - sw, 18, L.t.color('card'), f'{total - sent} not sent', L.t.color('body'))
    marks[1] = (FIG_RIGHT - 12, y + 9)
    y += 22
    put(L, p, slide['bar_caption'], LEFT, y, W, 8, 'body')
    y += 18
    pw = 330
    end = code_panel(L, p, LEFT, y, pw, 140, slide['code_title'], slide['code'])
    marks[2] = (LEFT + pw - 12, y + 12)
    lx = LEFT + pw + 14
    lw = FIG_RIGHT - lx
    ly = y
    for title, items, art, colour in slide['lists']:   # rows on the code panel's 12 pt line grid
        card(L, p, lx, ly, lw, 64, weight=0)
        cap(L, p, title, lx + 10, ly + 8, lw - 20, 'ink')
        iy = ly + 26
        for t in items:
            icon(L, p, f'assets/icons/{art}-{colour}.png', '', lx + 10, iy + 1, 10)
            put(L, p, t, lx + 24, iy, lw - 34, 8, 'body')
            iy += 12
        ly += 72
    marks[4] = (FIG_RIGHT - 12, y + 72 + 10)
    y += 152
    cw = (W - 14) / 2
    for k, (title, text, art) in enumerate(slide['models']):
        x = LEFT + k * (cw + 14)
        card(L, p, x, y, cw, 46)
        icon(L, p, f'assets/icons/{art}-ink.png', title, x + 10, y + 13, 20)
        put(L, p, title, x + 38, y + 9, cw - 48, 12, 'ink', True)
        put(L, p, text, x + 38, y + 26, cw - 48, 8, 'body')
    marks[3] = (LEFT + cw + 7, y - 4)
    note(L, p, slide['note'], LEFT, y + 56, W)
    right_column(L, p, slide, marks, halo=True)


def arch_page(L, p, slide):
    """Architecture: eight steps in two rows (prepare left to right, check and run right to left), the engine band
    between them, the one repair try as a dashed arrow, technology logos on each step."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    W = FIG_RIGHT - LEFT
    gap = 18
    bw = (W - 3 * gap) / 4
    bh = 66
    acc = L.t.data['accents']

    def box(x, y, step, fill=None):
        p.rect(x, y, bw, bh, fill or L.t.color('card'))
        p.rect(x, y, bw, 3, step.get('rule', L.t.color('accent')))
        p.rect(x + 8, y + 10, 14, 14, L.t.color('ink'))
        paint(L, p, str(step['n']), x + 8, y + 10.5, 14, 8, '#FFFFFF', True, 'center')
        put(L, p, step['title'], x + 28, y + 9, bw - 36, 10, 'ink', True)
        put(L, p, step['text'], x + 8, y + 28, bw - 16, 8, 'body')
        lx = x + bw - 8
        for logo in reversed(step.get('logos', [])):
            lx -= 14
            icon(L, p, logo, '', lx, y + bh - 18, 12)

    y1 = TOP + 14
    cap(L, p, slide['rows'][0], LEFT, TOP, W, 'body')
    for k, st in enumerate(slide['top']):
        x = LEFT + k * (bw + gap)
        box(x, y1, st)
        if k < 3:
            p.connector(x + bw + 2, y1 + bh / 2, x + bw + gap - 2, y1 + bh / 2, color=L.t.color('rule'))
    ey = y1 + bh + 22
    eh = 34
    p.rect(LEFT, ey, W, eh, acc['slate']['fill'])
    p.rect(LEFT, ey, 2.5, eh, acc['slate']['ink'])
    put(L, p, slide['engine']['title'], LEFT + 8, ey + 5, 260, 10, 'ink', True)
    put(L, p, slide['engine']['text'], LEFT + 8, ey + 19, 260, 8, 'body')
    ex = LEFT + 290
    for logo, name in slide['engine']['logos']:
        icon(L, p, logo, name, ex, ey + 9, 16)
        tw = width_of(L, name, 10, True) + 2
        put(L, p, name, ex + 20, ey + 10, tw, 10, 'ink', True)
        ex += 20 + tw + 18
    marks[3] = (FIG_RIGHT - 12, ey + 10)
    # read schema reads the engine; prepare flows down into generate
    p.connector(LEFT + bw + gap + bw / 2, ey - 2, LEFT + bw + gap + bw / 2, y1 + bh + 2, color=L.t.color('rule'))
    y2 = ey + eh + 34
    cap(L, p, slide['rows'][1], LEFT, y2 - 14, W, 'body')
    xs = [LEFT + k * (bw + gap) for k in range(4)]
    p.connector(xs[3] + bw / 2, y1 + bh + 2, xs[3] + bw / 2, ey - 2, color=L.t.color('rule'))
    p.connector(xs[3] + bw / 2, ey + eh + 2, xs[3] + bw / 2, y2 - 2, color=L.t.color('rule'))
    for k, st in enumerate(slide['bottom']):   # 5 at the right, 8 at the left
        x = xs[3 - k]
        box(x, y2, st, SERIES['pale'] if st.get('model') else None)
        if k < 3:
            p.connector(x - 2, y2 + bh / 2, x - gap + 2, y2 + bh / 2, color=L.t.color('rule'))
    marks[1] = (xs[3] + bw - 10, y2 + 12)
    marks[2] = (xs[2] + bw - 10, y2 + 12)
    run_x = xs[1] + bw / 2
    p.connector(run_x, y2 - 2, run_x, ey + eh + 2, color=L.t.color('rule'))
    # one repair try: dashed from Run back to Generate, under the row
    ry = y2 + bh + 12
    p.line(xs[1] + bw / 2, y2 + bh, xs[1] + bw / 2, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.line(xs[1] + bw / 2, ry, xs[3] + bw / 2, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.connector(xs[3] + bw / 2, ry, xs[3] + bw / 2, y2 + bh + 2, color=L.t.color('ink'))
    put(L, p, slide['repair'], xs[2] - 10, ry + 3, bw + 40, 8, 'body')
    marks[4] = (xs[2] - 22, ry)
    py = END - 30   # the person at both ends
    card(L, p, LEFT, py, W, 30, weight=0)
    icon(L, p, 'assets/icons/person-ink.png', 'Person', LEFT + 10, py + 7, 16)
    put(L, p, slide['person'], LEFT + 34, py + 8, W - 44, 10, 'ink')
    right_column(L, p, slide, marks, halo=True)


def stack_page(L, p, slide):
    """Technology stack: groups of tools, each a logo, its name and the job it does here."""
    groups = slide['groups']
    cols = 3
    gap = 16
    cw = (RIGHT - LEFT - gap * (cols - 1)) / cols
    y0 = TOP
    rows = (len(groups) + cols - 1) // cols
    ch = (END - 40 - y0 - gap * (rows - 1)) / rows
    for k, g in enumerate(groups):
        x = LEFT + (k % cols) * (cw + gap)
        y = y0 + (k // cols) * (ch + gap)
        card(L, p, x, y, cw, ch)
        cap(L, p, g['title'], x + 14, y + 12, cw - 24, 'ink')
        yy = y + 32
        for logo, name, role in g['items']:
            icon(L, p, logo, name, x + 14, yy + 1, 20)
            put(L, p, name, x + 42, yy, cw - 52, 10, 'ink', True)
            put(L, p, role, x + 42, yy + 14, cw - 52, 8, 'body')
            yy += 38
    L.band(p, slide.get('takeaway'))


def summary_page(L, p, slide):
    """Executive summary: four stat tiles, then the large-database comparison in two small bar panels."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    acc = L.t.data['accents']
    W = FIG_RIGHT - LEFT
    gap = 10
    tw = (W - 3 * gap) / 4
    th = 116
    for k, t in enumerate(slide['tiles']):
        x = LEFT + k * (tw + gap)
        colour = SERIES[t['series']]
        p.rect(x, TOP, tw, th, L.t.color('card'))
        p.rect(x, TOP, tw, 4, colour)
        icon(L, p, f"assets/icons/{t['icon']}-ink.png", t['label'], x + tw - 28, TOP + 12, 18)
        put(L, p, t['label'], x + 12, TOP + 12, tw - 46, 10, 'ink', True)
        paint(L, p, t['value'], x + 12, TOP + 34, tw - 24, 24, L.t.color('ink'), True)
        put(L, p, t['text'], x + 12, TOP + 72, tw - 24, 8, 'body')
        if t.get('marker'):
            marks[t['marker']] = (x + 8, TOP - 1)
    y = TOP + th + 18
    put(L, p, slide['panel_title'], LEFT, y, W, 12, 'ink', True)
    marks[slide['panel_marker']] = (LEFT + width_of(L, slide['panel_title'], 12, True) + 14, y + 8)
    y += 24
    pw = 2 * tw + gap   # each panel spans two tiles, so their text columns line up
    ph = END - 30 - y
    for k, pn in enumerate(slide['panels']):
        x = LEFT + k * (pw + gap)
        card(L, p, x, y, pw, ph, weight=0)
        put(L, p, pn['title'], x + 12, y + 12, pw - 24, 12, 'ink', True)
        lw, bw = 112, pw - 24 - 112 - 44
        by = y + 38
        for r in pn['rows']:
            put(L, p, r['label'], x + 12, by + 4, lw - 6, 10, 'body')
            w = bw * r['value'] / pn['max']
            p.rect(x + 12 + lw, by, w, 22, SERIES[r['series']])
            paint(L, p, r['text'], x + 12 + lw + w + 6, by + 4, 44, 10, L.t.color('ink'), True)
            by += 32
        put(L, p, pn['reading'], x + 12, by + 6, pw - 24, 10, 'body')
        if pn.get('marker'):
            marks[pn['marker']] = (x + pw - 12, y + 12)
    note(L, p, slide['note'], LEFT, END - 22, W)
    right_column(L, p, slide, marks, halo=True)


LAYOUTS = {'summary_page': summary_page, 'stack_page': stack_page, 'demo_page': demo_page, 'boundary_page': boundary_page, 'arch_page': arch_page, 'tools_page': tools_page, 'close_page': close_page, 'hard_page': hard_page, 'bars_page': bars_page, 'aim_page': aim_page}
