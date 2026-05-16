#!/usr/bin/env python3
"""Generate 1200x630 blog cover PNGs (covers + og)."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
COVERS_DIR = ROOT / "blog" / "assets" / "covers"
OG_DIR = ROOT / "blog" / "assets" / "og"
W, H = 1200, 630

# slug, badge, title, accent (r,g,b)
SPECS = [
    (
        "day-0-series-roadmap",
        "DAY 0 OF N · AI LEARNING SERIES",
        "Why I'm Writing This Series",
        (91, 211, 122),
    ),
    (
        "day-1-kv-cache-memory-bandwidth",
        "DAY 1 OF N · AI LEARNING SERIES",
        "The KV Cache Is a\nMemory Bandwidth Problem",
        (91, 211, 122),
    ),
    (
        "day-2-continuous-batching-vllm",
        "DAY 2 OF N · AI LEARNING SERIES",
        "Continuous Batching in vLLM:\nThe Scheduler Design That\nKeeps GPUs Busy",
        (91, 211, 122),
    ),
    (
        "day-3-token-budgets-cost-structure",
        "DAY 3 OF N · AI LEARNING SERIES",
        "Token Budgets and\nReal Cost Structure",
        (91, 211, 122),
    ),
    (
        "building-tsdb-at-agoda",
        "EXPERIENCE 1 OF N",
        "1.5 Trillion Events/Day\nTSDB at Agoda",
        (147, 197, 253),
    ),
    (
        "when-percentiles-lie-cross-tier-queries",
        "EXPERIENCE 2 OF N",
        "When Percentiles Lie:\nCross-Tier Queries in a\n1.8T/day TSDB",
        (147, 197, 253),
    ),
    (
        "seven-million-iot-sensors-failure-modes",
        "EXPERIENCE 3 OF N",
        "Seven Million IoT Sensors\n— Failure Modes Textbooks Skip",
        (147, 197, 253),
    ),
    (
        "building-ai-inference-observability",
        "LENSAI · PRODUCT",
        "Building a Production-Grade\nAI Inference Observability Pipeline",
        (167, 139, 250),
    ),
]


def _fonts():
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    mono_candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
    ]
    title = badge = None
    for p in candidates:
        if Path(p).exists():
            title = ImageFont.truetype(p, 52)
            badge = ImageFont.truetype(p, 22)
            break
    mono = None
    for p in mono_candidates:
        if Path(p).exists():
            mono = ImageFont.truetype(p, 14)
            break
    if title is None:
        title = ImageFont.load_default()
        badge = title
        mono = title
    return title, badge, mono


def draw_grid(draw: ImageDraw.ImageDraw, accent: tuple[int, int, int]) -> None:
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8))
    draw.rectangle([72, 120, W - 72, H - 80], outline=(*accent, 40), width=1)


def render(slug: str, badge: str, title: str, accent: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (W, H), (15, 15, 14))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_grid(draw, accent)

    title_font, badge_font, mono_font = _fonts()

    # badge pill
    badge_upper = badge.upper()
    bbox = draw.textbbox((0, 0), badge_upper, font=badge_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 18, 10
    px, py = 72, 56
    draw.rounded_rectangle(
        [px, py, px + tw + pad_x * 2, py + th + pad_y * 2],
        radius=6,
        fill=(23, 23, 22),
        outline=(*accent, 180),
        width=1,
    )
    draw.text((px + pad_x, py + pad_y), badge_upper, fill=accent, font=badge_font)

    # title
    y = 160
    for line in title.split("\n"):
        draw.text((72, y), line, fill=(236, 236, 234), font=title_font)
        bbox = draw.textbbox((72, y), line, font=title_font)
        y = bbox[3] + 12

    draw.text((72, H - 56), "AKSHANT SHARMA", fill=(124, 124, 116), font=mono_font)

    # accent bar
    draw.rectangle([72, H - 28, 72 + 120, H - 24], fill=accent)

    out = COVERS_DIR / f"{slug}.png"
    img.save(out, "PNG", optimize=True)
    shutil.copy2(out, OG_DIR / f"{slug}.png")
    print(f"  {slug}.png  badge={badge_upper}")


def main() -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    OG_DIR.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        render(*spec)


if __name__ == "__main__":
    main()
