#!/usr/bin/env python3
"""
Create LinkedIn draft posts for CEO review
Creates tomorrow's posts as drafts in LinkedIn UI for manual review and scheduling
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

from post_to_linkedin import LinkedInPoster, parse_linkedin_export


async def create_draft_for_review(export_file: Path, email: str, password: str):
    """
    Create a LinkedIn draft post for manual review.
    
    Since LinkedIn scheduling requires Premium, we'll create the post in the composer
    and leave it as a draft for the CEO to review and schedule manually.
    """
    print(f"\n{'='*80}")
    print(f"Creating draft for review: {export_file.name}")
    print(f"{'='*80}\n")
    
    # Parse the export file
    post_text, image_paths = parse_linkedin_export(export_file)
    
    print(f"[{datetime.now().isoformat()}] Post length: {len(post_text)} chars")
    print(f"[{datetime.now().isoformat()}] Images: {len(image_paths)}")
    for img in image_paths:
        print(f"  - {img.name}")
    
    print(f"\n[{datetime.now().isoformat()}] Opening LinkedIn composer...")
    print(f"[{datetime.now().isoformat()}] ⚠️  You will need to:")
    print(f"  1. Review the post content")
    print(f"  2. Click the clock icon to schedule")
    print(f"  3. Set time: Tomorrow at 9:00 AM")
    print(f"  4. Save as scheduled post")
    print(f"\n[{datetime.now().isoformat()}] Starting browser (NOT headless for review)...\n")
    
    async with LinkedInPoster(headless=False) as poster:
        # Login
        logged_in = await poster.login(email, password)
        if not logged_in:
            print(f"[{datetime.now().isoformat()}] ❌ Login failed")
            return False
        
        # Navigate to feed
        await poster.page.goto('https://www.linkedin.com/feed/')
        await poster.page.wait_for_load_state('networkidle')
        
        # Click "Start a post"
        print(f"[{datetime.now().isoformat()}] Opening post composer...")
        try:
            start_post_selector = 'button:has-text("Start a post")'
            await poster.page.wait_for_selector(start_post_selector, timeout=10000)
            await poster.page.click(start_post_selector)
        except:
            await poster.page.click('.share-box-feed-entry__trigger')
        
        # Wait for modal
        await poster.page.wait_for_selector('.share-creation-state__text-editor', timeout=10000)
        
        # Fill text
        print(f"[{datetime.now().isoformat()}] Filling post text...")
        editor_selector = '.share-creation-state__text-editor .ql-editor'
        await poster.page.fill(editor_selector, post_text)
        
        # Upload images
        if image_paths:
            print(f"[{datetime.now().isoformat()}] Uploading images...")
            for idx, img_path in enumerate(image_paths, 1):
                if not img_path.exists():
                    print(f"  ⚠️  Image not found: {img_path}")
                    continue
                
                # Click image upload button
                await poster.page.click('button[aria-label*="Add a photo"]')
                
                # Upload file
                file_input = await poster.page.wait_for_selector('input[type="file"]')
                await file_input.set_input_files(str(img_path))
                await asyncio.sleep(2)
                print(f"  ✅ Uploaded image {idx}/{len(image_paths)}: {img_path.name}")
        
        print(f"\n{'='*80}")
        print(f"[{datetime.now().isoformat()}] ✅ Draft ready for review")
        print(f"{'='*80}")
        print(f"\nPost is loaded in LinkedIn composer. You can now:")
        print(f"  1. Review the content and images")
        print(f"  2. Click the clock/schedule icon (if you have LinkedIn Premium)")
        print(f"  3. Set schedule time: Tomorrow at 9:00 AM")
        print(f"  4. OR: Click 'Post' to publish immediately")
        print(f"  5. OR: Close the modal to discard")
        print(f"\nBrowser will stay open for 5 minutes for your review...")
        print(f"Press Ctrl+C to close browser now.\n")
        
        # Keep browser open for manual review
        try:
            await asyncio.sleep(300)  # 5 minutes
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().isoformat()}] Browser closed by user")
        
        return True


async def main():
    """Create both of tomorrow's posts as drafts for review."""
    import os
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set")
        print("\nSet in ~/.zshrc:")
        print('  export LINKEDIN_EMAIL="your@email.com"')
        print('  export LINKEDIN_PASSWORD="your_password"')
        sys.exit(1)
    
    export_dir = Path('~/Desktop/Github/Profile/scripts/linkedin-export').expanduser()
    
    # Tomorrow's posts
    posts = [
        ('ai-day-15-multi-model-routing-strategies.txt', 'AI Learning Day 15'),
        ('exp-day-18-supplier-rate-limiting.txt', 'Experience Day 18')
    ]
    
    print(f"\n{'='*80}")
    print(f"Creating LinkedIn drafts for CEO review")
    print(f"Tomorrow's posts: {len(posts)}")
    print(f"{'='*80}\n")
    
    for filename, title in posts:
        export_file = export_dir / filename
        
        if not export_file.exists():
            print(f"❌ File not found: {export_file}")
            continue
        
        print(f"\n{'─'*80}")
        print(f"Post: {title}")
        print(f"File: {filename}")
        print(f"{'─'*80}")
        
        input(f"\nPress Enter to create this draft in LinkedIn... ")
        
        success = await create_draft_for_review(export_file, email, password)
        
        if not success:
            print(f"❌ Failed to create draft for {filename}")
            break
        
        print(f"\n✅ Draft created for review")
        
        if filename != posts[-1][0]:  # Not the last post
            print(f"\nReady to create next post...")
    
    print(f"\n{'='*80}")
    print(f"✅ All drafts created")
    print(f"{'='*80}")
    print(f"\nNext steps:")
    print(f"  1. Check your LinkedIn feed for scheduled/draft posts")
    print(f"  2. Review content and alignment with existing series")
    print(f"  3. Confirm or adjust scheduling")
    print(f"\nNote: If you don't have LinkedIn Premium, you'll need to:")
    print(f"  - Save posts as drafts")
    print(f"  - Schedule them manually from your LinkedIn drafts")


if __name__ == '__main__':
    asyncio.run(main())
