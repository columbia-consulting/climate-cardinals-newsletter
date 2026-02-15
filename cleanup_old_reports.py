#!/usr/bin/env python3
"""
Utility script to manually clean up old HTML reports
Use this if you want to free up space or remove outdated reports
"""

import sys
from pathlib import Path
from datetime import datetime

# Configuration
WEEKLY_DATA_DIR = Path("weekly_data")
KEEP_RECENT_REPORTS = 3  # Number of reports to keep (change as needed)

def cleanup_old_reports(keep=KEEP_RECENT_REPORTS, dry_run=False):
    """
    Remove old HTML reports, keeping only the N most recent ones
    
    Args:
        keep (int): Number of recent reports to keep
        dry_run (bool): If True, show what would be deleted without deleting
    """
    # Get all report files sorted by modification time (newest first)
    html_files = sorted(
        WEEKLY_DATA_DIR.glob("climate_cardinals_report_*.html"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not html_files:
        print("📁 No reports found in weekly_data folder")
        return
    
    print(f"\n{'='*70}")
    print(f"🗑️  CLEANUP OLD REPORTS")
    print(f"{'='*70}")
    print(f"📊 Found {len(html_files)} report(s)")
    print(f"✅ Keeping {keep} most recent report(s)")
    
    if dry_run:
        print(f"🔍 DRY RUN MODE (nothing will be deleted)")
    
    print(f"\n{'='*70}")
    
    # List all reports with their dates
    print(f"\n📋 All Reports:")
    for i, report in enumerate(html_files, 1):
        mod_time = datetime.fromtimestamp(report.stat().st_mtime)
        status = "✅ KEEP" if i <= keep else "❌ DELETE"
        print(f"   {i}. {report.name}")
        print(f"      Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')} - {status}")
    
    # Delete old reports
    if len(html_files) > keep:
        old_reports = html_files[keep:]
        print(f"\n{'='*70}")
        print(f"🗑️  Reports to delete: {len(old_reports)}")
        print(f"{'='*70}")
        
        deleted_count = 0
        for old_report in old_reports:
            try:
                if not dry_run:
                    old_report.unlink()
                    print(f"   ✅ Deleted: {old_report.name}")
                else:
                    print(f"   [DRY RUN] Would delete: {old_report.name}")
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Failed to delete {old_report.name}: {e}")
        
        if not dry_run:
            print(f"\n✅ Successfully deleted {deleted_count} old report(s)")
        else:
            print(f"\n🔍 Would delete {deleted_count} report(s) in real run")
    else:
        print(f"\n✅ No cleanup needed (have {len(html_files)}, keeping {keep})")
    
    # Update index.html if reports were deleted
    if not dry_run and len(html_files) > keep:
        try:
            from web_report_generator import update_index_html
            update_index_html(str(WEEKLY_DATA_DIR))
            print(f"✅ Updated index.html")
        except Exception as e:
            print(f"⚠️  Could not update index.html: {e}")
    
    print(f"\n{'='*70}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean up old HTML reports from weekly_data folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be deleted (keeps 3 most recent)
  python cleanup_old_reports.py --dry-run
  
  # Delete old reports, keeping 3 most recent
  python cleanup_old_reports.py
  
  # Keep only the most recent report
  python cleanup_old_reports.py --keep 1
  
  # Keep last 5 reports
  python cleanup_old_reports.py --keep 5
        """
    )
    
    parser.add_argument(
        '--keep',
        type=int,
        default=KEEP_RECENT_REPORTS,
        help=f'Number of recent reports to keep (default: {KEEP_RECENT_REPORTS})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    args = parser.parse_args()
    
    if args.keep < 1:
        print("❌ Error: --keep must be at least 1")
        sys.exit(1)
    
    cleanup_old_reports(keep=args.keep, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
