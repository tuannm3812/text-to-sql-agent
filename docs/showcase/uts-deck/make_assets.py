"""Batch 1 assets (19 November 2026): cover motif strip, cover image with the real app card, tick and cross icons,
summary rings. Run: ~/Documents/GitHub/deck-kit/.venv/bin/python make_assets.py (Pillow)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
FIG = HERE / 'assets/figures'
ICON = HERE / 'assets/project/icons'

# 1. Motif: a row of small schema cards, one chosen (gold header), linked by thin lines. 478 x 46 pt.
cards = []
x = 4
for i in range(10):
    cards.append(x)
    x += 47.4
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 478 46" width="478" height="46">']
for a in cards[:-1]:
    svg.append(f'<line x1="{a + 36}" y1="23" x2="{a + 47.4}" y2="23" stroke="#C9D6E3" stroke-width="1.5"/>')
for i, a in enumerate(cards):
    chosen = i in (3, 6)
    fill = '#32658A' if chosen else '#EDF0F3'
    head = '#B89245' if chosen else '#C9D6E3'
    row = '#8FA9C0' if chosen else '#D8DEE3'
    svg.append(f'<rect x="{a}" y="7" width="36" height="32" rx="5" fill="{fill}"/>')
    svg.append(f'<rect x="{a + 5}" y="12" width="20" height="4" rx="2" fill="{head}"/>')
    for k in range(3):
        svg.append(f'<rect x="{a + 5}" y="{20 + k * 6}" width="{26 - (k % 2) * 8}" height="3" rx="1.5" fill="{row}"/>')
svg.append('</svg>')
(FIG / 'cover-motif.svg').write_text('\n'.join(svg))

# 2. Cover image: the illustration, with a framed crop of the real app's answer card below the lens.
W, H = 1200, 1620
art = Image.open(FIG / 'cover-art.png').convert('RGB')
s = H / art.height
art = art.resize((round(art.width * s), H), Image.LANCZOS)
x0 = (art.width - W) // 2
base = art.crop((x0, 0, x0 + W, H))
shot = Image.open(HERE / '../slides/captures/2026-11-06-retail-syntax.png').convert('RGB').crop((136, 357, 823, 680))
cw = 820
shot = shot.resize((cw, round(shot.height * cw / shot.width)), Image.LANCZOS)
pad = 18
card = Image.new('RGB', (shot.width + 2 * pad, shot.height + 2 * pad), 'white')
card.paste(shot, (pad, pad))
cx, cy = (W - card.width) // 2, H - card.height - 120
shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((cx + 10, cy + 14, cx + card.width + 10, cy + card.height + 14), 24, fill=(0, 0, 0, 120))
base = Image.alpha_composite(base.convert('RGBA'), shadow.filter(ImageFilter.GaussianBlur(14))).convert('RGB')
mask = Image.new('L', card.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 22, fill=255)
base.paste(card, (cx, cy), mask)
base.save(FIG / 'cover-combined.png')

# 3. Tick and cross for Best for and Risk.
(ICON / 'tick.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="#2E8B57"/><path d="M5.5 10.3l3 3 6-6.3" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
(ICON / 'cross.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="#C0392B"/><path d="M6.5 6.5l7 7M13.5 6.5l-7 7" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/></svg>')

# 4. Rings for the summary tiles: share in teal on a hair ring (supersampled).
for name, share in (('ring-64-6', .646), ('ring-35-2', .352)):
    S = 400
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (30, 30, S - 30, S - 30)
    d.arc(box, 0, 360, fill='#D8DEE3', width=56)
    d.arc(box, -90, -90 + 360 * share, fill='#21918C', width=56)
    im.resize((120, 120), Image.LANCZOS).save(FIG / f'{name}.png')
print('ok')

# 5. Batch 2 (19 November 2026): the demo's answer card crop. The QR code is made with segno:
#    uv run --no-project --with segno python -c "import segno; segno.make('https://aipa-text-to-sql-agent.streamlit.app',
#    error='m').save('assets/figures/qr-live-demo.svg', scale=4, border=0, dark='#1B2430', light=None)"
Image.open(HERE / '../slides/captures/2026-11-06-retail-syntax.png').convert('RGB').crop((136, 357, 823, 680)).save(FIG / 'demo-answer.png')
