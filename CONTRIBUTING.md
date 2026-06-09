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

**When adding a new review, you MUST also:**
1. Add the review card to `_src/reviews.html` (the reviews index page) — newest first
2. Update the review count in the same file
3. Update `sitemap.xml` with the new review URL and today's date

**Every review card on the /reviews index MUST include a `<div class="review-snippet">` with a short, compelling tagline** (1-2 sentences max) to drive interest and clicks. See Spiral Dynamics or The Wealth of Nations for examples.

**Always use `_src/reviews/_TEMPLATE.html`** as the starting point for new reviews. It includes:
- Proper `INCLUDE` markers (head-css, review-css, nav, footer, nav-js)
- Structured data (JSON-LD for Review + optional Video)
- OG/Twitter meta tags with hero image
- Tagline, hero image, video embed, takeaway, verdict, related books
- Delete the `VIDEO BLOCK` sections if there's no video

Copy the template, find-replace the ALL_CAPS placeholders, add content.

## Video Placement

When a review has a video, place the video embed **in the middle of the review** (between content sections), not at the bottom. This keeps readers engaged and breaks up the text naturally. The exact position depends on the review, but aim for roughly the halfway point — after the setup/summary sections and before the opinion/verdict sections.

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

### Image Optimization Guidelines

**All images MUST be optimized before committing/deploying:**

- **Hero/OG images:** Max **1200px wide**, JPEG quality **80**, target **under 200KB**
- **Book covers:** Max **400px wide**, JPEG quality **80**, target **under 100KB**
- **Format:** Always use **JPEG** (`.jpg`) for hero/OG images — not PNG. JPEG is smaller and universally supported by social crawlers for `og:image`.
- **No PNGs for photos.** PNG is only acceptable for graphics/logos with transparency.
- **Resize on ingest:** When adding a new image from a phone or camera, always resize it down before placing it. Raw phone photos (3000-4000px wide, 2-5MB) are never acceptable.
- **Command:** `convert input.jpg -resize "1200x>" -quality 80 output.jpg`

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

When an article mentions a book that has a full review on the site (`/reviews/`), **always add a visible "Read Review →" button** next to the Amazon affiliate link. Use this standard style:

```html
<a href="/reviews/SLUG" class="btn-amazon" style="background:var(--card);border:2px solid var(--gold);color:var(--gold);">Read Review →</a>
```

This gives a solid dark background with gold border and gold text — visible and clickable, but distinct from the solid-gold Amazon button. **Always use this exact pattern** for review links on all pages (great books list, articles, etc.).

- Check `_src/reviews/` for existing review pages before publishing any article that mentions books.
- Only add the button for books that actually have a review page — don't link to pages that don't exist.
- This applies to all article types: listicles, topic pages, and recommendation articles.

## Newsletter Creation (Beehiiv)

When creating a weekly newsletter:
1. Receive draft/notes from Bjorn (usually a .docx)
2. Verify all links: review pages exist and return 200, Amazon affiliate links use `?tag=poorbjorn-20`
3. Check book titles, authors, and facts (search if unsure)
4. **Output as a single `.html` file** in `/home/bjorn/shared/content/` — raw HTML that can be pasted directly into Beehiiv's code editor
5. Use semantic HTML: `<h2>` for sections, `<p>` for text, `<em>` for book titles, `<strong>` for emphasis, `<a>` for links, `<hr>` for section dividers
6. Mark image/video insertion points with `<strong>[BJORN: description]</strong>` — Bjorn adds these manually in Beehiiv
7. Send the file via Discord (message tool with filePath)

## New Articles / Pillar Pages

When creating a new article or pillar page, you MUST also:
1. **Add the article card to `_src/articles.html`** (the articles index) — newest first
2. **Add a hero image** to the page itself (not just OG meta tags — display it visually)
3. **Verify all book covers visually** before using them — never trust that an existing ISBN file contains the right cover. Use the `image` tool to confirm.
4. **Use Amazon search links** (`amazon.com/s?k=Title+Author&tag=poorbjorn-20`) instead of specific edition links (`/dp/ASIN`). Search links are more reliable and won't break when editions change.
5. **Update `sitemap.xml`** with the new URL and today's date
6. If the article references books with existing reviews, **add crosslinks from those review pages back to the article** (see Crosslinking section)

## New Behind the Book Pages

A "Behind the Book" page tells the story of how a famous book got written, based on Bjorn's video.

1. Get subtitles from the YouTube video (yt-dlp)
2. Write the page from Bjorn's actual words — clean up, structure into sections, keep his voice
3. Use the review template as a base but with `Article` structured data (not `Review`)
4. Breadcrumb: Home → Behind the Book → Title
5. Include video embed in the middle of the page
6. Add "📚 You Might Also Like" with link to the review (if exists) and related books
7. Use the book's hero/OG image for the page, book cover for the index card
8. Add to `_src/behind-the-book.html` index (newest first)
9. Crosslink from the review page back to the Behind the Book page
10. Update `sitemap.xml`

## New Highlight Pages (Sponsored)

A highlight page is a dedicated page for a sponsored/submitted book. Structure:

1. Breadcrumb: Home → Highlight
2. "📣 Sponsored Highlight" badge for transparency
3. Book cover, description, "Why It's on BookLab" quick take, key topics
4. Amazon affiliate link + author website link
5. Add to `_src/highlights.html` index (newest first)
6. Add to "Featured This Month" on landing page when actively promoting
7. Update `sitemap.xml`

## Monthly Hub Page (/monthly/)

The monthly hub is a pillar page. When adding a new month:

1. **Create the monthly page** (`_src/monthly/[month]-2026.html`) with book cards, Pick of the Month, etc.
2. **Update the hub page** (`_src/monthly/index.html`):
   - Move the previous "Coming Up" hero content into a regular month card in the archive
   - Update the hero module with the new upcoming month
   - Add Pick of the Month (Bjorn's Pick + Community Pick if applicable) to the new card
   - The data block at the top of the month card section has HTML comments explaining the structure
3. **Update `_src/monthly/index.html` ItemList JSON-LD** — add the new month, increment `numberOfItems`
4. **Add browse-months links** to the new monthly page (include "All Monthly Releases" pill linking to `/monthly/`)
5. **Update sitemap.xml** with the new monthly page URL
6. **Update the hub's hero** when Pick of the Month is decided (for preview months)

**Card structure:** Each month card has:
- Upper section: gold month label (uppercase), Playfair Display title, description, "See the full [Month] list →" CTA
- Lower section: Bjorn's Pick (gold label) on the left, Community Pick (teal label) on the right (if applicable). 60px cover thumbnails.
- No emojis on cards. Match the gradient background style of the hero module.

**Low-maintenance rule:** When a new month is published, only the hub page needs editing — no redesign, just add a card block and update the hero. Keep it mechanical.

## URL Format

**All internal links MUST use extensionless URLs.** Examples:
- ✅ `/reviews/flow-mihaly-csikszentmihalyi`
- ❌ `/reviews/flow-mihaly-csikszentmihalyi.html`
- ✅ `/monthly/`
- ❌ `/monthly/index.html` or `/monthly/index`

Cloudflare Pages resolves both, but consistent extensionless links preserve crawl equity.

## Surgical Changes

- Only touch what was asked
- Don't "improve" adjacent code or formatting
- Match existing style
- Every changed line should trace to the request
