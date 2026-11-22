"""UTS poster blocks for the deck-kit poster engine, drawn natively at poster type sizes (no slide screenshots).

First built for the Synogize harness poster (17 November 2026). Point a poster spec's "plugin" at this file and its
"css" at uts_poster.css (portrait) or uts_poster_landscape.css (landscape); see templates/POSTER-TEMPLATE.md.

  ptake      answer band: key number, verdict with reason lines, numbered next steps ("Step: detail")
  ploop      a loop diagram on fixed geometry: a box, a tool-call bus with an arrow into each action, a return arrow
  pdumbbell  paired scores per row on one axis, two role colours, the gap at the right
  pmatrix    one line per comparison: interval coloured by side of zero, values in arm colours, better value bold
  ptasks     outcome boxes per attempt for two arms, a ratio bar against 1x, notes; key rows tinted; optional summary row
  ptrade     per step: what each arm does, then offers (tick) and costs (cross); candidate rows marked
  parrows    before-to-after arrow panels on one scale per panel, with an optional limits line
  pslopes    small slope panels; pscale and psteps6 are earlier, simpler variants

Field names (t2, ours, custom) come from the first project; they mean "reference arm" and "our arm".
"""
from __future__ import annotations

import html
import re

from deck_kit import poster as P

T2, CUSTOM, DIFF = '#375A8C', '#3BBB75', '#440154'
PAGE_REF = re.compile(r' ?\(page \{p:[^}]+\}\)')
LEVEL = {'easy': ('E', '#FDE725', '#1D2229'), 'medium': ('M', '#21918C', '#FFFFFF'), 'hard': ('H', '#440154', '#FFFFFF')}


def rich(text, t):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)


def head(block, t):
    h = f'<h2>{rich(block["heading"], t)}</h2>' if block.get('heading') else ''
    return h


def card(kind, block, inner):
    span = f' style="grid-column: span {block.get("span", 12)}"'
    role = f' data-role="{block["role"]}"' if block.get('role') else ''
    return f'<section class="block card {kind}"{span}{role}>{inner}</section>'


def boxes(outcomes, colour):
    out = []
    for o in outcomes:
        cls = {'s': 'ob s', 'c': 'ob c', 'f': 'ob f'}[o]
        out.append(f'<i class="{cls}" style="--c:{colour}"></i>')
    return '<span class="obox">' + ''.join(out) + '</span>'


def ptasks(block, base, t):
    top = block.get('max_ratio', 8)
    rows = []
    keep = (lambda r: r.get('decides') or r['task'].strip('`') in block.get('also', [])) if block.get('only_decides') else (lambda r: not (block.get('summary') and r['t2'] == 0 and r['ours'] == 0))
    for r in [r for r in block['rows'] if keep(r)]:
        letter, fill, ink = LEVEL[r['level']]
        ratio = r.get('ratio') or r['ours_in'] / r['t2_in']
        width = min(ratio, top) / top * 100
        one = 1 / top * 100
        t2 = ['s'] * r['t2'] + ['x'] * (3 - r['t2'])
        rows.append(
            f'<div class="trow2{" decide" if r.get("decides") else ""}">'
            f'<span class="tname"><i class="lvl" style="--f:{fill};--k:{ink}">{letter}</i><code>{html.escape(r["task"].strip("`"))}</code></span>'
            + boxes(['s' if x == 's' else 'f' for x in t2], T2) + boxes(r['ours_out'], CUSTOM)
            + f'<span class="tbar"><i style="width:{width:.2f}%"></i><u style="left:{one:.2f}%"></u><b>{ratio:.2f}×</b></span>'
            f'<span class="tnote">{rich(PAGE_REF.sub("", r["note"]), t)}</span></div>')
    if block.get('summary'):
        sm = block['summary']
        rows.append(f'<div class="trow2 tsum"><span class="tname"><b>{html.escape(sm["label"])}</b></span>'
                    + (f'<span></span><span></span>' if sm.get('no_boxes') else boxes(['f', 'f', 'f'], T2) + boxes(['f', 'f', 'f'], CUSTOM))
                    + f'<span class="tbar"><b>{html.escape(sm["ratio"])}</b></span><span class="tnote">{rich(sm["note"], t)}</span></div>')
    heads = ('<div class="thead2"><b>Task</b><b class="c" style="color:#375A8C">T2</b><b class="c" style="color:#1F7A4F">Custom</b>'
             '<b>Custom input ÷ T2 <span>(line at 1×)</span></b><b>What the logs show</b></div>')
    key = ''.join(f'<span class="k"><i class="ob {c}" style="--c:#526174"></i>{l}</span>'
                  for c, l in (('s', 'Solved'), ('c', 'Ran out of turns'), ('f', 'Finished, tests failed')))
    key += '<span class="k"><i class="kdec"></i>Decides the gap</span>'
    return card('ptasks', block, head(block, t) + f'<div class="pkey">{key}</div>' + heads + ''.join(rows)
                + (f'<p class="caption">{rich(block["caption"], t)}</p>' if block.get('caption') else ''))


def pslopes(block, base, t):
    modes = block['modes']
    key = ''.join(f'<span class="k"><i class="kline" style="--c:{c}"></i>{html.escape(n)}</span>' for n, c in modes)
    panels = []
    for p in block['panels']:
        lo, hi = p['range']
        Y = lambda v: 88 - (v - lo) / (hi - lo) * 76
        lines, labels = [], []
        seen = {}
        for (a, b), (_, c) in zip(p['values'], modes):
            lines.append(f'<line x1="18" y1="{Y(a):.1f}" x2="82" y2="{Y(b):.1f}" stroke="{c}" stroke-width="2.4" vector-effect="non-scaling-stroke"/>'
                         f'<circle cx="18" cy="{Y(a):.1f}" r="2.2" fill="{c}"/><circle cx="82" cy="{Y(b):.1f}" r="2.2" fill="{c}"/>')
            for side, v in (('l', a), ('r', b)):
                if (side, v) in seen:
                    continue
                seen[(side, v)] = 1
                labels.append((side, v, Y(v)))
        # keep labels on one side apart
        for side in ('l', 'r'):
            pts = sorted([l for l in labels if l[0] == side], key=lambda l: l[2])
            for i in range(1, len(pts)):
                if pts[i][2] - pts[i - 1][2] < 34:
                    pts[i] = (pts[i][0], pts[i][1], pts[i - 1][2] + 34)
            labels = [l for l in labels if l[0] != side] + pts
        fmt = p.get('fmt', '{:g}')
        lab = ''.join(f'<span class="sv {s}" style="top:{y:.1f}%">{html.escape(fmt.format(v))}</span>' for s, v, y in labels)
        panels.append(f'<div class="spanel2"><b>{html.escape(p["title"])}</b><span class="su">{html.escape(p["unit"])}</span>'
                      f'<div class="splot2"><svg viewBox="0 0 100 100" preserveAspectRatio="none">'
                      f'<line x1="18" y1="8" x2="18" y2="92" class="ax"/><line x1="82" y1="8" x2="82" y2="92" class="ax"/>{"".join(lines)}</svg>{lab}</div>'
                      f'<div class="sx"><span>Full</span><span>Reduced</span></div>'
                      + (f'<p class="caption">{rich(p["insight"], t)}</p>' if block.get('insights', True) else '') + '</div>')
    return card('pslopes', block, head(block, t) + f'<div class="pkey">{key}</div><div class="spanels">{"".join(panels)}</div>'
                + (f'<p class="caption">{rich(block["caption"], t)}</p>' if block.get('caption') else ''))


def pscale(block, base, t):
    lo, hi = block['domain']
    x = lambda v: (max(lo, min(hi, v)) - lo) / (hi - lo) * 100
    rows = []
    for r in block['rows']:
        hollow = r['high'] >= 0
        rows.append(f'<div class="crow"><span class="cname"><b>{rich(r["name"], t)}</b><span>{rich(r["sub"], t)}</span></span>'
                    f'<span class="cplot"><i style="left:{x(r["low"]):.2f}%;width:{x(r["high"]) - x(r["low"]):.2f}%"></i>'
                    f'<em class="{"open" if hollow else ""}" style="left:{x(r["est"]):.2f}%"></em></span>'
                    f'<span class="cval"><b>{html.escape(r["value"])}</b> {html.escape(r["ci"])}</span>'
                    f'<span class="csolve"><b style="color:{T2}">{html.escape(r["t2"])}</b><span>{html.escape(r["custom"])}</span></span></div>')
    ticks = ''.join(f'<span style="left:{x(v):.2f}%">{html.escape(l)}</span>' for v, l in block['ticks'])
    zero = x(0)
    key = ('<span class="k"><i class="kdot open"></i>Interval includes zero</span>'
           '<span class="k"><i class="kdot"></i>Excludes zero</span>')
    heads = ('<div class="chead"><b>Comparison</b><b>Gap, Custom minus T2, pp, 95% interval</b><b></b>'
             '<b>Solved, <span style="color:#375A8C">T2</span> · Custom</b></div>')
    return card('pscale', block, head(block, t) + f'<div class="pkey">{key}</div>' + heads
                + f'<div class="cbody"><u class="czero" style="--z:{zero / 100:.4f}"></u>{"".join(rows)}</div>'
                + f'<div class="caxis"><span></span><span class="cticks">{ticks}</span></div>'
                + (f'<p class="caption">{rich(block["caption"], t)}</p>' if block.get('caption') else ''))


PLUGIN_BLOCKS = {'ptasks': ptasks, 'pslopes': pslopes, 'pscale': pscale}


def header_extra(spec, t, base):
    return ('<link href="https://fonts.googleapis.com/css2?family=Google+Sans+Code:wght@400;700&display=block" '
            'rel="stylesheet">')


def pdumbbell(block, base, t):
    """Same model, different harness: one line per model (logo, name, a dumbbell, the gap). Harnesses are told apart
    by colour and logo in one legend above, so each dot carries only its score."""
    lo, hi = block['domain']
    x = lambda v: (v - lo) / (hi - lo) * 100
    logo = lambda path: f'<img src="{P.data_uri((base / path).expanduser())}" alt="">'
    colours = block['colours']
    tag = lambda n, r: ''
    rows = []
    for r in block['rows']:
        pts = sorted([(r['t2'], 'Terminus 2'), (r['other'], 'maker')])
        (lv, ln), (hv, hn) = pts
        rows.append(
            f'<div class="drow"><span class="dname">{logo(r["logo"])}<b>{html.escape(r["model"])}</b></span>'
            f'<span class="dplot"><i style="left:{x(lv):.2f}%;width:{x(hv) - x(lv):.2f}%;background:{colours[hn]};opacity:.35"></i>'
            f'<em style="left:{x(lv):.2f}%;background:{colours[ln]}"></em><em style="left:{x(hv):.2f}%;background:{colours[hn]}"></em>'
            f'<span class="dl left" style="right:calc({100 - x(lv):.2f}% + 3.2mm);color:{colours[ln]}">{tag(ln, r)}{lv:.1f}</span>'
            f'<span class="dl right" style="left:calc({x(hv):.2f}% + 3.2mm);color:{colours[hn]}">{tag(hn, r)}{hv:.1f}</span></span>'
            f'<b class="dgap" style="color:{colours[hn]}">{r["gap"]}</b></div>')
    key = ''.join(f'<span class="k"><i class="kdot2" style="--c:{colours[n]}"></i>{html.escape(l)}</span>'
                  for n, l in block['legend'])
    return card('pdumbbell', block, head(block, t) + f'<div class="pkey">{key}</div>'
                + '<div class="dhead"><b>Model</b><b>Resolution rate, same model (%)</b><b>Own − T2</b></div>'
                + ''.join(rows)
                + (f'<p class="caption">{rich(block["caption"], t)}</p>' if block.get('caption') else ''))


def ploop(block, base, t):
    """The harness loop on a fixed geometry, so every connector meets its box: the model, a tool-call line to a bus,
    an arrow into each of three actions, and the output returning to the model."""
    icon = lambda path: f'<img src="{P.data_uri((base / path).expanduser())}" alt="">'
    MX, BUS, AX = 34, 45, 52            # % of the width: model right edge, bus, actions left edge
    H, GAP = 16, 2.5                    # action height and gap, mm
    tops = [k * (H + GAP) for k in range(3)]
    mids = [tp + H / 2 for tp in tops]
    bottom = tops[-1] + H
    m0, m1 = mids[1] - 12, mids[1] + 12  # model box, mm
    ret = bottom + 5
    g = []
    hl = lambda x0, x1, y: g.append(f'<i class="lh" style="left:{x0}%;width:{x1 - x0}%;top:{y}mm"></i>')
    vl = lambda x, y0, y1, c='': g.append(f'<i class="lv{c}" style="left:{x}%;top:{y0}mm;height:{y1 - y0}mm"></i>')
    hl(MX, BUS, mids[1]); vl(BUS, mids[0], mids[2])
    for y in mids:
        hl(BUS, AX, y)
        g.append(f'<i class="ah" style="left:{AX}%;top:{y}mm"></i>')
    vl(76, bottom, ret, ' t'); g.append(f'<i class="lh t" style="left:17%;width:59%;top:{ret}mm"></i>')
    vl(17, m1, ret, ' t'); g.append(f'<i class="au" style="left:17%;top:{m1}mm"></i>')
    acts = ''.join(f'<div class="lact" style="--c:{a["colour"]};top:{tp}mm;height:{H}mm">{icon(a["icon"])}<div><b>{rich(a["name"], t)}</b>'
                   f'<span>{rich(a["text"], t)}</span></div></div>' for a, tp in zip(block['actions'], tops))
    m = block['model']
    stage = (f'<div class="lstage" style="height:{ret + 9}mm">{"".join(g)}'
             f'<div class="lmodel" style="--c:{m["colour"]};top:{m0}mm;height:{m1 - m0}mm;width:{MX}%"><b>Model</b><span>{rich(m["text"], t)}</span></div>'
             f'<span class="lcall" style="left:{MX}%;width:{BUS - MX}%;top:{mids[1] - 10.5}mm">tool call</span>'
             f'{acts}<span class="lret" style="top:{ret + 1.5}mm">{rich(block["return"], t)}</span></div>')
    owns = (f'<div class="lowns"><b>{html.escape(block["owns_label"])}</b>' + ''.join(f'<span style="--c:{c}">{html.escape(o)}</span>' for o, c in block['owns']) + '</div>'
            if block.get('owns') else '')
    return card('ploop', block, head(block, t) + stage + owns)


def psteps6(block, base, t):
    """The six parts of the loop side by side: what each harness does; candidate causes of the gap tinted."""
    cols = []
    for s in block['steps']:
        icon = f'<img src="{P.data_uri((base / s["icon"]).expanduser())}" alt="">' if s.get('icon') else ''
        cols.append(f'<div class="s6{" cand" if s.get("candidate") else ""}"><div class="s6h">{icon}<b>{html.escape(s["step"])}</b></div>'
                    f'<p><span class="who t2">T2</span>{rich(s["t2"], t)}</p>'
                    f'<p><span class="who cu">Custom</span>{rich(s["custom"], t)}</p></div>')
    key = '<span class="k"><i class="kcand"></i>Candidate cause of the gap, not a measured cause</span>'
    return card('psteps6', block, head(block, t) + f'<div class="pkey">{key}</div><div class="s6row">{"".join(cols)}</div>')


PLUGIN_BLOCKS.update({'pdumbbell': pdumbbell, 'psteps6': psteps6, 'ploop': ploop})


def pdiff(block, base, t):
    """Slide 11 on the poster: the shared setup as one strip, then each loop step as a row (what both share,
    Terminus 2, Custom), multi-item cells as bullets; candidate causes marked with an ochre edge."""
    compact = block.get('compact')
    bullets = (lambda text: '<li>' + ' · '.join(rich(x, t) for x in text.split('; ')) + '</li>') if compact else \
              (lambda text: ''.join(f'<li>{rich(x, t)}</li>' for x in text.split('; ')))
    setup = ''.join(f'<span><b>{html.escape(k)}:</b> {rich(v, t)}</span>' for k, v in block['setup'])
    rows = []
    for st in block['steps']:
        icon = f'<img src="{P.data_uri((base / st["icon"]).expanduser())}" alt="">' if st.get('icon') else ''
        rows.append(f'<div class="dfrow{" cand" if st.get("candidate") else ""}">'
                    f'<div class="dfstep">{icon}<div><b>{html.escape(st["step"])}</b><span>{html.escape(st["what"])}</span></div></div>'
                    + ('' if compact else f'<p class="dfsame">{rich(st["same"], t)}</p>') + f'<ul class="dft2">{bullets(st["t2"])}</ul>'
                    f'<ul class="dfcu">{bullets(st["ours"])}</ul></div>')
    key = '<span class="k"><i class="kcand2"></i>Candidate explanation for the gap, not a measured cause</span>'
    heads = ('<div class="dfrow dfhead"><b>Step</b>' + ('' if compact else '<b>Same in both</b>') + '<b class="h2">Terminus 2, the reference</b>'
             '<b class="hc">Custom, Revision 7 (LangGraph)</b></div>')
    top = (f'<p class="caption dfline">{rich(block["setup_line"], t)}</p>' if compact else f'<div class="dfsetup"><b>Shared setup</b>{setup}</div>')
    return card('pdiff' + (' compact' if compact else ''), block, head(block, t) + top
                + f'<div class="pkey">{key}</div>' + heads + ''.join(rows))


PLUGIN_BLOCKS['pdiff'] = pdiff


def ptrade(block, base, t):
    """Each loop step: what each harness does, then what it offers (green tick) and costs (red cross)."""
    yes = P.data_uri((base / block['yes']).expanduser()); no = P.data_uri((base / block['no']).expanduser())
    def side(d):
        tags = ''.join(f'<span class="tg"><img src="{yes if k == "offer" else no}" alt="{"offer" if k == "offer" else "cost"}">{rich(l, t)}</span>'
                       for l, k in d['tags'])
        return f'<div class="trs"><p>{rich(d["how"], t)}</p><div class="tgs">{tags}</div></div>'
    rows = []
    for st in block['steps']:
        icon = f'<img class="ti" src="{P.data_uri((base / st["icon"]).expanduser())}" alt="">' if st.get('icon') else ''
        rows.append(f'<div class="trrow{" cand" if st.get("candidate") else ""}"><div class="trstep">{icon}<b class="chip" style="--c:{st.get("colour", "#5A6370")}">{html.escape(st["step"])}</b></div>'
                    + side(st['t2']) + side(st['ours']) + '</div>')
    key = (f'<span class="k"><img src="{yes}" alt="">Offers</span><span class="k"><img src="{no}" alt="">Costs or risks</span>'
           '<span class="k"><i class="kcand2"></i>Candidate explanation for the gap, not a measured cause</span>')
    hi = lambda k: f'<img class="hi" src="{P.data_uri((base / block[k]).expanduser())}" alt="">' if block.get(k) else ''
    heads = (f'<div class="trrow trhead"><b>Step</b><b class="h2">{hi("t2_icon")}Terminus 2'
             '<span> · the benchmark’s reference harness</span></b>'
             f'<b class="hc">{hi("custom_icon")}Custom<span> · our LangGraph harness, Revision 7</span></b></div>')
    top = f'<p class="caption dfline">{rich(block["setup_line"], t)}</p>' if block.get('setup_line') else ''
    return card('ptrade', block, head(block, t) + top + f'<div class="pkey">{key}</div>' + heads + ''.join(rows))


def ptake(block, base, t):
    """The answer first: the key number, the verdict, and the next steps, in one dark band."""
    steps = ''.join(f'<li><i>{n}</i><span>{rich(x[0], t)}:<em>{rich(x[1], t)}</em></span></li>' if isinstance(x, list)
                    else f'<li><i>{n}</i><span>{rich(x, t)}</span></li>' for n, x in enumerate(block['next'], 1))
    return (f'<section class="block ptake" style="grid-column: span {block.get("span", 12)}">'
            f'<div class="tkfig"><b>{html.escape(block["value"])}</b><span>{rich(block["value_label"], t)}</span></div>'
            f'<div class="tkmain"><b>{rich(block["verdict"], t)}</b>' + ''.join(f'<span>{rich(x, t)}</span>' for x in block['lines']) + '</div>'
            f'<div class="tknext"><b>Next</b><ol>{steps}</ol></div></section>')


PLUGIN_BLOCKS.update({'ptrade': ptrade, 'ptake': ptake})


def pmatrix(block, base, t):
    """Slide 9 on the poster, one line per comparison: setup, the gap with its interval (a compact plot), solves, input
    ratio and cost per solve; the better value bold in its arm colour; the highlighted row tinted."""
    lo, hi = block['domain']
    x = lambda v: (max(lo, min(hi, v)) - lo) / (hi - lo) * 100
    col = {'t2': '#375A8C', 'ours': '#1F7A4F'}
    fmt = lambda v: '0.0' if v == 0 else f'{v:+.1f}'.replace('-', '−')
    def pair(vals, better, key):
        if not vals:
            return '<span class="mx2">—</span>'
        a, b = vals
        st = lambda arm: f' style="color:{col[arm]}{";font-weight:700" if better.get(key) == arm else ""}"'
        return f'<span class="mx2"><span{st("t2")}>{html.escape(a)}</span><span{st("ours")}>{html.escape(b)}</span></span>'
    rows = []
    for r in block['rows']:
        b = r.get('better', {})
        inp_style = f' style="color:{col[b["input"]]}"' if b.get('input') else ''
        rows.append(f'<div class="mxrow{" hl" if r.get("hl") else ""}"><span class="mxname"><b>{rich(r["name"], t)}</b>'
                    f'<span>{rich(r["short"], t)}</span></span>'
                    f'<b class="mxv" style="color:{"#375A8C" if r["gap"] < 0 else "#1F7A4F"}">{fmt(r["gap"])}</b>'
                    f'<span class="mxplot"><u style="left:{x(0):.2f}%"></u>'
                    + (f'<i style="left:{x(r["low"]):.2f}%;width:{x(min(r["high"], 0)) - x(r["low"]):.2f}%;background:#375A8C"></i>' if r["low"] < 0 else '')
                    + (f'<i style="left:{x(max(r["low"], 0)):.2f}%;width:{x(r["high"]) - x(max(r["low"], 0)):.2f}%;background:#3BBB75"></i>' if r["high"] > 0 else '')
                    + f'<em style="left:{x(r["gap"]):.2f}%;background:{"#375A8C" if r["gap"] < 0 else "#3BBB75"}"></em></span>'
                    f'<span class="mxci">[{fmt(r["low"])}, {fmt(r["high"])}]</span>'
                    + pair(r.get('solved'), b, 'solved') + f'<b class="mxin"{inp_style}>{html.escape(r["input"])}</b>'
                    + pair(r.get('per'), b, 'per') + '</div>')
    heads = ('<div class="mxrow mxhead"><b>Comparison</b><b class="r">Gap<span>pp</span></b><b class="c">Custom minus T2<span>95% interval</span></b><b></b>'
             '<b class="c">Solved<span>T2 · Custom</span></b><b class="c">Input<span>Custom ÷ T2</span></b>'
             '<b class="c">Cost per solve<span>T2 · Custom</span></b></div>')
    ticks = ''.join(f'<span style="left:{x(v):.2f}%">{html.escape(l)}</span>' for v, l in block['ticks'])
    return card('pmatrix', block, head(block, t) + heads + ''.join(rows)
                + (f'<p class="caption">{rich(block["caption"], t)}</p>' if block.get('caption') else ''))


def pmoved(block, base, t):
    """Small panels of paired bars: each panel a heading, rows of labelled bars with values, and a reading line."""
    panels = []
    for p in block['panels']:
        top = p['max']
        ref = (f'<u class="mvref" style="left:calc(var(--lw) + (100% - var(--lw) - var(--vw)) * {p["ref"] / top:.4f})"><span>{html.escape(p["ref_label"])}</span></u>'
               if p.get('ref') is not None else '')
        rows = ''.join(f'<div class="mvrow"><span class="mvl">{html.escape(l)}</span><span class="mvbar"><i style="width:{v / top * 100:.2f}%;background:{c}"></i></span>'
                       f'<b style="color:{c}">{html.escape(txt)}</b></div>' for l, v, txt, c in p['bars'])
        rows = f'<div class="mvrows">{ref}{rows}</div>'
        panels.append(f'<div class="mvpanel"><b class="mvh">{rich(p["title"], t)}</b><span class="mvu">{html.escape(p["unit"])}</span>{rows}'
                      f'<p class="caption">{rich(p["text"], t)}</p></div>')
    return card('pmoved', block, head(block, t) + f'<div class="mvpanels">{"".join(panels)}</div>')


PLUGIN_BLOCKS.update({'pmatrix': pmatrix, 'pmoved': pmoved})


def parrows(block, base, t):
    """Small panels of before-to-after arrows: each row a label, a start dot, an arrow to the end dot, both values;
    one shared scale per panel, an optional reference line."""
    panels = []
    for p in block['panels']:
        lo, hi = p['domain']
        X = lambda v: (v - lo) / (hi - lo) * 100
        rows = []
        for r in p['rows']:
            a, b = r['from'], r['to']
            c0, c1 = r.get('c0', '#BCC3CA'), r.get('c1', '#440154')
            left, right = min(X(a), X(b)), max(X(a), X(b))
            arrow = (f'<i class="ar" style="left:{left:.2f}%;width:{right - left:.2f}%;--c:{c1}" data-dir="{"r" if b >= a else "l"}"></i>'
                     if abs(b - a) > 1e-9 else '')
            rows.append(f'<div class="arow"><span class="al">{rich(r["label"], t)}</span><span class="ap">{arrow}'
                        f'<em style="left:{X(a):.2f}%;background:{c0}"></em><em style="left:{X(b):.2f}%;background:{c1}"></em></span>'
                        f'<span class="av"><span style="color:{c0}">{html.escape(r["a"])}</span> → <b style="color:{c1}">{html.escape(r["b"])}</b></span></div>')
        ref = f'<u class="aref" style="--x:{X(p["ref"]) / 100:.4f}"></u>' if p.get('ref') is not None else ''
        panels.append(f'<div class="apanel"><b class="ah">{rich(p["title"], t)}</b><span class="au">{rich(p["unit"], t)}</span>'
                      f'<div class="arows">{ref}{"".join(rows)}</div><p class="caption">{rich(p["text"], t)}</p></div>')
    limits = f'<p class="alimits">{rich(block["limits"], t)}</p>' if block.get('limits') else ''
    st = ' stacked' if block.get('stacked') else ''
    return card('parrows' + st, block, ('' if block.get('stacked') else head(block, t)) + f'<div class="apanels">{"".join(panels)}</div>' + limits)


PLUGIN_BLOCKS['parrows'] = parrows


def ptrap(block, base, t):
    """Text-to-SQL poster (22 November 2026): the 21 % trap. One question, the SQL the model wrote with the lines a
    completed-revenue question adds, and the two revenue figures on one scale, the gap marked."""
    code = ''.join(f'<div class="tl{" add" if add else ""}">{html.escape(line)}</div>' for line, add in block['code'])
    top = max(b['value'] for b in block['bars'])
    bars = ''.join(
        f'<div class="tbar"><span class="tlab">{rich(b["label"], t)}</span><span class="ttrack">'
        f'<span class="tfill" style="width:{b["value"] / top * 100:.2f}%;background:{b["colour"]}"><b>{html.escape(b["text"])}</b></span>'
        + (f'<span class="tgap" style="width:{(top - b["value"]) / top * 100:.2f}%">{rich(b["gap"], t)}</span>' if b.get('gap') else '')
        + '</span></div>' for b in block['bars'])
    return (f'<section class="block card ptrap" style="grid-column: span {block.get("span", 12)}" data-role="{block.get("role", "blue")}">'
            f'{head(block, t)}<p class="tq">{rich(block["question"], t)}</p>'
            f'<div class="tcode"><span class="tct">{html.escape(block["code_title"])}</span>{code}</div>'
            f'<div class="tbars">{bars}</div><p class="caption">{rich(block["caption"], t)}</p></section>')


PLUGIN_BLOCKS['ptrap'] = ptrap


def pwaffle(block, base, t):
    """Text-to-SQL poster: one square per item, the counted ones in colour, a big number beside it."""
    n, k, per = block['total'], block['count'], block.get('per_row', 38)
    cells = ''.join(f'<i style="background:{block["colour"] if i < k else "#D8DEE3"}"></i>' for i in range(n))
    return (f'<section class="block card pwaffle" style="grid-column: span {block.get("span", 4)}" data-role="{block.get("role", "blue")}">'
            f'{head(block, t)}<div class="wtop"><b>{html.escape(block["value"])}</b><span>{rich(block["label"], t)}</span></div>'
            f'<div class="wgrid" style="grid-template-columns: repeat({per}, 1fr)">{cells}</div>'
            f'<p class="caption">{rich(block["caption"], t)}</p></section>')


def pcols(block, base, t):
    """Text-to-SQL poster: vertical columns, each with its own colour, value on top and label below; optional groups."""
    top = block.get('max') or max(c['value'] for c in block['cols'])
    cols = ''.join(
        f'<div class="pc{" gap" if c.get("gap_before") else ""}"><b>{html.escape(c["text"])}</b>'
        f'<span class="pbar" style="height:{c["value"] / top * 100:.1f}%;background:{c["colour"]}"></span>'
        f'<em>{rich(c["label"], t)}</em></div>' for c in block['cols'])
    legend = ''.join(f'<span class="sw" style="background:{c}"></span><span>{html.escape(l)}</span>' for c, l in block.get('legend', []))
    return (f'<section class="block card pcols" style="grid-column: span {block.get("span", 4)}" data-role="{block.get("role", "plum")}">'
            f'{head(block, t)}' + (f'<div class="plegend">{legend}</div>' if legend else '')
            + f'<div class="pcrow">{cols}</div><p class="caption">{rich(block["caption"], t)}</p></section>')


PLUGIN_BLOCKS.update({'pwaffle': pwaffle, 'pcols': pcols})


K = 4 / 3   # px per pt: chart geometry is given in pt and drawn in px, so text sizes read as their pt level


def _svgtext(x, y, s, size=18, colour='#1B2430', weight=400, anchor='start'):
    return (f'<text x="{x * K:.1f}" y="{y * K:.1f}" font-size="{size * K:.2f}" font-weight="{weight}" fill="{colour}" '
            f'text-anchor="{anchor}" font-family="Google Sans">{html.escape(s)}</text>')


def pslope(block, base, t):
    """Text-to-SQL poster: a slope chart. Each series is a line between two (or more) named points on one scale;
    labels at both ends; an optional note where lines cross. Drawn as SVG in poster points."""
    W, H = block.get('w', 520), block.get('h', 230)
    lo, hi = block['scale']
    pad_l, pad_r, pad_t, pad_b = block.get('pad', (150, 150, 30, 36))
    xs = [pad_l + i * (W - pad_l - pad_r) / (len(block['points']) - 1) for i in range(len(block['points']))]
    Y = lambda v: pad_t + (hi - v) / (hi - lo) * (H - pad_t - pad_b)
    out = [f'<line x1="{x:.1f}" y1="{pad_t - 6}" x2="{x:.1f}" y2="{H - pad_b + 4}" stroke="#D8DEE3" stroke-width="1.5"/>' for x in xs]
    out += [_svgtext(x, H - 8, p, 18, '#5A6370', 700, 'middle') for x, p in zip(xs, block['points'])]
    for s in block['series']:
        pts = [(x, Y(v)) for x, v in zip(xs, s['values'])]
        out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{s["colour"]}" stroke-width="{s.get("width", 5)}"/>')
        out += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{s["colour"]}"/>' for x, y in pts]
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        out.append(_svgtext(x0 - 14, y0 + 6, s['start'], 20, s['colour'], 700, 'end'))
        out.append(_svgtext(x1 + 14, y1 + 6, s['end'], 20, s['colour'], 700, 'start'))
        for (x, y), m in zip(pts[1:-1], s.get('mids', [])):
            out.append(_svgtext(x, y - 16, m, 20, s['colour'], 700, 'middle'))
    if block.get('note'):
        nx, ny, txt = block['note']
        out.append(_svgtext(nx, ny, txt, 18, '#B8452E', 700, 'middle'))
    shapes = ''.join(o for o in out if not o.startswith('<text'))
    texts = ''.join(o for o in out if o.startswith('<text'))
    svg = (f'<svg viewBox="0 0 {W * K:.1f} {H * K:.1f}" width="{W * K:.1f}px" height="{H * K:.1f}px">'
           f'<g transform="scale({K:.6f})">{shapes}</g>{texts}</svg>')
    legend = ''.join(f'<span class="sw" style="background:{s["colour"]}"></span><span>{html.escape(s["name"])}</span>' for s in block['series'] if s.get('name'))
    return (f'<section class="block card pslope" style="grid-column: span {block.get("span", 6)}" data-role="{block.get("role", "plum")}">'
            f'{head(block, t)}' + (f'<div class="plegend">{legend}</div>' if legend else '')
            + f'<div class="sframe">{svg}</div><p class="caption">{rich(block["caption"], t)}</p></section>')


def pdots(block, base, t):
    """Text-to-SQL poster: one row per item, a dot on a shared scale; dot area sized by a second measure (tokens)."""
    W = block.get('w', 520)
    rows = block['rows']
    lo, hi = block['scale']
    lab, right = block.get('label_w', 170), block.get('right_w', 120)
    rh = block.get('row_h', 54)
    H = rh * len(rows) + 34
    X = lambda v: lab + (v - lo) / (hi - lo) * (W - lab - right)
    out = []
    for tick in block.get('ticks', []):
        out.append(f'<line x1="{X(tick):.1f}" y1="6" x2="{X(tick):.1f}" y2="{H - 26}" stroke="#D8DEE3" stroke-width="1.2"/>')
        out.append(_svgtext(X(tick), H - 6, f'{tick:g}{block.get("unit", "")}', 18, '#5A6370', 400, 'middle'))
    smax = max(r['size'] for r in rows)
    for i, r in enumerate(rows):
        y = 10 + rh * i + rh / 2
        rad = 6 + 20 * (r['size'] / smax) ** .5
        out.append(f'<line x1="{lab}" y1="{y:.1f}" x2="{X(r["value"]):.1f}" y2="{y:.1f}" stroke="{r["colour"]}" stroke-width="2" stroke-dasharray="4 4"/>')
        out.append(f'<circle cx="{X(r["value"]):.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{r["colour"]}" fill-opacity=".85"/>')
        out.append(_svgtext(lab - 12, y + 6, r['label'], 20, '#1B2430', 700 if r.get('bold') else 400, 'end'))
        out.append(_svgtext(W - right + 10, y + 6, r['text'], 20, '#1B2430', 700, 'start'))
    shapes = ''.join(o for o in out if not o.startswith('<text'))
    texts = ''.join(o for o in out if o.startswith('<text'))
    svg = (f'<svg viewBox="0 0 {W * K:.1f} {H * K:.1f}" width="{W * K:.1f}px" height="{H * K:.1f}px">'
           f'<g transform="scale({K:.6f})">{shapes}</g>{texts}</svg>')
    return (f'<section class="block card pdots" style="grid-column: span {block.get("span", 6)}" data-role="{block.get("role", "plum")}">'
            f'{head(block, t)}<div class="sframe">{svg}</div><p class="caption">{rich(block["caption"], t)}</p></section>')


PLUGIN_BLOCKS.update({'pslope': pslope, 'pdots': pdots})
