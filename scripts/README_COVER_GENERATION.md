# Blog Cover Generation (Zero Cost with Cursor)

## Quick Start

### Step 1: Get Prompts

```bash
cd ~/Desktop/Github/Profile
python3 scripts/generate_covers_from_content.py --print-prompts --slug <your-slug>
```

### Step 2: Generate with Cursor

In Cursor chat:
```
Generate an image with this description:
[paste the prompt from step 1]
Save it as scripts/cover_generated/<your-slug>.png
```

### Step 3: Install Covers

```bash
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

Done! Your covers are now in `blog/assets/covers/` and `blog/assets/og/`.

## Alternative Methods

### ChatGPT Web (Free/Plus)

1. Get prompt with `--print-prompts`
2. Paste into chat.openai.com
3. Download image to `scripts/cover_generated/<slug>.png`
4. Run install command

### Open Source (Stable Diffusion)

1. Get prompts with `--print-prompts`
2. Generate with ComfyUI/Automatic1111/Fooocus
3. Save to `scripts/cover_generated/<slug>.png`
4. Run install command

## Integration with 10PM Routine

Add to your routine script:

```python
import subprocess

def generate_blog_covers(experience_slug: str, ai_slug: str):
    """Generate and install covers using Cursor GenerateImage."""
    # Print prompts
    result = subprocess.run([
        "python3", "scripts/generate_covers_from_content.py",
        "--print-prompts",
        "--slug", experience_slug,
        "--slug", ai_slug
    ], capture_output=True, text=True, cwd="/Users/akshant/Desktop/Github/Profile")
    
    print("📝 Use these prompts with Cursor GenerateImage:")
    print(result.stdout)
    
    # After manual generation, install:
    # python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/

# Manual step: Generate images in Cursor before continuing routine
```

## Cost

**All methods are zero cost:**
- Cursor GenerateImage: $0 (included with subscription)
- ChatGPT Free: $0
- Stable Diffusion: $0 (local, requires GPU)

## Files

- **Script**: `scripts/generate_covers_from_content.py`
- **Workflow**: `scripts/CURSOR_COVER_WORKFLOW.md` (detailed guide)
- **Generated**: `scripts/cover_generated/<slug>.png`
- **Installed**: `blog/assets/covers/<slug>.png` (1200×630)
- **OG copy**: `blog/assets/og/<slug>.png`

## Examples

### Generate One Cover

```bash
# 1. Get prompt
python3 scripts/generate_covers_from_content.py --print-prompts \
  --slug day-11-semantic-caching-vs-exact-match-redis

# 2. In Cursor: "Generate image with prompt: [paste], save as scripts/cover_generated/day-11-semantic-caching-vs-exact-match-redis.png"

# 3. Install
python3 scripts/generate_covers_from_content.py \
  scripts/cover_generated/day-11-semantic-caching-vs-exact-match-redis.png
```

### Batch Mode

```bash
# Print all prompts
python3 scripts/generate_covers_from_content.py --print-prompts > prompts.txt

# Generate images (manually or in batch)
# Save to scripts/cover_generated/

# Install all
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

## Styling

All prompts follow the style guide:
- **AI Learning**: Neon green #5bd37a, "AI LEARNING SERIES" badge
- **Experience**: Electric blue #64b4ff, "EXPERIENCE SERIES" badge
- **LensAI**: Violet #a78bfa, "LENSAI · PRODUCT" badge
- Dark navy background #080e1c
- No day/episode numbers on covers
- 1200×630 final size

See `scripts/CURSOR_COVER_WORKFLOW.md` for detailed instructions.
