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

    # Relative link audit
    relative_link_audit()

    # Canonical / og:url consistency
    canonical_og_audit()

    # Sitemap coverage audit
    sitemap_audit()


def relative_link_audit():
    """Flag any href/src in _src/ (or _includes/) that isn't root-relative, absolute, or anchor-only."""
    import re
    violations = []
    SAFE = ('/','#','https://','http://','mailto:','tel:','javascript:','${','data:','\'')
    ATTR_RE = re.compile(r'(?:href|src)="([^"]*)"')
    # Check _includes/
    for fname in os.listdir(INCLUDES_DIR):
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(INCLUDES_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for m in ATTR_RE.finditer(line):
                    val = m.group(1)
                    if val.startswith(SAFE):
                        continue
                    violations.append((os.path.join('_includes', fname), i, val))
    # Check _src/
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.html'):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, SITE_DIR)
            with open(fpath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    for m in ATTR_RE.finditer(line):
                        val = m.group(1)
                        if val.startswith(SAFE):
                            continue
                        # Allow INCLUDE markers (they get replaced)
                        if 'INCLUDE:' in line:
                            continue
                        violations.append((rel, i, val))
    if violations:
        print(f'\n⚠️  Relative link audit: {len(violations)} non-root-relative href/src found:')
        for path, line, val in violations[:20]:
            print(f'   {path}:{line} → href="{val}"')
        if len(violations) > 20:
            print(f'   ... and {len(violations) - 20} more')
        print('All internal hrefs should start with / (root-relative) or be absolute URLs.')
    else:
        print('✅ Relative link audit passed (all href/src root-relative or absolute)')


def canonical_og_audit():
    """Check that canonical and og:url match on every page."""
    import re
    DOMAIN = 'https://booklabbybjorn.com'
    mismatches = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.html') or fname.startswith('_'):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, SITE_DIR)
            content = read_file(fpath)
            canon = re.search(r'rel="canonical"\s+href="([^"]*)"', content)
            og = re.search(r'property="og:url"\s+content="([^"]*)"', content)
            if not canon or not og:
                continue  # pages without both tags are fine
            c_path = canon.group(1).replace(DOMAIN, '')
            o_path = og.group(1).replace(DOMAIN, '')
            if c_path.rstrip('/') != o_path.rstrip('/'):
                mismatches.append((rel, canon.group(1), og.group(1)))
    if mismatches:
        print(f'\n⚠️  Canonical/og:url mismatch on {len(mismatches)} page(s):')
        for path, c, o in mismatches[:10]:
            print(f'   {path}: canonical={c}  og:url={o}')
    else:
        print('✅ Canonical/og:url audit passed (all matching)')


def sitemap_audit():
    """Warn about _src/ pages that are missing from sitemap.xml."""
    import xml.etree.ElementTree as ET

    sitemap_path = os.path.join(SITE_DIR, 'sitemap.xml')
    if not os.path.exists(sitemap_path):
        print('⚠️  No sitemap.xml found — skipping sitemap audit')
        return

    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree = ET.parse(sitemap_path)
    locs = {u.find('s:loc', ns).text for u in tree.getroot().findall('s:url', ns)}

    # Normalize sitemap URLs to paths: https://booklabbybjorn.com/foo → /foo
    sitemap_paths = set()
    for loc in locs:
        path = loc.replace('https://booklabbybjorn.com', '')
        # Normalize: /foo/ → /foo, but keep / as /
        sitemap_paths.add(path.rstrip('/') or '/')

    # Walk _src/ and find pages not in sitemap
    # Skip: _TEMPLATE files, partials
    missing = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.html'):
                continue
            if fname.startswith('_'):
                continue  # templates, partials

            src_path = os.path.join(root, fname)
            rel = os.path.relpath(src_path, SRC_DIR)

            # Convert to URL path: reviews/foo.html → /reviews/foo
            # index.html → /dirname/ (or / for top-level)
            if fname == 'index.html':
                dir_rel = os.path.dirname(rel)
                if dir_rel == '' or dir_rel == '.':
                    url_path = '/'
                else:
                    url_path = '/' + dir_rel.replace(os.sep, '/')
            else:
                url_path = '/' + rel.replace(os.sep, '/').replace('.html', '')

            if url_path not in sitemap_paths:
                missing.append(url_path)

    if missing:
        missing.sort()
        print(f'\n⚠️  Sitemap gap: {len(missing)} page(s) in _src/ but NOT in sitemap.xml:')
        for m in missing:
            print(f'   {m}')
        print('Add these to sitemap.xml or this is intentional (e.g. landing pages).')
    else:
        print('✅ Sitemap coverage: all _src/ pages found in sitemap.xml')


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
