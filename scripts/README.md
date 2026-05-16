# Profile scripts

## `html_to_linkedin_article.py`

Convert a blog post HTML file to LinkedIn-friendly article text (headings, bold, links, diagram notes, image upload markers).

```bash
python scripts/html_to_linkedin_article.py blog/series/agoda/seven-million-iot-sensors-failure-modes.html
python scripts/html_to_linkedin_article.py path/to/post.html --output scripts/output/article.md
```

Stdlib only (`html.parser`). Local images are copied to `scripts/output/` when present.
