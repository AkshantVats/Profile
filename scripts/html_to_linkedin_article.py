#!/usr/bin/env python3
"""
Convert Profile blog post HTML to LinkedIn article paste text (with image placeholders).

LinkedIn paste tips:
  - Paste section by section; LinkedIn's editor can drop formatting on huge pastes.
  - Upload images via LinkedIn's image button at each [IMAGE N: caption] marker.
  - Apply heading styles with the toolbar, or keep ## lines and format manually.
  - External image URLs are listed at the top for download/upload; local paths are copied
    to scripts/output/ when possible.

Usage:
  python scripts/html_to_linkedin_article.py path/to/post.html
  python scripts/html_to_linkedin_article.py path/to/post.html --output article.md
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional, Tuple

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

SKIP_CLASS_PREFIXES = ("series-footer", "footnote-row")


def extract_tag_content(html: str, pattern: str) -> Optional[str]:
    m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def normalize_ws(s: str) -> str:
    s = unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_metadata(html: str) -> Tuple[str, str]:
    title = extract_tag_content(
        html, r'<h1[^>]*class="[^"]*post-title[^"]*"[^>]*>(.*?)</h1>'
    )
    if not title:
        title = extract_tag_content(html, r"<h1[^>]*>(.*?)</h1>")
    subtitle = extract_tag_content(
        html, r'<p[^>]*class="[^"]*post-subtitle[^"]*"[^>]*>(.*?)</p>'
    )
    return normalize_ws(strip_tags(title or "")), normalize_ws(strip_tags(subtitle or ""))


def extract_prose_html(html: str) -> str:
    m = re.search(
        r'<article[^>]*class="[^"]*prose[^"]*"[^>]*>(.*?)</article>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        raise SystemExit('Could not find <article class="prose"> in HTML.')
    return m.group(1)


def split_prose_and_footnotes(prose_html: str) -> Tuple[str, str]:
    """Footnote block is last in article; split at footnote-row open tag."""
    marker = 'class="footnote-row"'
    idx = prose_html.find(marker)
    if idx < 0:
        return prose_html, ""
    start = prose_html.rfind("<div", 0, idx)
    if start < 0:
        return prose_html, ""
    return prose_html[:start].rstrip(), prose_html[start:]


def resolve_image_src(src: str, html_path: Path) -> Tuple[str, Optional[Path]]:
    src = src.strip()
    if src.startswith("//"):
        src = "https:" + src
    if src.startswith(("http://", "https://")):
        return src, None
    local = (html_path.parent / src).resolve()
    if local.is_file():
        return str(local), local
    return src, None


class LinkedInHTMLConverter(HTMLParser):
    def __init__(self, html_path: Path):
        super().__init__(convert_charrefs=True)
        self.html_path = html_path
        self.lines: List[str] = []
        self._buf: List[str] = []
        self._stack: List[dict] = []
        self._list_depth = 0
        self._in_pre = False
        self._pre_class = ""
        self._pre_lines: List[str] = []
        self._in_table = False
        self._table_rows: List[List[str]] = []
        self._current_row: List[str] = []
        self._in_cell = False
        self._cell_buf: List[str] = []
        self._skip_depth = 0
        self.images: List[dict] = []
        self._image_counter = 0
        self._diagram_counter = 0
        self._stat_num = ""
        self._in_stat_cell = False
        self._in_attr_box = False
        self._attr_label_done = False

    def _classes(self, attrs: dict) -> set:
        return set(attrs.get("class", "").split())

    def _text(self) -> str:
        return normalize_ws("".join(self._buf))

    def _clear_buf(self) -> None:
        self._buf = []

    def _line(self, s: str = "") -> None:
        if s or (self.lines and self.lines[-1] != ""):
            self.lines.append(s.rstrip())

    def _blank(self) -> None:
        if not self.lines or self.lines[-1] != "":
            self.lines.append("")

    def _push(self, **frame) -> None:
        self._stack.append(frame)

    def _pop(self) -> dict:
        return self._stack.pop() if self._stack else {}

    def _skipping(self) -> bool:
        return self._skip_depth > 0

    def handle_starttag(self, tag: str, attrs_list: List[Tuple[str, Optional[str]]]) -> None:
        attrs = {k: (v or "") for k, v in attrs_list}
        classes = self._classes(attrs)

        if any(c.startswith(p) for c in classes for p in SKIP_CLASS_PREFIXES):
            self._skip_depth += 1
            self._push(tag=tag, skip=True)
            return

        if tag in ("div", "span") and "attr-label" in classes:
            self._clear_buf()
            self._push(tag="attr-label", classes=classes)
            return

        if tag == "a":
            self._push(tag="a", attrs=attrs, classes=classes, href=attrs.get("href", ""))
            if self._skipping():
                return
            return

        self._push(tag=tag, attrs=attrs, classes=classes)

        if self._skipping():
            return

        if tag == "img":
            src = attrs.get("src", "")
            alt = attrs.get("alt", "") or "Image"
            url, local = resolve_image_src(src, self.html_path)
            self._image_counter += 1
            entry = {"n": self._image_counter, "caption": alt, "url": url, "local": local}
            self.images.append(entry)
            self._blank()
            self._line(f"[IMAGE {self._image_counter}: {alt}]")
            self._line(f"  ({url})")
            self._blank()
            return

        if tag == "h2":
            self._clear_buf()
            self._blank()
            return
        if tag == "h3":
            self._clear_buf()
            self._blank()
            return
        if tag == "p":
            return
        if tag in ("strong", "b"):
            self._buf.append("**")
            return
        if tag in ("em", "i"):
            self._buf.append("*")
            return
        if tag == "code" and not self._in_pre:
            self._buf.append("`")
            return
        if tag == "br":
            self._buf.append("\n")
            return
        if tag in ("ul", "ol"):
            self._list_depth += 1
            return
        if tag == "li":
            indent = "  " * max(0, self._list_depth - 1)
            self._buf.append(f"\n{indent}• ")
            return
        if tag == "pre":
            self._in_pre = True
            self._pre_class = attrs.get("class", "")
            self._pre_lines = []
            return
        if tag == "table":
            self._in_table = True
            self._table_rows = []
            return
        if tag == "tr" and self._in_table:
            self._current_row = []
            return
        if tag in ("th", "td") and self._in_table:
            self._in_cell = True
            self._cell_buf = []
            return
        if tag == "div":
            if "stat-callout" in classes:
                self._blank()
            elif "stat-cell" in classes:
                self._in_stat_cell = True
                self._stat_num = ""
            elif "attr-box" in classes:
                self._in_attr_box = True
                self._attr_label_done = False
                self._blank()
            elif "pullquote" in classes:
                self._blank()
                self._push(tag="pullquote")
            elif "diagram-box" in classes:
                self._blank()
                self._push(tag="diagram")
        if tag == "sup":
            self._buf.append("(")

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return

        top = self._stack[-1]
        if top.get("skip"):
            self._pop()
            if self._skip_depth:
                self._skip_depth -= 1
            return

        if self._skipping():
            self._pop()
            return

        if tag == "a" and top.get("tag") == "a":
            frame = self._pop()
            href = frame.get("href", "")
            link_text = self._text()
            self._clear_buf()
            if link_text and href:
                self._buf.append(f"{link_text} ({href})")
            elif href:
                self._buf.append(href)
            return

        if top.get("tag") == "pullquote" and tag == "div":
            self._pop()
            return
        if top.get("tag") == "diagram" and tag == "div":
            t = self._text()
            self._clear_buf()
            if t:
                short = t[:240] + ("…" if len(t) > 240 else "")
                self._line(f"*[Diagram: {short}]*")
            self._pop()
            self._blank()
            return
        if top.get("tag") == "attr-label" and tag in ("span", "div"):
            label = self._text()
            self._clear_buf()
            self._line(f"**{label}**")
            self._attr_label_done = True
            self._pop()
            return

        attrs = top.get("attrs", {})
        classes = top.get("classes", set())

        if tag == "h2":
            self._line(f"## {self._text().upper()}")
            self._clear_buf()
            self._blank()
        elif tag == "h3":
            self._line(f"### {self._text()}")
            self._clear_buf()
            self._blank()
        elif tag == "p":
            t = self._text()
            if t:
                if any(f.get("tag") == "pullquote" for f in self._stack):
                    for ln in t.split("\n"):
                        self._line(f"> {ln}")
                else:
                    self._line(t)
            self._clear_buf()
            if not self._in_stat_cell:
                self._blank()
        elif tag in ("strong", "b"):
            self._buf.append("**")
        elif tag in ("em", "i"):
            self._buf.append("*")
        elif tag == "code" and not self._in_pre:
            self._buf.append("`")
        elif tag in ("ul", "ol"):
            self._list_depth = max(0, self._list_depth - 1)
            self._blank()
        elif tag == "pre":
            self._in_pre = False
            body = "\n".join(self._pre_lines).strip()
            self._blank()
            if "mermaid" in self._pre_class:
                self._diagram_counter += 1
                self._line(
                    f"*[Diagram {self._diagram_counter}: Mermaid — screenshot from live post or redraw]*"
                )
                for ln in body.splitlines():
                    self._line(f"  {ln}")
            else:
                for ln in body.splitlines():
                    self._line(f"    {ln}")
            self._blank()
            self._pre_lines = []
        elif tag == "table" and self._in_table:
            self._in_table = False
            if self._table_rows:
                self._blank()
                for row in self._table_rows:
                    self._line(" | ".join(row))
                self._blank()
        elif tag == "tr" and self._in_table:
            if self._current_row:
                self._table_rows.append(self._current_row)
        elif tag in ("th", "td") and self._in_table:
            self._in_cell = False
            self._current_row.append(normalize_ws("".join(self._cell_buf)))
            self._cell_buf = []
        elif tag == "div":
            if "stat-cell" in classes:
                self._in_stat_cell = False
            elif "stat-callout" in classes:
                self._blank()
            elif "attr-box" in classes:
                t = self._text()
                if t:
                    self._line(t)
                self._clear_buf()
                self._in_attr_box = False
                self._blank()
            elif "pullquote" in classes:
                self._blank()
        elif tag == "span":
            if "stat-num" in classes:
                self._stat_num = self._text()
                self._clear_buf()
            elif "stat-label" in classes:
                label = self._text()
                self._clear_buf()
                if self._stat_num:
                    self._line(f"**{self._stat_num}** — {label}")
                else:
                    self._line(f"**{label}**")
        elif tag == "sup":
            self._buf.append(")")

        if self._stack and self._stack[-1].get("tag") == tag:
            self._pop()

    def handle_data(self, data: str) -> None:
        if self._skipping():
            return
        if self._in_pre:
            self._pre_lines.append(data)
            return
        if self._in_cell:
            self._cell_buf.append(data)
            return
        self._buf.append(data)

    def convert(self, fragment: str) -> str:
        self.feed(fragment)
        text = "\n".join(self.lines)
        text = re.sub(r"\*\*\*\*+", "**", text)
        text = re.sub(r"^## \s*$\n", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def format_footnotes(footnotes_html: str) -> str:
    if not footnotes_html.strip():
        return ""
    bullets: List[str] = []
    for m in re.finditer(
        r'<a\s+href="([^"]+)"[^>]*>.*?<span>(.*?)</span>\s*</a>',
        footnotes_html,
        re.DOTALL | re.IGNORECASE,
    ):
        href = m.group(1)
        text = normalize_ws(strip_tags(m.group(2)))
        bullets.append(f"• {text} ({href})")
    if not bullets:
        return ""
    return "\n".join(["", "---", "", "## END NOTES", ""] + bullets)



def copy_local_images(images: List[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for img in images:
        local: Optional[Path] = img.get("local")
        if not local:
            continue
        dest = OUTPUT_DIR / f"image_{img['n']}{local.suffix or '.bin'}"
        shutil.copy2(local, dest)
        img["copied_to"] = dest


def preprocess_prose_html(html: str) -> str:
    """Simplify footnote markers and in-page anchor links for LinkedIn paste."""
    html = re.sub(r"<sup[^>]*>.*?</sup>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(
        r'<a\s+href="#[^"]*"[^>]*>\s*(\d+)\s*</a>',
        r"(\1)",
        html,
        flags=re.IGNORECASE,
    )
    return html


def build_document(html_path: Path, include_footnotes: bool = True) -> str:
    html = html_path.read_text(encoding="utf-8")
    title, subtitle = extract_metadata(html)
    prose_html = preprocess_prose_html(extract_prose_html(html))

    prose_html = re.sub(
        r'<div class="series-footer">.*?</div>',
        "",
        prose_html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    body_html, footnotes_html = split_prose_and_footnotes(prose_html)

    conv = LinkedInHTMLConverter(html_path)
    body = conv.convert(body_html)

    parts: List[str] = []
    if conv.images:
        copy_local_images(conv.images)
        parts.extend(
            [
                "=== IMAGES TO UPLOAD ===",
                "Upload via LinkedIn's image button at each [IMAGE N] marker below.",
                "",
            ]
        )
        for img in conv.images:
            line = f"  {img['n']}. {img['caption']}"
            if img.get("copied_to"):
                line += f"\n     → {img['copied_to']}"
            else:
                line += f"\n     → {img['url']}"
            parts.append(line)
        parts.extend(["", "=== ARTICLE ===", ""])

    parts.append(title)
    if subtitle:
        parts.extend(["", subtitle])
    parts.extend(["", body])

    if include_footnotes:
        fn = format_footnotes(footnotes_html)
        if fn:
            parts.append(fn)

    if conv._diagram_counter:
        parts.extend(
            [
                "",
                "---",
                "*Tip: Mermaid diagrams export as text — screenshot the live post for LinkedIn visuals.*",
            ]
        )

    doc = "\n".join(parts)
    doc = re.sub(r"\n{3,}", "\n\n", doc)
    return doc.strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert a Profile blog HTML post to LinkedIn article text."
    )
    ap.add_argument("html_file", type=Path, help="Path to blog post .html")
    ap.add_argument("-o", "--output", type=Path, help="Write to file instead of stdout")
    ap.add_argument("--no-footnotes", action="store_true", help="Skip end notes")
    args = ap.parse_args()

    html_path = args.html_file.resolve()
    if not html_path.is_file():
        sys.exit(f"File not found: {html_path}")

    doc = build_document(html_path, include_footnotes=not args.no_footnotes)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(doc, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
