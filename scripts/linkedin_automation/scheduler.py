#!/usr/bin/env python3
"""
LinkedIn Posting Scheduler
Runs daily to post scheduled LinkedIn content based on posting_schedule.json
"""

import asyncio
import json
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict
import os

from post_to_linkedin import LinkedInPoster, parse_linkedin_export


class PostingScheduler:
    """Manages scheduled LinkedIn posts."""
    
    def __init__(self, schedule_file: Path, export_dir: Path):
        self.schedule_file = schedule_file
        self.export_dir = export_dir
        self.schedule_data = self._load_schedule()
        
    def _load_schedule(self) -> Dict:
        """Load the posting schedule from JSON."""
        if not self.schedule_file.exists():
            raise FileNotFoundError(f"Schedule file not found: {self.schedule_file}")
        return json.loads(self.schedule_file.read_text())
    
    def _save_schedule(self):
        """Save updated schedule back to JSON."""
        self.schedule_file.write_text(json.dumps(self.schedule_data, indent=2))
    
    def get_todays_posts(self) -> List[Dict]:
        """Get posts scheduled for today."""
        today = date.today().isoformat()
        
        for day_schedule in self.schedule_data['schedule']:
            if day_schedule['date'] == today:
                return day_schedule['posts']
        
        return []
    
    def mark_post_completed(self, filename: str, status: str = 'posted'):
        """Mark a post as completed in the schedule."""
        today = date.today().isoformat()
        
        for day_schedule in self.schedule_data['schedule']:
            if day_schedule['date'] == today:
                for post in day_schedule['posts']:
                    if post['file'] == filename:
                        post['status'] = status
                        post['posted_at'] = datetime.now().isoformat()
        
        self._save_schedule()
    
    async def run_daily_posts(self, email: str, password: str, 
                             headless: bool = True, dry_run: bool = False):
        """
        Run today's scheduled posts.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            headless: Run browser in headless mode
            dry_run: If True, don't actually post
        """
        posts = self.get_todays_posts()
        
        if not posts:
            print(f"[{datetime.now().isoformat()}] No posts scheduled for today")
            return
        
        print(f"\n{'='*80}")
        print(f"LinkedIn Posting Scheduler - {date.today().isoformat()}")
        print(f"Posts scheduled: {len(posts)}")
        print(f"Dry run: {dry_run}")
        print(f"{'='*80}\n")
        
        interval_minutes = self.schedule_data['config'].get('post_interval_minutes', 5)
        
        for idx, post in enumerate(posts, 1):
            filename = post['file']
            export_file = self.export_dir / filename
            
            if post.get('status') == 'posted':
                print(f"[{datetime.now().isoformat()}] ⏭️  Skipping {filename} (already posted)")
                continue
            
            if not export_file.exists():
                print(f"[{datetime.now().isoformat()}] ⚠️  Export file not found: {export_file}")
                self.mark_post_completed(filename, status='error_file_not_found')
                continue
            
            print(f"\n{'─'*80}")
            print(f"Post {idx}/{len(posts)}: {filename}")
            print(f"Type: {post.get('type', 'unknown')}, Day: {post.get('day', '?')}")
            print(f"{'─'*80}\n")
            
            if dry_run:
                print(f"[{datetime.now().isoformat()}] 🔍 DRY RUN - would post: {filename}")
                self.mark_post_completed(filename, status='dry_run')
            else:
                try:
                    # Parse the export file
                    post_text, image_paths = parse_linkedin_export(export_file)
                    
                    print(f"[{datetime.now().isoformat()}] Post length: {len(post_text)} chars")
                    print(f"[{datetime.now().isoformat()}] Images: {len(image_paths)}")
                    
                    # Create poster and post
                    async with LinkedInPoster(headless=headless) as poster:
                        logged_in = await poster.login(email, password)
                        if not logged_in:
                            print(f"[{datetime.now().isoformat()}] ❌ Login failed")
                            self.mark_post_completed(filename, status='error_login_failed')
                            break
                        
                        success = await poster.create_post(post_text, image_paths)
                        
                        if success:
                            print(f"[{datetime.now().isoformat()}] ✅ Posted successfully")
                            self.mark_post_completed(filename, status='posted')
                        else:
                            print(f"[{datetime.now().isoformat()}] ❌ Post failed")
                            self.mark_post_completed(filename, status='error_post_failed')
                    
                except Exception as e:
                    print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
                    self.mark_post_completed(filename, status=f'error_{type(e).__name__}')
            
            # Wait between posts
            if idx < len(posts):
                wait_seconds = interval_minutes * 60
                print(f"\n[{datetime.now().isoformat()}] ⏳ Waiting {interval_minutes} minutes before next post...")
                await asyncio.sleep(wait_seconds)
        
        print(f"\n{'='*80}")
        print(f"[{datetime.now().isoformat()}] ✅ Daily posting completed")
        print(f"{'='*80}\n")


async def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    schedule_file = script_dir / 'posting_schedule.json'
    
    # Load config
    schedule_data = json.loads(schedule_file.read_text())
    export_dir = Path(schedule_data['config']['export_dir'])
    dry_run = schedule_data['config'].get('dry_run', False)
    
    # Get credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set")
        sys.exit(1)
    
    # Run scheduler
    scheduler = PostingScheduler(schedule_file, export_dir)
    await scheduler.run_daily_posts(email, password, headless=True, dry_run=dry_run)


if __name__ == '__main__':
    asyncio.run(main())
