#!/usr/bin/env python3
"""
Validation script to test newsletter automation fixes
Tests data accumulation, deduplication, and state tracking
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

def test_data_accumulation():
    """Test that data accumulates across multiple runs"""
    print("\n" + "="*60)
    print("TEST 1: Data Accumulation")
    print("="*60)
    
    weekly_data = Path("weekly_data")
    grants_csv = weekly_data / "grants.csv"
    
    if not grants_csv.exists():
        print("❌ FAILED: grants.csv not found")
        print("   Run 'python automated_newsletter.py' first")
        return False
    
    # Check CSV has data
    df = pd.read_csv(grants_csv)
    row_count = len(df)
    
    if row_count == 0:
        print("❌ FAILED: grants.csv is empty")
        return False
    
    print(f"✅ PASSED: grants.csv has {row_count} rows")
    print(f"   Columns: {list(df.columns)}")
    
    # Check if URL column exists
    if 'URL' not in df.columns:
        print("❌ FAILED: URL column missing (needed for deduplication)")
        return False
    
    print("✅ PASSED: URL column exists for deduplication")
    return True

def test_deduplication():
    """Test that duplicate URLs are removed"""
    print("\n" + "="*60)
    print("TEST 2: Deduplication")
    print("="*60)
    
    weekly_data = Path("weekly_data")
    csv_files = ['grants.csv', 'events.csv', 'csr_reports.csv', 'experts.csv']
    
    all_passed = True
    
    for csv_file in csv_files:
        csv_path = weekly_data / csv_file
        
        if not csv_path.exists():
            print(f"⏭️  SKIPPED: {csv_file} not found")
            continue
        
        df = pd.read_csv(csv_path)
        
        if len(df) == 0:
            print(f"⏭️  SKIPPED: {csv_file} is empty")
            continue
        
        # Check for duplicate URLs
        url_column = 'URL' if 'URL' in df.columns else 'LinkedIn'
        
        if url_column not in df.columns:
            print(f"❌ FAILED: {csv_file} - No URL/LinkedIn column for deduplication")
            all_passed = False
            continue
        
        duplicates = df[df.duplicated(subset=[url_column], keep=False)]
        
        if len(duplicates) > 0:
            print(f"❌ FAILED: {csv_file} - Found {len(duplicates)} duplicate {url_column}s")
            print(f"   Sample duplicates:")
            print(duplicates[[url_column]].head())
            all_passed = False
        else:
            print(f"✅ PASSED: {csv_file} - No duplicate {url_column}s ({len(df)} unique entries)")
    
    return all_passed

def test_state_tracking():
    """Test that state.json tracks scraping"""
    print("\n" + "="*60)
    print("TEST 3: State Tracking")
    print("="*60)
    
    state_path = Path("weekly_data/state.json")
    
    if not state_path.exists():
        print("❌ FAILED: state.json not found")
        return False
    
    import json
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    # Check required fields
    required_fields = ['last_scrape_date', 'last_email_sent', 'week_start_date']
    missing_fields = [f for f in required_fields if f not in state]
    
    if missing_fields:
        print(f"❌ FAILED: Missing fields in state.json: {missing_fields}")
        return False
    
    print("✅ PASSED: state.json has all required fields")
    print(f"   Last scrape: {state.get('last_scrape_date')}")
    print(f"   Last email: {state.get('last_email_sent')}")
    print(f"   Week start: {state.get('week_start_date')}")
    
    # Check if last_scrape_date is today
    today = str(datetime.now().date())
    if state['last_scrape_date'] == today:
        print(f"✅ PASSED: Last scrape date is today ({today})")
    else:
        print(f"⚠️  WARNING: Last scrape date is {state['last_scrape_date']}, not today ({today})")
    
    return True

def test_file_structure():
    """Test that all necessary files exist"""
    print("\n" + "="*60)
    print("TEST 4: File Structure")
    print("="*60)
    
    required_files = [
        "automated_newsletter.py",
        "email_template_condensed.py",
        "web_report_generator.py",
        "netlify.toml",
        ".github/workflows/newsletter.yml",
        "requirements.txt"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ MISSING: {file_path}")
            all_exist = False
    
    return all_exist

def test_netlify_config():
    """Test that Netlify configuration is correct"""
    print("\n" + "="*60)
    print("TEST 5: Netlify Configuration")
    print("="*60)
    
    netlify_toml = Path("netlify.toml")
    
    if not netlify_toml.exists():
        print("❌ FAILED: netlify.toml not found")
        return False
    
    content = netlify_toml.read_text()
    
    checks = [
        ('publish = "weekly_data"', "Publish directory"),
        ('[[redirects]]', "Redirects configuration")
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"✅ PASSED: {description} configured")
        else:
            print(f"❌ FAILED: {description} missing")
            all_passed = False
    
    return all_passed

def main():
    print("="*60)
    print("🧪 NEWSLETTER AUTOMATION - VALIDATION TESTS")
    print("="*60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    results = {
        "Data Accumulation": test_data_accumulation(),
        "Deduplication": test_deduplication(),
        "State Tracking": test_state_tracking(),
        "File Structure": test_file_structure(),
        "Netlify Config": test_netlify_config()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Connect Netlify to your GitHub repository")
        print("2. Add WEB_REPORT_BASE_URL secret to GitHub Actions")
        print("3. Push changes to GitHub")
        print("4. Monitor the first week of operation")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
