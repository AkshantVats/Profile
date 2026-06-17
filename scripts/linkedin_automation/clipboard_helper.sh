#!/bin/bash
# One-command posting helper
# Copies post text to clipboard and opens image folder

echo "LinkedIn Post Creator - Clipboard Mode"
echo "======================================="
echo

# Post 1
echo "POST 1: AI Learning Day 15"
echo "---------------------------"
echo
cat ~/Desktop/Github/Profile/scripts/linkedin_automation/post1_ai_day15.txt | pbcopy
echo "✅ Post 1 text copied to clipboard"
echo
echo "Image to upload:"
echo "  ~/Desktop/Github/Profile/scripts/linkedin-export/day-15-multi-model-routing-strategies/diagram-1.png"
echo
open ~/Desktop/Github/Profile/scripts/linkedin-export/day-15-multi-model-routing-strategies/
echo "✅ Opened image folder"
echo
echo "Now in LinkedIn:"
echo "  1. Click 'Start a post'"
echo "  2. Paste (Cmd+V)"
echo "  3. Upload diagram-1.png from opened folder"
echo "  4. Click clock icon → Schedule for tomorrow 9:00 AM"
echo
read -p "Press Enter when Post 1 is scheduled... "

# Post 2
echo
echo "POST 2: Experience Day 18"
echo "-------------------------"
echo
cat ~/Desktop/Github/Profile/scripts/linkedin_automation/post2_exp_day18.txt | pbcopy
echo "✅ Post 2 text copied to clipboard"
echo
echo "Images to upload (2 diagrams):"
echo "  - diagram-1.png"
echo "  - diagram-2.png"
echo
open ~/Desktop/Github/Profile/scripts/linkedin-export/day-18-supplier-rate-limiting/
echo "✅ Opened image folder"
echo
echo "Now in LinkedIn:"
echo "  1. Click 'Start a post'"
echo "  2. Paste (Cmd+V)"
echo "  3. Upload both diagrams from opened folder"
echo "  4. Click clock icon → Schedule for tomorrow 9:05 AM"
echo
read -p "Press Enter when Post 2 is scheduled... "

echo
echo "✅ Done! Check your LinkedIn scheduled posts to verify."
echo "   https://www.linkedin.com/feed/"
