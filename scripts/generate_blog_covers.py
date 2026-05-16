#!/usr/bin/env python3
"""Generate 1200×630 blog cover PNGs (covers/ + og/).

Modes:
  --rich (default)  Copy user infographic art (with badge fixes) or pre-generated rich PNGs.
  --plain           Deprecated: dark grid + plain text (avoid for published posts).

Cover badges: series label only (no Day X, Experience N, Post X of N on the image).
Episode numbers belong in HTML kickers/meta, not on cover art.

User art lives outside the repo; set PROFILE_COVER_ASSETS to override the default path.
Rich AI-generated PNGs for posts without user art: scripts/cover_assets_rich/ (committed).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
COVERS_DIR = ROOT / "blog" / "assets" / "covers"
OG_DIR = ROOT / "blog" / "assets" / "og"
SCRIPT_DIR = Path(__file__).resolve().parent
RICH_GENERATED_DIR = SCRIPT_DIR / "cover_assets_rich"

DEFAULT_ASSETS = Path(
    "/Users/akshant/.cursor/projects/Users-akshant-Desktop-github-Profile/assets"
)

# LinkedIn / Open Graph standard (1.91:1). All exports are exactly W×H — never square.
W, H = 1200, 630
LETTERBOX_BG = (8, 14, 28)  # dark bars for square/tall sources

# slug → series label painted on cover (no episode / day numbering)
SERIES_LABEL: dict[str, str] = {
    "day-0-series-roadmap": "AI LEARNING SERIES",
    "day-1-kv-cache-memory-bandwidth": "AI LEARNING SERIES",
    "day-2-continuous-batching-vllm": "AI LEARNING SERIES",
    "day-3-token-budgets-cost-structure": "AI LEARNING SERIES",
    "building-tsdb-at-agoda": "EXPERIENCE SERIES",
    "when-percentiles-lie-cross-tier-queries": "EXPERIENCE SERIES",
    "seven-million-iot-sensors-failure-modes": "EXPERIENCE SERIES",
    "building-ai-inference-observability": "LENSAI · PRODUCT",
}

# slug → source filename under assets dir (user-provided infographic art)
USER_ART: dict[str, str] = {
    "day-1-kv-cache-memory-bandwidth": "image-867abcea-3cc1-4eb4-bdaf-3b68e8c15f3a.png",
    "day-2-continuous-batching-vllm": "image-93553678-49bb-4ff3-8e77-8d51800cd048.png",
    "when-percentiles-lie-cross-tier-queries": "image-4fab7b85-37ca-479b-995c-6b2732134a0e.png",
    "seven-million-iot-sensors-failure-modes": "image-d0c044a3-cbb9-43bf-8b90-31f83b07c948.png",
}

# slug → filename under cover_assets_rich/
RICH_GENERATED: dict[str, str] = {
    "day-0-series-roadmap": "day-0-series-roadmap.png",
    "day-3-token-budgets-cost-structure": "day-3-token-budgets-cost-structure.png",
    "building-tsdb-at-agoda": "building-tsdb-at-agoda.png",
    "building-ai-inference-observability": "building-ai-inference-observability.png",
}

ALL_SLUGS = list(SERIES_LABEL)

# Deprecated plain-text specs ( --plain only )
PLAIN_SPECS = [
    (
        "day-0-series-roadmap",
        "AI LEARNING SERIES",
        "Why I'm Writing This Series",
        (91, 211, 122),
    ),
    (
        "day-1-kv-cache-memory-bandwidth",
        "AI LEARNING SERIES",
        "The KV Cache Is a\nMemory Bandwidth Problem",
        (91, 211, 122),
    ),
    (
        "day-2-continuous-batching-vllm",
        "AI LEARNING SERIES",
        "Continuous Batching in vLLM:\nThe Scheduler Design That\nKeeps GPUs Busy",
        (91, 211, 122),
    ),
    (
        "day-3-token-budgets-cost-structure",
        "AI LEARNING SERIES",
        "Token Budgets and\nReal Cost Structure",
        (91, 211, 122),
    ),
    (
        "building-tsdb-at-agoda",
        "EXPERIENCE SERIES",
        "1.5 Trillion Events/Day\nTSDB at Agoda",
        (147, 197, 253),
    ),
    (
        "when-percentiles-lie-cross-tier-queries",
        "EXPERIENCE SERIES",
        "When Percentiles Lie:\nCross-Tier Queries in a\n1.8T/day TSDB",
        (147, 197, 253),
    ),
    (
        "seven-million-iot-sensors-failure-modes",
        "EXPERIENCE SERIES",
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


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    if not bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ] + candidates
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def resize_cover(img: Image.Image, bg: tuple[int, int, int] = LETTERBOX_BG) -> Image.Image:
    """Fit inside W×H with minimal letterboxing (dark bars), never center-crop to square."""
    img = img.convert("RGB")
    scale = min(W / img.width, H / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    fitted = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), bg)
    canvas.paste(fitted, ((W - nw) // 2, (H - nh) // 2))
    return canvas


def _draw_series_pill(
    draw: ImageDraw.ImageDraw,
    label: str,
    *,
    cx: int,
    cy: int,
    font_size: int = 15,
    fill: tuple[int, int, int] = (28, 28, 32),
    outline: tuple[int, int, int] = (80, 120, 200),
    text_fill: tuple[int, int, int] = (220, 225, 235),
    pad_x: int = 20,
    pad_y: int = 7,
    radius: int = 8,
) -> None:
    font = _font(font_size, bold=False)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x0 = cx - tw // 2 - pad_x
    y0 = cy - th // 2 - pad_y
    x1 = cx + tw // 2 + pad_x
    y1 = cy + th // 2 + pad_y
    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=radius,
        fill=fill,
        outline=outline,
        width=1,
    )
    draw.text((x0 + pad_x, y0 + pad_y), label, fill=text_fill, font=font)


def _patch_badge_day1(img: Image.Image, label: str) -> Image.Image:
    """Yellow brush badge, upper-left — replace DAY X OF 30."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 6, 268, 98], fill=(8, 14, 28))
    draw.rounded_rectangle([18, 18, 248, 82], radius=14, fill=(245, 200, 35))
    font = _font(22)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    tx = 133 - tw // 2
    draw.text((tx, 34), label, fill=(12, 12, 12), font=font)
    return img


def _patch_badge_day2(img: Image.Image, label: str) -> Image.Image:
    """Center-top pill — remove DAY X OF 30 split badge."""
    x0, y0, x1, y1 = 248, 4, 776, 58
    # Blend with nearby header pixels instead of flat fill
    sample = img.crop((x0, y1 + 4, x1, y1 + 36)).resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    img.paste(sample, (x0, y0))
    draw = ImageDraw.Draw(img)
    _draw_series_pill(draw, label, cx=img.width // 2, cy=28, font_size=15)
    return img


def _patch_badge_experience_pill(
    img: Image.Image,
    label: str,
    *,
    box: tuple[int, int, int, int],
    accent: tuple[int, int, int],
    bg: tuple[int, int, int] = (16, 18, 22),
) -> Image.Image:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], fill=bg)
    font = _font(14, bold=False)
    pad_x, pad_y = 12, 6
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = x0, y0
    draw.rounded_rectangle(
        [px, py, px + tw + pad_x * 2, py + th + pad_y * 2],
        radius=6,
        fill=(22, 24, 30),
        outline=accent,
        width=2,
    )
    draw.text((px + pad_x, py + pad_y), label, fill=accent, font=font)
    return img


def _patch_rich_ai_learning_badge_tl(img: Image.Image, label: str) -> Image.Image:
    """Green-outline top-left badge on 1536×1024 rich AI Learning covers."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([24, 20, 560, 108], fill=(8, 14, 28))
    font = _font(20, bold=False)
    pad_x, pad_y = 16, 10
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = 40, 36
    draw.rounded_rectangle(
        [px, py, px + tw + pad_x * 2 + 8, py + th + pad_y * 2],
        radius=10,
        fill=(12, 20, 16),
        outline=(91, 211, 122),
        width=2,
    )
    draw.text((px + pad_x, py + pad_y), label, fill=(91, 211, 122), font=font)
    return img


def _patch_rich_day3_badge_tr(img: Image.Image) -> Image.Image:
    """Top-right circuit badge with DAY 3 OF N on day-3 cover."""
    x0, y0, x1, y1 = 1080, 12, 1520, 130
    sample = img.crop((x0, y1 + 8, x1, y1 + 48)).resize(
        (x1 - x0, y1 - y0), Image.Resampling.LANCZOS
    )
    img.paste(sample, (x0, y0))
    return img


def _patch_rich_experience_badge_tr(img: Image.Image, label: str) -> Image.Image:
    """Top-right experience pill on building-tsdb rich cover."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([1120, 16, 1520, 88], fill=(8, 14, 28))
    font = _font(18, bold=False)
    pad_x, pad_y = 14, 8
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px = 1500 - tw - pad_x * 2
    py = 28
    draw.rounded_rectangle(
        [px, py, px + tw + pad_x * 2, py + th + pad_y * 2],
        radius=8,
        fill=(18, 24, 36),
        outline=(100, 180, 255),
        width=2,
    )
    draw.text((px + pad_x, py + pad_y), label, fill=(100, 180, 255), font=font)
    return img


def fix_badge(slug: str, img: Image.Image) -> Image.Image:
    label = SERIES_LABEL.get(slug, "")
    if not label:
        return img
    if slug == "day-1-kv-cache-memory-bandwidth":
        return _patch_badge_day1(img, label)
    if slug == "day-2-continuous-batching-vllm":
        return _patch_badge_day2(img, label)
    if slug == "when-percentiles-lie-cross-tier-queries":
        x0, y0, x1, y1 = 158, 8, 498, 108
        # Inpaint POST X OF N zone from nearby dark grid (keep WHITEFALCON intact)
        sample = img.crop((520, 118, 920, 188)).resize(
            (x1 - x0, y1 - y0), Image.Resampling.LANCZOS
        )
        img.paste(sample, (x0, y0))
        return _patch_badge_experience_pill(
            img,
            label,
            box=(178, 54, 330, 90),
            accent=(100, 180, 255),
            bg=(8, 10, 14),
        )
    if slug == "seven-million-iot-sensors-failure-modes":
        x0, y0, x1, y1 = 168, 6, 420, 68
        sample = img.crop((x0, y1 + 8, x1, y1 + 44)).resize(
            (x1 - x0, y1 - y0), Image.Resampling.LANCZOS
        )
        img.paste(sample, (x0, y0))
        return _patch_badge_experience_pill(
            img, label, box=(188, 24, 340, 60), accent=(0, 210, 230), bg=(10, 12, 16)
        )
    if slug == "day-0-series-roadmap":
        return _patch_rich_ai_learning_badge_tl(img, label)
    if slug == "day-3-token-budgets-cost-structure":
        img = _patch_rich_ai_learning_badge_tl(img, label)
        return _patch_rich_day3_badge_tr(img)
    if slug == "building-tsdb-at-agoda":
        return _patch_rich_experience_badge_tr(img, label)
    # building-ai-inference-observability: LENSAI · PRODUCT already in source art
    return img


def write_cover(slug: str, img: Image.Image) -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    OG_DIR.mkdir(parents=True, exist_ok=True)
    out = resize_cover(img)
    cover_path = COVERS_DIR / f"{slug}.png"
    out.save(cover_path, "PNG", optimize=True)
    shutil.copy2(cover_path, OG_DIR / f"{slug}.png")
    print(f"  ✓ {slug}.png  ({out.size[0]}×{out.size[1]})  badge: {SERIES_LABEL.get(slug, '—')}")


def process_user_art(assets_dir: Path, slug: str, filename: str) -> None:
    src = assets_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"User art missing: {src}")
    img = Image.open(src).convert("RGB")
    img = fix_badge(slug, img)
    write_cover(slug, img)


def process_rich_generated(slug: str, filename: str) -> None:
    for base in (RICH_GENERATED_DIR, DEFAULT_ASSETS):
        src = base / filename
        if src.exists():
            img = Image.open(src).convert("RGB")
            img = fix_badge(slug, img)
            write_cover(slug, img)
            return
    raise FileNotFoundError(
        f"No rich cover for {slug}: expected {RICH_GENERATED_DIR / filename}"
    )


def run_rich(assets_dir: Path, slugs: list[str] | None = None) -> None:
    targets = slugs or ALL_SLUGS
    print("Rich infographic covers → blog/assets/{covers,og}/")
    for slug in targets:
        if slug in USER_ART:
            process_user_art(assets_dir, slug, USER_ART[slug])
        elif slug in RICH_GENERATED:
            process_rich_generated(slug, RICH_GENERATED[slug])
        else:
            print(f"  ? unknown slug: {slug}")


# --- Deprecated plain generator ---


def _plain_fonts():
    title = _font(52)
    badge = _font(22)
    mono = _font(14, bold=False)
    return title, badge, mono


def draw_grid(draw: ImageDraw.ImageDraw, accent: tuple[int, int, int]) -> None:
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8))
    draw.rectangle([72, 120, W - 72, H - 80], outline=(*accent, 40), width=1)


def render_plain(slug: str, badge: str, title: str, accent: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (W, H), (15, 15, 14))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_grid(draw, accent)
    title_font, badge_font, mono_font = _plain_fonts()
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
    y = 160
    for line in title.split("\n"):
        draw.text((72, y), line, fill=(236, 236, 234), font=title_font)
        bbox = draw.textbbox((72, y), line, font=title_font)
        y = bbox[3] + 12
    draw.text((72, H - 56), "AKSHANT SHARMA", fill=(124, 124, 116), font=mono_font)
    draw.rectangle([72, H - 28, 72 + 120, H - 24], fill=accent)
    write_cover(slug, img)


def run_plain() -> None:
    print("WARNING: --plain generates boring grid covers. Prefer --rich.")
    for spec in PLAIN_SPECS:
        render_plain(*spec)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Deprecated dark-grid text-only covers (default is --rich)",
    )
    parser.add_argument(
        "--assets",
        type=Path,
        default=None,
        help="Directory with user infographic PNGs (default: PROFILE_COVER_ASSETS or cursor assets)",
    )
    parser.add_argument("--slug", action="append", dest="slugs", help="Only process these slugs")
    args = parser.parse_args()

    import os

    assets_dir = args.assets or Path(
        os.environ.get("PROFILE_COVER_ASSETS", DEFAULT_ASSETS)
    )

    if args.plain:
        run_plain()
    else:
        run_rich(assets_dir, args.slugs)


if __name__ == "__main__":
    main()
