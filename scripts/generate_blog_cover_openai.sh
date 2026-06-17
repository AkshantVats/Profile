#!/usr/bin/env bash
# Generate blog cover image using OpenAI DALL-E 3
# Usage: ./generate_blog_cover_openai.sh <slug>
#
# Example:
#   ./generate_blog_cover_openai.sh day-12-example
#   ./generate_blog_cover_openai.sh building-ai-inference-observability

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <slug> [<slug2> ...]"
    echo ""
    echo "Examples:"
    echo "  $0 day-12-example"
    echo "  $0 day-12-example building-ai-inference-observability"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROFILE_DIR"

# Check for OPENAI_API_KEY
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo "Then add to ~/.zshrc:"
    echo "  export OPENAI_API_KEY='sk-proj-...'"
    echo ""
    echo "Then reload: source ~/.zshrc"
    exit 1
fi

# Generate covers for all provided slugs
for slug in "$@"; do
    echo "🎨 Generating cover for: $slug"
    python3 scripts/generate_covers_from_content.py --generate --slug "$slug"
done

echo "✅ All covers generated successfully!"
