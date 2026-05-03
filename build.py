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
MANAGED_DIRS = ['reviews', 'articles', 'topics', 'monthly']

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

            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)

            count += 1

    print(f'Built {count} pages')

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
