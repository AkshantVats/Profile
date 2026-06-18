# Blog Cover Generation with Cursor (Free, No API Key)

## Quick Start - Zero Cost Method

### Option 1: Cursor GenerateImage Tool (Recommended)

Use Cursor's built-in image generation (included with your subscription):

```bash
# 1. Print prompts for the slugs you need
cd ~/Desktop/Github/Profile
python3 scripts/generate_covers_from_content.py --print-prompts --slug day-12-example

# 2. Use the prompt with Cursor's GenerateImage tool:
#    - Copy the printed prompt
#    - Ask Cursor to generate the image with that prompt
#    - Save to scripts/cover_generated/<slug>.png

# 3. Install the generated covers
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

**Workflow in Cursor Chat:**

```
User: Generate an image with this description:
[paste the prompt from --print-prompts]
Save it as scripts/cover_generated/day-12-example.png
```

Cursor will generate the image and save it automatically!

### Option 2: ChatGPT Web Interface (Free/Manual)

If you have ChatGPT Plus or can use the free DALL-E in ChatGPT:

```bash
# 1. Get the prompt
python3 scripts/generate_covers_from_content.py --print-prompts --slug day-12-example

# 2. Go to chat.openai.com and paste the prompt

# 3. Download the generated image and save as:
#    scripts/cover_generated/day-12-example.png

# 4. Install
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

### Option 3: Open Source (Stable Diffusion)

Use ComfyUI, Automatic1111, or Fooocus locally:

```bash
# 1. Get prompts
python3 scripts/generate_covers_from_content.py --print-prompts > prompts.txt

# 2. Generate with your local Stable Diffusion installation
#    Model: SDXL or SD1.5
#    Size: 1024x1024 or larger
#    CFG Scale: 7-9
#    Steps: 30-50

# 3. Save outputs to scripts/cover_generated/<slug>.png

# 4. Install all at once
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

## Integration with 10PM Routine

### Manual Workflow (Best for Quality Control)

Add this to your 10PM routine notes:

```markdown
## Blog Cover Generation

1. Generate prompts:
   ```bash
   cd ~/Desktop/Github/Profile
   python3 scripts/generate_covers_from_content.py --print-prompts \
     --slug <experience-slug> --slug <ai-learning-slug>
   ```

2. Generate images:
   - Use Cursor: Ask Cursor to generate images from prompts
   - Use ChatGPT: Paste prompts into chat.openai.com
   - Use local SD: Run through ComfyUI/A1111

3. Install covers:
   ```bash
   python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
   ```

4. Commit:
   ```bash
   git add blog/assets/covers/ blog/assets/og/
   git commit -m "feat: add blog covers for day X"
   ```
```

### Batch Mode

Generate all prompts at once for the week:

```bash
# Print all prompts to a file
python3 scripts/generate_covers_from_content.py --print-prompts > weekly_prompts.txt

# Review prompts.txt and generate images in bulk
# Then install all at once
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

## File Locations

- **Prompts**: Generated on-the-fly with `--print-prompts`
- **Generated sources**: `scripts/cover_generated/<slug>.png` (1024×1024 or larger)
- **Final covers**: `blog/assets/covers/<slug>.png` (1200×630 letterboxed)
- **OG images**: `blog/assets/og/<slug>.png` (copy of final cover)

## Cost Comparison

| Method | Cost | Speed | Quality |
|--------|------|-------|---------|
| **Cursor GenerateImage** | $0 (included) | Fast | High |
| **ChatGPT Free** | $0 | Medium | High |
| **ChatGPT Plus** | $20/month flat | Fast | High |
| **Stable Diffusion Local** | $0 (+ hardware) | Medium | Very High |
| ~~OpenAI API~~ | ~~$0.04/image~~ | Fast | High |

**Recommended: Cursor GenerateImage** - Zero cost, integrated, fast.

## Styling Guidelines

All methods use the same style-aware prompts:

### AI Learning Series
- Accent: Neon green `#5bd37a`
- Badge: "AI LEARNING SERIES"

### Experience Series
- Accent: Electric blue `#64b4ff` or cyan `#00d2e6`
- Badge: "EXPERIENCE SERIES"

### LensAI Product
- Accent: Violet `#a78bfa`
- Badge: "LENSAI · PRODUCT"

### Common Elements
- Dark navy background: `#080e1c`
- No day/episode numbers on cover art
- Rich infographic content (charts, pipelines, icons)
- Professional systems-engineering blog thumbnail style
- Final size: 1200×630 (LinkedIn/OG standard)

## Examples

### Generate One Cover

```bash
# Get prompt
python3 scripts/generate_covers_from_content.py --print-prompts \
  --slug day-11-semantic-caching-vs-exact-match-redis

# In Cursor chat:
# "Generate an image with this prompt: [paste]
#  Save as scripts/cover_generated/day-11-semantic-caching-vs-exact-match-redis.png"

# Install
python3 scripts/generate_covers_from_content.py \
  scripts/cover_generated/day-11-semantic-caching-vs-exact-match-redis.png
```

### Generate Multiple Covers

```bash
# Print prompts for both posts
python3 scripts/generate_covers_from_content.py --print-prompts \
  --slug building-tsdb-at-agoda \
  --slug day-12-embeddings-as-dense-time-series-ids

# Generate both images (in Cursor or ChatGPT)
# Save to scripts/cover_generated/

# Install both
python3 scripts/generate_covers_from_content.py --from-dir scripts/cover_generated/
```

## Troubleshooting

### Missing Generated Images

```
FileNotFoundError: Missing generated art: scripts/cover_generated/<slug>.png
```

**Fix**: Generate and save the image first, then run install.

### Wrong Image Size

The script automatically letterboxes any size to 1200×630. Generate at:
- 1024×1024 (DALL-E default)
- 1536×1024 (landscape)
- Any size ≥ 1200×630

### Image Quality Issues

For Stable Diffusion:
- Use SDXL for best quality
- CFG Scale: 7-9 (not too high)
- Steps: 30-50
- Add negative prompt: "text, watermark, signature, low quality"

## Migration Note

This replaces the previous OpenAI API integration to eliminate costs.
The prompts remain identical - only the generation method changed.
