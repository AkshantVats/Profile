# Profile scripts

## `html_to_linkedin_article.py`

Convert a blog post HTML file to LinkedIn-friendly article text: plain headings (original casing), stat callouts as simple lines, Mermaid diagrams as PNGs, and image upload markers.

```bash
python scripts/html_to_linkedin_article.py blog/series/experience/seven-million-iot-sensors-failure-modes.html
```

Defaults:

- Article text: `scripts/linkedin-export/<post-slug>.txt`
- Diagram PNGs + `.mmd` sources: `scripts/linkedin-export/<post-slug>/diagram-1.png`, …

**Social link previews:** commit a **1200×630** image to `blog/assets/og/<slug>.png` and set `og:image` / `twitter:image` in the post HTML (absolute `https://akshantvats.github.io/Profile/blog/assets/og/...` URLs). Stat/diagram PNGs from this export can be cropped for OG art (see `seven-million-iot-sensors.png`). After deploy, refresh LinkedIn cache via [Post Inspector](https://www.linkedin.com/post-inspector/).

Mermaid rendering tries, in order: [Kroki](https://kroki.io) HTTP API → `npx @mermaid-js/mermaid-cli` → `docker run minlag/mermaid-cli`.

Stdlib + network for Kroki. Local images (if any) are copied to `scripts/output/`.

## `check-blog-links.py`

Validate internal links in blog HTML (see script help).
