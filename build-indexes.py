#!/usr/bin/env python3
"""Auto-generate articles.html and monthly/index.html from existing files.
Run before every deploy to prevent listing regressions."""

import re, os, glob
from pathlib import Path

SITE = Path(__file__).parent

def extract_meta(filepath):
    """Extract title, description, og:image from an HTML file."""
    html = filepath.read_text(encoding='utf-8', errors='replace')
    
    # Title: strip " | BookLab..." or " — BookLab..." suffix
    m = re.search(r'<title>(.*?)</title>', html)
    title = m.group(1).strip() if m else filepath.stem.replace('-', ' ').title()
    title = re.sub(r'\s*[\|—–]\s*BookLab.*$', '', title)
    
    m = re.search(r'<meta name="description" content="(.*?)"', html)
    desc = m.group(1) if m else ''
    
    m = re.search(r'og:image" content="(.*?)"', html)
    og_img = m.group(1) if m else ''
    og_img = og_img.replace('https://booklabbybjorn.com', '')
    if not og_img:
        og_img = '/images/og-kit/og-bookshelf-02.jpg'
    
    return title, desc, og_img

# ─── MONTHLY INDEX ───────────────────────────────────────────────────────────

MONTH_ORDER = ['january','february','march','april','may','june',
               'july','august','september','october','november','december']
MONTH_EMOJI = ['🎆','❄️','🌱','🌷','🌸','☀️','🏖️','🌻','🍂','🎃','🍁','🎄']

def build_monthly():
    idx = SITE / 'monthly' / 'index.html'
    html = idx.read_text()
    
    months = []
    for f in sorted(SITE.glob('monthly/*-*.html')):
        if f.name == 'index.html':
            continue
        # parse "march-2026.html" -> (month_name, year)
        m = re.match(r'(\w+)-(\d{4})\.html', f.name)
        if not m:
            continue
        month_name, year = m.group(1), int(m.group(2))
        month_idx = MONTH_ORDER.index(month_name) if month_name in MONTH_ORDER else 0
        _, desc, _ = extract_meta(f)
        if len(desc) > 120:
            desc = desc[:117] + '...'
        if not desc:
            desc = 'Nonfiction picks including top recommendations'
        pretty = f"{month_name.capitalize()} {year}"
        emoji = MONTH_EMOJI[month_idx]
        sort_key = year * 100 + month_idx
        months.append((sort_key, f.name, pretty, emoji, desc))
    
    months.sort(key=lambda x: x[0], reverse=True)
    
    cards = []
    for i, (_, fname, pretty, emoji, desc) in enumerate(months):
        # Badge logic: first month = "Preview", second = "New"
        if i == 0:
            badge = '\n<span class="month-badge">Preview</span>'
        elif i == 1:
            badge = '\n<span class="month-badge">New</span>'
        else:
            badge = ''
        cards.append(f'''
<a href="{fname}" class="month-card">
<div class="month-emoji">{emoji}</div>
<div class="month-info">
<div class="month-title">{pretty}</div>
<div class="month-desc">{desc}</div>
</div>{badge}
</a>''')
    
    card_html = '\n'.join(cards)
    
    # Replace between <div class="month-list"> and the closing </div>\n</div>\n before <footer
    new_html = re.sub(
        r'(<div class="month-list">).*?(</div>\s*</div>\s*<footer)',
        rf'\1\n{card_html}\n</div>\n</div>\n\n<footer',
        html, flags=re.DOTALL
    )
    idx.write_text(new_html)
    print(f"✅ monthly/index.html rebuilt with {len(months)} months")

# ─── ARTICLES INDEX ──────────────────────────────────────────────────────────

def build_articles():
    idx = SITE / 'articles.html'
    html = idx.read_text()
    
    entries = []
    
    # Collect articles
    for f in SITE.glob('articles/*.html'):
        title, desc, og_img = extract_meta(f)
        href = f'/articles/{f.name}'
        mtime = f.stat().st_mtime
        if len(desc) > 160:
            desc = desc[:157] + '...'
        entries.append((mtime, href, title, desc, og_img))
    
    # Collect topics
    for f in SITE.glob('topics/*.html'):
        title, desc, og_img = extract_meta(f)
        href = f'/topics/{f.name}'
        mtime = f.stat().st_mtime
        if len(desc) > 160:
            desc = desc[:157] + '...'
        entries.append((mtime, href, title, desc, og_img))
    
    entries.sort(key=lambda x: x[0], reverse=True)
    
    cards = []
    for _, href, title, desc, og_img in entries:
        # Escape HTML entities in title/desc
        safe_title = title.replace('&', '&amp;').replace('"', '&quot;')
        cards.append(f'''
<a href="{href}" class="article-card">
<img src="{og_img}" alt="{safe_title}">
<div class="article-info">
<div class="article-title">{title}</div>
<div class="article-desc">{desc}</div>
</div>
</a>''')
    
    card_html = '\n'.join(cards)
    
    new_html = re.sub(
        r'(<div class="article-list">).*?(</div>\s*</div>\s*<footer)',
        rf'\1\n{card_html}\n</div>\n</div>\n\n<footer',
        html, flags=re.DOTALL
    )
    idx.write_text(new_html)
    print(f"✅ articles.html rebuilt with {len(entries)} entries")

# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("🔨 Building indexes...")
    build_monthly()
    build_articles()
    
    # Sync to _src
    import shutil
    shutil.copy(SITE / 'monthly' / 'index.html', SITE / '_src' / 'monthly' / 'index.html')
    shutil.copy(SITE / 'articles.html', SITE / '_src' / 'articles.html')
    print("📋 Synced to _src/")
    print("Done!")
