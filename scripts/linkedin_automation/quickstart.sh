#!/bin/bash
# Quick Start Guide - LinkedIn Automation
# Run this script to get started immediately

set -e

echo "🚀 LinkedIn Automation Quick Start"
echo "==================================="
echo

# Step 1: Install dependencies
echo "Step 1: Installing Playwright..."
pip3 install playwright
playwright install chromium
echo "✅ Playwright installed"
echo

# Step 2: Set credentials
echo "Step 2: Set your LinkedIn credentials"
echo
echo "Add to ~/.zshrc (or ~/.bashrc):"
echo "  export LINKEDIN_EMAIL=\"your@email.com\""
echo "  export LINKEDIN_PASSWORD=\"your_password\""
echo
read -p "Have you set LINKEDIN_EMAIL and LINKEDIN_PASSWORD? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please set credentials first, then run this script again"
    exit 1
fi
source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null || true

if [ -z "$LINKEDIN_EMAIL" ] || [ -z "$LINKEDIN_PASSWORD" ]; then
    echo "❌ Credentials not found. Please reload your shell and try again."
    exit 1
fi
echo "✅ Credentials loaded"
echo

# Step 3: Test dry run
echo "Step 3: Testing with dry run..."
cd "$(dirname "$0")"

# Enable dry run
jq '.config.dry_run = true' posting_schedule.json > posting_schedule.json.tmp
mv posting_schedule.json.tmp posting_schedule.json

python3 scheduler.py
echo "✅ Dry run completed"
echo

# Step 4: Disable dry run for production
echo "Step 4: Disabling dry run for production..."
jq '.config.dry_run = false' posting_schedule.json > posting_schedule.json.tmp
mv posting_schedule.json.tmp posting_schedule.json
echo "✅ Production mode enabled"
echo

# Step 5: Install LaunchAgent
echo "Step 5: Installing LaunchAgent for daily automation..."
./setup.sh
echo

echo "✅ Setup complete!"
echo
echo "📅 Next scheduled run: Tomorrow at 9:00 AM IST"
echo
echo "Useful commands:"
echo "  Monitor logs:  tail -f ~/Library/Logs/linkedin-poster.log"
echo "  Check status:  launchctl list | grep linkedin-poster"
echo "  Manual run:    launchctl start com.akshantvats.linkedin-poster"
echo
