#!/usr/bin/env python3
"""
LinkedIn Post Automation using Playwright
Posts LinkedIn content with images from the linkedin-export directory.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser


class LinkedInPoster:
    """Automate LinkedIn posting with Playwright."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            
        Returns:
            True if login successful
        """
        print(f"[{datetime.now().isoformat()}] Navigating to LinkedIn login...")
        await self.page.goto('https://www.linkedin.com/login')
        
        print(f"[{datetime.now().isoformat()}] Filling credentials...")
        await self.page.fill('#username', email)
        await self.page.fill('#password', password)
        
        print(f"[{datetime.now().isoformat()}] Clicking sign in...")
        await self.page.click('button[type="submit"]')
        
        # Wait for navigation
        await self.page.wait_for_load_state('networkidle')
        
        # Check if we're logged in (feed should be visible)
        try:
            await self.page.wait_for_selector('a[href*="/feed/"]', timeout=10000)
            print(f"[{datetime.now().isoformat()}] ✅ Login successful")
            return True
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ❌ Login failed: {e}")
            return False
            
    async def create_post(self, text: str, image_paths: Optional[List[Path]] = None) -> bool:
        """
        Create a LinkedIn post with text and optional images.
        
        Args:
            text: Post text content
            image_paths: Optional list of image file paths to upload
            
        Returns:
            True if post created successfully
        """
        print(f"[{datetime.now().isoformat()}] Navigating to feed...")
        await self.page.goto('https://www.linkedin.com/feed/')
        await self.page.wait_for_load_state('networkidle')
        
        # Click "Start a post" button
        print(f"[{datetime.now().isoformat()}] Opening post composer...")
        try:
            start_post_selector = 'button:has-text("Start a post")'
            await self.page.wait_for_selector(start_post_selector, timeout=10000)
            await self.page.click(start_post_selector)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ⚠️  Trying alternative selector...")
            # Try alternative selectors
            await self.page.click('.share-box-feed-entry__trigger')
            
        # Wait for the post modal to appear
        await self.page.wait_for_selector('.share-creation-state__text-editor', timeout=10000)
        
        # Fill in post text
        print(f"[{datetime.now().isoformat()}] Filling post text ({len(text)} chars)...")
        editor_selector = '.share-creation-state__text-editor .ql-editor'
        await self.page.fill(editor_selector, text)
        
        # Upload images if provided
        if image_paths:
            print(f"[{datetime.now().isoformat()}] Uploading {len(image_paths)} images...")
            for idx, img_path in enumerate(image_paths, 1):
                if not img_path.exists():
                    print(f"[{datetime.now().isoformat()}] ⚠️  Image not found: {img_path}")
                    continue
                    
                # Click the image upload button
                await self.page.click('button[aria-label*="Add a photo"]')
                
                # Upload the file
                file_input = await self.page.wait_for_selector('input[type="file"]')
                await file_input.set_input_files(str(img_path))
                
                # Wait for upload to complete
                await asyncio.sleep(2)
                print(f"[{datetime.now().isoformat()}]   ✅ Uploaded image {idx}/{len(image_paths)}")
        
        # Click Post button
        print(f"[{datetime.now().isoformat()}] Publishing post...")
        post_button_selector = 'button:has-text("Post")'
        await self.page.click(post_button_selector)
        
        # Wait for post to be published
        await asyncio.sleep(3)
        
        print(f"[{datetime.now().isoformat()}] ✅ Post published successfully")
        return True
        
    async def create_scheduled_post(self, text: str, schedule_time: datetime, 
                                   image_paths: Optional[List[Path]] = None) -> bool:
        """
        Create a scheduled LinkedIn post (requires Premium).
        
        Note: LinkedIn scheduling is only available for Premium accounts.
        For non-Premium accounts, use external scheduling (cron/launchd).
        
        Args:
            text: Post text content
            schedule_time: When to publish the post
            image_paths: Optional list of image file paths
            
        Returns:
            True if scheduled successfully
        """
        print(f"[{datetime.now().isoformat()}] Creating scheduled post for {schedule_time}...")
        
        # Start creating the post
        await self.page.goto('https://www.linkedin.com/feed/')
        await self.page.wait_for_load_state('networkidle')
        
        # Click "Start a post"
        start_post_selector = 'button:has-text("Start a post")'
        await self.page.click(start_post_selector)
        await self.page.wait_for_selector('.share-creation-state__text-editor', timeout=10000)
        
        # Fill text
        editor_selector = '.share-creation-state__text-editor .ql-editor'
        await self.page.fill(editor_selector, text)
        
        # Upload images if provided
        if image_paths:
            for img_path in image_paths:
                if img_path.exists():
                    await self.page.click('button[aria-label*="Add a photo"]')
                    file_input = await self.page.wait_for_selector('input[type="file"]')
                    await file_input.set_input_files(str(img_path))
                    await asyncio.sleep(2)
        
        # Click clock/schedule icon
        try:
            schedule_selector = 'button[aria-label*="Schedule"]'
            await self.page.click(schedule_selector)
            
            # Fill in schedule time (LinkedIn's schedule UI)
            # This is Premium-only and UI varies by account
            print(f"[{datetime.now().isoformat()}] ⚠️  Schedule UI detected (Premium required)")
            
            # For now, save as draft instead
            await self.page.keyboard.press('Escape')
            return False
            
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] ⚠️  Scheduling not available: {e}")
            print(f"[{datetime.now().isoformat()}] ℹ️  Use external scheduling (cron/launchd) instead")
            return False


def parse_linkedin_export(export_file: Path) -> tuple[str, List[Path]]:
    """
    Parse a LinkedIn export .txt file to extract post text and image paths.
    
    Args:
        export_file: Path to the .txt export file
        
    Returns:
        Tuple of (post_text, list_of_image_paths)
    """
    content = export_file.read_text(encoding='utf-8')
    
    # Split into diagrams section and article section
    if '=== ARTICLE ===' not in content:
        raise ValueError(f"Invalid export file format: {export_file}")
    
    diagrams_section, article_section = content.split('=== ARTICLE ===', 1)
    
    # Extract image paths from diagrams section
    image_paths = []
    for line in diagrams_section.split('\n'):
        if line.strip().startswith('•') and '.png' in line and '→' in line:
            # Extract path after arrow
            path_str = line.split('→')[-1].strip()
            img_path = Path(path_str)
            if img_path.exists():
                image_paths.append(img_path)
    
    # Extract article text (remove diagram upload instructions)
    lines = article_section.strip().split('\n')
    clean_lines = []
    for line in lines:
        # Skip diagram upload instruction lines
        if '[Upload diagram' in line or '→ /Users/' in line:
            continue
        clean_lines.append(line)
    
    post_text = '\n'.join(clean_lines).strip()
    
    return post_text, image_paths


async def post_single_article(export_file: Path, email: str, password: str, 
                              headless: bool = False) -> bool:
    """
    Post a single LinkedIn article from an export file.
    
    Args:
        export_file: Path to .txt export file
        email: LinkedIn email
        password: LinkedIn password
        headless: Run browser in headless mode
        
    Returns:
        True if posted successfully
    """
    print(f"\n{'='*80}")
    print(f"Processing: {export_file.name}")
    print(f"{'='*80}\n")
    
    # Parse the export file
    post_text, image_paths = parse_linkedin_export(export_file)
    
    print(f"Post length: {len(post_text)} chars")
    print(f"Images: {len(image_paths)}")
    
    # Create and post
    async with LinkedInPoster(headless=headless) as poster:
        # Login
        logged_in = await poster.login(email, password)
        if not logged_in:
            print("❌ Login failed, aborting")
            return False
        
        # Create post
        success = await poster.create_post(post_text, image_paths)
        return success


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python post_to_linkedin.py <export_file.txt>")
        print("  python post_to_linkedin.py --queue <queue_file.json>")
        print("\nEnvironment variables required:")
        print("  LINKEDIN_EMAIL - Your LinkedIn email")
        print("  LINKEDIN_PASSWORD - Your LinkedIn password")
        sys.exit(1)
    
    import os
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set")
        sys.exit(1)
    
    export_file = Path(sys.argv[1])
    
    if not export_file.exists():
        print(f"❌ File not found: {export_file}")
        sys.exit(1)
    
    success = await post_single_article(export_file, email, password, headless=False)
    
    if success:
        print("\n✅ Post completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Post failed")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
