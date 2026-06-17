#!/bin/bash
#
# Setup script for LinkedIn posting automation
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.akshantvats.linkedin-poster.plist"
PLIST_SRC="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "LinkedIn Posting Automation - Setup"
echo "===================================="
echo

# Check if Playwright is installed
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "❌ Playwright not installed"
    echo "Installing Playwright..."
    pip3 install playwright
    playwright install chromium
    echo "✅ Playwright installed"
else
    echo "✅ Playwright found"
fi

# Check credentials
if [ -z "$LINKEDIN_EMAIL" ] || [ -z "$LINKEDIN_PASSWORD" ]; then
    echo
    echo "⚠️  Warning: LINKEDIN_EMAIL and LINKEDIN_PASSWORD not set"
    echo
    echo "Add these to your ~/.zshrc:"
    echo "  export LINKEDIN_EMAIL=\"your@email.com\""
    echo "  export LINKEDIN_PASSWORD=\"your_password\""
    echo
    echo "Then run: source ~/.zshrc"
    echo
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update plist with actual credentials if available
if [ -n "$LINKEDIN_EMAIL" ] && [ -n "$LINKEDIN_PASSWORD" ]; then
    echo "Updating plist with credentials..."
    sed -i.bak "s/REPLACE_WITH_YOUR_EMAIL/$LINKEDIN_EMAIL/g" "$PLIST_SRC"
    sed -i.bak "s/REPLACE_WITH_YOUR_PASSWORD/$LINKEDIN_PASSWORD/g" "$PLIST_SRC"
    echo "✅ Credentials updated"
fi

# Copy plist to LaunchAgents
echo "Installing LaunchAgent..."
cp "$PLIST_SRC" "$PLIST_DST"
chmod 600 "$PLIST_DST"
echo "✅ LaunchAgent installed: $PLIST_DST"

# Load the agent
echo "Loading LaunchAgent..."
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"
echo "✅ LaunchAgent loaded"

# Verify
if launchctl list | grep -q linkedin-poster; then
    echo "✅ LaunchAgent is active"
else
    echo "⚠️  LaunchAgent not found in launchctl list"
fi

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Test with dry run: cd $SCRIPT_DIR && python3 scheduler.py"
echo "2. Check schedule: cat $SCRIPT_DIR/posting_schedule.json"
echo "3. Monitor logs: tail -f ~/Library/Logs/linkedin-poster.log"
echo "4. First run: Tomorrow at 9:00 AM IST"
echo
