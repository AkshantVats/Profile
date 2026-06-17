# Blog Cover Generation with OpenAI DALL-E 3

## Quick Start

### 1. Set up OpenAI API Key

```bash
# Get key from: https://platform.openai.com/api-keys
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.zshrc
source ~/.zshrc
```

### 2. Generate Covers

```bash
# Single cover
./scripts/generate_blog_cover_openai.sh day-12-example

# Multiple covers
./scripts/generate_blog_cover_openai.sh day-11-semantic-caching-vs-exact-match-redis day-12-example
```

## Integration with 10PM Routine

Add to the 10PM main run script after blog HTML generation:

```python
import subprocess
import os

def generate_blog_covers(experience_slug: str, ai_learning_slug: str):
    """Generate cover images for today's blog posts using OpenAI DALL-E 3."""
    profile_dir = "/Users/akshant/Desktop/Github/Profile"
    
    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping cover generation")
        return False
    
    try:
        subprocess.run([
            os.path.join(profile_dir, "scripts/generate_blog_cover_openai.sh"),
            experience_slug,
            ai_learning_slug
        ], check=True, cwd=profile_dir)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Cover generation failed: {e}")
        return False

# Usage in 10PM routine:
experience_slug = "ten-thousand-concurrent-requests-eks-patterns-delivery-hero"
ai_learning_slug = "day-11-semantic-caching-vs-exact-match-redis"

if generate_blog_covers(experience_slug, ai_learning_slug):
    print("✅ Blog covers generated")
    # Continue with git commit of blog assets
else:
    print("⚠️  Using existing/placeholder covers")
    # Continue anyway with existing covers
```

## Manual Usage

### Generate with Python directly

```bash
cd ~/Desktop/Github/Profile

# Single slug
python3 scripts/generate_covers_from_content.py --generate --slug day-12-example

# Multiple slugs
python3 scripts/generate_covers_from_content.py --generate --slug day-11-semantic-caching-vs-exact-match-redis --slug day-12-example

# All slugs (expensive!)
python3 scripts/generate_covers_from_content.py --generate
```

### Test without installing

```bash
# Download to scripts/cover_generated/ only (no install to blog/assets/)
python3 scripts/generate_covers_from_content.py --generate --no-install --slug day-12-example
```

### View prompts

```bash
python3 scripts/generate_covers_from_content.py --print-prompts --slug day-12-example
```

## File Locations

- **Script**: `scripts/generate_covers_from_content.py`
- **Wrapper**: `scripts/generate_blog_cover_openai.sh`
- **Generated sources**: `scripts/cover_generated/<slug>.png` (1024×1024 from DALL-E)
- **Final covers**: `blog/assets/covers/<slug>.png` (1200×630 letterboxed)
- **OG images**: `blog/assets/og/<slug>.png` (copy of final cover)

## Cost

- **DALL-E 3** (1024×1024, standard quality): ~$0.040 per image
- **Daily** (2 posts): ~$0.08
- **Monthly** (60 posts): ~$2.40

## Styling

All covers follow these guidelines:

### AI Learning Series
- Accent: Neon green `#5bd37a`
- Badge: "AI LEARNING SERIES"
- Topics: KV cache, batching, token budgets, tensor parallelism, etc.

### Experience Series
- Accent: Electric blue `#64b4ff` or cyan `#00d2e6`
- Badge: "EXPERIENCE SERIES"
- Topics: TSDB, IoT sensors, EKS patterns, geo-events, etc.

### LensAI Product
- Accent: Violet `#a78bfa`
- Badge: "LENSAI · PRODUCT"
- Topics: AI inference observability

### Common Elements
- Dark navy background: `#080e1c`
- No day/episode numbers on cover art
- Rich infographic content (charts, pipelines, icons, glowing accents)
- Professional systems-engineering blog thumbnail style
- Final size: 1200×630 (LinkedIn/OG standard)

## Troubleshooting

### Missing API Key

```
❌ Error: OPENAI_API_KEY environment variable not set
```

**Fix**: Set in `~/.zshrc` and reload: `source ~/.zshrc`

### Rate Limit

```
RuntimeError: OpenAI DALL-E generation failed: Rate limit exceeded
```

**Fix**: Wait 60 seconds and retry. Free tier has rate limits.

### Invalid API Key

```
RuntimeError: OpenAI DALL-E generation failed: Incorrect API key provided
```

**Fix**: Check key at https://platform.openai.com/api-keys

## Fallback (No OpenAI)

If OpenAI is unavailable, use placeholder generator:

```bash
python3 scripts/generate_cover_generated_sources_day12.py --slug <slug>
python3 scripts/generate_blog_covers.py --from-content --slug <slug>
```

## Examples

### Day 11: Semantic Caching

```bash
./scripts/generate_blog_cover_openai.sh day-11-semantic-caching-vs-exact-match-redis
```

Prompt: "Exact-match Redis vs semantic embedding ANN cache: byte hash keys vs embedding vectors, similarity threshold τ tuned like tail-latency SLO, false positive risk + observability..."

### Building TSDB at Agoda

```bash
./scripts/generate_blog_cover_openai.sh building-tsdb-at-agoda
```

Prompt: "Kafka → Rust ingestion → Redis hot tier → S3 Parquet cold tier, RoaringBitmap inverted index, 1.5T events/day counter, WhiteFalcon query path..."
