#!/usr/bin/env python3
"""Build script for BookLab site. Assembles _src/ pages with _includes/ into final HTML.

SAFETY: Before building, checks that every HTML file in the output dirs also exists
in _src/. Aborts if orphan files would be overwritten/lost. Run with --force to skip.
"""

import os
import sys
import shutil
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SITE_DIR, '_src')
INCLUDES_DIR = os.path.join(SITE_DIR, '_includes')
BACKUP_DIR = os.path.join(SITE_DIR, '.backups', 'pre-build')

# Dirs that the build system manages (output mirrors _src)
MANAGED_DIRS = ['reviews', 'articles', 'topics', 'monthly', 'behind-the-book', 'highlights']

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_includes():
    """Load all include files and resolve nested includes."""
    base_css = read_file(os.path.join(INCLUDES_DIR, 'base.css'))
    head_raw = read_file(os.path.join(INCLUDES_DIR, 'head.html'))
    head = head_raw.replace('<!-- INCLUDE:base-css -->', base_css)

    review_css = read_file(os.path.join(INCLUDES_DIR, 'review.css'))

    return {
        'head-css': head,
        'review-css': f'<style>\n{review_css}\n</style>',
        'nav': read_file(os.path.join(INCLUDES_DIR, 'nav.html')),
        'footer': read_file(os.path.join(INCLUDES_DIR, 'footer.html')),
        'nav-js': read_file(os.path.join(INCLUDES_DIR, 'nav.js')),
    }

def check_orphans():
    """Find HTML files in output that don't exist in _src/. These would be lost."""
    orphans = []

    # Check top-level HTML
    for f in os.listdir(SITE_DIR):
        if f.endswith('.html'):
            src = os.path.join(SRC_DIR, f)
            if os.path.exists(src):
                # _src version exists, build will overwrite — that's fine
                pass
            # If no _src version, build won't touch it — also fine

    # Check managed subdirs: files in output but not in _src
    for d in MANAGED_DIRS:
        out_dir = os.path.join(SITE_DIR, d)
        src_dir = os.path.join(SRC_DIR, d)
        if not os.path.isdir(out_dir):
            continue
        for f in os.listdir(out_dir):
            if not f.endswith('.html'):
                continue
            if not os.path.exists(os.path.join(src_dir, f)):
                orphans.append(os.path.join(d, f))

    return orphans

def backup_before_build():
    """Snapshot all output HTML before building."""
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, stamp)
    os.makedirs(backup_path, exist_ok=True)

    for f in os.listdir(SITE_DIR):
        if f.endswith('.html'):
            shutil.copy2(os.path.join(SITE_DIR, f), backup_path)

    for d in MANAGED_DIRS:
        out_dir = os.path.join(SITE_DIR, d)
        if not os.path.isdir(out_dir):
            continue
        dest = os.path.join(backup_path, d)
        os.makedirs(dest, exist_ok=True)
        for f in os.listdir(out_dir):
            if f.endswith('.html'):
                shutil.copy2(os.path.join(out_dir, f), dest)

    print(f'Backup saved to {backup_path}')
    return backup_path

def prerender_reviews(content):
    """Extract REVIEWS JSON from the page and inject static HTML cards for SEO.
    The JS on the page will take over for search/filter/sort on load."""
    import json, re, html as html_mod

    # Extract the var REVIEWS = [...]; block
    m = re.search(r'var REVIEWS\s*=\s*\[(.+?)\];', content, re.DOTALL)
    if not m:
        return content

    # Parse the JS array — it's almost JSON, convert to valid JSON
    raw = '[' + m.group(1) + ']'
    # JS uses unquoted keys — quote them (keep delimiter, add quotes around key)
    raw = re.sub(r'(?<=\{)\s*(\w+)\s*:', r'"\1":', raw)
    raw = re.sub(r',\s*(\w+)\s*:', r',"\1":', raw)
    # Fix JS-escaped single quotes (\') which aren't valid JSON
    raw = raw.replace("\\'", "'")

    try:
        reviews = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'  ⚠️  Could not parse REVIEWS JSON for pre-render: {e}')
        return content

    # Build static HTML
    cards = []
    for r in reviews:
        rating_val = r.get('rating', 0)
        if rating_val == 0:
            stars_html = '<div class="review-rating">Personal Reflection</div>'
        else:
            stars_html = f'<div class="review-rating">{"⭐" * rating_val}</div>'

        snippet_html = ''
        if r.get('snippet'):
            snippet_html = f'<div class="review-snippet">{html_mod.escape(r["snippet"])}</div>'

        card = (
            f'<a href="/reviews/{html_mod.escape(r["slug"])}" class="review-card">'
            f'<img src="{html_mod.escape(r["cover"])}" alt="{html_mod.escape(r["title"])}">'
            f'<div class="review-info">'
            f'<div class="review-title">{html_mod.escape(r["title"])}</div>'
            f'<div class="review-author">{html_mod.escape(r["author"])}</div>'
            f'{stars_html}'
            f'{snippet_html}'
            f'</div></a>'
        )
        cards.append(card)

    static_html = '\n'.join(cards)
    count_html = f'{len(reviews)} review{"s" if len(reviews) != 1 else ""}'

    # Inject static cards into the reviewList div (between open and close tags)
    content = re.sub(
        r'(<div[^>]*id="reviewList"[^>]*>)(</div>)',
        lambda m: m.group(1) + '\n' + static_html + '\n' + m.group(2),
        content
    )

    # Inject count into the reviewCount element
    content = re.sub(
        r'(<p[^>]*id="reviewCount"[^>]*>)(</p>)',
        lambda m: m.group(1) + count_html + m.group(2),
        content
    )

    return content


def build():
    includes = load_includes()
    count = 0

    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for fname in files:
            if not fname.endswith('.html'):
                continue

            src_path = os.path.join(root, fname)
            rel_path = os.path.relpath(src_path, SRC_DIR)
            out_path = os.path.join(SITE_DIR, rel_path)

            content = read_file(src_path)

            for key, value in includes.items():
                marker = f'<!-- INCLUDE:{key} -->'
                content = content.replace(marker, value)

            # Pre-render reviews page for SEO
            if fname == 'reviews.html' and root == SRC_DIR:
                content = prerender_reviews(content)

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)

            count += 1

    print(f'Built {count} pages')

    # Post-build lint: catch bad internal links
    bad_patterns = ['/monthly/index']
    violations = []
    for root, dirs, files in os.walk(SRC_DIR):
        pass  # We check built output, not _src
    for subdir in MANAGED_DIRS:
        if not os.path.isdir(subdir):
            continue
        for root, dirs, files in os.walk(subdir):
            for fname in files:
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    text = f.read()
                for pat in bad_patterns:
                    if pat in text:
                        violations.append((fpath, pat))
    # Also check top-level built HTML
    for fname in os.listdir('.'):
        if fname.endswith('.html') and os.path.isfile(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                text = f.read()
            for pat in bad_patterns:
                if pat in text:
                    violations.append((fname, pat))
    if violations:
        print(f'\n⚠️  Link lint: found {len(violations)} bad internal link(s):')
        for path, pat in violations[:10]:
            print(f'   {path}: contains "{pat}"')
        print('Fix these in _src/ or _includes/ and rebuild.')
    else:
        print('✅ Link lint passed (no /monthly/index)')

if __name__ == '__main__':
    force = '--force' in sys.argv

    # Safety check: find orphan files that exist in output but not _src
    orphans = check_orphans()
    if orphans and not force:
        print(f'\n⚠️  ABORT: Found {len(orphans)} HTML file(s) in output that are NOT in _src/:')
        for o in orphans[:10]:
            print(f'   {o}')
        if len(orphans) > 10:
            print(f'   ... and {len(orphans) - 10} more')
        print(f'\nThese files were likely added directly to the output folder.')
        print(f'Copy them to _src/ first, then re-run build.py.')
        print(f'Or run with --force to skip this check (NOT recommended).')
        sys.exit(1)

    # Backup before building
    backup_before_build()

    # Build
    build()
