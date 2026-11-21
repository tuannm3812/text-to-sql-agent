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


def put(L, p, raw, x, y, w, size=10, role='body', bold=False, align=None, h=None, href=None):
    """Kit text in a frame measured to its own height; returns the height used. href links the whole frame."""
    h = need(L, raw, w, size, bold) if h is None else h
    L.text(p, raw, x, y, w, h, size, role, bold, align)
    if href:
        next(op for op in reversed(p.ops) if op['op'] == 'add-textbox')['href'] = href
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


def right_column(L, p, slide, marks, halo=True):
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
    strip = 24 if slide.get('ours') else 0
    step = (causes_y - 18 - (y + 22) - 26 - strip) / len(fig['bars'])   # bars share the height left above the causes
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
    put(L, p, fig['caption'], LEFT, y, FIG_RIGHT - LEFT, L.size('caption'), href=fig.get('caption_url'))
    if slide.get('ours'):
        sy = y + 16
        p.rect(LEFT, sy, FIG_RIGHT - LEFT, 20, '#E4F2F1')
        p.rect(LEFT, sy, 2.5, 20, SERIES['primary'])
        put(L, p, slide['ours'], LEFT + 10, sy + 4, FIG_RIGHT - LEFT - 20, 8, 'ink')
    y = causes_y
    for i, c in enumerate(causes):
        x = LEFT + i * (cw + 20)
        card(L, p, x, y, cw, ch)
        if c.get('icon'):
            icon(L, p, f"assets/icons/{c['icon']}-ink.png", c['title'], x + cw - 30, y + 10, 18)
        put(L, p, c['title'], x + 12, y + 12, cw - 24, 12, 'ink', True)
        put(L, p, c['text'], x + 12, y + 32, cw - 24, 10)
        if c.get('marker'):
            marks[c['marker']] = (x + 12 + width_of(L, c['title'], 12, True) + 12, y + 20)
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
    if slide.get('boxes'):   # the groups a chart is split by, as a row of small cards above it
        n = len(slide['boxes'])
        bw = (FIG_RIGHT - LEFT - 10 * (n - 1)) / n
        for k, (head, body, art) in enumerate(slide['boxes']):
            bx = LEFT + k * (bw + 10)
            card(L, p, bx, y, bw, 38, weight=0)
            icon(L, p, f'assets/icons/{art}.png', head, bx + 10, y + 11, 16)
            put(L, p, head, bx + 34, y + 6, bw - 44, 10, 'ink', True)
            put(L, p, body, bx + 34, y + 21, bw - 44, 8, 'body')
        y += 50
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
        put(L, p, slide['caption'], LEFT, END - cap_h + 8, FIG_RIGHT - LEFT, L.size('caption'), href=slide.get('caption_url'))
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
            marks[c['marker']] = (tx + width_of(L, c['title'], 12, True) + 12, TOP + 17)
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
            if j > 0:
                x0, w = x0 + 6, w - 6   # inner padding from the column rule
            if isinstance(cell, dict):   # bullets with a tick or a cross, centred in the row
                hs = [need(L, t, w - 20, 8) for t in cell['items']]
                by = y + (h - sum(hs) - 2 * (len(hs) - 1)) / 2
                for t in cell['items']:
                    L.image(p, {'path': f"assets/project/icons/{cell['mark']}.svg", 'alt': 'Best for' if cell['mark'] == 'tick' else 'Risk'}, x0, by + 1, 8, 8)
                    by += put(L, p, t, x0 + 12, by, w - 20, 8, 'body') + 2
                continue
            if isinstance(cell, list):   # [dots, text], centred as a pair
                if cell[0] is not None:
                    dots(L, p, cell[0], x0, y + h / 2 - 8)
                put(L, p, cell[1], x0, y + h / 2 - 1, w - 8, 8, 'body')
                continue
            tx = x0 + (28 if j == 0 else 0)
            th = need(L, cell, x0 + w - 8 - tx, 10, j == 0)
            put(L, p, cell, tx, y + (h - th) / 2, x0 + w - 8 - tx, 10, 'ink' if j == 0 else 'body', j == 0,
                href=row.get('url') if j == 0 else None)
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
    put(L, p, L.content['author'], LEFT, 410, 330, 12, 'ink', True)
    put(L, p, f"{L.content['affiliation']}  \u00b7  {L.content['date']}", LEFT, 428, 330, 10, 'body')
    if slide.get('qr'):   # scan to try the live demo
        L.image(p, slide['qr'], 405, 392, 64, 64)
        put(L, p, 'Scan to try it', 405, 460, 64, 8, 'body', align='center')
    L.image(p, slide['image'], 505, 0, 455, 540)


CODE_BG, CODE_INK, CODE_ADD = '#1B2430', '#FFFFFF', '#5EC962'   # added lines in Viridis green (added), never amber on navy


def code_panel(L, p, x, y, w, h, title, lines, step=12):
    """A dark code panel: small caps title, then code lines; an added line is bold pale blue."""
    p.rect(x, y, w, h, CODE_BG)
    paint(L, p, title.upper(), x + 10, y + 8, w - 20, 8, '#FFFFFF', True)
    yy = y + 26
    for text, added in lines:
        paint(L, p, f'`{text}`', x + 10, yy, w - 20, 8, CODE_ADD if added else CODE_INK, added)
        yy += step
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
    ih = 222   # the code panel's height; the answer card and the QR row share it
    ah = iw * 323 / 687
    p.rect(LEFT, TOP, iw, ah, '#FFFFFF')
    L.image(p, slide['image'], LEFT, TOP, iw, ah)
    p.line(LEFT, TOP, LEFT + iw, TOP, L.t.color('hair'))
    p.line(LEFT, TOP + ah, LEFT + iw, TOP + ah, L.t.color('hair'))
    marks[1] = (LEFT + iw * 0.56, TOP + ah * 0.2)
    qy = TOP + ah + 12
    qs = ih - ah - 12
    card(L, p, LEFT, qy, iw, qs, weight=0)
    L.image(p, slide['qr'], LEFT + 10, qy + 8, qs - 16, qs - 16)
    tx = LEFT + qs + 2
    put(L, p, slide['qr_title'], tx, qy + 12, iw - qs - 12, 12, 'ink', True)
    put(L, p, slide['qr_text'], tx, qy + 30, iw - qs - 12, 8, 'body', href=slide['qr_url'])
    cx = LEFT + iw + 14
    code_panel(L, p, cx, TOP, FIG_RIGHT - cx, ih, slide['code_title'], slide['code'])
    marks[2] = (cx + 10 + width_of(L, slide['code_title'].upper(), 8, True) + 12, TOP + 13.5)
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
            marks[3] = (LEFT + width_of(L, b['label'], 10) + 12, y + 11)
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
    per, step = 110, W / 110   # one square per distinct stored text value, sent ones first
    for k in range(total):
        p.rect(LEFT + (k % per) * step, y + (k // per) * step, step - 1.2, step - 1.2,
               SERIES['primary'] if k < sent else L.t.color('hair'))
    marks[1] = (LEFT + width_of(L, slide['bar_title'], 12, True) + 14, y - 12)
    y += ((total - 1) // per + 1) * step + 6
    put(L, p, slide['bar_caption'], LEFT, y, W, 8, 'body')
    y += 16
    pw = 330
    end = code_panel(L, p, LEFT, y, pw, 152, slide['code_title'], slide['code'], 14)
    marks[2] = (LEFT + 10 + width_of(L, slide['code_title'].upper(), 8, True) + 12, y + 13.5)
    lx = LEFT + pw + 14
    lw = FIG_RIGHT - lx
    ly = y
    for title, items, art, colour in slide['lists']:   # rows on the code panel's 12 pt line grid
        card(L, p, lx, ly, lw, 68, weight=0)
        cap(L, p, title, lx + 10, ly + 8, lw - 20, 'ink')
        iy = ly + 26
        for t in items:
            icon(L, p, f'assets/icons/{art}-{colour}.png', '', lx + 10, iy + 1, 10)
            put(L, p, t, lx + 24, iy, lw - 34, 8, 'body')
            iy += 14
        ly += 84
    marks[4] = (lx + 10 + width_of(L, slide['lists'][1][0].upper(), 8, True) + 12, y + 84 + 13.5)
    y += 166
    cw = (W - 14) / 2
    for k, (title, text, art) in enumerate(slide['models']):
        x = LEFT + k * (cw + 14)
        card(L, p, x, y, cw, 54)
        icon(L, p, f'assets/icons/{art}-ink.png', title, x + 10, y + 17, 20)
        put(L, p, title, x + 38, y + 12, cw - 48, 12, 'ink', True)
        put(L, p, text, x + 38, y + 30, cw - 48, 10, 'body')
    marks[3] = (LEFT + cw + 14 + 38 + width_of(L, slide['models'][1][0], 12, True) + 12, y + 20)
    note(L, p, slide['note'], LEFT, y + 66, W)
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
    marks[3] = (LEFT + 8 + width_of(L, slide['engine']['title'], 10, True) + 12, ey + 12)
    # read schema reads the engine; prepare flows down into generate
    p.connector(LEFT + bw + gap + bw / 2, ey - 2, LEFT + bw + gap + bw / 2, y1 + bh + 2, color=L.t.color('rule'))
    y2 = ey + eh + 34
    xs = [LEFT + k * (bw + gap) for k in range(4)]
    cap(L, p, slide['rows'][1], LEFT, y2 - 16, bw, 'body')
    for (x_a, x_b, label, colour) in ((xs[1], xs[2] + bw, slide['brackets'][0], SERIES['primary']),
                                      (xs[3], xs[3] + bw, slide['brackets'][1], SERIES['model'])):
        p.rect(x_a, y2 - 6, x_b - x_a, 2.5, colour)
        cap(L, p, label, x_a, y2 - 16, x_b - x_a, 'ink')
    p.connector(xs[3] + bw / 2, y1 + bh + 2, xs[3] + bw / 2, ey - 2, color=L.t.color('rule'))
    p.connector(xs[3] + bw / 2, ey + eh + 2, xs[3] + bw / 2, y2 - 2, color=L.t.color('rule'))
    for k, st in enumerate(slide['bottom']):   # 5 at the right, 8 at the left
        x = xs[3 - k]
        box(x, y2, st, SERIES['pale'] if st.get('model') else None)
        if k < 3:
            p.connector(x - 2, y2 + bh / 2, x - gap + 2, y2 + bh / 2, color=L.t.color('rule'))
    marks[1] = (xs[3] + 28 + width_of(L, slide['bottom'][0]['title'], 10, True) + 12, y2 + 16)
    marks[2] = (xs[2] + 28 + width_of(L, slide['bottom'][1]['title'], 10, True) + 12, y2 + 16)
    run_x = xs[1] + bw / 2
    p.connector(run_x, y2 - 2, run_x, ey + eh + 2, color=L.t.color('rule'))
    # one repair try: dashed from Run back to Generate, under the row
    ry = y2 + bh + 12
    p.line(xs[1] + bw / 2, y2 + bh, xs[1] + bw / 2, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.line(xs[1] + bw / 2, ry, xs[3] + bw / 2, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.connector(xs[3] + bw / 2, ry, xs[3] + bw / 2, y2 + bh + 2, color=L.t.color('ink'))
    put(L, p, slide['repair'], xs[2] - 10, ry + 3, bw + 40, 8, 'body')
    marks[4] = (xs[2] - 10 + width_of(L, slide['repair'], 8) + 12, ry + 8.5)
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
    story_strip(L, p, slide)
    marks = {}
    acc = L.t.data['accents']
    W = FIG_RIGHT - LEFT
    gap = 10
    tw = (W - 3 * gap) / 4
    th = 142
    for k, t in enumerate(slide['tiles']):
        x = LEFT + k * (tw + gap)
        colour = SERIES[t['series']]
        p.rect(x, TOP, tw, th, L.t.color('card'))
        p.rect(x, TOP, tw, 4, colour)
        v = t.get('visual', {})
        vx, vy = x + tw - 44, TOP + 10
        if v.get('kind') == 'dots':   # one dot per test, all passed
            for k in range(v['n']):
                p.rect(vx - 14 + (k % 9) * 5.6, vy + 2 + (k // 9) * 5.6, 4.2, 4.2, colour, 'ELLIPSE')
        elif v.get('kind') == 'ring':
            L.image(p, {'path': v['path'], 'alt': v['alt']}, vx + 4, vy, 30, 30)
        elif v.get('kind') == 'interval':   # the paired interval clear of zero
            p.rect(vx - 4, vy + 2, 1, 26, L.t.color('rule'))
            p.rect(vx + 2, vy + 14, 30, 2.5, colour)
            p.rect(vx + 13, vy + 11, 8, 8, colour, 'ELLIPSE')
        else:
            icon(L, p, f"assets/icons/{t['icon']}-ink.png", t['label'], x + tw - 28, TOP + 12, 18)
        put(L, p, t['label'], x + 12, TOP + 14, tw - 70, 10, 'ink', True)
        paint(L, p, t['value'], x + 12, TOP + 46, tw - 24, 24, L.t.color('ink'), True)
        put(L, p, t['text'], x + 12, TOP + 80, tw - 24, 8, 'body')
        if t.get('caveat'):
            p.line(x + 12, TOP + 108, x + tw - 12, TOP + 108, L.t.color('hair'))
            put(L, p, t['caveat'], x + 12, TOP + 113, tw - 24, 8, 'ink')
        if t.get('marker'):
            marks[t['marker']] = (x + 12 + width_of(L, t['value'], 24, True) + 14, TOP + 62)
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
        by = y + 34
        for r in pn['rows']:
            put(L, p, r['label'], x + 12, by + 4, lw - 6, 10, 'body')
            w = bw * r['value'] / pn['max']
            p.rect(x + 12 + lw, by, w, 22, SERIES[r['series']])
            paint(L, p, r['text'], x + 12 + lw + w + 6, by + 4, 44, 10, L.t.color('ink'), True)
            by += 28
        put(L, p, pn['reading'], x + 12, by + 2, pw - 24, 8, 'body')
        if pn.get('marker'):
            marks[pn['marker']] = (x + 12 + width_of(L, pn['title'], 12, True) + 14, y + 20)
    note(L, p, slide['note'], LEFT, END - 22, W)
    right_column(L, p, slide, marks, halo=True)


KIND = {'app': ('#1B2430', '#F4F5F6'), 'model': ('#FDE725', '#FDF7C7'), 'code': ('#21918C', '#E4F2F1')}


def flow_legend(L, p, slide, x, y, w):
    items = [{'kind': 'swatch', 'color': KIND[k][0], 'label': lab} for k, lab in slide['legend_kinds']]
    return legend(L, p, items, x, y, w)


def flow_box(L, p, x, y, w, h, st, size=10):
    rule, fill = KIND[st['kind']]
    p.rect(x, y, w, h, fill)
    p.rect(x, y, w, 3, rule)
    tx = x + 10
    if st.get('n'):
        p.rect(x + 10, y + 11, 14, 14, L.t.color('ink'))
        paint(L, p, str(st['n']), x + 10, y + 11.5, 14, 8, '#FFFFFF', True, 'center')
        tx = x + 30
    elif st.get('icon'):
        icon(L, p, f"assets/icons/{st['icon']}-ink.png", st['title'], x + 10, y + 9, 18)
        tx = x + 34
    th = put(L, p, st['title'], tx, y + 10, x + w - 10 - tx, 12 if size > 9 else 10, 'ink', True)
    put(L, p, st['text'], x + 10, y + max(32, 10 + th + 6), w - 20, 8, 'body')
    lx = x + w - 10
    for logo in reversed(st.get('logos', [])):
        lx -= 15
        icon(L, p, logo, '', lx, y + h - 19, 12)
    return tx


def arch_summary(L, p, slide):
    """Architecture in four stages: what runs where, the one model call, the two gates, the one repair try."""
    slide.setdefault('marker_pairs', [])
    marks = {}
    W = FIG_RIGHT - LEFT
    flow_legend(L, p, slide, LEFT, TOP, W)
    gap = 22
    bw = (W - 3 * gap) / 4
    bh = 140
    y0 = TOP + 58
    xs = [LEFT + k * (bw + gap) for k in range(4)]
    for k, st in enumerate(slide['stages']):
        tx = flow_box(L, p, xs[k], y0, bw, bh, st)
        if st.get('marker'):
            marks[st['marker']] = (tx + width_of(L, st['title'], 12, True) + 12, y0 + 18)
        if k < 3:
            p.connector(xs[k] + bw + 3, y0 + bh / 2, xs[k + 1] - 3, y0 + bh / 2, color=L.t.color('ink'))
    # one repair try: dashed from Check and run back to Generate, above the row
    ry = y0 - 12
    a, b = xs[2] + bw / 2, xs[1] + bw / 2
    p.line(a, y0 - 2, a, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.line(a, ry, b, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.connector(b, ry, b, y0 - 2, color=L.t.color('ink'))
    put(L, p, slide['repair'], b + 8, ry - 13, a - b - 16, 8, 'body', align='center')
    marks[4] = (a + 14, ry)
    # engine band under the row; the app reads the schema from it and runs the query on it
    ey = y0 + bh + 30
    eh = 44
    p.rect(LEFT, ey, W, eh, KIND['code'][1])
    p.rect(LEFT, ey, 2.5, eh, KIND['code'][0])
    put(L, p, slide['engine']['title'], LEFT + 10, ey + 8, 200, 12, 'ink', True)
    put(L, p, slide['engine']['text'], LEFT + 10, ey + 26, 220, 8, 'body')
    marks[3] = (LEFT + 10 + width_of(L, slide['engine']['title'], 12, True) + 12, ey + 16)
    ex = LEFT + 250
    for logo, name in slide['engine']['logos']:
        icon(L, p, logo, name, ex, ey + 14, 16)
        tw = width_of(L, name, 10, True) + 2
        put(L, p, name, ex + 20, ey + 15, tw, 10, 'ink', True)
        ex += 20 + tw + 22
    for k in (0, 2):
        p.connector(xs[k] + bw / 2, y0 + bh + 3, xs[k] + bw / 2, ey - 3, start=True, color=L.t.color('ink'))
    py = END - 30
    card(L, p, LEFT, py, W, 30, weight=0)
    icon(L, p, 'assets/icons/person-ink.png', 'Person', LEFT + 10, py + 7, 16)
    put(L, p, slide['person'], LEFT + 34, py + 8, W - 44, 10, 'ink')
    right_column(L, p, slide, marks)


def arch_detail(L, p, slide):
    """Appendix: the full eight-step flow across the whole width, with each step explained; no takeaway column."""
    W = RIGHT - LEFT
    flow_legend(L, p, slide, LEFT, TOP, W)
    gap = 26
    bw = (W - 3 * gap) / 4
    bh = 82
    ya = TOP + 26
    xs = [LEFT + k * (bw + gap) for k in range(4)]
    cap(L, p, slide['rows'][0], LEFT, ya - 2, W, 'body')
    ya += 12
    for k, st in enumerate(slide['top']):
        flow_box(L, p, xs[k], ya, bw, bh, st, 9)
        if k < 3:
            p.connector(xs[k] + bw + 3, ya + bh / 2, xs[k + 1] - 3, ya + bh / 2, color=L.t.color('ink'))
    yb = ya + bh + 44
    p.connector(xs[3] + bw / 2, ya + bh + 3, xs[3] + bw / 2, yb - 3, color=L.t.color('ink'))
    for k, st in enumerate(slide['bottom']):   # 5 at the right, 8 at the left
        x = xs[3 - k]
        flow_box(L, p, x, yb, bw, bh, st, 9)
        if k < 3:
            p.connector(x - 3, yb + bh / 2, x - gap + 3, yb + bh / 2, color=L.t.color('ink'))
    # repair: from Run (column 2) back to Generate (column 4), in the gap above the lower row
    ry = yb - 14
    a, b = xs[1] + bw / 2, xs[3] + 30
    p.line(a, yb - 2, a, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.line(a, ry, b, ry, L.t.color('ink'), 1.2, dash='DASH')
    p.connector(b, ry, b, yb - 2, color=L.t.color('ink'))
    put(L, p, slide['repair'], a + 10, ry - 13, b - a - 30, 8, 'body')
    ey = yb + bh + 16
    eh = 46
    p.rect(LEFT, ey, W, eh, KIND['code'][1])
    p.rect(LEFT, ey, 2.5, eh, KIND['code'][0])
    put(L, p, slide['engine']['title'], LEFT + 10, ey + 8, 170, 10, 'ink', True)
    put(L, p, slide['engine']['text'], LEFT + 10, ey + 26, 170, 8, 'body')
    ew = (W - 200) / 3
    for k, (logo, name, how) in enumerate(slide['engine']['detail']):
        x = LEFT + 190 + k * ew
        icon(L, p, logo, name, x, ey + 8, 14)
        put(L, p, name, x + 20, ey + 8, ew - 30, 10, 'ink', True)
        put(L, p, how, x, ey + 26, ew - 14, 8, 'body')
    p.connector(xs[1] + bw / 2, yb + bh + 3, xs[1] + bw / 2, ey - 3, color=L.t.color('ink'))
    py = ey + eh + 8
    put(L, p, slide['person'], LEFT, py, W, 8, 'body')


PILL = {'app': ('#E3E6EA', '#1B2430'), 'model': ('#FDF3A6', '#1B2430'), 'code': ('#D3EDEB', '#14605C')}
HEAD_INK = {'app': '#FFFFFF', 'model': '#1B2430', 'code': '#FFFFFF'}


def pill(L, p, text, kind, x, y):
    fill, ink = PILL[kind]
    w = width_of(L, text, 8, True) + 16
    p.rect(x, y, w, 14, fill, 'ROUND_RECTANGLE')
    paint(L, p, text, x + 8, y + 1.5, w - 12, 8, ink, True)
    return w


def arch_board(L, p, slide):
    """Appendix architecture board, after the transit lakehouse diagram: one column per stage with a coloured
    header bar, a status pill, short lines and its tools; full-width bands below for what cuts across stages."""
    W = RIGHT - LEFT
    x = LEFT
    for kind, label in slide['legend_kinds']:   # the pills double as the legend
        x += pill(L, p, label, kind, x, TOP) + 8
    put(L, p, slide['legend_note'], x + 4, TOP + 1.5, RIGHT - x - 4, 8, 'body')
    cols = slide['columns']
    gap = 16
    cw = (W - gap * (len(cols) - 1)) / len(cols)
    y0 = TOP + 24
    ch = 214
    for k, c in enumerate(cols):
        cx = LEFT + k * (cw + gap)
        rule = KIND[c['kind']][0]
        p.rect(cx, y0, cw, ch, KIND[c['kind']][1])
        p.rect(cx, y0, cw, 24, rule)
        paint(L, p, c['title'], cx + 8, y0 + 5, cw - 16, 12, HEAD_INK[c['kind']], True)
        yy = y0 + 32
        pill(L, p, c['pill'], c['kind'], cx + 8, yy)
        yy += 22
        for line in c['lines']:
            yy += put(L, p, line, cx + 8, yy, cw - 16, 8, 'ink') + 5
        lx = cx + 8
        for logo in c.get('logos', []):
            icon(L, p, logo, '', lx, y0 + ch - 22, 14)
            lx += 20
        if k < len(cols) - 1:
            p.connector(cx + cw + 2, y0 + ch / 2, cx + cw + gap - 2, y0 + ch / 2, color=L.t.color('ink'))
    by = y0 + ch + 10
    bh = (END - by - 2 * 4) / len(slide['bands'])
    for b in slide['bands']:
        rule = KIND[b['kind']][0]
        p.rect(LEFT, by, W, bh, L.t.color('card'))
        p.rect(LEFT, by, 3, bh, rule)
        icon(L, p, f"assets/icons/{b['icon']}-ink.png", b['title'], LEFT + 12, by + (bh - 16) / 2, 16)
        put(L, p, b['title'], LEFT + 36, by + (bh - 16) / 2, 150, 12, 'ink', True)
        put(L, p, b['text'], LEFT + 196, by + (bh - 10.8) / 2, W - 196 - 130, 8, 'ink')
        pw = width_of(L, b['pill'], 8, True) + 16
        pill(L, p, b['pill'], b['kind'], RIGHT - pw - 10, by + (bh - 14) / 2)
        by += bh + 4


def arch_rows(L, p, slide):
    """Appendix architecture as one row per stage, top to bottom, across the full width: the stage, what happens,
    where it lives in the code, and what it guarantees or leaves open. Arrows run down the stage column."""
    cols = [('Stage', 0, 150), ('What happens', 164, 300), ('Where in the code', 476, 190), ('Guarantees and limits', 678, RIGHT - LEFT - 678)]
    # each stage's pill names its kind (app, model, code), so the colours need no separate legend
    y = TOP - 2
    for head, dx, w in cols:
        if head:
            cap(L, p, head, LEFT + dx, y, w, 'body')
    y += 14
    p.rect(LEFT, y, RIGHT - LEFT, 1, L.t.color('ink'))
    n = len(slide['stages'])
    gap = 6
    rh = (END - y - 4 - gap * (n - 1)) / n
    y += 4
    for k, st in enumerate(slide['stages']):
        rule, fill = KIND[st['kind']]
        p.rect(LEFT, y, cols[0][2], rh, fill)
        p.rect(LEFT, y, 3, rh, rule)
        p.rect(LEFT + 10, y + 8, 14, 14, L.t.color('ink'))
        paint(L, p, str(k + 1), LEFT + 10, y + 8.5, 14, 8, '#FFFFFF', True, 'center')
        put(L, p, st['title'], LEFT + 30, y + 7, cols[0][2] - 40, 12, 'ink', True)
        pill(L, p, st['pill'], st['kind'], LEFT + 10, y + 28)
        lx = LEFT + cols[0][2] - 10
        for logo in reversed(st.get('logos', [])):
            lx -= 15
            icon(L, p, logo, '', lx, y + rh - 18, 12)
        put(L, p, st['what'], LEFT + cols[1][1], y + 6, cols[1][2], 8, 'ink')
        put(L, p, st['code'], LEFT + cols[2][1], y + 6, cols[2][2], 8, 'body')
        put(L, p, st['limits'], LEFT + cols[3][1], y + 6, cols[3][2], 8, 'body')
        if k < n - 1:
            p.line(LEFT + cols[1][1], y + rh + gap / 2, RIGHT, y + rh + gap / 2, L.t.color('hair'))
            p.connector(LEFT + 75, y + rh, LEFT + 75, y + rh + gap, color=L.t.color('ink'))
        y += rh + gap


def flow_page(L, p, slide):
    """A full-width rendered flowchart (make_flow.py) from just under the title to the content floor; the page has
    no subtitle, so the figure takes that band too. No takeaway column."""
    top = TOP - 6 if slide.get('subtitle') else END - (RIGHT - LEFT) * 432 / 1000
    h = END - top
    w = min(RIGHT - LEFT, h * 1000 / 432)
    L.image(p, slide['image'], LEFT + (RIGHT - LEFT - w) / 2, top, w, h)


def persona_page(L, p, slide):
    """The store manager's situation: her illustration at the left, her question, today's options and what she needs."""
    ih = END - TOP - 14
    iw = ih * 600 / 560
    L.image(p, slide['image'], LEFT, TOP, iw, ih)
    if slide.get('credit'):
        put(L, p, slide['credit']['label'], LEFT, END - 10, iw, 8, 'body', href=slide['credit']['url'])
    x = LEFT + iw + 20
    w = RIGHT - x
    qy = TOP + put(L, p, slide['who'], x, TOP, w, 10, 'body') + 8
    p.rect(x, qy, w, 50, '#E4F2F1')
    p.rect(x, qy, 3, 50, '#21918C')
    paint(L, p, slide['question'], x + 14, qy + 9, w - 28, 12, '#14605C', True)
    put(L, p, slide['question_note'], x + 14, qy + 30, w - 28, 8, 'body')
    y = qy + 66
    gap = 12
    cw = (w - gap) / 2
    for k, (head, items, art, tone) in enumerate(slide['columns']):
        cx = x + k * (cw + gap)
        card(L, p, cx, y, cw, END - 56 - y, weight=3)
        icon(L, p, f'assets/icons/{art}.png', head, cx + 12, y + 12, 16)
        put(L, p, head, cx + 34, y + 12, cw - 46, 12, 'ink', True)
        yy = y + 44
        for t in items:
            L.image(p, {'path': f'assets/project/icons/{tone}.svg', 'alt': ''}, cx + 12, yy + 2, 10, 10)
            yy += put(L, p, t, cx + 26, yy, cw - 38, 12, 'ink') + 12
    L.band(p, slide.get('takeaway'), x, END - 44, w, 44)


def answer_page(L, p, slide):
    """Her answer: three outcomes as cards with an icon, then what the project contributes."""
    n = len(slide['outcomes'])
    gap = 16
    ch = 170
    x0 = LEFT
    if slide.get('photo'):   # a callback to her shop, from the store manager slide
        pw = ch * 600 / 560
        L.image(p, slide['photo'], LEFT, TOP, pw, ch)
        x0 = LEFT + pw + gap
    cw = (RIGHT - x0 - gap * (n - 1)) / n
    for k, (art, head, big, items) in enumerate(slide['outcomes']):
        x = x0 + k * (cw + gap)
        card(L, p, x, TOP, cw, ch, weight=4)
        icon(L, p, f'assets/icons/{art}.png', head, x + 14, TOP + 16, 22)
        put(L, p, head, x + 44, TOP + 18, cw - 58, 12, 'ink', True)
        paint(L, p, big, x + 14, TOP + 50, cw - 28, 24, '#1B2430', True)
        yy = TOP + 92
        for t in items:
            yy += put(L, p, '\u2022  ' + t, x + 14, yy, cw - 28, 10, 'body') + 4
    y = TOP + ch + 22
    put(L, p, slide['contribution_title'], LEFT, y, RIGHT - LEFT, 12, 'ink', True)
    y += 22
    cw2 = (RIGHT - LEFT - gap * 2) / 3
    for k, (head, body) in enumerate(slide['contribution']):
        x = LEFT + k * (cw2 + gap)
        p.rect(x, y, 3, 52, '#21918C')
        put(L, p, head, x + 14, y, cw2 - 18, 10, 'ink', True)
        put(L, p, body, x + 14, y + 18, cw2 - 18, 10, 'body')
    L.band(p, slide.get('takeaway'))


def roadmap_page(L, p, slide):
    """Next tests as a roadmap: four milestones on one line, each with why, what we measure and what it decides."""
    ms = slide['milestones']
    n = len(ms)
    gap = 16
    cw = (RIGHT - LEFT - gap * (n - 1)) / n
    ly = TOP + 24
    p.line(LEFT + cw / 2, ly, RIGHT - cw / 2, ly, L.t.color('rule'), 2)
    for k, m in enumerate(ms):
        x = LEFT + k * (cw + gap)
        cx = x + cw / 2
        p.rect(cx - 16, ly - 16, 32, 32, '#896521', 'ELLIPSE')
        icon(L, p, f"assets/icons/{m['icon']}-white.png", m['title'], cx - 9, ly - 9, 18)
        y = ly + 26
        cap(L, p, f"Test {k + 1}", x, y, cw, 'ink')
        put(L, p, m['title'], x, y + 14, cw, 12, 'ink', True)
        y += 40
        card(L, p, x, y, cw, END - 56 - y, weight=0)
        yy = y + 10
        for head, body in (('Why', m['why']), ('We would measure', m['measure']), ('It decides', m['decides'])):
            cap(L, p, head, x + 14, yy, cw - 28, 'body')
            yy += 13 + put(L, p, body, x + 14, yy + 13, cw - 28, 10, 'ink') + 8
        put(L, p, m['evidence'], x + 14, END - 56 - 22, cw - 28, 8, 'body')
    L.band(p, slide.get('takeaway'))


def serves_page(L, p, slide):
    """Who it serves: one card per group, with an icon, why it helps (ticks) and where it does not fit (crosses)."""
    rows = slide['groups']
    n = len(rows)
    gap = 16
    cw = (RIGHT - LEFT - gap * (n - 1)) / n
    h = END - 66 - TOP
    photos = slide.get('photos', [])
    ph = cw / 3   # 3:1 banner
    for k, (art, who, helps, nofit) in enumerate(rows):
        x = LEFT + k * (cw + gap)
        card(L, p, x, TOP, cw, h, weight=0)
        top = TOP
        if k < len(photos):
            L.image(p, photos[k]['image'], x, TOP, cw, ph)
            top = TOP + ph - 17
        p.rect(x + 14, top, 34, 34, '#FFFFFF', 'ELLIPSE')
        icon(L, p, f'assets/icons/{art}.png', who, x + 22, top + 8, 18)
        put(L, p, who, x + 56, top + 20, cw - 70, 12, 'ink', True)
        y = top + 50
        cap(L, p, 'Why it helps', x + 14, y, cw - 28, 'body')
        y += 16
        for t in helps:
            L.image(p, {'path': 'assets/project/icons/tick.svg', 'alt': ''}, x + 14, y + 1.5, 10, 10)
            y += put(L, p, t, x + 30, y, cw - 44, 10, 'ink') + 7
        y += 4
        p.line(x + 14, y, x + cw - 14, y, L.t.color('hair'))
        y += 8
        cap(L, p, 'Where it does not fit', x + 14, y, cw - 28, 'body')
        y += 16
        for t in nofit:
            L.image(p, {'path': 'assets/project/icons/cross.svg', 'alt': ''}, x + 14, y + 1.5, 10, 10)
            y += put(L, p, t, x + 30, y, cw - 44, 10, 'ink') + 7
    if photos:
        put(L, p, 'Photos: ' + '; '.join(ph_['credit'] for ph_ in photos), LEFT, END - 60, RIGHT - LEFT, 8, 'body')
    L.band(p, slide.get('takeaway'))


def sources_page(L, p, slide):
    """Sources in two groups, each line with an icon and a link."""
    gap = 24
    cw = (RIGHT - LEFT - gap) / 2
    for k, (head, art, items) in enumerate(slide['groups']):
        x = LEFT + k * (cw + gap)
        icon(L, p, f'assets/icons/{art}.png', head, x, TOP + 2, 16)
        put(L, p, head, x + 24, TOP + 2, cw - 24, 12, 'ink', True)
        y = TOP + 30
        for label, detail, url in items:
            card(L, p, x, y, cw, 52, weight=0)
            put(L, p, label, x + 14, y + 10, cw - 28, 10, 'ink', True, href=url)
            put(L, p, detail, x + 14, y + 28, cw - 28, 8, 'body')
            y += 60


LAYOUTS = {'serves_page': serves_page, 'sources_page': sources_page, 'persona_page': persona_page, 'answer_page': answer_page, 'roadmap_page': roadmap_page, 'flow_page': flow_page, 'arch_rows': arch_rows, 'arch_board': arch_board, 'arch_summary': arch_summary, 'arch_detail': arch_detail, 'summary_page': summary_page, 'stack_page': stack_page, 'demo_page': demo_page, 'boundary_page': boundary_page, 'arch_page': arch_page, 'tools_page': tools_page, 'close_page': close_page, 'hard_page': hard_page, 'bars_page': bars_page, 'aim_page': aim_page}


def story_strip(L, p, slide):
    """The story line under the subtitle, drawn once per page."""
    if slide.get('story') and slide.get('_story_page') != p.id:
        slide['_story_page'] = p.id
        paint(L, p, slide['story'], LEFT, 116.5, RIGHT - LEFT, 8, '#14605C')   # on the title's edge; teal marks the story


# -- story thread (22 November 2026): the store manager's question ------------------------------
# A one-line strip under the subtitle on any slide with a 'story' field, whatever its layout: a person icon and
# one sentence tying the slide back to her question. Project-local: wraps the kit's header without editing it.
from uts_kit.layouts import Layouts as _Layouts

if not getattr(_Layouts.header, '_story', False):
    _kit_header = _Layouts.header

    def _header(self, p, slide, n):
        _kit_header(self, p, slide, n)
        story_strip(self, p, slide)

    _header._story = True
    _Layouts.header = _header
