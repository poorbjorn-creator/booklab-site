# BookLab Site — Editing Rules

**⚠️ READ THIS FILE BEFORE ANY SITE EDIT. No exceptions.**

## Source of Truth

- **`_src/`** is the source of truth. ALL edits go here.
- **Never edit built output files directly** — `build.py` will overwrite them.
- If you need to add a new page, add it to `_src/` (correct subdirectory).

## Build & Deploy

1. Edit files in `_src/`
2. Run `python3 build.py` — it will:
   - Check for orphan files (output files missing from `_src/`) and abort if found
   - Back up all output HTML before overwriting
   - Build from `_src/` → output
3. Deploy with wrangler (see deploy instructions)

## Editing Checklist

Before making changes:
- [ ] State what you're changing and what you're NOT touching
- [ ] Edits go in `_src/`, not the output files

After making changes:
- [ ] Run `build.py` successfully (no orphan warnings)
- [ ] Verify the live page renders correctly
- [ ] Check mobile rendering
- [ ] Update `sitemap.xml` if pages were added/changed (update `<lastmod>` dates)

## New Reviews

**Always use `_src/reviews/_TEMPLATE.html`** as the starting point for new reviews. It includes:
- Proper `INCLUDE` markers (head-css, review-css, nav, footer, nav-js)
- Structured data (JSON-LD for Review + optional Video)
- OG/Twitter meta tags with hero image
- Tagline, hero image, video embed, takeaway, verdict, related books
- Delete the `VIDEO BLOCK` sections if there's no video

Copy the template, find-replace the ALL_CAPS placeholders, add content.

## Shared CSS (`_includes/`)

- `base.css` — global styles (nav, footer, variables, typography)
- `review.css` — review page styles (based on Fahrenheit 451 gold standard)
- `head.html` — shared `<head>` block (includes base.css)
- `nav.html` / `nav.js` — navigation
- `footer.html` — footer

Use `<!-- INCLUDE:key -->` markers in `_src/` files. The build system resolves them.

## Images

### Book Covers

Canonical book covers live in `images/covers/`, named by ISBN: `images/covers/9781785152610.jpg`

- **One cover per book, one location.** If a book appears on multiple pages (reviews, articles, reading list, monthly), always reference the same canonical path.
- When adding a new cover, save it as `images/covers/{ISBN}.jpg`.
- Before creating a new cover file, check if one already exists.
- Older pages may still reference one-off paths (e.g. `images/reading-list-2026/foo.jpg`). Migrate these to `images/covers/` when you touch that page.

### Hero / OG Images

Review pages use a **custom hero image** — NOT the book cover. These are editorial images stored as `images/og-{slug}.jpg` (e.g. `images/og-in-the-realm-of-hungry-ghosts.jpg`).

- Hero images are set in the `<img class="hero-img">` tag and in OG/Twitter meta tags.
- Don't use a plain book cover as the hero image on review pages.

## Before ANY Change

1. **State what you plan to change** — describe the approach
2. **State what you will NOT touch**
3. **Wait for approval** — do not implement until Bjorn says go
4. If multiple approaches exist, present them. Don't pick silently.

## Star Ratings

- **NEVER put star ratings in the `<div class="meta">` block at the top of a review.**
- Stars appear ONLY at the bottom of the review (in the `<div class="rating">` block).
- The meta block should just be: `<div class="meta">by AUTHOR</div>`

## Crosslinking

When an article mentions a book that has a full review on the site (`/reviews/`), **always add a visible "Read Review →" button** next to the Amazon affiliate link. Use the outline button style:

```html
<a href="/reviews/SLUG" class="btn-buy" style="background:transparent;border:2px solid var(--gold);color:var(--gold)">Read Review →</a>
```

- Check `_src/reviews/` for existing review pages before publishing any article that mentions books.
- Only add the button for books that actually have a review page — don't link to pages that don't exist.
- This applies to all article types: listicles, topic pages, and recommendation articles.

## Surgical Changes

- Only touch what was asked
- Don't "improve" adjacent code or formatting
- Match existing style
- Every changed line should trace to the request
