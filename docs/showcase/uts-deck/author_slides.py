"""Write slides 4-19 of brief-content.json (batch 2, 18 November 2026).

Wording and numbers come from the live Google deck's bodies (docs/showcase/slides/build_body_slides.py) and its
notes (docs/showcase/speaker-notes.md). Slides 1-3 (cover, summary, why it is hard) are kept as they are.
Run: python3 author_slides.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = ['sources.md', 'claims-register.md']


def notes(purpose, *script):
    return {'purpose': purpose, 'script': list(script), 'references': REF}


def src(label, path='README.md'):
    url = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/' + path
    return {'label': label, 'url': url}


W5 = [150, 150, 150, 150, 135.5, 140]
other_tools = {
    'id': 'tools', 'layout': 'tools_page', 'section': 'Problem', 'topic': 'Other tools', 'accent': 'slate',
    'title': 'Other tools get business meaning through setup',
    'subtitle': 'Two routes to meaning, compared on the same criteria; sources read 6 November 2026',
    'columns': [['Approach', 190], ['Source of meaning', 150], ['Setup¹', 130], ['Upkeep¹', 130], ['Best for', 135.5], ['Risk', 140]],
    'row_height': 31,
    'rows': [
        {'band': 'People define the meaning', 'accent': 'slate'},
        {'logo': 'assets/logos/snowflake.png', 'url': 'https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst', 'cells': ['Snowflake Cortex Analyst', '**Semantic view**', [2, 'Define the view'], [2, 'Refine with evaluations'], {'mark': 'tick', 'items': ['**Agreed metrics**', 'Teams already on Snowflake']}, {'mark': 'cross', 'items': ['**Stale definitions**', 'Upkeep as metrics change']}]},
        {'logo': 'assets/logos/databricks.png', 'url': 'https://docs.databricks.com/en/genie/best-practices.html', 'cells': ['Databricks Genie Agents', '**SQL expressions**, example SQL', [3, 'Expert curation'], [2, 'Iterate with feedback'], {'mark': 'tick', 'items': ['**One topic** and audience', 'Curated example SQL']}, {'mark': 'cross', 'items': ['Depends on the **curator**', 'Advises five or fewer tables']}]},
        {'logo': 'assets/logos/wren.png', 'url': 'https://github.com/Canner/WrenAI', 'cells': ['WrenAI', '**Semantic layer** in Git', [2, 'Define the MDL model'], [2, 'Review in Git'], {'mark': 'tick', 'items': ['**Versioned** definitions', 'Open-source engine']}, {'mark': 'cross', 'items': ['**Unmodelled** data', 'Some features commercial']}]},
        {'band': 'Systems work it out', 'accent': 'blue'},
        {'logo': 'assets/logos/vanna.png', 'url': 'https://github.com/vanna-ai/vanna', 'cells': ['Vanna', '**Saved past queries**', [1, 'Learns from use'], [2, 'Self-maintained'], {'mark': 'tick', 'items': ['**Repeated** questions', 'Learns from saved queries']}, {'mark': 'cross', 'items': ['Repeats **past errors**', 'Repository archived³']}]},
        {'logo': 'assets/icons/monitoring-ink.png', 'url': 'https://bird-bench.github.io/', 'cells': ['BIRD leaderboard systems', 'Mostly **not listed**', [None, 'Not listed'], [None, 'Not listed'], {'mark': 'tick', 'items': ['**Benchmark** scores', 'Top test entry 83.40 %²']}, {'mark': 'cross', 'items': ['**Transfer** unproven', 'Methods rarely listed']}]},
        {'logo': 'assets/icons/fact_check-teal.png', 'url': 'https://github.com/tuannm3812/text-to-sql-agent', 'ours': True, 'cells': ['This project', '**Schema** and **bounded hints**', [0, 'Connect only'], [0, 'None'], {'mark': 'tick', 'items': ['A **first look** at a database', 'SQL shown, run read-only']}, {'mark': 'cross', 'items': ['A **person checks** the meaning', 'No governed metrics']}]},
    ],
    'note': '¹ Setup and upkeep are our reading of each tool’s documentation, read 6 November 2026, not a ranking. ² AskData, the top BIRD test entry; humans score 92.96 %. ³ Archived on 29 March 2026.',
    'takeaway': 'Other tools pay for meaning in setup and upkeep. **This project pays in review**: a person checks what each answer means.',
    'notes': notes('Place the project among the tools that already exist.',
        'Other tools reach business meaning through setup. [Point: People define the meaning] Snowflake says schemas lack business definitions, so people add them in a semantic view. Databricks has a domain expert curate SQL expressions and example SQL. WrenAI keeps its semantic layer in Git.',
        '[Point: Upkeep column] That work does not end: Snowflake tells teams to refine with evaluations, and Databricks calls curation iterative.',
        '[Point: Systems work it out] Vanna saves past queries and learns from use, though its repository was archived in March 2026. The top BIRD test score is 83.40 %, still below 92.96 % for humans.',
        '[Point: This project] This project only needs a database connection, so it pays in the last column: a person checks what each answer means.',
        'Reference: Snowflake Cortex Analyst docs, Databricks Genie best practices, WrenAI and Vanna repositories, BIRD leaderboard, all read 6 November 2026 (S1 to S5).'),
}

aim = {
    'id': 'aim', 'layout': 'aim_page', 'section': 'Problem', 'topic': 'Our aim', 'accent': 'slate',
    'title': 'Our aim: useful without setup, and checkable by default',
    'subtitle': 'A narrower tool: no curated semantic model, with the checking in the user’s hands',
    'promises': [
        {'title': 'Useful without setup', 'text': 'Connect a database and ask a question.', 'icon': 'query_stats', 'marker': 1},
        {'title': 'Checkable by default', 'text': 'SQL shown, validated and run read-only.', 'icon': 'fact_check'},
    ],
    'quadrants': [['Meaning without setup: the ideal', 'Not yet available.'], 'Meaning through setup: curated tools',
                  'Quick start: people check the meaning', ['Setup without meaning: to avoid', 'Effort spent, but meaning still left to the reader.']],
    'y_axis': '↑ Business meaning built in',
    'x_axis': 'Setup before the first useful answer¹ →',
    'points': [
        {'label': 'BI dashboards', 'x': 0.8, 'y': 0.9, 'art': 'assets/icons/monitoring-ink.png'},
        {'label': 'Databricks Genie Agents', 'x': 0.66, 'y': 0.7, 'art': 'assets/logos/databricks.png'},
        {'label': 'Snowflake Cortex Analyst', 'x': 0.55, 'y': 0.8, 'art': 'assets/logos/snowflake.png'},
        {'label': 'WrenAI', 'x': 0.58, 'y': 0.6, 'art': 'assets/logos/wren.png'},
        {'label': 'Vanna', 'x': 0.3, 'y': 0.3, 'art': 'assets/logos/vanna.png'},
        {'label': 'This project', 'x': 0.06, 'y': 0.38, 'ours': True, 'marker': 2, 'art': 'assets/icons/fact_check-teal.png'},
        {'label': 'General chatbot', 'x': 0.06, 'y': 0.14, 'marker': 3, 'art': 'assets/icons/chat-ink.png'},
    ],
    'takeaway': 'A quick start that **people check**, not a governed metrics layer.',
    'annotations': [
        {'title': 'Who it helps', 'text': 'An analyst who knows the question but not the schema, and a reviewer deciding whether to trust the answer.'},
        {'title': 'What we chose', 'text': 'A quick start that uses the real schema and bounded hints. Query-result rows are never sent to the model.'},
        {'title': 'What we gave up', 'text': 'No governed metric definitions, so a word like revenue stays ambiguous until a person checks it. If metrics must match across teams, choose a curated tool.'},
    ],
    'note': '¹ Product positions follow the Setup column on the previous slide; other placements are our judgement.',
    'notes': notes('State the aim and what it costs.',
        'Our aim has two halves: useful without setup, and checkable by default. [Point: Who it helps] It is for an analyst who knows the question but not the schema, and for a reviewer deciding whether to trust the answer.',
        '[Point: The matrix] Left to right is the setup needed before the first useful answer. Bottom to top is how much business meaning is built in. Curated tools and dashboards sit top right. Top left would be the ideal, which is not yet available.',
        '[Point: This project] This project sits bottom left, a quick start, but above a general chatbot because it uses the real schema and bounded hints. [Point: What we gave up] There are no governed metric definitions, so revenue stays ambiguous until a person checks it.',
        'Reference: docs/1_brief.md; README, What It Does. Placements are qualitative.'),
}

demo = {
    'id': 'demo', 'layout': 'demo_page', 'section': 'Solution', 'topic': 'Demo', 'accent': 'blue',
    'title': 'The SQL shows which revenue the answer counted',
    'subtitle': 'One revenue question on the retail demo, answered by the local 9B model',
    'image': {'path': 'assets/figures/demo-answer.png', 'alt': 'The app answers which product categories generate the most revenue: Electronics leads with 173,366, with a bar chart by category.'},
    'qr': {'path': 'assets/figures/qr-live-demo.svg', 'alt': 'QR code for the live demo at aipa-text-to-sql-agent.streamlit.app'},
    'qr_title': 'Try it live',
    'qr_text': 'aipa-text-to-sql-agent.streamlit.app: the same question on the same demo database',
    'qr_url': 'https://aipa-text-to-sql-agent.streamlit.app',
    'code_title': 'The SQL, and what completed revenue adds²',
    'code': [['SELECT category, SUM(unit_price * quantity', False], ['+   * (1 - discount_pct)', True], ['  ) AS total_revenue', False],
             ['FROM order_items oi', False], ['JOIN products p', False], ['  ON oi.product_id = p.product_id', False],
             ['+ JOIN orders o ON oi.order_id = o.order_id', True], ["+ WHERE o.order_status = 'Completed'", True],
             ['GROUP BY category', False], ['ORDER BY total_revenue DESC;', False]],
    'bars_title': 'Same top category, two definitions of revenue¹',
    'bars': [{'label': 'All 220 orders, list price', 'value': 173366, 'text': '173,366'},
             {'label': '179 completed, after discounts', 'value': 136984, 'text': '136,984', 'gap': '21 % lower'}],
    'note': '¹ Electronics revenue, recomputed on data/retail_analytics.db; this illustrates inspection, not a benchmark failure. ² Lines marked + are added by the benchmark’s completed-revenue question.',
    'annotations': [
        {'title': 'The answer looks finished', 'text': 'Electronics leads with 173,366, but the chart does not say which orders it counted.'},
        {'title': 'The SQL shows the choice', 'text': 'Price times quantity, no status filter and no discounts, so all 220 orders count.'},
        {'title': 'Wording changes the number', 'text': 'Completed orders after discounts give 136,984, about 21 % lower, with the same top category.'},
    ],
    'takeaway': 'Neither figure is wrong. The question did not say which revenue, so **a person decides**.',
    'notes': notes('Show the agent answering one question, and why the SQL matters.',
        '[Point: The answer] Asked which product categories generate the most revenue, the local model says Electronics leads with 173,366. It looks complete, but the chart does not say which orders it counted.',
        '[Point: The SQL] The SQL sums price times quantity. It has no status filter and no discounts, so all 220 orders count, including cancelled and returned ones.',
        '[Point: Wording] A separate benchmark question asks for completed order revenue. That counts 179 orders with discounts and gives 136,984, about 21 % lower, with the same top category. This illustrates inspection; it is not a benchmark failure.',
        'Reference: evaluation/cases.json, retail_revenue_by_category; recomputed on data/retail_analytics.db, 6 November 2026.'),
}

boundary = {
    'id': 'boundary', 'layout': 'boundary_page', 'section': 'Solution', 'topic': 'Data boundary', 'accent': 'blue',
    'title': 'The model sees the schema and a few stored values, never result rows',
    'subtitle': 'What the prompt held for the demo question on the retail database',
    'bar_title': '79 of the 608 stored text values reach the prompt¹',
    'sent': 79, 'total': 608,
    'bar_caption': 'Each square is one distinct stored text value across the database’s 30 text columns: 79 sent as lists, never linked to a row; 529 not sent.',
    'code_title': 'From the real prompt (shortened)²',
    'code': [['CREATE TABLE orders (', False], ['  order_id INTEGER PRIMARY KEY,', False], ['  order_status TEXT NOT NULL ...', False], [');', False],
             ['-- order_status sample values:', True], ['     Completed, Returned, Cancelled', True], ['-- gender sample values: Female, Other, Male', True],
             ['### User question', False], ['Which product categories generate the most revenue?', False]],
    'lists': [['In the prompt', ['Tables, columns, keys', '79 stored values as hints', 'The question'], 'check_circle', 'teal'],
              ['Not in the prompt', ['Result rows', 'Names and emails: over the limit', 'All other stored values'], 'cancel', 'purple']],
    'models': [['Local model', 'The prompt stays on your machine.', 'verified_user'],
               ['Hosted model', 'Question, schema and hints go to the provider.', 'chat']],
    'note': '¹ Counted for this question on data/retail_analytics.db; it varies by question. Numeric columns send no values. ² Hint lines in green.',
    'takeaway': 'Before using real data, **check what the prompt contains** and where it goes.',
    'annotations': [
        {'title': 'The prompt is mostly structure', 'text': 'About 71 % of the schema text is table definitions; hints are the rest.'},
        {'title': 'Hints are real stored values', 'text': 'Up to 6 values from columns with at most 20 distinct values. The limit counts values, not sensitivity.'},
        {'title': 'The model choice moves the boundary', 'text': 'With a local model nothing leaves the machine. A hosted model receives the whole prompt.'},
        {'title': 'Check before real data', 'text': 'Review which columns qualify, or turn table selection off to send no hints.'},
    ],
    'notes': notes('Say what the model sees before anyone points it at their own data.',
        '[Point: Structure] For the demo question, the prompt held nine table definitions and 79 stored values. That is 79 of the 608 distinct text values, about 13 %, sent as lists and never linked to a row. Result rows are never sent.',
        '[Point: Hints] The hints are real stored values, such as order status. The limit counts distinct values, not sensitivity. Customer emails stay out only because there are more than twenty of them.',
        '[Point: Model] With a local model, nothing leaves your machine. With a hosted model, the question, schema and hints go to the provider. So review the prompt first, or turn table selection off.',
        'Reference: 608 is the sum of COUNT(DISTINCT) over the 30 text columns; 79 / 608 = 13.0 %; 4,971 schema characters, 1,419 on hint lines.'),
}

architecture = {
    'id': 'architecture', 'layout': 'arch_summary', 'section': 'Solution', 'topic': 'Architecture', 'accent': 'blue',
    'title': 'The model proposes SQL; the application controls execution',
    'subtitle': 'One question’s path through the app, in four stages; the full eight-step flow is in the appendix',
    'legend_kinds': [['app', 'App step, no model'], ['model', 'The model: behaviour'], ['code', 'Enforced in code']],
    'stages': [
        {'title': 'Ask and prepare', 'kind': 'app', 'icon': 'chat', 'text': 'A plain question. The app reads the schema, keeps the top 6 tables and builds the prompt.', 'logos': ['assets/logos/tech-streamlit.png', 'assets/logos/tech-python.png']},
        {'title': 'Generate', 'kind': 'model', 'icon': 'code', 'marker': 1, 'text': 'Gemini or Ollama writes one SQL statement, or declines. It never sees result rows.', 'logos': ['assets/logos/tech-ollama.png', 'assets/logos/tech-googlegemini.png']},
        {'title': 'Check and run', 'kind': 'code', 'icon': 'verified_user', 'marker': 2, 'text': 'sqlglot allows one read only; the engine runs it read-only with a budget and a row cap.', 'logos': ['assets/logos/tech-sqlglot.png']},
        {'title': 'Answer', 'kind': 'app', 'icon': 'table_rows', 'text': 'The answer, table, chart, the SQL and why those tables, for the person to inspect.', 'logos': ['assets/logos/tech-streamlit.png']},
    ],
    'repair': 'One repair try on a query error',
    'engine': {'title': 'Database engine', 'text': 'Set by the connection string; read-only on all three.',
               'logos': [['assets/logos/tech-sqlite.png', 'SQLite'], ['assets/logos/tech-duckdb.png', 'DuckDB'], ['assets/logos/tech-postgresql.png', 'PostgreSQL']]},
    'person': 'The person asks first and inspects last: the SQL is always shown with the answer.',
    'takeaway': 'One stage uses a model; **the application decides** what runs.',
    'annotations': [
        {'title': 'Only one stage is a model', 'text': 'It returns text and never sees result rows.'},
        {'title': 'Two gates, both in code', 'text': 'sqlglot, then a read-only engine. Neither checks meaning.'},
        {'title': 'One flow, three engines', 'text': 'Each passes the same 15 conformance tests.'},
        {'title': 'One repair try', 'text': 'The repaired query passes the same checks; nothing skips a gate.'},
    ],
    'notes': notes('Walk one question through the app.',
        'This is the path of one question in four stages, and only one is the model. [Point: Ask and prepare] A person asks in plain English; the application reads the schema, keeps the top six tables and builds the prompt, with no model.',
        '[Point: Generate, marker 1] The model writes one SQL statement, or declines. It never sees result rows. [Point: Check and run, marker 2] Then two gates in code: sqlglot allows one read only, and the engine runs the query read-only with a work budget and a row cap.',
        '[Point: engine band, marker 3] The same flow runs on SQLite, DuckDB and PostgreSQL. [Point: dashed arrow, marker 4] A query error goes back to the model once, and the repair passes the same checks. The full eight-step flow is in the appendix.',
        'Reference: pipeline.answer_question (max_repair_attempts=1); config.py; docs/2_architecture.md. Conformance: 45 tests, 15 per engine, 0 skipped.'),
}

W10 = [262, 150, 128, 175, 160.5]
safety = {
    'id': 'safety', 'layout': 'table_page', 'section': 'Solution', 'topic': 'Safety', 'accent': 'blue',
    'title': 'Safety does not rest on the model',
    'subtitle': 'Three lines of defence stop different threats, and each is tested on its own',
    'icon_key': [['yes', 'Stops it'], ['no', 'Does not stop it']],
    'tables': [{
        'bold_first': False,
        'headers': ['Threat, with an example', '1 Model declines¹', '2 Application check', '3 Engine, read-only', 'Lines of defence'],
        'widths': W10, 'size': 10, 'row_height': 24,
        'rows': [
            {'band': 'Stopped in code by the application or the engine', 'accent': 'blue'},
            ['**Write or schema change**  `DROP TABLE students`', {'items': [['yes', 'Declined 6 of 6']]}, {'items': [['yes', 'Blocked']]}, {'items': [['yes', 'Denied on 3 engines']]}, [['3 lines', 'strength']]],
            ['**Engine internals**  `SELECT * FROM sqlite_master`', {'items': [['yes', 'Declined 3 of 3']]}, {'items': [['yes', 'Blocked']]}, {'items': [['no', 'Would run']]}, [['2 lines', 'constraint']]],
            ['**Files on disk**  `read_csv(\'local.csv\')`', '–', {'items': [['yes', 'Blocked']]}, {'items': [['yes', 'Denied']]}, [['2 lines', 'constraint']]],
            ['**Runaway query**  a cross join of large tables', '–', '–', {'items': [['yes', 'Stopped by work budget']]}, [['1 line', 'limit']]],
            ['**Oversized result**  more rows than the cap', '–', '–', {'items': [['yes', 'Cut at 1,000 rows']]}, [['1 line', 'limit']]],
            {'band': 'Only the model declines', 'accent': 'ochre'},
            ['**Data the schema lacks**  each patient’s blood type', {'items': [['yes', 'Declined 5 of 6']]}, '–', '–', [['1 line', 'limit']]],
            {'band': 'The limit: no layer checks meaning', 'accent': 'plum'},
            ['**Wrong meaning**  average shipping weight', {'items': [['no', 'Returned average unit cost']]}, {'items': [['no', 'Passed: valid read']]}, {'items': [['no', 'Ran']]}, [['None', 'cost']]],
        ]}],
    'note': '⁠¹ The model’s decline is behaviour and can change with the model or prompt: 14 of 15 safety cases ended in its own decline. The other two columns are enforced in code and tested on their own.',
    'takeaway': 'Writes meet three lines of defence. **A wrong meaning meets none**, so the person is the last check.',
    'notes': notes('Show which defence stops which threat.',
        'Safety here does not rest on the model. [Point: Column headers] There are three lines of defence. The first is the model, which declines; in our safety run, 14 of 15 cases ended in its own decline. That is behaviour, and it can change.',
        '[Point: Application and engine] The application check uses sqlglot. For the engine, writes run straight at each one, bypassing the application check, and all three refuse them.',
        '[Point: Lines column] A write meets all three lines. A runaway query or an oversized result meets only the engine. [Point: Would run] A read of engine internals would run if it reached the engine, so the application check is what stops it.',
        '[Point: Last row] Asked for average shipping weight, the model returned average unit cost. That query was valid, so every check passed. No layer checks meaning.',
        'Reference: safety run 2026-10-10T061911, 15 cases; tests/test_engine_conformance.py, 45 tests, 15 per engine; tests/test_safety.py.'),
}

method = {
    'id': 'method', 'layout': 'bars_page', 'section': 'Evidence', 'topic': 'Method', 'accent': 'plum',
    'title': 'Read the interval, not the point',
    'subtitle': '3,817 questions in five suites, 37 recorded runs, each change paired against a named baseline',
    'panels': [
        {'title': 'Questions per suite', 'scale': [0, 1600], 'unit': '', 'rows': [
            {'label': 'Spider dev', 'value': 1034, 'series': 'published', 'text': '1,034  accuracy'},
            {'label': 'BIRD dev', 'value': 1534, 'series': 'published', 'text': '1,534  accuracy'},
            {'label': 'Large schemas', 'value': 1222, 'series': 'published', 'text': '1,222  table selection', 'marker': 1},
            {'label': 'Demo', 'value': 12, 'text': '12  behaviour', 'series': 'muted'},
            {'label': 'Safety', 'value': 15, 'text': '15  behaviour', 'series': 'muted', 'marker': 2},
        ]},
        {'title': 'How to read a paired change, accuracy points¹', 'kind': 'dot', 'scale': [-3, 7], 'unit': 'points', 'rows': [
            {'label': 'Top 6 vs every table + hints', 'value': 3.6, 'lo': 1.4, 'hi': 5.8, 'marker': 3},
            {'label': 'Shared + summaries vs shared', 'value': 0.2, 'lo': -1.5, 'hi': 2.0, 'series': 'muted'},
        ]},
    ],
    'caption': '**Note:** ¹ Results are compared by value and type, so the SQL’s wording does not matter. Intervals are 95 % paired bootstrap, 10,000 resamples. Not leaderboard scoring.',
    'takeaway': 'A change counts only when its **whole interval sits clear of zero**.',
    'annotations': [
        {'title': 'Each suite answers one question', 'text': 'Spider and BIRD measure accuracy. The large-schema suite tests table selection, because the dev databases have at most 14 tables.'},
        {'title': 'Small suites show behaviour', 'text': 'With 12 and 15 cases, Demo and Safety have intervals too wide to measure accuracy.'},
        {'title': 'Measurable, or not', 'text': 'The top change of 3.6 points sits above zero. The second crosses zero, so we cannot say it did anything.'},
    ],
    'notes': notes('Say why the numbers can be trusted and how to read them.',
        '[Point: Suites] We ran 3,817 questions in five suites, and each answers one question. Spider and BIRD measure accuracy. The large-schema suite tests table selection. Demo and Safety are small diagnostics.',
        '[Point: Method] Results are compared by value and type. Every rate carries a 95 percent bootstrap interval. Each of the 37 recorded runs pins its commit, data, prompt and model.',
        '[Point: Intervals] Here is the one rule for the next slides. Read the interval, not the point. On the top line the whole interval sits above zero, so that change of 3.6 points is measurable. On the second line it crosses zero.',
        'Reference: evaluation/suites (1,034 + 1,534 + 1,222 + 12 + 15 = 3,817); 37 run directories under evaluation/results; stats.py 10,000 resamples, seed 0.'),
}

benchmarks = {
    'id': 'benchmarks', 'layout': 'bars_page', 'section': 'Evidence', 'topic': 'Benchmarks', 'accent': 'plum',
    'title': 'The local model scored 64.6 % on Spider and 35.2 % on BIRD',
    'subtitle': 'Share of answers that matched the reference; one local 9B model, runs of 10 October 2026',
    'panels': [
        {'title': 'Overall, with 95 % interval', 'kind': 'dot', 'scale': [0, 100], 'unit': '%', 'rows': [
            {'label': 'Spider dev', 'value': 64.6, 'lo': 61.6, 'hi': 67.5},
            {'label': 'BIRD dev, with evidence', 'value': 35.2, 'lo': 32.9, 'hi': 37.6},
            {'label': 'Demo suite, 4 of 12', 'value': 33.3, 'lo': 8.3, 'hi': 58.3, 'series': 'muted', 'text': '4 of 12, interval 50 points wide', 'marker': 3},
        ]},
        {'title': 'Spider by difficulty', 'scale': [0, 100], 'unit': '%', 'marker': 1, 'rows': [
            {'label': 'Easy', 'series': 'd1', 'value': 84.3}, {'label': 'Medium', 'series': 'd2', 'value': 65.9},
            {'label': 'Hard', 'series': 'd3', 'value': 58.6}, {'label': 'Extra hard', 'series': 'd4', 'value': 38.0},
        ]},
        {'title': 'BIRD by difficulty, with and without evidence', 'scale': [0, 100], 'unit': '%', 'marker': 2, 'rows': [
            {'label': 'Simple', 'value': 43.1, 'series': 'd1'}, {'label': 'Simple, no evidence', 'value': 34.2, 'series': 'muted'},
            {'label': 'Challenging', 'value': 17.3, 'series': 'd3'}, {'label': 'Challenging, no evidence', 'value': 8.2, 'series': 'muted'},
        ]},
    ],
    'max_step': 22,
    'caption': '**Source:** release runs at 7708295, qwen3.5 9B; this project’s scorer, not leaderboard scores. Spider 1,034 and BIRD 1,534 questions.',
    'takeaway': 'Harder questions score lower, and **a good demo proves little**.',
    'annotations': [
        {'title': 'Harder questions score lower', 'text': 'Spider sets the level from how many SQL parts a query needs. Scores fall from 84.3 % to 38.0 %.'},
        {'title': 'Evidence hints help', 'text': 'Paired on the same questions, BIRD’s evidence hints add 10.1 points, at every level.'},
        {'title': 'The demo suite is too small', 'text': 'It matched 4 of 12. Turning model thinking off added 8.5 points on Spider, by not running out of output.'},
    ],
    'notes': notes('Give the headline results and how to read them.',
        '[Point: Top chart] Each dot is the share of questions whose result matched the reference, and the line is its 95 percent interval. Spider reached 64.6 percent and BIRD with evidence 35.2 percent.',
        '[Point: Spider panel] Harder questions score lower. Scores fall from 84.3 to 38.0 percent. [Point: BIRD panel] Evidence is a hint the benchmark supplies. Paired on the same questions, it adds 10.1 points.',
        '[Point: Demo suite] Our own demo suite matched 4 of 12, with an interval 50 points wide. A good demo on stage proves little. Turning thinking off added 8.5 points on Spider.',
        'Reference: runs of 10 October 2026 at 7708295. BIRD moderate 29.1 with evidence, 16.3 without; README Evaluation Results.'),
}

large = {
    'id': 'large', 'layout': 'bars_page', 'section': 'Evidence', 'topic': 'Large schemas', 'accent': 'plum',
    'title': 'On large databases, sending fewer tables scored 3.6 points higher',
    'subtitle': '1,222 BIRD train questions on 4 databases of 21 to 65 tables; runs of 19 October 2026',
    'panels': [
        {'title': 'Answers matched, by schema sent', 'scale': [0, 40], 'unit': '%', 'rows': [
            {'label': 'Every table + hints', 'value': 25.5, 'series': 'muted', 'text': '25.5 %  8,501 tokens, 4.0 s', 'marker': 2},
            {'label': 'Every table, no hints', 'value': 26.8, 'series': 'muted', 'text': '26.8 %  6,221 tokens, 4.2 s'},
            {'label': 'Top 6 + neighbours', 'value': 29.1, 'bold': True, 'text': '29.1 %  2,670 tokens, 6.0 s'},
        ]},
        {'title': 'Top 6 against every table + hints, by database size, points', 'kind': 'dot', 'scale': [-8, 12], 'unit': 'points', 'marker': 1, 'rows': [
            {'label': '65 tables, 464 questions', 'value': 5.6, 'lo': 1.7, 'hi': 9.5},
            {'label': '34 tables, 293 questions', 'value': 6.1, 'lo': 2.0, 'hi': 10.6},
            {'label': '22 tables, 207 questions', 'value': -2.4, 'lo': -6.8, 'hi': 1.9, 'series': 'muted'},
            {'label': '21 tables, 258 questions', 'value': 1.9, 'lo': -3.1, 'hi': 7.0, 'series': 'muted'},
        ]},
        {'title': 'When a needed table is dropped', 'scale': [0, 40], 'unit': '%', 'marker': 3, 'rows': [
            {'label': 'All sent, top 6', 'value': 32.9, 'text': '32.9 %  on 1,055 questions'},
            {'label': 'All sent, every table', 'value': 26.7, 'series': 'muted'},
            {'label': 'Table dropped, top 6', 'value': 5.4, 'series': 'loss', 'text': '5.4 %  on 167 questions'},
            {'label': 'Table dropped, every table', 'value': 18.0, 'series': 'muted'},
        ]},
    ],
    'max_step': 21,
    'caption': '**Source:** evaluation/results/bird_train_large at 47284f5. Paired 95 % intervals; the dropped-table split is observed, not causal.',
    'takeaway': '+3.6 points [+1.4, +5.8] with **69 % fewer tokens**, but about 2 s slower per answer.',
    'annotations': [
        {'title': 'The gain is concentrated', 'text': 'The 65- and 34-table databases gain 5 to 6 points. The two smaller ones cross zero.'},
        {'title': 'Hints on a full schema did not help', 'text': 'About half the values the questions need sit in columns too large to hint.'},
        {'title': 'Dropping a table is the real risk', 'text': 'Top 6 scored 5.4 % against 18.0 % when a needed table was dropped. Selection stays the default for its overall gain.'},
    ],
    'notes': notes('Show the three-sided trade-off of table selection.',
        '[Point: Top panel] Here are three ways to send the schema on the same 1,222 questions. Top 6 plus neighbours is the most accurate at 29.1 percent and uses the fewest prompt tokens, but it is the slowest.',
        '[Point: Middle panel] The gain is concentrated. The 65-table and 34-table databases gain 5 to 6 points, and their intervals sit clear of zero. [Point: Every table + hints] Adding hints to a full schema did not help.',
        '[Point: Bottom panel] This is the real risk. When every needed table was sent, top 6 scored 32.9 percent against 26.7. When a needed table was dropped, on 167 questions, it scored 5.4 against 18.0. Fewer tokens did not mean faster: about 2 seconds longer, because the local model cannot reuse its cache.',
        'Reference: runs of 19 October 2026 at 47284f5. Latency +2.0 s [+1.8, +2.2]. Sources: evaluation/results/bird_train_large/README.md, evaluation/results/retrieval/README.md.'),
}

W14 = [200, 230, 125.5, 200, 120]
trials = {
    'id': 'trials', 'layout': 'table_page', 'section': 'Evidence', 'topic': 'Trials', 'accent': 'plum',
    'title': 'Later trials found trade-offs, not a further accuracy gain',
    'subtitle': '1,222 large-schema questions; paired change against each row’s own baseline',
    'tables': [{
        'headers': ['Trial', 'Change, and its baseline', 'Accuracy points¹', 'Side effect', 'Decision'],
        'widths': W14, 'size': 10, 'row_height': 42,
        'rows': [
            ['Top 6 + neighbours', 'Send the best tables, vs every table + hints', '+3.6 [+1.4, +5.8]', '69 % fewer tokens, 2 s slower', [['Default', 'strength']]],
            ['Question value matching', 'Add stored values the question names, vs top 6', '+0.4 [−0.9, +1.6]', 'Reads row data at question time', [['Off', 'limit']]],
            ['Scorer signals', 'Weight hints down, match plurals, vs top 6', '+0.9 [−0.7, +2.4]', 'All needed tables sent: 1,055 to 1,094', [['Kept', 'strength']]],
            ['Dense embeddings', 'Add sentence embeddings, vs the kept scorer', '+0.2 [−1.6, +2.0]', 'All needed tables sent: 1,094 to 1,148', [['Off', 'limit']]],
            ['Shared layout', 'Send every table, name the top 6, vs top 6', '−2.4 [−4.6, −0.2]', '58 % faster, 3 times the tokens', [['Opt-in', 'constraint']]],
            ['Shared plus summaries', 'Also list their columns, vs top 6, not controlled', '−2.1 [−4.3, +0.0]', 'Same speed as shared', [['Opt-in', 'constraint']]],
        ]}],
    'note': '⁠¹ Paired 95 % intervals. Only the first row’s interval sits clear of zero above it; the shared layout’s sits clear below it. The others cross zero.',
    'takeaway': 'Table selection is the **one clear gain**. Five later trials traded speed or recall, not accuracy.',
    'notes': notes('Show what the later trials found.',
        '[Point: Top row] Each row shows what changed, the paired result, the side effect and the decision. Sending the best tables is the one clear gain. None of the five later trials added to it.',
        '[Point: Scorer signals] The scorer change sent all needed tables more often, from 1,055 questions to 1,094. Its 0.9 points still spans zero, so better retrieval did not become measurably better answers. We kept it for the retrieval gain.',
        '[Point: Dense embeddings] Dense embeddings helped dropped-table questions, but other answers churned, so the whole suite moved only 0.2 points. [Point: Shared layout] The shared layout cut latency by 58 percent and lost 2.4 points. Both layouts stay opt-in.',
        'Reference: evaluation/results/value_matches, scorer_signals, dense_embeddings, shared_layout.'),
}

retrieval = {
    'id': 'retrieval', 'layout': 'bars_page', 'section': 'Evidence', 'topic': 'Retrieval', 'accent': 'plum',
    'title': 'Better table coverage did not measurably improve accuracy',
    'subtitle': 'Correct answers gained and lost by each fix against selected tables, on 1,222 questions',
    'panels': [
        {'title': 'Dense embeddings: net +2 answers¹', 'scale': [-50, 25], 'unit': '', 'marker': 1, 'rows': [
            {'label': 'Gained', 'value': 18, 'series': 'secondary', 'text': '+18'},
            {'label': 'Lost', 'value': -16, 'series': 'loss', 'text': '−16'},
        ]},
        {'title': 'Every table, shared layout: net −29 answers', 'scale': [-50, 25], 'unit': '', 'marker': 2, 'rows': [
            {'label': 'Gained', 'value': 15, 'series': 'secondary', 'text': '+15'},
            {'label': 'Lost', 'value': -44, 'series': 'loss', 'text': '−44'},
        ]},
        {'title': 'Shared plus summaries: net −26 answers', 'scale': [-50, 25], 'unit': '', 'marker': 3, 'rows': [
            {'label': 'Gained', 'value': 13, 'series': 'secondary', 'text': '+13'},
            {'label': 'Lost', 'value': -39, 'series': 'loss', 'text': '−39'},
        ]},
    ],
    'caption': '**Note:** ¹ Gained and lost are net changes per group, not flip counts. Baseline: selected tables with the kept scorer, 8 of 128 and 359 of 1,094 correct.',
    'takeaway': 'Each fix helps where it aims, and **the other questions pay**.',
    'annotations': [
        {'title': 'Fixes help where they aim', 'text': 'Dense embeddings took the missed-table questions from 8 to 26 correct.'},
        {'title': 'The other questions pay', 'text': 'Sending every table won 15 answers and lost 44. Even reordering the same tables changed 22 of 480 answers.'},
        {'title': 'A live system cannot see the groups', 'text': 'The next test is targeted recovery: recover missed tables only where needed, and report both groups.'},
    ],
    'notes': notes('Explain why better coverage did not become better accuracy.',
        '[Point: Two groups] The later scorer leaves two groups. On 128 questions a needed table was missed, and top 6 got 8 right. On the other 1,094 every needed table was sent.',
        '[Point: Dense embeddings] Each fix helps where it aims. Dense embeddings took those questions from 8 to 26 correct. [Point: Every table] But the other questions pay. Sending every table won 15 answers and lost 44, a net of minus 29.',
        '[Point: Churn] Small prompt changes flip answers: reordering the same tables changed 22 of 480 answers. The groups come from the evaluation, so a live system cannot see them.',
        'Reference: evaluation/results/dense_embeddings, shared_layout, scorer_signals. Baseline 367 of 1,222 (8 + 359).'),
}

W16 = [180, 260, 235.5, 200]
next_tests = {
    'id': 'next', 'layout': 'table_page', 'section': 'Next steps', 'topic': 'Next tests', 'accent': 'ochre',
    'title': 'Four tests would close the main gaps in the evidence',
    'subtitle': 'Each needs a measured outcome before any default changes',
    'tables': [{
        'headers': ['Test', 'Why it is needed', 'What we would measure', 'What it decides¹'],
        'widths': W16, 'size': 10, 'row_height': 60,
        'rows': [
            ['1  Business definitions', 'Revenue stays ambiguous until a person checks it.', 'Answers on ambiguous questions, with and without a few definitions.', 'Whether to carry a definitions layer.'],
            ['2  Targeted table recovery', 'On 128 questions a needed table is missed.', 'Gains on those, and losses on the other 1,094.', 'Whether recovery keeps its gains.'],
            ['3  New large schemas', 'The gain comes from 2 of 4 databases.', 'Top 6 on databases outside these four, one by one.', 'Whether top 6 stays the default at every size.'],
            ['4  A hosted model', 'All results use one local model.', 'The same suites on a hosted model.', 'Whether it is worth sending it the prompt.'],
        ]}],
    'note': '⁠¹ Proposals, not results. Broader value hints would need a data-boundary decision first.',
    'takeaway': 'Measure first, then **change a default only on evidence**.',
    'notes': notes('Name the four tests that would close the gaps.',
        '[Point: Row 1] First, business definitions: add a few and compare answers on ambiguous questions. [Point: Row 2] Second, targeted table recovery, reporting gains on the 128 and losses on the 1,094.',
        '[Point: Row 3] Third, new large schemas, because the gain comes from 2 of 4 databases. [Point: Row 4] Fourth, a hosted model, since all results use one local model.',
        'Reference: all accuracy figures use one local model and this project’s comparison.'),
}

references = {
    'id': 'references', 'layout': 'references', 'section': 'Next steps', 'topic': 'Sources', 'accent': 'ochre',
    'title': 'Sources behind the claims',
    'subtitle': 'Every number traces to the repository or to a source read on the date given',
    'items': [
        {'label': 'Repository: README Evaluation Results; large-schema and retrieval results', 'url': 'https://github.com/tuannm3812/text-to-sql-agent/tree/main/evaluation/results'},
        {'label': 'Spider: Yu et al. (2018), EMNLP, arXiv 1809.08887', 'url': 'https://arxiv.org/abs/1809.08887'},
        {'label': 'BIRD: Li et al. (2023), NeurIPS, arXiv 2305.03111; leaderboard read 6 November 2026', 'url': 'https://bird-bench.github.io/'},
        {'label': 'Spider 2.0: Lei et al. (2024), arXiv 2411.07763 (read 6 November 2026)', 'url': 'https://arxiv.org/abs/2411.07763'},
        {'label': 'Snowflake Cortex Analyst documentation (read 6 November 2026)', 'url': 'https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst'},
        {'label': 'Databricks Genie best practices (read 6 November 2026)', 'url': 'https://docs.databricks.com/en/genie/best-practices.html'},
        {'label': 'WrenAI and Vanna repositories; Vanna archived 29 March 2026 (read 6 November 2026)', 'url': 'https://github.com/Canner/WrenAI'},
    ],
    'notes': notes('List where the audience can check the claims.', 'These are the sources behind every number in the deck.'),
}

close = {
    'id': 'close', 'layout': 'close_page', 'section': '', 'accent': 'blue', 'header_style': 'appendix',
    'kicker': 'Thank you',
    'title': 'Inspectable SQL, measured trade-offs and a clear next experiment',
    'subtitle': 'Questions and feedback are welcome.',
    'links': [
        ['Live demo', 'aipa-text-to-sql-agent.streamlit.app', 'https://aipa-text-to-sql-agent.streamlit.app', 'query_stats'],
        ['Code and runs', 'github.com/tuannm3812/text-to-sql-agent', 'https://github.com/tuannm3812/text-to-sql-agent', 'code'],
    ],
    'image': {'path': 'assets/figures/close-portrait.png', 'alt': 'Illustration: table cards around a lens showing a small bar chart. Decorative, no real data.'},
    'notes': notes('Close on the contribution.',
        'The contribution is an inspectable SQL application and an evaluation record that makes its trade-offs visible. The default keeps table selection because it improved the large-schema comparison. Answer accuracy remains limited, and better retrieval alone has not added a gain.',
        '[Point: links] The demo shows the interaction; the repository holds the code, runs and decisions behind every claim. Thank you.'),
}

appendix = {
    'id': 'appendix-rag', 'layout': 'bars_page', 'section': 'Appendix', 'topic': 'Schema RAG', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: how the top 6 tables are chosen',
    'subtitle': 'Relevance score by table for: Which product categories generate the most revenue?',
    'legend': [{'kind': 'swatch', 'color': '#21918C', 'label': 'Top 6, sent'},
               {'kind': 'swatch', 'color': '#5EC962', 'label': 'Foreign-key neighbour, added'},
               {'kind': 'swatch', 'color': '#ADB5BD', 'label': 'Not sent'}],
    'label_width': 170,
    'panels': [{'title': 'Score, no fixed scale; it only ranks tables for one question', 'scale': [0, 40], 'unit': '', 'rows': [
        {'label': 'products', 'value': 30.13, 'mono': True, 'text': '30.1  used by the SQL'},
        {'label': 'returns', 'value': 11.73, 'mono': True, 'text': '11.7'},
        {'label': 'order_items', 'value': 9.92, 'mono': True, 'text': '9.9  used by the SQL'},
        {'label': 'inventory_snapshots', 'value': 9.78, 'mono': True, 'text': '9.8'},
        {'label': 'customer_support_tickets', 'value': 5.82, 'mono': True, 'text': '5.8'},
        {'label': 'suppliers', 'value': 1.71, 'mono': True, 'text': '1.7', 'marker': 1},
        {'label': 'marketing_campaigns', 'value': 1.65, 'mono': True, 'series': 'muted', 'text': '1.6'},
        {'label': 'customers', 'value': 1.45, 'mono': True, 'series': 'secondary', 'text': '1.4'},
        {'label': 'regions', 'value': 1.31, 'mono': True, 'series': 'muted', 'text': '1.3'},
        {'label': 'orders', 'value': 1.31, 'mono': True, 'series': 'secondary', 'text': '1.3', 'marker': 2},
        {'label': 'stores', 'value': 1.30, 'mono': True, 'series': 'secondary', 'text': '1.3'},
    ]}],
    'caption': '**Source:** rag.rank_schema_chunks on data/retail_analytics.db with the default scorer, 6 November 2026.',
    'takeaway': '9 tables reached the model; its SQL used 2. **No rows are searched and no model is called.**',
    'annotations': [
        {'title': 'The cut can be close', 'text': 'Words are widened with synonyms, then each table is scored from names, keywords, trigrams and value hints. suppliers made it at 1.7; marketing campaigns missed at 1.6.'},
        {'title': 'Neighbours are added', 'text': 'orders ranks tenth, yet arrives through a foreign key from order_items. The benchmark’s answer needs it.'},
    ],
    'notes': notes('Backup for questions about table selection.',
        '[Point: Steps] First the question’s words are widened with synonyms, so revenue also searches amount, sales and total. Then every table gets a relevance score from its names, keywords, trigrams and value hints. No model is called.',
        '[Point: The cut] The top six are kept. suppliers made it at 1.7 and marketing campaigns missed at 1.6. [Point: Neighbours] orders ranks tenth, yet it arrives because a foreign key links it to order_items. Nine tables reached the model, and its SQL used two.',
        'Reference: weights in config.py; dense off.'),
}

W_A1 = [150, 400, 325.5]
scoring = {
    'id': 'appendix-scoring', 'layout': 'table_page', 'section': 'Appendix', 'topic': 'How answers are scored', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: matched means the same rows as the reference',
    'subtitle': 'The project’s own result comparison, used for every accuracy figure in this deck',
    'tables': [
        {'title': 'How two result sets are compared', 'headers': ['Part', 'Rule', 'Why'], 'widths': W_A1, 'size': 10, 'row_height': 26,
         'rows': [
            ['Columns', 'Same number of columns, compared by position; names do not matter.', 'The SQL’s aliases are free.'],
            ['Rows', 'Compared as a set with repeats, matched one to one. Order counts only when the reference SQL ends in ORDER BY.', 'Row order is not part of the answer unless asked.'],
            ['Numbers', 'Equal across integer and decimal types; otherwise within one part in a million.', '1 and 1.0 are the same answer.'],
            ['Text and NULL', 'Text matches exactly after trimming and never equals a number. NULL equals only NULL.', 'No loose string matching.'],
         ]},
        {'title': 'What each outcome means¹', 'headers': ['Outcome', 'When', 'Counts as'], 'widths': W_A1, 'size': 10, 'row_height': 22,
         'rows': [
            ['Correct', 'Rows match the reference, or a request that should be refused was refused.', 'Matched'],
            ['Wrong, refused, unanswerable or error', 'Rows differ, a safe question was blocked or declined, or the SQL failed or came back empty.', 'Not matched'],
         ]},
    ],
    'note': '⁠¹ This is not the Spider or BIRD leaderboard scorer, so scores are not comparable with published ones. An empty answer is an error, never a correct refusal.',
    'takeaway': 'Matched means **the same rows**, not similar SQL.',
    'notes': notes('Backup for questions about how accuracy is measured.',
        'An answer counts as matched when its rows equal the reference rows. Columns compare by position, rows as a set unless the reference orders them, numbers across integer and decimal types, and text exactly.',
        'Reference: text_to_sql_agent/evaluation_v2/comparator.py and scoring.py (scorer version 2).'),
}

W_A2 = [170, 470, 235.5]
glossary = {
    'id': 'appendix-glossary', 'layout': 'table_page', 'section': 'Appendix', 'topic': 'Glossary', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: terms used in this deck',
    'subtitle': 'Plain meanings for the words on the evidence slides',
    'tables': [{'headers': ['Term', 'Meaning', 'Where it appears'], 'widths': W_A2, 'size': 10, 'row_height': 38,
        'rows': [
            ['Schema', 'The tables, columns and keys of a database, without its rows.', 'Why it is hard, data boundary'],
            ['Value hints', 'Up to 6 stored values from text columns with at most 20 distinct values, sent with the schema.', 'Data boundary, large schemas'],
            ['Top 6 + neighbours', 'The six most relevant tables for a question, plus tables one foreign key away.', 'Architecture, large schemas'],
            ['Every table + hints', 'The whole schema with value hints; the baseline for table selection.', 'Large schemas, trials'],
            ['Evidence hints', 'BIRD’s own note for each question, such as which column a phrase refers to.', 'Benchmarks'],
            ['Paired change', 'The difference between two settings on the same questions, in accuracy points.', 'Method, trials'],
            ['95 % interval', 'The range the change could plausibly take; measurable when it sits clear of zero.', 'Method onwards'],
            ['Conformance tests', 'The same 15 read-only tests run on each engine, none skipped.', 'Summary, safety'],
        ]}],
    'notes': notes('Backup glossary.', 'These are the plain meanings of the terms on the evidence slides.'),
}

W_A3 = [130, 290, 230, 225.5]
engines = {
    'id': 'appendix-engines', 'layout': 'table_page', 'section': 'Appendix', 'topic': 'Read-only per engine', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: each engine enforces read-only in its own way',
    'subtitle': 'The engine layer of the safety slide; each mechanism is required, not optional',
    'tables': [{'headers': ['Engine¹', 'Writes refused by', 'Files and internals', 'Work budget'], 'widths': W_A3, 'size': 10, 'row_height': 76,
        'rows': [
            ['SQLite', 'A read-only connection, query_only on, and an authorizer that denies every write action.', 'The authorizer also denies ATTACH, so other files cannot be opened.', '100,000 virtual-machine steps, then the query stops.'],
            ['DuckDB', 'The read_only connect flag, which protects the database file.', 'External access off, so read_csv and other file readers are refused.', '5,000 ms, then the query stops.'],
            ['PostgreSQL', 'A least-privilege role and a read-only transaction, each enough on its own.', 'A superuser or file-reading role is refused at connect.', '5,000 ms, then the query stops.'],
        ]}],
    'note': '⁠¹ All three pass the same 15 conformance tests, 45 in all, none skipped. Every engine also caps results at 1,000 rows.',
    'takeaway': 'Read-only is **enforced by each engine**, not assumed from the application check.',
    'notes': notes('Backup for questions about engine safety.',
        'Each engine enforces read-only in its own way, and every mechanism is load-bearing. SQLite uses a read-only connection, query_only and an authorizer. DuckDB uses its read_only flag plus external access off. PostgreSQL uses a least-privilege role and a read-only transaction.',
        'Reference: text_to_sql_agent/engines/sqlite.py, duckdb.py, postgres.py; docs/0_coding_standards.md; tests/test_engine_conformance.py.'),
}

stack = {
    'id': 'appendix-stack', 'layout': 'stack_page', 'section': 'Appendix', 'topic': 'Technology', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: the technology behind each step',
    'subtitle': 'Open-source tools, plus a hosted model only when the user picks one',
    'groups': [
        {'title': 'App', 'items': [['assets/logos/tech-streamlit.png', 'Streamlit', 'The question box, answer, chart and SQL'],
                                   ['assets/logos/tech-pandas.png', 'pandas', 'Result tables and CSV uploads']]},
        {'title': 'Model', 'items': [['assets/logos/tech-ollama.png', 'Ollama', 'A local model; nothing leaves the machine'],
                                     ['assets/logos/tech-googlegemini.png', 'Gemini', 'A hosted model, when chosen'],
                                     ['assets/logos/tech-langchain.png', 'LangChain', 'The Ollama client']]},
        {'title': 'Checks', 'items': [['assets/logos/tech-sqlglot.png', 'sqlglot', 'Parses the SQL and refuses anything but one read'],
                                      ['assets/logos/tech-python.png', 'Python', 'Table selection, prompts and the evaluation harness']]},
        {'title': 'Engines', 'items': [['assets/logos/tech-sqlite.png', 'SQLite', 'The demo databases and uploaded files'],
                                       ['assets/logos/tech-duckdb.png', 'DuckDB', 'Analytical files, read-only'],
                                       ['assets/logos/tech-postgresql.png', 'PostgreSQL', 'A live server, through a least-privilege role']]},
    ],
    'takeaway': 'No model is trained: the app **wraps an existing model** with checks around it.',
    'notes': notes('Backup for questions about the stack.', 'These are the tools behind each step. Nothing is trained; the evaluation harness measures the agent.',
        'Reference: pyproject.toml; ui/connection.py; text_to_sql_agent/llm.py.'),
}

arch_full = {
    'id': 'appendix-architecture', 'layout': 'flow_page', 'section': 'Appendix', 'topic': 'Full flow', 'accent': 'slate',
    'header_style': 'appendix',
    'title': 'Backup: one question’s path through the app, as a flowchart',
    'subtitle': '',
    'image': {'path': 'assets/figures/flowchart.png', 'alt': 'Flowchart: a plain question goes to read schema, select tables, then generate (the one model call, Ollama or Gemini), then validate. If it is one read, it runs read-only and the answer is shown; if not, it is refused and explained. A query error loops back to generate once.'},
    'notes': notes('Backup for questions about the full flow.',
        'One question passes six stages, top to bottom. Ask and Prepare use no model; Generate is the only model call; Validate and Run are the two gates in code; Show puts the answer and the SQL in front of the person.',
        'Reference: pipeline.answer_question; schema.py; rag.py; llm.py; safety.py; execution.py; engines/; ui/results.py. AGENTS.md 2026-10-19 for the 4 ms retrieval.'),
}

agenda = {
    'id': 'agenda', 'layout': 'agenda', 'agenda_style': 'kaggle', 'page_position': 'right', 'chapter_fill': 'accent_pale',
    'section': 'AGENDA', 'accent': 'slate', 'title': 'Agenda', 'subtitle': '',
    'contents': [
        {'title': 'Problem', 'accent': 'slate', 'entries': [
            {'title': 'Summary', 'from': 'summary', 'through': 'summary'},
            {'title': 'Why it is hard', 'from': 'hard', 'through': 'hard'},
            {'title': 'Other tools', 'from': 'tools', 'through': 'tools'},
            {'title': 'Our aim', 'from': 'aim', 'through': 'aim'}]},
        {'title': 'Solution', 'accent': 'blue', 'entries': [
            {'title': 'Demo', 'from': 'demo', 'through': 'demo'},
            {'title': 'Data boundary', 'from': 'boundary', 'through': 'boundary'},
            {'title': 'Architecture', 'from': 'architecture', 'through': 'architecture'},
            {'title': 'Safety', 'from': 'safety', 'through': 'safety'}]},
        {'title': 'Evidence', 'accent': 'plum', 'entries': [
            {'title': 'Method', 'from': 'method', 'through': 'method'},
            {'title': 'Benchmarks', 'from': 'benchmarks', 'through': 'benchmarks'},
            {'title': 'Large schemas', 'from': 'large', 'through': 'large'},
            {'title': 'Trials and retrieval', 'from': 'trials', 'through': 'retrieval'}]},
        {'title': 'Next steps', 'accent': 'ochre', 'entries': [
            {'title': 'Next tests', 'from': 'next', 'through': 'next'},
            {'title': 'Sources', 'from': 'references', 'through': 'references'}]},
    ],
    'notes': notes('Show the order of the talk.',
        'The deck follows four questions. [Point: Problem] Why is this hard, and what do other tools do? [Point: Solution] What was built, and how it is controlled. [Point: Evidence] What was measured, including the ideas that did not help. [Point: Next steps] What is still unproven and how to test it.'),
}

brief = json.loads((HERE / 'brief-content.json').read_text())
first = [s for s in brief['slides'] if s['id'] in ('cover', 'summary', 'hard')]
cover, summary, hard = first
summary['section'] = 'Problem'
cover['title'] = 'Ask your data.\nInspect the answer.'
cover['subtitle'] = 'A text-to-SQL agent that writes read-only SQL, shows its work and measures where it fails'
cover['image'] = {'path': 'assets/figures/cover-portrait.png', 'alt': 'Illustration: linked table cards around a lens over a small bar chart. Decorative, no real data.'}
cover['motif'] = {'path': 'assets/figures/cover-motif.svg', 'alt': 'Decorative row of small table cards, two highlighted as chosen.'}
brief['author'] = 'Manh Tuan (Mike) Nguyen'
brief['affiliation'] = 'TD School, University of Technology Sydney'
for k in ('problem', 'approach', 'findings'):
    summary.pop(k, None)
summary.update({
    'layout': 'summary_page',
    'tiles': [
        {'label': 'Read-only checks', 'value': '45 of 45', 'text': 'tests passed, none skipped, on 3 database engines', 'icon': 'verified_user', 'series': 'primary', 'marker': 1, 'visual': {'kind': 'dots', 'n': 45}, 'caveat': 'Read-only, not proof of right answers.'},
        {'label': 'Spider', 'value': '64.6 %', 'text': 'of answers matched¹: common test, local 9B model', 'icon': 'target', 'series': 'primary', 'marker': 3, 'visual': {'kind': 'ring', 'path': 'assets/figures/ring-64-6.png', 'alt': 'Ring filled to 64.6 %'}, 'caveat': 'Our scorer, not the leaderboard.'},
        {'label': 'BIRD', 'value': '35.2 %', 'text': 'of answers matched: harder test, with evidence hints', 'icon': 'target', 'series': 'primary', 'visual': {'kind': 'ring', 'path': 'assets/figures/ring-35-2.png', 'alt': 'Ring filled to 35.2 %'}, 'caveat': 'One local model only.'},
        {'label': 'Large databases', 'value': '+3.6 pts', 'text': 'from choosing tables [+1.4, +5.8]', 'icon': 'trending_up', 'series': 'secondary', 'visual': {'kind': 'interval'}, 'caveat': 'From 2 of 4 databases.'},
    ],
    'panel_title': 'Large databases: more correct answers from less context²',
    'panel_marker': 2,
    'panels': [
        {'title': 'Answers matched', 'max': 32, 'rows': [
            {'label': 'Every table + hints', 'value': 25.5, 'text': '25.5 %', 'series': 'muted'},
            {'label': 'Top 6 tables', 'value': 29.1, 'text': '29.1 %', 'series': 'primary'}],
         'reading': 'Sending only the most relevant tables scored 3.6 points higher.'},
        {'title': 'Prompt size, every table = 100', 'max': 110, 'marker': 4, 'rows': [
            {'label': 'Every table + hints', 'value': 100, 'text': '100', 'series': 'muted'},
            {'label': 'Top 6 tables', 'value': 31, 'text': '31', 'series': 'primary'}],
         'reading': 'The prompt was 69 % smaller, but each answer took about two seconds longer.'},
    ],
    'note': '¹ This project’s result comparison, not leaderboard scoring; Spider (Yu et al., 2018) and BIRD (Li et al., 2023). ² 1,222 BIRD train questions on 4 databases of 21 to 65 tables.',
    'takeaway': 'Inspectable and read-only, but **a person should still review** each answer.',
    'annotations': [
        {'title': 'Read-only is not the same as right', 'text': 'The controls limit what can run. They do not show the answer is correct.'},
        {'title': 'Selection helps at scale', 'text': 'The gain comes from the 65- and 34-table databases. It is not a universal result.'},
        {'title': 'Judge the whole answer', 'text': 'About one in three Spider answers still did not match.'},
        {'title': 'Smaller prompts are not faster here', 'text': 'Each question gets a different schema, so the local model cannot reuse its cache.'},
    ],
})
hard['ours'] = '**This project, for comparison:** 64.6 % on Spider dev and 35.2 % on BIRD dev, local 9B model, our own scorer; not comparable with the bars above.'
for c, ic in zip(hard['causes'], ('menu_book', 'table_rows', 'verified_user')):
    c['icon'] = ic
hard['chain'] = [['Question', 'What the person asks', 'chat'], ['Schema', 'Tables and columns', 'schema'], ['SQL', 'The generated query', 'code'], ['Rows', 'The answer returned', 'table_rows']]
summary['accent'] = 'slate'
hard['figure']['caption_url'] = 'https://arxiv.org/abs/2411.07763'
benchmarks['caption_url'] = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/README.md'
large['caption_url'] = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/evaluation/results/bird_train_large/README.md'
retrieval['caption_url'] = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/evaluation/results/dense_embeddings/README.md'
method['caption_url'] = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/evaluation/results'
appendix['caption_url'] = 'https://github.com/tuannm3812/text-to-sql-agent/blob/main/text_to_sql_agent/rag.py'
brief['slides'] = [cover, agenda, summary, hard, other_tools, aim, demo, boundary, architecture, safety, method,
                   benchmarks, large, trials, retrieval, next_tests, references, close, appendix, arch_full, scoring, engines, stack, glossary]
for sl in brief['slides']:   # the kit's table_page reads its face notes from notes_on_face, not note
    if sl['layout'] == 'table_page' and 'note' in sl:
        sl['notes_on_face'] = [sl.pop('note')]
(HERE / 'brief-content.json').write_text(json.dumps(brief, indent=2, ensure_ascii=False) + '\n')
print(len(brief['slides']), 'slides')
