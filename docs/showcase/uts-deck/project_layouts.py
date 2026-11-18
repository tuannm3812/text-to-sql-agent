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




VIRIDIS = {'ours': '#31688E', 'published': '#31688E', 'gap': '#D6E1EC'}   # Viridis blue; the gap is its tint


# -- problem ---------------------------------------------------------------------------------
def hard_page(L, p, slide):
    """Why it is hard: the four-step chain, published scores by benchmark, and the three causes."""
    slide.setdefault('marker_pairs', [])
    chain = slide['chain']
    gap = 14
    w = (FIG_RIGHT - LEFT - gap * (len(chain) - 1)) / len(chain)
    for i, (head, body) in enumerate(chain):
        x = LEFT + i * (w + gap)
        card(L, p, x, TOP, w, 46)
        put(L, p, head, x + 8, TOP + 9, w - 16, 12, 'ink', True)
        put(L, p, body, x + 8, TOP + 26, w - 16, 8, 'body')
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
            paint(L, p, bar['gap'], gx + 8, y + 5, gw - 16, 10, VIRIDIS['ours'], True)
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


SERIES = {'primary': '#31688E', 'secondary': '#35B779', 'muted': '#A9B4BF', 'loss': '#440154', 'pale': '#D6E1EC'}


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
        put(L, p, c['title'], x + 10, TOP + 9, w - 20, 12, 'ink', True)
        put(L, p, c['text'], x + 10, TOP + 26, w - 20, 10)
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
        cap(L, p, q, qx + 8, qy + 7, hw - 16, 'ink')
    p.line(mx, my, mx, my + mh, L.t.color('rule'), 1)
    p.line(mx, my + mh, mx + mw, my + mh, L.t.color('rule'), 1)
    put(L, p, slide['x_axis'], mx, my + mh + 6, mw, 8, 'body', True)
    put(L, p, slide['y_axis'], mx, my - 14, mw, 8, 'body', True)
    for pt in slide['points']:
        cx, cy = mx + pt['x'] * mw, my + (1 - pt['y']) * mh
        colour = SERIES['primary'] if pt.get('ours') else L.t.color('ink')
        p.rect(cx - 4, cy - 4, 8, 8, colour, 'ELLIPSE')
        tw = width_of(L, pt['label'], 10, bool(pt.get('ours'))) + 2
        paint(L, p, pt['label'], cx + 8, cy - 7, tw, 10, colour, bool(pt.get('ours')))
        if pt.get('marker'):
            marks[pt['marker']] = (cx + 8 + tw + 12, cy)
    right_column(L, p, slide, marks)


LAYOUTS = {'hard_page': hard_page, 'bars_page': bars_page, 'aim_page': aim_page}
