# New blog post checklist (Profile / GitHub Pages)

Use this whenever you publish a post in an existing series.

---

## Before you start

- [ ] **Delivery Hero Experience posts:** confirm system design with the user **or** read the canonical doc at `akshant-150-day-plan/docs/delivery-hero-rider-tracking-system.md` (image: `docs/assets/delivery-hero-rider-tracking-architecture.png`). DH rider-tracking posts must use that diagram as the architectural core; EKS/HPA stories layer on **Route Service + Route Consumers + OSRM**, not invented Kinesis-only pipelines unless the user adds them. See `.cursor/rules/dh-experience-blogs.mdc`.
- [ ] Pick **series** (`ai-learning`, `experience`, `lensai` — three series only on index/profile).
- [ ] Open the **previous post in that series** as your HTML template (layout, nav, TOC, Mermaid, footer).
- [ ] Note **post number / kicker** by series:
  - **AI Learning** — `Day X of N` (sequential learning index; matches filenames like `day-2-…`).
  - **Experience** — `Experience X of N` only in `series-index.json` sidebar kickers (series position). Do **not** append calendar `Day Y` from the 150-day plan — plan days 1–2 may be code/AI-only while published experience posts skip ahead (e.g. plan day 0 → post 1, day 3 → post 2). Calendar days belong in prose links to AI Learning companions, not sidebar kickers.
  - **LensAI** — product kickers (e.g. `LensAI · Product`).

---

## 1. Create the HTML post

- [ ] Add file under `blog/series/<series-slug>/` with a **kebab-case** name (e.g. `day-2-continuous-batching-vllm.html`).
- [ ] Copy structure from the latest post in that series (nav, hero, grid, TOC sidebar, prose classes, theme toggle, author footer).
- [ ] Set **`data-series-slug`** on `#series-nav-mount` to match the series (e.g. `ai-learning`).
- [ ] Include **`series-nav-dynamic.js`** (same path pattern as sibling posts).
- [ ] Paste your content into the prose area — **no need to refactor** copy for the site.

### Required in `<head>` (sorting + listings depend on this)

- [ ] `<title>` and **`og:title`** — canonical title for homepage / all-posts cards.
- [ ] **`meta name="description"`** and **`og:description`** — excerpt for cards.
- [ ] **Cover image** (LinkedIn / X + on-page hero): add a **1200×630** PNG (infographic style) in **both**:
  - `blog/assets/og/<slug>.png` — used by `og:image` / `twitter:image`
  - `blog/assets/covers/<slug>.png` — same file (or copy) for the visible hero
  - In `<head>`:
  - `og:url` — canonical `https://akshantvats.github.io/Profile/blog/series/.../your-file.html`
  - `og:image` + `og:image:width` (1200) + `og:image:height` (630) — **absolute HTTPS** URL, e.g. `https://akshantvats.github.io/Profile/blog/assets/og/<slug>.png`
  - `twitter:card` = `summary_large_image` and `twitter:image` (same URL as `og:image`)
  - Reuse patterns from the latest post in the same series; defaults: `default-experience.png`, `default-ai-learning.png`, `default-lensai.png`
  - **Badge on cover art:** series label only — `AI LEARNING SERIES`, `EXPERIENCE SERIES`, or `LENSAI · PRODUCT` (plus the post title as the main headline on the infographic). Do **not** put episode numbers on the PNG (`Day X of N`, `Experience X of N`, `Post 2 of 5`, `3 of N`, etc.). Episode kickers stay in HTML tags/meta and sidebar only.
- [ ] **On-page cover** — after `</header>`, before `.post-layout` / prose:
  ```html
  <figure class="post-cover">
    <img src="../../assets/covers/<slug>.png" alt="…" width="1200" height="630" loading="eager">
  </figure>
  ```
  Wrap in `<div class="post-cover-wrap">` (full layout width, not `--read`). CSS from a sibling post:
  `.post-cover-wrap { max-width: var(--layout-max); … }` · `.post-cover img { width:100%; height:auto }` · assets **1200×630** (1.91:1).
- [ ] **`article:published_time`** — ISO date `YYYY-MM-DD` (this is the **sort date**; do not rely on JSON). Set it to the **real go-live date** from your 150-day calendar (not a placeholder month in the future). Within a series, the **newest post must have the latest date** so `blog/index.html` and the homepage sort correctly.
- [ ] Optional: **`article:modified_time`** only if you revise the post later (sort uses the **later** of published vs modified; keep modified ≥ published).

### Required in the body

- [ ] **`.post-meta`** line (e.g. `Jun 2026 · 12 min read`) — display only; sorting uses `<head>` meta above.
- [ ] **Tags** in `.post-tags` if you use filters on the blog index.
- [ ] Series footer / “Up next” if your series uses it.

### Diagrams (required)

Architecture, data-path, and flow posts **must** include Mermaid diagrams. Any post with `<pre class="mermaid">` blocks **must** follow this section — no exceptions.

- [ ] Read **[DIAGRAM-STYLE.md](DIAGRAM-STYLE.md)** — the only Mermaid standard for this blog (GitHub Primer palette, `theme: 'base'`, shared assets).
- [ ] **MUST** link shared assets in every post with diagrams:
  - `<link rel="stylesheet" href="../../assets/blog-diagrams.css">` in `<head>`
  - `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>` before `</body>`
  - `<script src="../../assets/blog-diagrams.js"></script>` after Mermaid CDN (adjust `../../` depth to match series folder)
- [ ] **MUST** wrap diagram source in `<pre class="mermaid">` (not fenced markdown alone).
- [ ] **MUST** use the standard `classDef` pattern from [DIAGRAM-STYLE.md](DIAGRAM-STYLE.md). Copy this block into every comparison or pipeline diagram:

  ```
  classDef pipeline fill:#ffffff,stroke:#059669,color:#111827
  classDef accent fill:#fef3c7,stroke:#d97706,color:#111827
  classDef exact fill:#ecfdf5,stroke:#059669,color:#111827
  classDef semantic fill:#f0f4ff,stroke:#2563eb,color:#111827
  ```

  Apply classes to nodes; use a single inline `style Node fill:#fef3c7,stroke:#d97706,color:#111827` only for accent/warning/Kafka nodes.
- [ ] **Gold reference:** diagram 2 in [Day 11 semantic caching post](series/ai-learning/day-11-semantic-caching-vs-exact-match-redis.html) — flat `flowchart LR`, `classDef pipeline` on default nodes, one cream accent via `style`.
- [ ] **MUST** run automated verification before push:

  ```bash
  node scripts/verify-blog-diagrams.mjs --slug <slug>
  ```

  Use `day11` or `ota` for known posts; add a new entry to `scripts/verify-blog-diagrams.mjs` when shipping a post with diagrams. Exit code must be `0`.
- [ ] **MUST** toggle `#theme-toggle` in the browser and visually confirm **both** themes:
  - **Light:** dark labels (`#111827`) on light/white fills; cream accent keeps dark text.
  - **Dark:** light/grey labels (`#ececea`) on dark green/blue fills; cream accent keeps dark text (`#111827`).

**Anti-patterns (do not ship):**

- `subgraph` wrappers for simple parallel paths — use flat `flowchart LR` / `flowchart TB` with `classDef` instead.
- Inline `style` on every node — use `classDef` + `class`; reserve inline `style` for one accent node per diagram.
- White or near-white text (`#fff`, `#ececea`) on pipeline/default nodes in light mode.
- Light text on dark pipeline fills without dark-mode `classDef` swap (shared JS handles swap — do not fight it with CSS `!important`).
- Missing `blog-diagrams.css` / `blog-diagrams.js` while using Mermaid blocks.
- `htmlLabels: true` or custom Mermaid init that bypasses `blog-diagrams.js`.

---

## 2. Update `blog/series-index.json`

- [ ] Add an entry under the correct **`series.posts`** array.
- [ ] **`href`**: real path when published, e.g. `blog/series/ai-learning/your-file.html` (not `#`).
- [ ] **`kicker`**, **`title`**, **`desc`**: used for **series sidebar** and fallback text; keep in sync with the post theme and the series kicker rules above (Experience = `Experience X of N` only).
- [ ] Put the new post **first** in the series `posts` array (newest at top — matches sort order on `blog/index.html`).
- [ ] **Do not add `addedAt`** — dates come from HTML only.
- [ ] For **drafts**: keep `"href": "#"` until the HTML file exists and is ready to ship.

---

## 3. You do **not** need to touch (already dynamic)

- [ ] ~~Hardcode cards on `index.html` (Writing)~~ — loads from JSON + fetches each post HTML.
- [ ] ~~Hardcode cards on `blog/index.html` (All posts)~~ — same.
- [ ] ~~Edit `series-nav-dynamic.js`~~ — sidebar reads `series-index.json` + current URL.
- [ ] ~~Add `addedAt` in JSON~~ — removed by design.

---

## 4. Editorial pass (AI Learning series)

Before publishing an AI Learning post, run an editorial pass to align voice with the series:

- [ ] **Re-read last 2–3 published AI posts** (e.g. Day 5, Day 6, Day 3) for voice: learning-while-building LensAI, connected sentences, no fake employer incidents, no footnote-stuffed hedging.
- [ ] **Fix awkward inline hedges** — move "verify in their docs" / "field names drift" to the footnote section; keep body prose smooth and confident.
- [ ] **Match Day 3/6 rhythm** — opening = what I built or noticed this week; sections flow with because/so causality, not listicle fragmentation.
- [ ] **LensAI ingest honest** — mention schema gaps and next steps concretely; do not oversell features that do not exist yet.
- [ ] **Experience companion: one short sentence** — do not weave a full narrative about the Experience post.
- [ ] **Max 2 in-body sibling links** — e.g. Day 1 + Day 3; verify `published_time` sort is still correct.
- [ ] **Format: deep-dive not incident** — AI Learning posts are conceptual deep-dives with systems parallels, not production incident stories.

**Anti-patterns (do not ship):**

- Do not leave editorial labels like `(cold open)` in headings.
- Do not rewrite **h1**, **og:title**, **post-subtitle**, or **h2/h3** for style — only strip plan/editorial artifacts (e.g. `(cold open)`, `Options table —`, `(bridge to today)`). Do not replace an existing h2 with new prose rewrites.
- Do not attribute **AI inference, semantic cache, LLM, or embedding** work to employers (Wayfair, Agoda, Walmart, Delivery Hero). Employer names are OK only for **real infra/SWE** work you actually did; use generic DS parallels or link to a separate Experience post instead.

---

## 5. Local sanity check

- [ ] Serve the repo root locally (e.g. `python3 -m http.server 8080` from repo root) so `fetch()` can load `series-index.json` and post HTML.
- [ ] Open the **post HTML**: layout, TOC, Mermaid, dark mode.
- [ ] Open **`blog/index.html`**: new post appears under the right series, **newest first** within the series.
- [ ] Open **`index.html` → Writing**: if the post is **live** (`article:published_time` ≤ today), it can surface in the top-2 series / top-2 posts rules.
- [ ] Open the post again: **series sidebar** shows the new entry and highlights the current page.

---

## 6. Publish

- [ ] `git add` the new HTML + `blog/series-index.json` (only those unless you changed something else).
- [ ] Commit with a clear message (only when the user asks).
- [ ] **Before push:** `git fetch origin` → merge or rebase `origin/main` → resolve conflicts if any (`blog/series-index.json`, shared scripts) → confirm mergeable locally or on GitHub → re-run [§5 Local sanity check](#5-local-sanity-check).
- [ ] `git push` to `main` (GitHub Pages deploys from there).
- [ ] After ~1–2 min, **hard refresh** (Cmd+Shift+R) on homepage, `/blog/`, and the post — cached `series-index.json` can look stale.

---

## Quick reference: what drives “recent” vs “published”

| Question | Answer |
|----------|--------|
| Is it listed on All posts / homepage fetch? | `href` ≠ `#` and HTML fetch succeeds with **`article:published_time`** |
| Sort order (newest first) | `max(published_time, modified_time)` from HTML |
| Homepage “top 2 series” priority | Among posts with date **≤ today** (`activityLive`), then fill if needed |
| Sidebar draft posts | `href: "#"` still listed, no link, draft styling |
| Card title / excerpt | Scraped from post HTML (`og:title`, description) |

---

## Optional: new series (rare)

- [ ] Add a full **`series`** block in `series-index.json` (`slug`, `title`, `slugLine`, `navSubtitle`, `posts`, …).
- [ ] Create first post HTML with matching **`data-series-slug`**.
- [ ] Copy nav/series patterns from an existing series post.

---

## Template reminder

`blog/POST-TEMPLATE.html` documents meta tags and structure — keep **`article:published_time`** in sync with when you want the post to rank as “live.”
