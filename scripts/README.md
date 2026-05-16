# Profile scripts

## `html_to_linkedin_article.py`

Convert a blog post HTML file to LinkedIn-friendly article text: plain headings (original casing), stat callouts as simple lines, Mermaid diagrams as PNGs, and image upload markers.

```bash
python scripts/html_to_linkedin_article.py blog/series/agoda/seven-million-iot-sensors-failure-modes.html
```

Defaults:

- Article text: `scripts/linkedin-export/<post-slug>.txt`
- Diagram PNGs + `.mmd` sources: `scripts/linkedin-export/<post-slug>/diagram-1.png`, …

Mermaid rendering tries, in order: [Kroki](https://kroki.io) HTTP API → `npx @mermaid-js/mermaid-cli` → `docker run minlag/mermaid-cli`.

Stdlib + network for Kroki. Local images (if any) are copied to `scripts/output/`.

## `check-blog-links.py`

Validate internal links in blog HTML (see script help).
