# LinkedIn Posting Automation

Automated LinkedIn posting system using Playwright for the 150-day build journey.

## Overview

This automation posts LinkedIn content (text + diagrams) from the `linkedin-export/` directory on a daily schedule. Posts are queued for 14 days starting June 18, 2026 at 9:00 AM IST.

## Components

### 1. `post_to_linkedin.py`
Core Playwright automation for LinkedIn posting.

**Features:**
- Browser automation using Playwright
- Login handling
- Post creation with text + multiple images
- Image upload from exported diagrams
- Detailed logging with timestamps

**Usage:**
```bash
export LINKEDIN_EMAIL="your@email.com"
export LINKEDIN_PASSWORD="your_password"

python post_to_linkedin.py ~/Desktop/Github/Profile/scripts/linkedin-export/ai-day-15-multi-model-routing-strategies.txt
```

### 2. `scheduler.py`
Daily job that runs scheduled posts from `posting_schedule.json`.

**Features:**
- Reads daily schedule from JSON
- Posts all content scheduled for today
- 5-minute interval between posts (configurable)
- Marks posts as completed
- Error handling and retry logic
- Dry-run mode for testing

**Usage:**
```bash
# Run today's posts
python scheduler.py

# Dry run (no actual posting)
# Set "dry_run": true in posting_schedule.json
```

### 3. `posting_schedule.json`
14-day posting schedule (June 18 - July 1, 2026).

**Structure:**
- 2 posts per day (AI Learning + Experience series)
- All posts at 9:00 AM IST
- Status tracking (pending → posted)
- Post metadata (type, day number, file)

### 4. `com.akshantvats.linkedin-poster.plist`
macOS LaunchAgent for daily execution.

## Setup

### 1. Install Dependencies

```bash
cd ~/Desktop/Github/Profile/scripts/linkedin_automation

# Install Playwright
pip install playwright

# Install browser drivers
playwright install chromium
```

### 2. Set Credentials

Add to your `~/.zshrc`:

```bash
export LINKEDIN_EMAIL="your@email.com"
export LINKEDIN_PASSWORD="your_password"
```

Then reload:
```bash
source ~/.zshrc
```

### 3. Configure Schedule

Edit `posting_schedule.json` to customize:
- Post order and dates
- Posting time
- Post interval between multiple posts
- Dry run mode

### 4. Install LaunchAgent (macOS)

```bash
# Copy plist to LaunchAgents
cp com.akshantvats.linkedin-poster.plist ~/Library/LaunchAgents/

# Load the agent
launchctl load ~/Library/LaunchAgents/com.akshantvats.linkedin-poster.plist

# Check if it's loaded
launchctl list | grep linkedin-poster
```

## Daily Schedule

| Date | Time | Posts |
|------|------|-------|
| Jun 18 | 9:00 AM | AI Day 15 + Experience Day 18 |
| Jun 19 | 9:00 AM | AI Day 16 + Experience Day 19 |
| Jun 20 | 9:00 AM | AI Day 17 + Experience Day 20 |
| Jun 21 | 9:00 AM | AI Day 18 + Experience Day 21 |
| Jun 22 | 9:00 AM | AI Day 19 + Experience Day 22 |
| Jun 23 | 9:00 AM | AI Day 20 + Experience Day 23 |
| Jun 24 | 9:00 AM | AI Day 21 + Experience Day 24 |
| Jun 25 | 9:00 AM | AI Day 22 + Experience Day 25 |
| Jun 26 | 9:00 AM | AI Day 23 + Experience Day 26 |
| Jun 27 | 9:00 AM | AI Day 24 + Experience Day 27 |
| Jun 28 | 9:00 AM | AI Day 25 + Experience Day 28 |
| Jun 29 | 9:00 AM | AI Day 26 + IoT Sensors Special |
| Jun 30 | 9:00 AM | AI Day 27 |
| Jul 1 | 9:00 AM | AI Day 28 |

## Testing

### Dry Run
1. Set `"dry_run": true` in `posting_schedule.json`
2. Run `python scheduler.py`
3. Check logs - no actual posting will occur

### Single Post Test
```bash
python post_to_linkedin.py ~/Desktop/Github/Profile/scripts/linkedin-export/ai-day-15-multi-model-routing-strategies.txt
```

### Verify Schedule
```bash
python -c "
import json
from pathlib import Path
schedule = json.loads(Path('posting_schedule.json').read_text())
for day in schedule['schedule']:
    print(f\"{day['date']}: {len(day['posts'])} posts\")
"
```

## Monitoring

### Check LaunchAgent Status
```bash
# View last run output
cat ~/Library/Logs/linkedin-poster.log

# Check if agent is running
launchctl list | grep linkedin-poster

# Manual trigger (for testing)
launchctl start com.akshantvats.linkedin-poster
```

### Check Posting Status
View `posting_schedule.json` to see which posts have `"status": "posted"`.

## Troubleshooting

### Login Fails
- Verify `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are set
- LinkedIn may require 2FA - run with `headless=False` to manually handle
- Check for "Verify it's you" challenges

### Images Not Uploading
- Verify diagram paths in export .txt files are absolute
- Check that PNG files exist in corresponding folders
- LinkedIn limits: max 20 images per post

### Posts Not Scheduled
- Check LaunchAgent is loaded: `launchctl list | grep linkedin-poster`
- Verify plist file has correct paths
- Check system time matches schedule (timezone: Asia/Kolkata)

### Rate Limiting
- Default 5-minute interval between posts
- Increase `post_interval_minutes` in config if needed
- LinkedIn may throttle rapid posting

## Important Notes

### LinkedIn Terms of Service
⚠️ **Automation Disclaimer:** Automated posting via browser automation may violate LinkedIn's Terms of Service. This tool is for personal use only. LinkedIn's official API requires OAuth2 and does not support cookie-based posting.

### Security
- Never commit credentials to git
- Store credentials in environment variables
- Keep `.plist` file permissions restricted: `chmod 600`

### Maintenance
- Update `posting_schedule.json` as new content is generated
- Monitor `linkedin-poster.log` for errors
- Adjust schedule if LinkedIn pattern detection occurs

## Architecture

```
linkedin_automation/
├── post_to_linkedin.py      # Core Playwright posting logic
├── scheduler.py               # Daily job runner
├── posting_schedule.json      # 14-day posting queue
├── README.md                  # This file
└── com.akshantvats.linkedin-poster.plist  # LaunchAgent config

linkedin-export/
├── ai-day-15-*.txt           # Post content
├── exp-day-18-*.txt
└── day-15-*/                 # Diagram PNGs
    └── diagram-1.png
```

## Next Steps

1. **Test dry run:** `python scheduler.py` with dry_run enabled
2. **Test single post:** Run `post_to_linkedin.py` with one file
3. **Install LaunchAgent:** Copy plist and load
4. **Monitor first day:** Watch logs on June 18 at 9 AM

---

**Created:** June 17, 2026
**Author:** Code Engineer (Paperclip Agent)
**Task:** AKSAA-6 - LinkedIn posting automation
