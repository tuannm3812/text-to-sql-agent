"""The page's visual system, injected once per render by `app.py`.

IBM Plex Sans for the interface, Plex Mono only for SQL and table names (they are code).
The approved blue/amber showcase palette: cream canvas, navy text, blue emphasis
and amber comparison/step accents (`docs/design/design.md`, 2026-11-05).
Warnings retain explicit text and a dark warning colour. Layout stays Streamlit's
columns; this sets type, colour,
spacing and the top bar.
"""

from __future__ import annotations

CHAT_CSS = """
<style>
/* IBM Plex, served locally from static/fonts (OFL-1.1, licence beside the files). */
@font-face { font-family: "IBM Plex Sans"; font-weight: 400; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexSans-Regular-Latin1.woff2") format("woff2"); }
@font-face { font-family: "IBM Plex Sans"; font-weight: 500; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexSans-Medium-Latin1.woff2") format("woff2"); }
@font-face { font-family: "IBM Plex Sans"; font-weight: 600; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexSans-SemiBold-Latin1.woff2") format("woff2"); }
@font-face { font-family: "IBM Plex Sans"; font-weight: 700; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexSans-Bold-Latin1.woff2") format("woff2"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 400; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexMono-Regular-Latin1.woff2") format("woff2"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 500; font-style: normal; font-display: swap;
    src: url("app/static/fonts/IBMPlexMono-Medium-Latin1.woff2") format("woff2"); }
:root {
    --ink: #17243b; --muted: #59636e; --line: #e6e9ed; --paper: #faf7f0;
    --amber: #e6a23c; --panel: #ffffff; --primary: #0f4beb; --primary-soft: #eef3ff;
    --well: #f5eee2; --border: #c5cbd4; --warn: #8a5a00; --warn-bg: #fff4d6;
    --fail: #b42318; --fail-bg: #fff0ee; --focus: #0f4beb;
}
*:focus-visible { outline: 3px solid var(--focus) !important; outline-offset: 2px; }
html, body, .stApp, [data-testid="stHeader"] { background: var(--paper); }
/* Streamlit sets its own font on headings, paragraphs and widgets, so the family is set on
   those elements directly; its icon spans (Material Symbols) are left alone. */
.stApp, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li, .stApp label, .stApp button,
.stApp input, .stApp textarea, .stApp td, .stApp th, .stApp summary, .stApp div[role="tab"],
.stApp .brand, .stApp .conn {
    font-family: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif !important;
}
/* Colour only on the root: buttons keep their own (white text on the blue Ask). */
.stApp { color: var(--ink); font-size: 16px; line-height: 1.5; }
.stApp .facts, .stApp .trace { font-variant-numeric: tabular-nums; }
[data-testid="stHeaderActionElements"] { display: none; }
/* Keep SQL overflow inside its own panel, never the page. */
[data-testid="stCode"] { max-width: 100%; overflow-x: auto; }
code, pre, .mono { font-family: "IBM Plex Mono", ui-monospace, monospace !important; }
[data-testid="stHeader"] { display: none; }
.main .block-container, [data-testid="stMainBlockContainer"] {
    max-width: 1240px; padding: 0 40px 64px;
}

/* top bar */
/* Full-bleed bar inside the centred column: a panel-coloured shadow widens the
   background, clip-path keeps it to the bar's own height. */
.st-key-topbar { position: relative; padding: 12px 0; margin: 0 0 32px;
    background: var(--panel); box-shadow: 0 0 0 100vmax var(--panel);
    clip-path: inset(0 -100vmax -1px -100vmax); }
.st-key-topbar::after { content: ""; position: absolute; left: 0; right: 0;
    bottom: -1px; height: 1px; background: var(--line); }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 17px;
         letter-spacing: -0.01em; white-space: nowrap; }
.mark { width: 30px; height: 30px; border-radius: 7px; background: var(--primary); color: #fff;
        display: grid; place-items: center; font: 600 13px "IBM Plex Mono", monospace; }
.conn { display: flex; align-items: center; justify-content: flex-end; gap: 8px;
        font-size: 14px; color: var(--muted); }
.conn b { color: var(--ink); font-weight: 600; }
.conn .setup { color: var(--warn); background: var(--warn-bg); border-radius: 6px;
               padding: 1px 8px; font-weight: 500; }

/* ask */
h1.hero { font-size: 31px; line-height: 1.2; font-weight: 600; letter-spacing: -0.02em;
          margin: 4px 0 6px; padding: 0; }
.stApp .hero-sub { color: var(--muted); max-width: 46rem; margin: 0 0 14px; }
.st-key-ask_box [data-baseweb="input"] { background: var(--panel); border: 1.5px solid var(--ink);
    border-radius: 10px; }
.st-key-ask_box input { font-size: 17px; background: var(--panel); padding: 12px 14px; }
.st-key-ask_box [data-testid="stHorizontalBlock"] { flex-wrap: nowrap; align-items: center; }
.st-key-ask_box [data-testid="stColumn"]:last-child { flex: 0 0 96px; min-width: 96px; }
.st-key-ask_box button { min-height: 48px; border-radius: 10px; font-weight: 600; }
.stApp .note { font-size: 14px; color: var(--muted); margin: 2px 0 18px; }

/* answer */
.stApp .q { font-size: 14px; color: var(--muted); margin: 0; }
h2.headline { font-size: 24px; font-weight: 600; line-height: 1.25; margin: 6px 0 4px;
              padding: 0; letter-spacing: -0.01em; }
h2.headline em { font-style: normal; color: var(--primary); }
h2.headline.refused { color: var(--warn); }
.stApp .facts { font-size: 14px; color: var(--muted); margin: 0 0 14px; }
.stApp .chart-title { font-size: 14px; font-weight: 600; margin: 8px 0 0; }

/* how this was answered */
.stApp .trace h2 { font-size: 16px; font-weight: 600; margin: 0; padding: 0; }
.stApp .trace .who { font-size: 13px; color: var(--muted); margin: 2px 0 0; }
.trace ol { list-style: none; margin: 14px 0 4px; padding: 0; counter-reset: step; }
.trace li { position: relative; padding: 0 0 16px 34px; counter-increment: step; }
.trace li::before { content: counter(step); position: absolute; left: 0; top: 0; width: 22px;
    height: 22px; border-radius: 50%; background: var(--amber); color: var(--ink);
    font: 600 12px "IBM Plex Mono", monospace; display: grid; place-items: center; }
.trace li::after { content: ""; position: absolute; left: 10.5px; top: 24px; bottom: 2px;
                   width: 1px; background: var(--line); }
.trace li:last-child::after { display: none; }
.stApp .trace h3 { font-size: 14px; font-weight: 600; margin: 0; padding: 0; }
.stApp .trace p { font-size: 14px; color: var(--muted); margin: 2px 0 0; }
.stApp .trace .size { margin-top: 8px; }
.trace .ok { color: var(--primary); font-weight: 600; }
.trace .bad { color: var(--warn); font-weight: 600; }
.trace details { margin-top: 6px; font-size: 13px; color: var(--muted); }
.trace summary { cursor: pointer; }
.trace pre code { color: var(--ink); background: transparent; padding: 0; font-size: inherit; }
.trace .sql-keyword { color: var(--primary); font-weight: 600; }
.trace .sql-function, .trace .sql-literal { color: #8a5a00; }
.trace .sql-comment { color: var(--muted); }
.trace pre { background: var(--well); border-radius: 8px; padding: 10px 12px; margin: 8px 0 0;
             font-size: 12.5px; line-height: 1.55; white-space: pre-wrap;
             overflow-wrap: anywhere; color: var(--ink); }
.tables { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tables span { font: 500 12.5px "IBM Plex Mono", monospace; padding: 2px 8px;
               border-radius: 6px; background: var(--well); max-width: 100%;
               overflow-wrap: anywhere; }
.tables span.hit { background: var(--primary-soft); color: var(--primary); }

/* The answer's two surfaces: white, a quiet but visible border, 20-24 px inside. */
[class*="st-key-answer_"][class*="_result"], [class*="st-key-answer_"][class*="_trace"] {
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 24px;
}
[class*="st-key-answer_"] { margin-bottom: 8px; }
.stPills label p { font-size: 13px; color: var(--muted); }

@media (max-width: 700px) {
    .main .block-container, [data-testid="stMainBlockContainer"] { padding: 0 16px 40px; }
    .st-key-topbar { margin-bottom: 16px; padding: 10px 0; }
    .st-key-topbar [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 8px; }
    .st-key-topbar [data-testid="stColumn"] { min-width: 0 !important; }
    .st-key-topbar [data-testid="stColumn"]:nth-child(1) { flex: 1 1 calc(100% - 120px); order: 1; }
    .st-key-topbar [data-testid="stColumn"]:nth-child(4) { flex: 0 0 110px; order: 2; }
    .st-key-topbar [data-testid="stColumn"]:nth-child(2) {
        flex: 0 0 auto; width: auto !important; order: 3; }
    .st-key-topbar [data-testid="stColumn"]:nth-child(3) { flex: 1 1 0; order: 4; }
    .st-key-ask_box [data-testid="stColumn"]:first-child { flex: 1 1 0; min-width: 0 !important; }
    .st-key-ask_box [data-testid="stColumn"]:last-child { flex: 0 0 72px; min-width: 72px; }
    .conn .full { display: none; }
    .stApp .hero-sub { margin-bottom: 8px; }
    .stApp .note { margin-bottom: 12px; line-height: 1.5; }
    .stApp .trace p { line-height: 1.5; }
    h1.hero { font-size: 24px; }
    h2.headline { font-size: 21px; }
    [class*="st-key-answer_"][class*="_result"], [class*="st-key-answer_"][class*="_trace"] {
        padding: 16px; }
    .st-key-ask_box input { font-size: 16px; }
}
</style>
"""
