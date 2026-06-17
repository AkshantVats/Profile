# OpenAI Cover Image Generation Setup

## Overview

Blog cover images are now automatically generated using OpenAI DALL-E 3 during the 10PM main run routine.

## Prerequisites

### 1. OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

Add to `~/.zshrc`:
```bash
export OPENAI_API_KEY='sk-proj-...'
```

Then reload:
```bash
source ~/.zshrc
```

### 2. Python Dependencies

Already installed:
- `openai` (v2.43.0)
- `pillow`
- `httpx`

## Usage

### Generate Single Cover

```bash
cd ~/Desktop/Github/Profile
python3 scripts/generate_covers_from_content.py --generate --slug day-12-example
```

### Generate Multiple Covers

```bash
python3 scripts/generate_covers_from_content.py --generate --slug day-11-semantic-caching-vs-exact-match-redis --slug day-12-example
```

### Generate All Covers

```bash
python3 scripts/generate_covers_from_content.py --generate
```

### Test Without Installing

```bash
python3 scripts/generate_covers_from_content.py --generate --no-install --slug day-12-example
```

This downloads to `scripts/cover_generated/` but doesn't install to `blog/assets/{covers,og}/`.

### Print Prompts Only

```bash
python3 scripts/generate_covers_from_content.py --print-prompts --slug day-12-example
```

## Integration with 10PM Routine

The 10PM main run routine should call:

```python
# After generating blog post HTML
import subprocess

slugs = ["experience-slug", "ai-learning-slug"]  # from current day's work
for slug in slugs:
    subprocess.run([
        "python3",
        "scripts/generate_covers_from_content.py",
        "--generate",
        "--slug", slug
    ], check=True, cwd="/Users/akshant/Desktop/Github/Profile")
```

## Cost Estimate

- DALL-E 3 (1024x1024, standard quality): ~$0.040 per image
- Daily cost (2 blog posts): ~$0.08
- Monthly cost (60 blog posts): ~$2.40

## Styling Guidelines

Covers automatically follow the style guide:
- **AI Learning Series**: Neon green (#5bd37a) accents
- **Experience Series**: Electric blue (#64b4ff) or cyan (#00d2e6) accents
- **LensAI Product**: Violet (#a78bfa) accents
- Dark navy background (#080e1c)
- Series badge (no day/episode numbers)
- Rich infographic content (charts, pipelines, icons)
- 1200×630 final size (letterboxed from 1024×1024)

## Troubleshooting

### Missing API Key

```
ValueError: OPENAI_API_KEY environment variable not set.
```

**Fix**: Set `OPENAI_API_KEY` in `~/.zshrc` and reload shell.

### Rate Limit Error

```
RuntimeError: OpenAI DALL-E generation failed: Rate limit exceeded
```

**Fix**: Wait 60 seconds and retry. OpenAI has rate limits for free tier accounts.

### API Error

```
RuntimeError: OpenAI DALL-E generation failed: ...
```

**Fix**: Check API key validity and account balance at https://platform.openai.com/

## Manual Fallback

If OpenAI is unavailable, use the placeholder generator:

```bash
python3 scripts/generate_cover_generated_sources_day12.py --slug <slug>
python3 scripts/generate_blog_covers.py --from-content --slug <slug>
```
