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
3. Deploy: `bash scripts/deploy.sh`
   - **ALWAYS use the deploy script** — never run `wrangler pages deploy` directly.
   - The script builds a clean temp directory (excluding `_src/`, dev files, etc.), deploys from there, and cleans up.
   - This is the ONLY way to prevent `_src/` duplicates from going live (`.cfignore` does NOT work with direct wrangler uploads).

## Editing Checklist

Before making changes:
- [ ] State what you're changing and what you're NOT touching
- [ ] Edits go in `_src/`, not the output files

After making changes:
- [ ] Run `build.py` successfully (no orphan warnings, no sitemap gaps)
- [ ] Verify the live page renders correctly
- [ ] Check mobile rendering
- [ ] **Update `sitemap.xml`** if pages were added/changed (update `<lastmod>` dates)
- [ ] **Sitemap audit must pass** — `build.py` will warn if any `_src/` page is missing from sitemap.xml. Fix before deploying.

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

### Contextual Inline Links

When a review or article **mentions another book by name** that has its own page on the site, **always link it inline** within the body text. These in-context links are the highest-value internal links for SEO — they signal topical relevance to search engines and keep readers clicking deeper.

Example: `I picked this up after reading Nassim Taleb's <em><a href="/reviews/antifragile-nassim-taleb">Antifragile</a></em>`

- Check `_src/reviews/` for existing review pages before publishing
- Link naturally within the sentence — don't force it
- One link per mention is enough (don't re-link every occurrence)
- **Only link to existing pages on the site** — do NOT add Amazon affiliate links inline in body text. Amazon links belong in the "Buy on Amazon" buttons only. This keeps navigation behavior predictable: inline links = our site, buttons = Amazon.

### "Read Review →" Buttons

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

## New Highlight Pages

A highlight page is a dedicated page for a highlighted/submitted book. Structure:

**Gold standard:** [`/highlights/the-curious-mind-of-elon-musk-charles-steel`](https://booklabbybjorn.com/highlights/the-curious-mind-of-elon-musk-charles-steel) — use this as the blueprint for all highlight pages.

1. Breadcrumb: Home → Highlight
2. "📣 Highlight" badge
3. Hero image, book cover, and highlighted page photos where relevant
4. **Required sections (in order):** What's It About?, 🎯 Why It's on BookLab, 📖 Key Topics, 📝 Highlights from My Reading, 📚 You Might Also Like
5. Amazon affiliate link + **backlink to author's homepage**
6. `<div class="might-also-like">` wrapper for the "You Might Also Like" section
7. Add to `_src/highlights.html` index (newest first)
8. Add to "Featured This Month" on landing page when actively promoting
9. Update `sitemap.xml`

## Breadcrumbs

Every content page needs a breadcrumb trail at the top (after nav, before header). Format:

- **Reviews:** `Home → Reviews → [Title]`
- **Monthly:** `Home → Monthly Releases → [Month Year]`
- **Articles:** `Home → Articles → [Title]`
- **Behind the Book:** `Home → Behind the Book → [Title]`
- **Highlights:** `Home → Highlight → [Title]`

For monthly pages, use inline styles (since they don't include `review.css`):

```html
<div style="max-width:900px;margin:0 auto;padding:20px 20px 0">
<div style="font-size:.85rem;color:var(--muted)"><a href="/" style="color:var(--muted)">Home</a> → <a href="/monthly/" style="color:var(--muted)">Monthly Releases</a> → August 2026</div>
</div>
```

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

## Internal Links

**All internal `href` and `src` attributes MUST be root-relative (leading `/`) or absolute URLs.**

- ✅ `href="/reviews/flow-mihaly-csikszentmihalyi"`
- ✅ `src="/images/covers/9780060984709.jpg"`
- ❌ `href="reviews/flow-mihaly-csikszentmihalyi"` (relative — will stack paths when crawled from subdirectories)
- ❌ `src="images/covers/9780060984709.jpg"` (relative)
- ❌ `href="../favicon.ico"` (relative)

`build.py` will flag violations in the relative link audit. Fix before deploying.

**Canonical and og:url MUST match the page's actual URL path.** Both should be identical. If you move a page, update both.

## Redirects (`_redirects`)

When renaming or moving a page, add a 301 redirect in `_redirects` (Cloudflare Pages format):

```
/old-path /new-path 301
/old-path.html /new-path 301
```

Always add both extensionless and `.html` variants.

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
