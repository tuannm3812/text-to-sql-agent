"""Build the Text-to-SQL Agent A1 portrait poster on the UTS poster template (22 November 2026) and render it with the
deck-kit poster engine, plus a 6000-pixel PNG for LinkedIn.

  python poster/make_poster.py --render

Same story as the deck: one store manager's question, how the app answers it, what was measured, and what is next.
Every number comes from the deck and ../claims-register.md. Charts are drawn natively by the engine, never slide
screenshots; the flowchart is the deck's rendered appendix figure (make_flow.py).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = Path.home() / 'Documents/GitHub/deck-kit'
PY = KIT / '.venv/bin/python'
I = '../assets/icons/'
L = '../assets/logos/'


def divider(label):
    return {'type': 'divider', 'label': label, 'span': 12}


SPEC = {
    'eyebrow': '36121 Artificial Intelligence Principles and Applications | Capstone project',
    'title': 'Ask your data. Inspect the answer.',
    'subtitle': 'Can a text-to-SQL agent give a store manager a fast answer she can check, without risking her data?',
    'authors': 'Manh Tuan (Mike) Nguyen · TD School, University of Technology Sydney',
    'logo': '../assets/brand/uts-logo.svg',
    'css': 'uts_poster.css',
    'plugin': 'uts_poster_blocks.py',
    'footer': '**Text-to-SQL Agent**  ·  Manh Tuan (Mike) Nguyen',
    'strict': True,
    'size': 'A1',
    'columns': 12,
    'landscape': False,
    'scale': {'title': 64, 'subtitle': 26, 'eyebrow': 20, 'figure': 48, 'heading': 28, 'body': 22, 'caption': 18,
              'marker': 24, 'margin_mm': 18, 'gap_mm': 5},
}

TAKE = {'type': 'ptake', 'span': 12, 'value': '173,366',
        'value_label': 'her answer in seconds, with the SQL behind it',
        'verdict': 'Read-only and inspectable; a person still checks the meaning',
        'lines': ['The SQL comes with every answer; **45 of 45** read-only tests passed. About **one answer in three** still did not match on Spider.'],
        'next': [['Definitions', 'one meaning of revenue'],
                 ['Table recovery', '128 missed-table questions'],
                 ['New schemas', 'and a hosted model']]}

PROBLEM = [
    {'type': 'photo', 'span': 3, 'image': '../assets/figures/photo-shop-wide.jpg',
     'alt': 'Interior of a small shop with wooden shelves (photograph).',
     },
    {'type': 'checks', 'span': 6, 'role': 'slate', 'columns': 1, 'compact': True,
     'heading': 'Her question is simple; **a trustworthy answer is not**',
     'items': [
         {'question': 'Her question', 'icon': I + 'chat-ink.png', 'role': 'slate',
          'text': '“Which product categories generate the most revenue?”',
          'action': 'She knows the business, not SQL; the data sits in an 11-table database.'},
         {'question': 'Her options today', 'icon': I + 'timer-ink.png', 'role': 'slate',
          'text': 'Wait about **three days** for an analyst, or **weeks** for a curated tool to be set up.',
          'action': 'Or learn the schema and SQL herself.'},
         {'question': 'What she needs', 'icon': I + 'check_circle-ink.png', 'role': 'slate',
          'text': 'An answer **today**, the **SQL behind it** so she can check it, and her data **never changed**.',
          'action': 'Other tools pay for meaning in setup; this project pays in **review**.'},
         {'question': 'Who else it serves', 'icon': I + 'person-ink.png', 'role': 'slate',
          'text': 'Managers new to a database, **privacy-sensitive** teams and teams with **large schemas**.',
          'action': 'Not for metrics that must match across teams.'},
         ]},
    {'type': 'pslope', 'span': 3, 'role': 'slate', 'scale': [0, 100], 'w': 300, 'h': 230, 'pad': (78, 78, 34, 34),
     'heading': 'Why it is hard: **scores fall** on real tasks',
     'points': ['Spider', 'BIRD', 'Spider 2.0'],
     'series': [{'values': [91.2, 73.0, 21.3], 'colour': '#440154', 'start': '91.2 %', 'end': '21.3 %', 'mids': ['73.0 %']}],
     'caption': 'Tasks solved, Spider 2.0 paper; “revenue” is not a column.'},
]

HOW = [
    {'type': 'figure', 'span': 7, 'role': 'blue', 'image': '../assets/figures/flowchart.png',
     'heading': 'One question’s path: **one model call**, two gates in code',
     'alt': 'Flowchart of the app in four stage lanes: prepare, generate, check and run, answer.',
     'caption': 'Yellow is the model, teal is enforced in code. Only **79 of 608** stored values reach the model, never result rows; **45 of 45** read-only tests passed on 3 engines.'},
    {'type': 'ptrap', 'span': 5, 'role': 'blue',
     'heading': 'The **21 % trap**: why she needs the SQL',
     'question': '“Which product categories generate the most revenue?”',
     'code_title': 'The SQL, and what “completed revenue” adds',
     'code': [['SELECT category, SUM(unit_price * quantity', False], ['+   * (1 - discount_pct)', True],
              ['FROM order_items JOIN products ...', False], ['+ JOIN orders ...', True],
              ["+ WHERE order_status = 'Completed'", True], ['GROUP BY category', False]],
     'bars': [{'label': 'All orders, list price', 'value': 173366, 'text': '173,366', 'colour': '#21918C'},
              {'label': 'Completed, discounted', 'value': 136984, 'text': '136,984', 'colour': '#3B528B',
               'gap': '21 % lower'}],
     'caption': 'Electronics revenue: all **220** orders, or the **179** completed ones after discounts. Neither is wrong: the SQL shows the choice, and **she decides**.'},
]

EVIDENCE = [
    {'type': 'pdots', 'span': 3, 'role': 'plum', 'scale': [24, 30], 'ticks': [24, 27, 30], 'unit': ' %',
     'w': 330, 'label_w': 120, 'right_w': 66, 'row_h': 62,
     'heading': 'Large databases: **fewer tables** scored higher',
     'rows': [{'label': 'All + hints', 'value': 25.5, 'size': 8501, 'text': '25.5 %', 'colour': '#ADB5BD'},
              {'label': 'Every table', 'value': 26.8, 'size': 6221, 'text': '26.8 %', 'colour': '#ADB5BD'},
              {'label': 'Top 6', 'value': 29.1, 'size': 2670, 'text': '29.1 %', 'colour': '#21918C', 'bold': True}],
     'caption': 'Dot area is prompt size: **8,501**, **6,221**, **2,670** tokens. **+3.6 [+1.4, +5.8]**, about 2 s slower.'},
    {'type': 'pwaffle', 'span': 3, 'role': 'plum', 'total': 608, 'count': 79, 'colour': '#21918C', 'per_row': 32,
     'heading': 'What the model saw of **her shop**',
     'value': '79 of 608', 'label': 'stored text values',
     'caption': 'One square per distinct stored value; **no result row** ever reaches the model.'},
    {'type': 'pdots', 'span': 3, 'role': 'plum', 'scale': [30, 90], 'ticks': [30, 60, 90], 'unit': ' %',
     'w': 330, 'label_w': 104, 'right_w': 70, 'row_h': 46,
     'heading': '**64.6 %** Spider, **35.2 %** BIRD',
     'rows': [{'label': 'Easy', 'value': 84.3, 'size': 248, 'text': '84.3 %', 'colour': '#5EC962'},
              {'label': 'Medium', 'value': 65.9, 'size': 446, 'text': '65.9 %', 'colour': '#21918C'},
              {'label': 'Hard', 'value': 58.6, 'size': 174, 'text': '58.6 %', 'colour': '#3B528B'},
              {'label': 'Extra hard', 'value': 38.0, 'size': 166, 'text': '38.0 %', 'colour': '#440154'}],
     'caption': 'Spider by difficulty; dot area is questions (248, 446, 174, 166).'},
    {'type': 'pslope', 'span': 3, 'role': 'plum', 'scale': [0, 36], 'w': 330, 'h': 240, 'pad': (76, 76, 16, 32),
     'heading': 'A dropped table: **the lines cross**',
     'points': ['All sent', 'One dropped'],
     'series': [{'name': 'Top 6', 'values': [32.9, 5.4], 'colour': '#21918C', 'start': '32.9 %', 'end': '5.4 %'},
                {'name': 'Every table', 'values': [26.7, 18.0], 'colour': '#ADB5BD', 'start': '26.7 %', 'end': '18.0 %'}],
     'caption': 'Answers matched on 1,055 and 167 questions.'},
]

NEXT = [
    {'type': 'checks', 'span': 12, 'role': 'ochre', 'columns': 4, 'compact': True,
     'heading': 'One answer in three is still wrong, and follow-ups and real schemas are untested: **four tests** come first',
     'items': [
         {'question': 'Business definitions', 'icon': I + 'menu_book-ink.png', 'role': 'ochre',
          'text': 'Revenue stays ambiguous.', 'action': 'Carry a definitions layer?'},
         {'question': 'Targeted table recovery', 'icon': I + 'schema-ink.png', 'role': 'ochre',
          'text': '**128** questions miss a table.', 'action': 'Does recovery keep its gains?'},
         {'question': 'New large schemas', 'icon': I + 'table_rows-ink.png', 'role': 'ochre',
          'text': 'The gain is from **2 of 4** databases.', 'action': 'Top 6 at every size?'},
         {'question': 'A hosted model', 'icon': I + 'chat-ink.png', 'role': 'ochre',
          'text': 'All results use **one local model**.', 'action': 'Worth sending it the prompt?'}]},
    {'type': 'band', 'span': 12, 'tone': 'ink',
     'text': '**A first, checkable answer** for people who know the question but not the schema.',
     'qr': 'https://aipa-text-to-sql-agent.streamlit.app', 'qr_label': 'Try the live demo'},
]


def highlights(block):
    """The engine's own blocks take highlight phrases, not **bold**: convert, and recurse into stacks."""
    import re
    if block.get('type') == 'stack':
        for b in block['blocks']:
            highlights(b)
    h = block.get('heading')
    if h and block['type'] not in ('ptake',) and '**' in h:
        block['highlight'] = re.findall(r'\*\*(.+?)\*\*', h)
        block['heading'] = h.replace('**', '')
    return block


def portrait():
    spec = dict(SPEC)
    spec['blocks'] = ([TAKE, divider('The problem')] + PROBLEM + [divider('How it works')] + HOW
                      + [divider('What we measured')] + EVIDENCE + [divider('What is next')] + NEXT)
    spec['blocks'] = [highlights(b) for b in spec['blocks']]
    return spec


def stack(span, blocks):
    return {'type': 'stack', 'span': span, 'blocks': blocks}


def landscape():
    """A1 landscape: the answer band, then problem | how it works | what we measured in three columns, then next."""
    import copy
    spec = dict(SPEC)
    spec['landscape'] = True
    # landscape stylesheet: the portrait one plus a figure that shrinks to its row
    (HERE / 'uts_poster_land.css').write_text((HERE / 'uts_poster.css').read_text() + '''
/* landscape only: the flowchart scales to the row height instead of pushing the row taller */
.figure { display: flex; flex-direction: column; }
.figure .frame { flex: 1 1 0; min-height: 0; display: flex; justify-content: center; }
.figure .frame img { height: 100%; width: auto; max-width: 100%; object-fit: contain; }
''')
    spec['css'] = 'uts_poster_land.css'
    P, H, E, N = (copy.deepcopy(x) for x in (PROBLEM, HOW, EVIDENCE, NEXT))
    for b in P + H + E:
        b['span'] = 12
    N[0]['span'], N[0]['columns'] = 12, 4
    P[1]['span'], H[0]['span'], H[1]['span'] = 3, 5, 4
    P[1]['items'] = [dict(i) for i in P[1]['items'][:3]]
    P[1]['items'][2]['action'] = ''
    H[0]['caption'] = 'Yellow is the model; teal is enforced in code.'
    P[0]['span'], P[2]['span'] = 2, 2
    for e in E:
        e['span'] = 2
    N[0]['span'], N[1]['span'] = 8, 4
    spec['blocks'] = [highlights(b) for b in [
        TAKE, divider('Her question, and how the app answers it'), P[1], H[0], H[1],
        divider('Why it is hard, and what we measured'), P[0], P[2], E[0], E[1], E[2], E[3],
        divider('What is next'), N[0], N[1]]]
    return spec


def render(name, spec):
    path = HERE / f'{name}.json'
    path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')
    out = HERE / 'output'
    out.mkdir(exist_ok=True)
    pdf = out / f'{name}.pdf'
    run = subprocess.run([str(PY), '-m', 'deck_kit.poster', '--project', str(HERE / 'poster-kit.json'),
                          '--spec', str(path), '--out', str(pdf), '--html', str(out / f'{name}.html')],
                         cwd=KIT, capture_output=True, text=True)
    print(name, run.stdout.strip(), run.stderr.strip()[-1500:])
    if run.returncode == 0:
        dpi = round(6000 / (841 / 25.4))   # the long side is 841 mm in both orientations
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', str(pdf), str(out / f'{name}-linkedin')],
                       check=True)
    return run.returncode


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--render', action='store_true')
    args = ap.parse_args()
    codes = []
    for name, make in (('poster-portrait', portrait), ('poster-landscape', landscape)):
        spec = make()
        if args.render:
            codes.append(render(name, spec))
        else:
            (HERE / f'{name}.json').write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')
    sys.exit(max(codes or [0]))
