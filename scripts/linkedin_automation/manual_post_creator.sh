#!/bin/bash
#
# Manual LinkedIn Post Creator - For CEO Review
# Opens LinkedIn in browser with pre-filled post text for manual scheduling
#

set -e

EXPORT_DIR="/Users/akshant/Desktop/Github/Profile/scripts/linkedin-export"

echo "LinkedIn Post Creator - Manual Mode"
echo "===================================="
echo
echo "This will open LinkedIn in your browser where you can:"
echo "  1. Copy the post text"
echo "  2. Paste into LinkedIn's 'Start a post' composer"
echo "  3. Upload the diagrams (paths provided)"
echo "  4. Click the clock icon to schedule for tomorrow 9 AM"
echo "  5. Check alignment with your existing series"
echo

# Post 1: AI Learning Day 15
echo "POST 1: AI Learning Day 15"
echo "────────────────────────────"

POST1_FILE="$EXPORT_DIR/ai-day-15-multi-model-routing-strategies.txt"
POST1_TEXT=$(awk '/^=== ARTICLE ===/,0' "$POST1_FILE" | sed '1,2d' | grep -v '^\[Upload diagram' | grep -v '^→ /Users/')

POST1_IMAGE="$EXPORT_DIR/day-15-multi-model-routing-strategies/diagram-1.png"

echo "Text copied to clipboard:"
echo "$POST1_TEXT" | pbcopy
echo "✅ Post text is now in your clipboard"
echo
echo "Image to upload:"
echo "  $POST1_IMAGE"
echo
echo "Next steps:"
echo "  1. Open LinkedIn: https://www.linkedin.com/feed/"
echo "  2. Click 'Start a post'"
echo "  3. Paste the text (Cmd+V)"
echo "  4. Upload the diagram image above"
echo "  5. Click clock icon → Schedule for tomorrow 9:00 AM"
echo
read -p "Press Enter when Post 1 is scheduled in LinkedIn... "

# Post 2: Experience Day 18
echo
echo "POST 2: Experience Day 18"
echo "────────────────────────────"

POST2_FILE="$EXPORT_DIR/exp-day-18-supplier-rate-limiting.txt"
POST2_TEXT=$(awk '/^=== ARTICLE ===/,0' "$POST2_FILE" | sed '1,2d' | grep -v '^\[Upload diagram' | grep -v '^→ /Users/')

POST2_IMAGES="$EXPORT_DIR/day-18-supplier-rate-limiting/"

echo "Text copied to clipboard:"
echo "$POST2_TEXT" | pbcopy
echo "✅ Post text is now in your clipboard"
echo
echo "Images to upload (2 diagrams):"
ls -1 "$POST2_IMAGES"*.png | while read img; do
    echo "  $img"
done
echo
echo "Next steps:"
echo "  1. Open LinkedIn: https://www.linkedin.com/feed/"
echo "  2. Click 'Start a post'"
echo "  3. Paste the text (Cmd+V)"
echo "  4. Upload both diagram images above"
echo "  5. Click clock icon → Schedule for tomorrow 9:00 AM"
echo
read -p "Press Enter when Post 2 is scheduled in LinkedIn... "

echo
echo "✅ Done!"
echo
echo "Both posts should now be in your LinkedIn scheduled posts."
echo "Check: https://www.linkedin.com/feed/ → Click profile → Creator tools → Scheduled posts"
echo
echo "Verify:"
echo "  - Post 1 (AI Day 15) scheduled for tomorrow 9:00 AM"
echo "  - Post 2 (Experience Day 18) scheduled for tomorrow 9:05 AM"
echo "  - Check alignment with your existing series posts"
