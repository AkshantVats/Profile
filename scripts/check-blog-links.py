#!/usr/bin/env python3
"""Verify series-index.json hrefs and relative links under blog/series/."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES_INDEX = ROOT / "blog" / "series-index.json"
SERIES_DIR = ROOT / "blog" / "series"

HREF_RE = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "#", "data:")


def is_checkable_relative(href: str) -> bool:
    if not href or href.startswith(SKIP_PREFIXES):
        return False
    if href.startswith("javascript:"):
        return False
    return True


def resolve_href(base_file: Path, href: str) -> Path:
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if clean.startswith("/"):
        return ROOT / clean.lstrip("/")
    return (base_file.parent / clean).resolve()


def check_series_index() -> list[str]:
    errors: list[str] = []
    if not SERIES_INDEX.is_file():
        return [f"missing manifest: {SERIES_INDEX.relative_to(ROOT)}"]

    data = json.loads(SERIES_INDEX.read_text(encoding="utf-8"))
    for series in data.get("series", []):
        slug = series.get("slug", "?")
        for post in series.get("posts", []):
            href = post.get("href", "")
            title = post.get("title", "(untitled)")
            if not href or href == "#":
                continue
            target = ROOT / href
            if not target.is_file():
                errors.append(
                    f"series-index [{slug}] {title!r}: missing file {href}"
                )
    return errors


def check_series_html() -> list[str]:
    errors: list[str] = []
    if not SERIES_DIR.is_dir():
        return errors

    for html in sorted(SERIES_DIR.rglob("*.html")):
        text = html.read_text(encoding="utf-8", errors="replace")
        for match in HREF_RE.finditer(text):
            href = match.group(1).strip()
            if not is_checkable_relative(href):
                continue
            target = resolve_href(html, href)
            try:
                target.relative_to(ROOT)
            except ValueError:
                continue
            if not target.is_file():
                errors.append(
                    f"{html.relative_to(ROOT)}: broken href {href!r}"
                )
    return errors


def main() -> int:
    errors = check_series_index() + check_series_html()
    if errors:
        print("Link check failed:\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("Link check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
