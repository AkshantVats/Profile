#!/usr/bin/env python3
"""
Generate scripts/cover_generated/<slug>.png sources for Day 12 posts.

Note: We can't use Cursor's GenerateImage tool in this environment, so we
create lightweight deterministic placeholder covers (badge + headline + grid).
These sources are then installed into blog/assets/{covers,og} via:
  python3 scripts/generate_blog_covers.py --from-content --slug <slug>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
GENERATED_DIR = SCRIPT_DIR / "cover_generated"

# Make sibling imports work when running from repo root.
sys.path.insert(0, str(SCRIPT_DIR))
from generate_blog_covers import (  # noqa: E402
    W,
    H,
    LETTERBOX_BG,
    SERIES_LABEL,
    draw_grid,
    _draw_series_pill,
    _font,
)


ACCENT_RGB: dict[str, tuple[int, int, int]] = {
    # electric blue #64b4ff
    "ota-at-scale-at-least-once-is-a-feature": (100, 180, 255),
    # neon green #5bd37a
    "day-11-semantic-caching-vs-exact-match-redis": (91, 211, 122),
}

TITLE_LINES: dict[str, list[str]] = {
    "ota-at-scale-at-least-once-is-a-feature": [
        "OTA at Scale — At-Least-Once",
        "Is a Feature, Not a Bug",
    ],
    "day-11-semantic-caching-vs-exact-match-redis": [
        "Semantic Caching vs",
        "Exact-Match Redis",
    ],
}


def render_placeholder(slug: str) -> None:
    accent = ACCENT_RGB[slug]
    label = SERIES_LABEL[slug]
    lines = TITLE_LINES[slug]

    # Base + grid (keeps covers visually consistent with the rest of the series)
    img = Image.new("RGB", (W, H), LETTERBOX_BG)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_grid(draw, accent)

    # Badge: series name only (no day numbers on covers)
    _draw_series_pill(
        draw,
        label,
        cx=165,
        cy=44,
        outline=accent,
        text_fill=(220, 225, 235),
        font_size=15,
    )

    # Headline
    title_font = _font(54, bold=True)
    y = 180
    for i, line in enumerate(lines):
        draw.text((72, y), line, fill=(236, 236, 234), font=title_font)
        bbox = draw.textbbox((72, y), line, font=title_font)
        y = bbox[3] + (16 if i == 0 else 10)

    # Small accent underline (subtle infographic flavor)
    underline_y = H - 84
    draw.rectangle([72, underline_y, 360, underline_y + 8], fill=accent)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GENERATED_DIR / f"{slug}.png"
    img.save(out_path, "PNG", optimize=True)
    print(f"  ✓ {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        help="Only generate these slugs (repeatable).",
    )
    args = parser.parse_args()

    slugs = args.slugs or list(ACCENT_RGB.keys())
    missing = [s for s in slugs if s not in ACCENT_RGB or s not in TITLE_LINES]
    if missing:
        raise SystemExit(f"Unknown/missing slug mappings: {missing}")

    for slug in slugs:
        if slug not in SERIES_LABEL:
            raise SystemExit(f"Slug not in SERIES_LABEL: {slug}")
        render_placeholder(slug)


if __name__ == "__main__":
    main()

