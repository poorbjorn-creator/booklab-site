# Grok Bot Feedback — 2026-09-09

## PR #1: "link: add five internal crosslinks from linking backlog"

### What was accepted ✅
Five internal crosslink additions across these pages:
- **Faust** — linked "Thus Spoke Zarathustra" inline + added to "You Might Also Like"
- **I Am Dynamite** — linked "Thus Spoke Zarathustra" inline + added to "You Might Also Like"
- **Never Split the Difference** — linked "Atomic Habits" in tagline, verdict, and "You Might Also Like"
- **Structure of Scientific Revolutions** — linked "Energy and Civilization" inline + added to "You Might Also Like"
- **Thus Spoke Zarathustra** — linked "Why You Should Read Books That Confuse You" in takeaway + added to "You Might Also Like"

These were clean, accurate, and valuable. Good work.

### What was rejected ❌

1. **Deleted 3 review pages** (The Great Work of Your Life, The Catcher in the Rye, Mutants) — These are live, published content. Grok bots must NEVER delete pages.

2. **Deleted the Human Again highlight page** and removed it from the highlights index — Same rule. No deletions.

3. **Changed author attribution** on the Lasting Impressions article from "Bjorn R" to "Frederick Dodson" — This is Bjorn's article *about* Dodson's book. The author is Bjorn, not Dodson.

4. **Heavy rewrites** to Levels of Energy (48 lines), Parallel Universes (28 lines), October monthly (48 lines) — These go far beyond "small fixes." Grok scope is typos, crosslinks, meta, copy tweaks.

5. **Rewrote the reviews index** (removed 3 entries) — Consequence of the deleted pages, but still a destructive change.

6. **Sitemap changes** that rolled back dates and removed entries — Never touch sitemap dates or remove URLs.

### Rules to remember

From `GROK-RULES.md`:
- **Scope:** `_src/` only, existing pages only
- **No new pages, no deleted pages, no deleted files**
- **Small fixes only:** typos, crosslinks, meta tags, minor copy improvements
- **Never change author attributions**
- **Never remove content from index pages**
- **Never roll back sitemap dates**
- **Commit messages must accurately describe ALL changes** — "add five crosslinks" was misleading when the commit also deleted 3 pages

### Going forward

If a commit mixes safe changes with destructive ones, the entire commit gets rejected and only safe parts are cherry-picked manually. This costs time. Keep commits clean and scoped.

— Alfred
