#!/usr/bin/env python3
"""Build script for BookLab site. Assembles _src/ pages with _includes/ into final HTML."""

import os
import sys

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SITE_DIR, '_src')
INCLUDES_DIR = os.path.join(SITE_DIR, '_includes')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_includes():
    """Load all include files and resolve nested includes."""
    base_css = read_file(os.path.join(INCLUDES_DIR, 'base.css'))
    head_raw = read_file(os.path.join(INCLUDES_DIR, 'head.html'))
    # Resolve nested base-css include in head.html
    head = head_raw.replace('<!-- INCLUDE:base-css -->', base_css)
    
    return {
        'head-css': head,
        'nav': read_file(os.path.join(INCLUDES_DIR, 'nav.html')),
        'footer': read_file(os.path.join(INCLUDES_DIR, 'footer.html')),
        'nav-js': read_file(os.path.join(INCLUDES_DIR, 'nav.js')),
    }

def build():
    includes = load_includes()
    count = 0
    
    for root, dirs, files in os.walk(SRC_DIR):
        # Skip hidden dirs
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
    build()
