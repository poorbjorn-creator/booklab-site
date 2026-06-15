#!/usr/bin/env python3
"""Migrate hardcoded nav/footer/nav-js blocks to INCLUDE markers.

For each _src/ HTML file that does NOT already have <!-- INCLUDE:nav -->:
1. Replace <nav>...</nav>\n<div class="nav-overlay-bg">...</div>\n<div class="nav-overlay...">...</div>
   with <!-- INCLUDE:nav -->
2. Replace <footer>...</footer> with <!-- INCLUDE:footer -->
3. Replace the nav toggle <script> block with <!-- INCLUDE:nav-js -->
4. Report what was changed.

DRY RUN by default. Pass --apply to write changes.
"""

import os, re, sys, glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SITE_DIR, '_src')

apply = '--apply' in sys.argv

# Pattern for nav block: <nav>...everything...</nav> + overlay-bg div + nav-overlay div
NAV_PATTERN = re.compile(
    r'<nav>\s*\n.*?</nav>\s*\n'                          # <nav>...</nav>
    r'(?:<div class="nav-overlay-bg"></div>\s*\n)?'       # overlay bg (optional)
    r'<div class="nav-overlay[^"]*"[^>]*>\s*\n'           # overlay start
    r'.*?</div>',                                         # overlay content + close
    re.DOTALL
)

# Pattern for footer
FOOTER_PATTERN = re.compile(r'<footer>.*?</footer>', re.DOTALL)

# Pattern for nav-js (the hamburger toggle script)
NAVJS_PATTERN = re.compile(
    r"<script>\s*\n?\s*\(function\(\)\{\s*\n?"
    r"var btn=document\.querySelector\('.hamburger'\).*?"
    r"\}\)\(\);\s*\n?\s*</script>",
    re.DOTALL
)

def find_html_files():
    files = []
    for root, dirs, fnames in os.walk(SRC_DIR):
        for f in fnames:
            if f.endswith('.html') and not f.startswith('_'):
                files.append(os.path.join(root, f))
    return sorted(files)

changed = 0
skipped = 0
errors = []

for fpath in find_html_files():
    rel = os.path.relpath(fpath, SRC_DIR)
    content = open(fpath, 'r', encoding='utf-8').read()
    
    # Skip if already using INCLUDE:nav
    if '<!-- INCLUDE:nav -->' in content:
        skipped += 1
        continue
    
    # Check if it has a hardcoded <nav>
    if '<nav>' not in content:
        skipped += 1
        continue
    
    original = content
    changes = []
    
    # Replace nav block
    m = NAV_PATTERN.search(content)
    if m:
        content = content[:m.start()] + '<!-- INCLUDE:nav -->' + content[m.end():]
        changes.append('nav')
    else:
        errors.append(f'{rel}: has <nav> but pattern did not match')
        continue
    
    # Replace footer
    m = FOOTER_PATTERN.search(content)
    if m:
        content = content[:m.start()] + '<!-- INCLUDE:footer -->' + content[m.end():]
        changes.append('footer')
    
    # Replace nav-js
    m = NAVJS_PATTERN.search(content)
    if m:
        content = content[:m.start()] + '<!-- INCLUDE:nav-js -->' + content[m.end():]
        changes.append('nav-js')
    
    if changes:
        print(f'  ✅ {rel}: replaced {", ".join(changes)}')
        if apply:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
        changed += 1

print(f'\n{"Applied" if apply else "Would change"}: {changed} files | Skipped (already using includes): {skipped}')
if errors:
    print(f'\n⚠️  Errors ({len(errors)}):')
    for e in errors:
        print(f'  {e}')
if not apply and changed > 0:
    print('\nRun with --apply to write changes.')
