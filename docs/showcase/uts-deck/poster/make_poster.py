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
    {'type': 'photo', 'span': 4, 'image': '../assets/figures/photo-shop-wide.jpg',
     'alt': 'Interior of a small shop with wooden shelves (photograph).',
     'credit': 'Photo: Steffen Mokosch, CC BY-SA 4.0. An illustrative persona.'},
    {'type': 'checks', 'span': 8, 'role': 'slate', 'columns': 2, 'compact': True,
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
         {'question': 'Why it is hard', 'icon': I + 'help-ink.png', 'role': 'slate',
          'text': 'Published scores fall from **91.2 %** on Spider 1.0 to **21.3 %** on enterprise tasks.',
          'action': '“Revenue” is not a column: meaning is the hard part.'},
         ]},
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
    {'type': 'hbars', 'span': 6, 'role': 'plum',
     'heading': 'Local 9B model: **64.6 %** on Spider, **35.2 %** on BIRD',
     'items': [{'label': 'Spider dev', 'value': 64.6, 'text': '**64.6 %** of 1,034', 'highlight': True},
               {'label': 'BIRD dev', 'value': 35.2, 'text': '**35.2 %** of 1,534, with evidence', 'highlight': True},
               {'label': 'Demo suite', 'value': 33.3, 'text': '**4 of 12**: too small to judge'}],
     'caption': 'Answers matching the reference rows; this project’s scorer, not leaderboard scoring.'},
    {'type': 'hbars', 'span': 6, 'role': 'plum',
     'heading': 'On large databases, **fewer tables scored higher**',
     'items': [{'label': 'Every table + hints', 'value': 25.5, 'text': '**25.5 %**, 8,501 tokens'},
               {'label': 'Every table', 'value': 26.8, 'text': '**26.8 %**, 6,221 tokens'},
               {'label': 'Top 6 + neighbours', 'value': 29.1, 'text': '**29.1 %**, 2,670 tokens', 'highlight': True}],
     'caption': '1,222 questions: **+3.6 [+1.4, +5.8]**, about 2 s slower. A dropped table cut top 6 to **5.4 %**; five later trials added no accuracy.'},
]

NEXT = [
    {'type': 'checks', 'span': 12, 'role': 'ochre', 'columns': 2, 'compact': True,
     'heading': 'What the store manager should know **before she trusts it**',
     'items': [
         {'question': 'Measured limits', 'icon': I + 'cancel-ink.png', 'role': 'ochre',
          'text': 'About **one answer in three** did not match on Spider; **nothing checks meaning**.',
          'action': 'A missed table usually means a wrong answer; table selection is about **2 s** slower.'},
         {'question': 'Not yet tested', 'icon': I + 'help-ink.png', 'role': 'ochre',
          'text': '**Follow-up questions**, other languages, and **real company schemas** of hundreds of tables.',
          'action': 'No user study yet, and running cost is not measured.'}]},
    {'type': 'checks', 'span': 12, 'role': 'ochre', 'columns': 4, 'compact': True,
     'heading': 'About one answer in three is still wrong: **four tests** come before any default changes',
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
        dpi = round(6000 / (841 / 25.4))
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', str(pdf), str(out / f'{name}-linkedin')],
                       check=True)
    return run.returncode


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--render', action='store_true')
    args = ap.parse_args()
    spec = portrait()
    if args.render:
        sys.exit(render('poster-portrait', spec))
    (HERE / 'poster-portrait.json').write_text(json.dumps(spec, indent=2, ensure_ascii=False) + '\n')
