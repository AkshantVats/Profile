#!/usr/bin/env python3
"""Generate 1200×630 blog cover PNGs (covers/ + og/).

Modes:
  --rich (default)  Copy user infographic art (with badge fixes) or pre-generated rich PNGs.
  --plain           Deprecated: dark grid + plain text (avoid for published posts).

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
COVER_ASPECT = W / H  # 1.904761…
LETTERBOX_BG = (8, 14, 28)  # dark bars for square/tall sources

# slug → (source filename under assets dir, new badge text)
USER_ART: dict[str, tuple[str, str]] = {
    "day-1-kv-cache-memory-bandwidth": (
        "image-867abcea-3cc1-4eb4-bdaf-3b68e8c15f3a.png",
        "DAY 1 OF N",
    ),
    "day-2-continuous-batching-vllm": (
        "image-93553678-49bb-4ff3-8e77-8d51800cd048.png",
        "DAY 2 OF N",
    ),
    "when-percentiles-lie-cross-tier-queries": (
        "image-4fab7b85-37ca-479b-995c-6b2732134a0e.png",
        "EXPERIENCE 2 OF N",
    ),
    "seven-million-iot-sensors-failure-modes": (
        "image-d0c044a3-cbb9-43bf-8b90-31f83b07c948.png",
        "EXPERIENCE 3 OF N",
    ),
}

# slug → filename under cover_assets_rich/ (or DEFAULT_ASSETS before first commit)
RICH_GENERATED: dict[str, str] = {
    "day-0-series-roadmap": "day-0-series-roadmap.png",
    "day-3-token-budgets-cost-structure": "day-3-token-budgets-cost-structure.png",
    "building-tsdb-at-agoda": "building-tsdb-at-agoda.png",
    "building-ai-inference-observability": "building-ai-inference-observability.png",
}

ALL_SLUGS = list(USER_ART) + list(RICH_GENERATED)

# Deprecated plain-text specs ( --plain only )
PLAIN_SPECS = [
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


def _patch_badge_day1(img: Image.Image, badge: str) -> Image.Image:
    """Yellow brush badge, upper-left."""
    draw = ImageDraw.Draw(img)
    # Cover old "DAY 1 OF 30" brush (~1024×575 source coords)
    draw.rectangle([8, 6, 268, 98], fill=(8, 14, 28))
    # Brush stroke
    draw.rounded_rectangle([18, 18, 248, 82], radius=14, fill=(245, 200, 35))
    font = _font(26)
    draw.text((36, 34), badge, fill=(12, 12, 12), font=font)
    return img


def _patch_badge_day2(img: Image.Image, badge: str) -> Image.Image:
    """Center-top dark pill."""
    draw = ImageDraw.Draw(img)
    draw.rectangle([318, 4, 706, 58], fill=(18, 18, 20))
    label = f"{badge} | AI LEARNING SERIES"
    font = _font(15, bold=False)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    px = (img.width - tw) // 2 - 20
    py = 14
    draw.rounded_rectangle(
        [px, py, px + tw + 40, py + 32],
        radius=8,
        fill=(28, 28, 32),
        outline=(80, 120, 200),
        width=1,
    )
    draw.text((px + 20, py + 7), label, fill=(220, 225, 235), font=font)
    return img


def _patch_badge_experience_pill(
    img: Image.Image,
    badge: str,
    *,
    box: tuple[int, int, int, int],
    accent: tuple[int, int, int],
    bg: tuple[int, int, int] = (16, 18, 22),
) -> Image.Image:
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rectangle([x0 - 4, y0 - 4, x1 + 80, y1 + 4], fill=bg)
    font = _font(14, bold=False)
    pad_x, pad_y = 12, 6
    bbox = draw.textbbox((0, 0), badge, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    px, py = x0, y0
    draw.rounded_rectangle(
        [px, py, px + tw + pad_x * 2, py + th + pad_y * 2],
        radius=6,
        fill=(22, 24, 30),
        outline=accent,
        width=2,
    )
    draw.text((px + pad_x, py + pad_y), badge, fill=accent, font=font)
    return img


def fix_badge(slug: str, img: Image.Image, badge: str) -> Image.Image:
    if slug == "day-1-kv-cache-memory-bandwidth":
        return _patch_badge_day1(img, badge)
    if slug == "day-2-continuous-batching-vllm":
        return _patch_badge_day2(img, badge)
    if slug == "when-percentiles-lie-cross-tier-queries":
        return _patch_badge_experience_pill(
            img, badge, box=(12, 52, 120, 88), accent=(100, 180, 255)
        )
    if slug == "seven-million-iot-sensors-failure-modes":
        return _patch_badge_experience_pill(
            img, badge, box=(198, 18, 310, 52), accent=(0, 210, 230), bg=(10, 12, 16)
        )
    return img


def write_cover(slug: str, img: Image.Image) -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    OG_DIR.mkdir(parents=True, exist_ok=True)
    out = resize_cover(img)
    cover_path = COVERS_DIR / f"{slug}.png"
    out.save(cover_path, "PNG", optimize=True)
    shutil.copy2(cover_path, OG_DIR / f"{slug}.png")
    print(f"  ✓ {slug}.png  ({out.size[0]}×{out.size[1]})")


def process_user_art(assets_dir: Path, slug: str, filename: str, badge: str) -> None:
    src = assets_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"User art missing: {src}")
    img = Image.open(src).convert("RGB")
    img = fix_badge(slug, img, badge)
    write_cover(slug, img)


def process_rich_generated(slug: str, filename: str) -> None:
    for base in (RICH_GENERATED_DIR, DEFAULT_ASSETS):
        src = base / filename
        if src.exists():
            write_cover(slug, Image.open(src))
            return
    raise FileNotFoundError(
        f"No rich cover for {slug}: expected {RICH_GENERATED_DIR / filename}"
    )


def run_rich(assets_dir: Path, slugs: list[str] | None = None) -> None:
    targets = slugs or ALL_SLUGS
    print("Rich infographic covers → blog/assets/{covers,og}/")
    for slug in targets:
        if slug in USER_ART:
            fname, badge = USER_ART[slug]
            process_user_art(assets_dir, slug, fname, badge)
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
