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
    'footer': '**Text-to-SQL Agent**  ·  github.com/tuannm3812/text-to-sql-agent',
    'strict': True,
    'size': 'A1',
    'columns': 12,
    'landscape': False,
    'scale': {'title': 64, 'subtitle': 26, 'eyebrow': 20, 'figure': 48, 'heading': 28, 'body': 22, 'caption': 18,
              'marker': 24, 'margin_mm': 18, 'gap_mm': 5},
}

TAKE = {'type': 'ptake', 'span': 12, 'value': '+3.6 pts',
        'value_label': 'top 6 tables against every table,<br>on 21- to 65-table databases',
        'verdict': 'Read-only and inspectable; a person still checks the meaning',
        'lines': ['The SQL comes with every answer; **45 of 45** read-only tests passed. About **one answer in three** still did not match on Spider.'],
        'next': [['Definitions', 'one meaning of revenue'],
                 ['Table recovery', '128 missed-table questions'],
                 ['New schemas', 'and a hosted model']]}

PROBLEM = [
    {'type': 'photo', 'span': 4, 'image': '../assets/figures/photo-shop.jpg',
     'alt': 'Interior of a small shop with wooden shelves (photograph).',
     'credit': 'Photo: Steffen Mokosch, Wikimedia Commons, CC BY-SA 4.0, cropped. The store manager is an illustrative persona.'},
    {'type': 'checks', 'span': 8, 'role': 'slate', 'columns': 2, 'compact': True,
     'heading': 'A store manager asks: **which product categories generate the most revenue?**',
     'items': [
         {'question': 'Her options today', 'icon': I + 'timer-ink.png', 'role': 'slate',
          'text': 'Wait about **three days** for an analyst, learn the schema and SQL herself, or wait weeks for a curated tool.',
          'action': 'Published scores fall from **91.2 %** on Spider 1.0 to **21.3 %** on enterprise tasks: a good demo is not evidence.'},
         {'question': 'What she needs', 'icon': I + 'check_circle-ink.png', 'role': 'slate',
          'text': 'An answer **today**, the **SQL behind it** so she can check it, and her data **never changed**.',
          'action': 'Other tools pay for meaning in setup; this project pays in **review**.'},
         {'question': 'Why it is hard', 'icon': I + 'help-ink.png', 'role': 'slate',
          'text': 'Words like “revenue” are not columns; real schemas can exceed **1,000** columns.',
          'action': 'And generated SQL runs on real data, so it must never change it.'},
         {'question': 'Who else it serves', 'icon': I + 'person-ink.png', 'role': 'slate',
          'text': 'Managers new to a database, privacy-sensitive teams and teams with large schemas.',
          'action': 'Not for metrics that must match across teams.'}]},
]

HOW = [
    {'type': 'figure', 'span': 8, 'role': 'blue', 'image': '../assets/figures/flowchart.png',
     'heading': 'One question’s path: **one model call**, two gates in code, then back to her',
     'alt': 'Flowchart of the app in four stage lanes: prepare, generate, check and run, answer.',
     'caption': 'Stages left to right, steps top to bottom. Yellow is the model, teal is enforced in code.'},
    {'type': 'key_figures', 'span': 4, 'direction': 'rows', 'items': [
        {'heading': 'Her answer', 'icon': I + 'check_circle-ink.png', 'value': '173,366', 'role': 'blue',
         'label': 'Electronics; the SQL shows it counts **all 220 orders**.'},
        {'heading': 'What the model saw', 'icon': I + 'fact_check-ink.png', 'value': '79 of 608', 'role': 'blue',
         'label': 'stored values; **result rows never**.'},
        {'heading': 'Read-only, tested', 'icon': I + 'verified_user-ink.png', 'value': '45 of 45', 'role': 'blue',
         'label': 'tests passed on **3 engines**.'}]},
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
    {'type': 'checks', 'span': 12, 'role': 'ochre', 'columns': 4, 'compact': True,
     'heading': 'Four tests would close the main gaps before any default changes',
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
