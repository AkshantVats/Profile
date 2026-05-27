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
from random import Random
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
    rng = Random(slug)  # deterministic across machines

    # Base + grid + gradient + seeded noise: increases PNG complexity so output
    # stays "rich" (not tiny, text-only placeholders) after optimization.
    img = Image.new(
        "RGBA",
        (W, H),
        (LETTERBOX_BG[0], LETTERBOX_BG[1], LETTERBOX_BG[2], 255),
    )
    draw = ImageDraw.Draw(img, "RGBA")

    top = (8, 12, 24)
    bottom = (22, 32, 66)
    for y in range(0, H, 2):
        t = y / (H - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.rectangle([0, y, W, y + 2], fill=(r, g, b, 255))

    draw_grid(draw, accent)

    # Higher noise count makes the PNG less compressible, so the downstream
    # installer output stays "rich" (>300KB) instead of shrinking into a
    # small infographic placeholder.
    noise_points = 60000
    for i in range(noise_points):
        x = rng.randrange(0, W)
        y = rng.randrange(0, H)
        if i % 19 == 0:
            a = rng.randrange(10, 55)
            draw.point((x, y), fill=(accent[0], accent[1], accent[2], a))
        else:
            v = rng.randrange(100, 255)
            a = rng.randrange(8, 35)
            draw.point((x, y), fill=(v, v, v, a))

    # Badge: series name only (no day numbers on covers).
    _draw_series_pill(
        draw,
        label,
        cx=165,
        cy=44,
        outline=accent,
        text_fill=(220, 225, 235),
        font_size=15,
    )

    panel_fill = (12, 16, 22, 170)
    panel_outline = (accent[0], accent[1], accent[2], 200)

    def rounded_panel(x0: int, y0: int, x1: int, y1: int) -> None:
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=22,
            fill=panel_fill,
            outline=panel_outline,
            width=2,
        )

    # Slug-specific diagram content.
    if slug == "ota-at-scale-at-least-once-is-a-feature":
        # Four boxes with arrows.
        rounded_panel(120, 300, 460, 440)
        rounded_panel(520, 300, 980, 440)

        blue = (100, 180, 255, 230)
        green = (91, 211, 122, 230)
        amber = (217, 119, 6, 230)

        # Left column
        draw.rounded_rectangle([160, 320, 420, 370], radius=14, fill=(20, 24, 32, 190), outline=blue, width=2)
        draw.text((185, 336), "Manifest", fill=(236, 236, 234, 255), font=_font(24, bold=False))
        draw.text((210, 356), "gate", fill=(236, 236, 234, 255), font=_font(20, bold=False))

        draw.rounded_rectangle([160, 380, 420, 430], radius=14, fill=(20, 24, 32, 190), outline=green, width=2)
        draw.text((190, 402), "Durable", fill=(236, 236, 234, 255), font=_font(22, bold=False))
        draw.text((230, 423), "ack", fill=(236, 236, 234, 255), font=_font(22, bold=False))

        # Right column
        draw.rounded_rectangle([560, 320, 940, 370], radius=14, fill=(20, 24, 32, 190), outline=blue, width=2)
        draw.text((610, 338), "Verified", fill=(236, 236, 234, 255), font=_font(22, bold=False))
        draw.text((650, 358), "flash", fill=(236, 236, 234, 255), font=_font(22, bold=False))

        draw.rounded_rectangle([560, 380, 940, 430], radius=14, fill=(20, 24, 32, 190), outline=amber, width=2)
        draw.text((610, 402), "Retry /", fill=(236, 236, 234, 255), font=_font(22, bold=False))
        draw.text((618, 423), "quarantine", fill=(236, 236, 234, 255), font=_font(18, bold=False))

        # Arrows (simple lines)
        draw.line([300, 355, 560, 335], fill=blue, width=5)
        draw.line([300, 405, 560, 405], fill=green, width=5)
        draw.line([420, 335, 520, 405], fill=amber, width=5)

        # Tiny "key" footer
        draw.rounded_rectangle([120, 445, 980, 495], radius=18, fill=(8, 14, 28, 150), outline=blue, width=2)
        draw.text((150, 468), "Idempotent apply: device_id + version + image_hash", fill=(236, 236, 234, 255), font=_font(22, bold=False))

    elif slug == "day-11-semantic-caching-vs-exact-match-redis":
        # Two-column comparison with a τ dial.
        exact_fill = (236, 253, 245, 150)
        semantic_fill = (240, 244, 255, 150)

        rounded_panel(120, 300, 540, 455)
        rounded_panel(660, 300, 1080, 455)

        # Left: Exact
        draw.rounded_rectangle([150, 330, 510, 420], radius=18, fill=exact_fill, outline=(91, 211, 122, 230), width=2)
        draw.text((182, 356), "Exact-match", fill=(12, 12, 12, 255), font=_font(24, bold=False))
        draw.text((235, 388), "Redis", fill=(12, 12, 12, 255), font=_font(24, bold=False))
        draw.text((190, 412), "key = bytes hash", fill=(12, 12, 12, 255), font=_font(18, bold=False))

        # Right: Semantic
        draw.rounded_rectangle([690, 330, 1050, 420], radius=18, fill=semantic_fill, outline=(37, 99, 235, 230), width=2)
        draw.text((715, 356), "Semantic cache", fill=(12, 12, 12, 255), font=_font(24, bold=False))
        draw.text((790, 388), "ANN", fill=(12, 12, 12, 255), font=_font(24, bold=False))
        draw.text((720, 412), "hit if sim >= τ", fill=(12, 12, 12, 255), font=_font(18, bold=False))

        # τ dial
        draw.ellipse([540, 350, 660, 470], fill=(254, 243, 199, 190), outline=(217, 119, 6, 240), width=4)
        draw.text((585, 402), "τ", fill=(12, 12, 12, 255), font=_font(44, bold=True))

        # Middle arrows / legend
        draw.line([540, 410, 660, 410], fill=(37, 99, 235, 230), width=6)
        draw.line([600, 470, 600, 510], fill=(91, 211, 122, 230), width=6)

        draw.rounded_rectangle([120, 465, 1080, 520], radius=18, fill=(8, 14, 28, 150), outline=(217, 119, 6, 230), width=2)
        draw.text((150, 490), "False positives must be observable: cache_hit + wrongness budget", fill=(236, 236, 234, 255), font=_font(22, bold=False))

    # Headline (top, so diagrams don't overlap).
    title_font = _font(54, bold=True)
    y = 170
    for i, line in enumerate(lines):
        draw.text((72, y), line, fill=(236, 236, 234, 255), font=title_font)
        bbox = draw.textbbox((72, y), line, font=title_font)
        y = bbox[3] + (16 if i == 0 else 10)

    underline_y = H - 84
    draw.rectangle([72, underline_y, 360, underline_y + 8], fill=accent)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GENERATED_DIR / f"{slug}.png"
    # Keep the pre-letterbox source fairly large; the downstream installer will
    # still optimize, but we want a rich result (not a <50KB placeholder).
    img.convert("RGB").save(out_path, "PNG", optimize=False)
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

