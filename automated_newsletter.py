#!/usr/bin/env python3
"""
Climate Cardinals - Automated Weekly Newsletter System
Uses DuckDuckGo (free, no API keys needed)
"""

import os
import sys
import json
import re
import csv
import time
import html
import random
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from ddgs import DDGS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------------- CONFIG ----------------------
POLITE_DELAY = 0.25
MAX_RESULTS_PER_KEYWORD = 4
MAX_ROWS_PER_SECTION = 40
MIN_YEAR = 2026  # Current year - update annually
OUTPUT_FOLDER = Path("weekly_data")
OUTPUT_FOLDER.mkdir(exist_ok=True)
TODAY = datetime.now().date()

# Email format configuration
USE_CONDENSED_EMAIL = True  # Set to False to use full format with all data

# Data retention configuration
KEEP_RECENT_REPORTS = 3  # Number of recent HTML reports to keep (0 = keep all, 1 = only latest)
CLEANUP_OLD_REPORTS = True  # Set to False to never delete old reports

# Web hosting configuration for full reports
# IMPORTANT: Set this to your hosted URL before sending to users!
# Options:
#   - GitHub Pages: "https://yourusername.github.io/climate-cardinals-reports"
#   - Netlify: "https://your-site.netlify.app"
#   - AWS S3: "https://your-bucket.s3.amazonaws.com"
#   - Custom domain: "https://reports.climatecaridinals.org"
#   - Leave empty "" to use local file:// URLs (only works on your computer)
WEB_REPORT_BASE_URL = os.getenv("WEB_REPORT_BASE_URL", "")

# Email config
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECIPIENT_EMAILS = [e.strip() for e in os.getenv("RECIPIENT_EMAILS", "").split(",") if e.strip()]

# ---------------------- KEYWORDS ----------------------
GRANT_KEYWORDS = [
    "resilience grant", "sustainability grant", "climate adaptation grant",
    "climate resilience funding", "community resilience grant"
]

EVENT_KEYWORDS = [
    "climate conference 2026", "sustainability summit 2026", "climate week 2026",
    "resilience symposium 2026", "environmental conference 2026 2027"
]

CSR_KEYWORDS = [
    "sustainability report pdf", "ESG report pdf", "impact report pdf",
    "climate disclosure report"
]

EXPERT_QUERIES = [
    "climate nonprofit executive director LinkedIn",
    "head of sustainability nonprofit LinkedIn",
    "climate resilience NGO director LinkedIn"
]

# ---------------------- RELEVANCE FILTER ----------------------
CLIMATE_TERMS = [
    "climate", "resilien", "adapt", "sustain", "environment", "decarbon",
    "net zero", "renewable", "flood", "heat", "wildfire", "community", "justice"
]

def looks_relevant(title, snippet, url):
    blob = f"{title} {snippet} {url}".lower()
    
    # Filter out Wikipedia, books, and other irrelevant content
    exclude_patterns = [
        "wikipedia.org",
        "grokipedia.com",
        "(book)",
        "book review",
        "amazon.com",
        "goodreads.com",
        "isbn"
    ]
    
    if any(pattern in blob for pattern in exclude_patterns):
        return False
    
    return any(t in blob for t in CLIMATE_TERMS)

# ---------------------- UTILS ----------------------
def clean_text(txt):
    return html.unescape(re.sub(r"\s+", " ", txt or "").strip())

def domain_from_url(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return "—"

def extract_year(text):
    try:
        return parser.parse(text, fuzzy=True).year
    except:
        return None

def extract_date_snippet(text, future=True):
    if not text:
        return "—"
    
    # Enhanced pattern to catch various date formats
    # Format 1: "January 15, 2026" or "Jan 15, 2026"
    month_full_pat = re.compile(
        r"(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"\.?\s+\d{1,2},?\s*(20\d{2})", re.I
    )
    
    # Format 2: "15 January 2026" or "15 Jan 2026"
    day_month_pat = re.compile(
        r"\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"\.?\s*(20\d{2})", re.I
    )
    
    # Format 3: "2026-01-15" or "01/15/2026" or "15-01-2026"
    numeric_pat = re.compile(r"(20\d{2})[/-](0?\d|1[0-2])[/-](0?\d|[12]\d|3[01])|"
                            r"(0?\d|1[0-2])[/-](0?\d|[12]\d|3[01])[/-](20\d{2})|"
                            r"(0?\d|[12]\d|3[01])[/-](0?\d|1[0-2])[/-](20\d{2})")
    
    # Look for deadline keywords followed by dates
    deadline_patterns = [
        r"(?:deadline|due|submit\s+by|applications?\s+(?:due|close)|closes?|ends?)[:\s]+(.*?)(?:\.|,|$)",
        r"(?:apply\s+by|applications?\s+accepted\s+until)[:\s]+(.*?)(?:\.|,|$)",
        r"(?:open\s+until|accepting\s+until)[:\s]+(.*?)(?:\.|,|$)"
    ]
    
    for pat in deadline_patterns:
        match = re.search(pat, text, re.I)
        if match:
            date_text = match.group(1)
            # Try to extract date from this snippet
            date_match = month_full_pat.search(date_text) or day_month_pat.search(date_text) or numeric_pat.search(date_text)
            if date_match:
                year_str = date_match.group(2) if len(date_match.groups()) >= 2 else date_match.group(0)[-4:]
                try:
                    year = int(re.search(r'20\d{2}', year_str).group())
                    if year >= MIN_YEAR:
                        return date_match.group(0)
                except:
                    pass
    
    # Standard date search
    for m in month_full_pat.finditer(text):
        year_match = re.search(r'20\d{2}', m.group(0))
        if year_match:
            year = int(year_match.group())
            if year >= MIN_YEAR:
                return m.group(0)
    
    for m in day_month_pat.finditer(text):
        year_match = re.search(r'20\d{2}', m.group(0))
        if year_match:
            year = int(year_match.group())
            if year >= MIN_YEAR:
                return m.group(0)
    
    if future and re.search(r"rolling|ongoing|open\s+until|continuous", text, re.I):
        return "Rolling / Ongoing"
    
    return "—"

def calculate_deadline_text(date_str):
    """Convert a date string into a countdown format like 'Due in 4 weeks'"""
    if not date_str or date_str == "—":
        return "—"
    
    if "rolling" in date_str.lower() or "ongoing" in date_str.lower():
        return "Rolling deadline"
    
    try:
        # Parse the date
        deadline_date = parser.parse(date_str, fuzzy=True)
        today = datetime.now()
        
        # Calculate difference
        days_until = (deadline_date - today).days
        
        if days_until < 0:
            return "Deadline passed"
        elif days_until == 0:
            return "Due today"
        elif days_until == 1:
            return "Due tomorrow"
        elif days_until < 7:
            return f"Due in {days_until} days"
        elif days_until < 30:
            weeks = days_until // 7
            return f"Due in {weeks} week{'s' if weeks > 1 else ''}"
        elif days_until < 365:
            months = days_until // 30
            return f"Due in {months} month{'s' if months > 1 else ''}"
        else:
            return date_str  # Far future, just show the date
    except:
        return date_str  # If parsing fails, return original date

# ---------------------- SEARCH ----------------------
def web_search(query, num=8):
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num):
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception as e:
        print(f"⚠️  Search error: {e}")
    return results

# ---------------------- CORE PIPELINE ----------------------
def run_section(keywords, future=True):
    rows = []
    seen_domains = set()
    for kw in keywords:
        if len(rows) >= MAX_ROWS_PER_SECTION:
            break
        print(f"🔍 Searching: {kw}")
        items = web_search(kw, num=8)[:MAX_RESULTS_PER_KEYWORD]
        for item in items:
            if len(rows) >= MAX_ROWS_PER_SECTION:
                break
            url = item["link"]
            domain = domain_from_url(url)
            if not url or domain in seen_domains:
                continue
            seen_domains.add(domain)
            title = clean_text(item["title"])
            snippet = clean_text(item["snippet"])
            if not looks_relevant(title, snippet, url):
                continue
            
            date_info = extract_date_snippet(f"{title} {snippet}", future=future)
            
            # For future events/grants, filter smartly
            if future:
                year = extract_year(date_info)
                
                # REJECT: Explicitly old events (with confirmed past dates)
                if year and year < MIN_YEAR:
                    continue
                
                # REJECT: Events with past dates we can parse
                if date_info != "—" and date_info != "Rolling / Ongoing":
                    try:
                        event_date = parser.parse(date_info, fuzzy=True)
                        if event_date.date() < TODAY:
                            continue  # Skip past events
                    except:
                        pass  # If parsing fails, include it
                
                # ACCEPT: Items with no date (most upcoming events don't have dates in snippets)
                # ACCEPT: Rolling/Ongoing items
                # ACCEPT: Items with future dates
            
            # Add deadline countdown for grants
            deadline_text = calculate_deadline_text(date_info) if future else date_info
            
            rows.append({
                "Title": title,
                "Organization": domain,
                "Description": snippet,
                "Date Info": date_info,
                "Deadline": deadline_text,
                "URL": url
            })
        time.sleep(POLITE_DELAY + random.uniform(0, 0.15))
    return rows

def looks_like_person(name):
    return (len(name.split()) >= 2 and name[0].isupper() and
            not any(x in name.lower() for x in ["jobs", "careers", "hiring"]))

def run_experts(queries):
    rows = []
    seen_profiles = set()
    for q in queries:
        print(f"🔍 Searching Experts: {q}")
        items = web_search(q, num=12)
        for item in items:
            url = item["link"]
            if "linkedin.com/in" not in url:
                continue
            if url in seen_profiles:
                continue
            seen_profiles.add(url)
            title = clean_text(item["title"])
            snippet = clean_text(item["snippet"])
            
            # Parse name and role - split only on the FIRST dash/em-dash separator
            # This preserves hyphens within job titles (e.g., "C-Suite Executive")
            name = "—"
            role = "—"
            
            if "–" in title:  # Em-dash separator
                parts = title.split("–", 1)  # Split only once
                name = parts[0].strip()
                role = parts[1].strip() if len(parts) > 1 else "—"
            elif " - " in title:  # Regular dash with spaces
                parts = title.split(" - ", 1)  # Split only once
                name = parts[0].strip()
                role = parts[1].strip() if len(parts) > 1 else "—"
            else:
                name = title.strip()
                role = "—"
            
            if not looks_like_person(name):
                continue
            
            # Clean up role - remove truncation artifacts or overly short roles
            if role != "—" and (len(role) <= 2 or not any(c.isalpha() for c in role[1:])):
                role = "—"
            
            org = "—"
            if " at " in snippet:
                org = snippet.split(" at ")[-1].split(".")[0].strip()
            rows.append({
                "Name": name,
                "Role": role,
                "Organization": org,
                "LinkedIn": url
            })
        time.sleep(POLITE_DELAY)
        if len(rows) >= 30:
            break
    return rows

# ---------------------- WRITE CSVs WITH ACCUMULATION ----------------------
def write_csv(name, data):
    """Accumulate data to CSV and remove duplicates by URL"""
    path = OUTPUT_FOLDER / name
    
    if not data:
        print(f"Saved {name} (0 rows)")
        return
    
    # Convert new data to DataFrame
    new_df = pd.DataFrame(data)
    
    # Load existing data if file exists
    if path.exists():
        try:
            existing_df = pd.read_csv(path)
            # Combine existing and new data
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except (pd.errors.EmptyDataError, FileNotFoundError):
            combined_df = new_df
    else:
        combined_df = new_df
    
    # Determine which column to use for deduplication
    # experts.csv uses 'LinkedIn', others use 'URL'
    if 'LinkedIn' in combined_df.columns:
        dedup_column = 'LinkedIn'
    elif 'URL' in combined_df.columns:
        dedup_column = 'URL'
    else:
        # No unique identifier column, save without deduplication
        combined_df.to_csv(path, index=False)
        print(f"Saved {name} (+{len(new_df)} new, {len(combined_df)} total, no deduplication)")
        return
    
    # Remove duplicates by unique column (keep first occurrence)
    deduplicated_df = combined_df.drop_duplicates(subset=[dedup_column], keep='first')
    
    # Save back to CSV
    deduplicated_df.to_csv(path, index=False)
    
    new_count = len(new_df)
    total_count = len(deduplicated_df)
    duplicates_removed = len(combined_df) - len(deduplicated_df)
    
    if duplicates_removed > 0:
        print(f"Saved {name} (+{new_count} new, {total_count} total, {duplicates_removed} duplicates removed)")
    else:
        print(f"Saved {name} (+{new_count} new, {total_count} total after deduplication)")

def clear_weekly_data():
    """Clear all CSV files and old HTML reports for fresh week"""
    csv_files = ['grants.csv', 'events.csv', 'csr_reports.csv', 'experts.csv']
    cleared_count = 0
    
    # Clear CSV data files
    for csv_file in csv_files:
        path = OUTPUT_FOLDER / csv_file
        if path.exists():
            path.unlink()
            cleared_count += 1
            print(f"🗑️  Cleared {csv_file}")
    
    print(f"✅ Weekly data cleared ({cleared_count} CSV files)")
    
    # Clean up old HTML reports based on configuration
    if CLEANUP_OLD_REPORTS:
        cleanup_old_reports()

def cleanup_old_reports():
    """Remove old HTML reports, keeping only the N most recent ones"""
    # Get all report files sorted by date (newest first)
    html_files = sorted(
        OUTPUT_FOLDER.glob("climate_cardinals_report_*.html"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not html_files:
        return
    
    # Determine how many to keep
    keep_count = max(1, KEEP_RECENT_REPORTS)  # Always keep at least 1
    
    if len(html_files) > keep_count:
        old_reports = html_files[keep_count:]
        print(f"\n🗑️  Cleaning up old reports (keeping {keep_count} most recent)...")
        
        for old_report in old_reports:
            try:
                old_report.unlink()
                print(f"   ✖️  Deleted: {old_report.name}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete {old_report.name}: {e}")
        
        print(f"✅ Cleaned up {len(old_reports)} old report(s)")
    else:
        print(f"\n📁 Currently have {len(html_files)} report(s) (keeping {keep_count})")

def load_or_create_state():
    """Load state.json or create new one"""
    state_path = OUTPUT_FOLDER / "state.json"
    
    if state_path.exists():
        try:
            with open(state_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Default state
    return {
        "queries_used_today": 0,
        "last_reset_date": str(TODAY),
        "last_email_sent": None,
        "last_scrape_date": None,
        "week_start_date": str(TODAY)
    }

def save_state(state):
    """Save state to state.json"""
    state_path = OUTPUT_FOLDER / "state.json"
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

# ---------------------- EMAIL ----------------------
def send_email(grants_data, events_data, csr_data, experts_data, use_condensed=True):
    """Send newsletter email using condensed or full template - only on Monday"""
    # Only send on Monday (weekday 0 = Monday)
    if datetime.now().weekday() != 0:
        print(f"⏭️  Not Monday (today is {datetime.now().strftime('%A')}), skipping email send")
        return False
    
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAILS:
        print("⚠️  Email config missing, skipping send")
        return False
    
    # Import template generator based on format choice
    if use_condensed:
        from email_template_condensed import generate_condensed_email_html as generate_template
        template_type = "Condensed Digest"
    else:
        from email_template import generate_email_html as generate_template
        template_type = "Full Report"
    
    # Convert to DataFrames and rename columns for template
    grants_df = pd.DataFrame(grants_data) if grants_data else pd.DataFrame()
    events_df = pd.DataFrame(events_data) if events_data else pd.DataFrame()
    csr_df = pd.DataFrame(csr_data) if csr_data else pd.DataFrame()
    experts_df = pd.DataFrame(experts_data) if experts_data else pd.DataFrame()
    
    # Rename Organization to Domain for template compatibility
    if not grants_df.empty:
        grants_df = grants_df.rename(columns={'Organization': 'Domain'})
    if not events_df.empty:
        events_df = events_df.rename(columns={'Organization': 'Domain'})
    if not csr_df.empty:
        csr_df = csr_df.rename(columns={'Organization': 'Domain'})
    
    # Generate HTML using selected template
    if use_condensed:
        html_content = generate_template(experts_df, grants_df, events_df, csr_df, base_url=WEB_REPORT_BASE_URL)
    else:
        html_content = generate_template(experts_df, grants_df, events_df, csr_df)
    
    # Send email
    try:
        msg = MIMEMultipart("alternative")
        subject_prefix = "🌍 Climate Cardinals Newsletter"
        if use_condensed:
            subject_prefix += " - Weekly Digest"
        msg["Subject"] = f"{subject_prefix} - {TODAY}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(RECIPIENT_EMAILS)
        
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        
        print(f"✅ Email sent ({template_type}) to {len(RECIPIENT_EMAILS)} recipients")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        print("⚠️  Data preserved - you can retry sending the email")
        return False

# ---------------------- MAIN ----------------------
def main():
    print("=" * 70)
    print("🌍 CLIMATE CARDINALS - AUTOMATED NEWSLETTER")
    print("=" * 70)
    print(f"📅 Date: {TODAY}")
    print(f"📆 Day: {datetime.now().strftime('%A')}")
    
    # Load state
    state = load_or_create_state()
    
    # Check if already scraped today
    if state.get('last_scrape_date') == str(TODAY):
        print(f"⏭️  Already scraped data today ({TODAY}), skipping scrape")
        print("   Run on a different day or delete state.json to force re-scrape")
        return
    
    # Scrape new data
    print("\n🔍 Scraping new data...")
    grants_data = run_section(GRANT_KEYWORDS, future=True)
    events_data = run_section(EVENT_KEYWORDS, future=True)
    csr_data = run_section(CSR_KEYWORDS, future=False)
    experts_data = run_experts(EXPERT_QUERIES)
    
    # Accumulate to CSV files (with deduplication)
    write_csv("grants.csv", grants_data)
    write_csv("events.csv", events_data)
    write_csv("csr_reports.csv", csr_data)
    write_csv("experts.csv", experts_data)
    
    print(f"\n✅ CSVs saved to: {OUTPUT_FOLDER.resolve()}")
    
    # Update state with last scrape date
    state['last_scrape_date'] = str(TODAY)
    save_state(state)
    
    # Load accumulated data for email (all data from the week)
    grants_df = pd.read_csv(OUTPUT_FOLDER / "grants.csv") if (OUTPUT_FOLDER / "grants.csv").exists() else pd.DataFrame()
    events_df = pd.read_csv(OUTPUT_FOLDER / "events.csv") if (OUTPUT_FOLDER / "events.csv").exists() else pd.DataFrame()
    csr_df = pd.read_csv(OUTPUT_FOLDER / "csr_reports.csv") if (OUTPUT_FOLDER / "csr_reports.csv").exists() else pd.DataFrame()
    experts_df = pd.read_csv(OUTPUT_FOLDER / "experts.csv") if (OUTPUT_FOLDER / "experts.csv").exists() else pd.DataFrame()
    
    # Convert back to list of dicts for email function
    all_grants = grants_df.to_dict('records') if not grants_df.empty else []
    all_events = events_df.to_dict('records') if not events_df.empty else []
    all_csr = csr_df.to_dict('records') if not csr_df.empty else []
    all_experts = experts_df.to_dict('records') if not experts_df.empty else []
    
    # Send email (only on Monday)
    email_sent = send_email(all_grants, all_events, all_csr, all_experts, use_condensed=USE_CONDENSED_EMAIL)
    
    # Clear data if email was successfully sent
    if email_sent:
        print("\n🗑️  Clearing weekly data for fresh start...")
        clear_weekly_data()
        state['last_email_sent'] = str(TODAY)
        state['week_start_date'] = str(TODAY + timedelta(days=1))  # Next week starts tomorrow
        save_state(state)
    
    # Display summary
    pd.set_option("display.max_colwidth", 120)
    print("\n===== 📊 WEEKLY TOTALS =====")
    print(f"📧 Grants: {len(all_grants)}")
    print(f"🎤 Events: {len(all_events)}")
    print(f"🏢 CSR Reports: {len(all_csr)}")
    print(f"👥 Experts: {len(all_experts)}")
    
    if grants_data:
        print("\n===== 🌍 NEW GRANTS (Today) =====")
        print(pd.DataFrame(grants_data).to_string())
    if events_data:
        print("\n===== 🎤 NEW EVENTS (Today) =====")
        print(pd.DataFrame(events_data).to_string())
    if csr_data:
        print("\n===== 🏢 NEW CSR REPORTS (Today) =====")
        print(pd.DataFrame(csr_data).to_string())
    if experts_data:
        print("\n===== 👥 NEW EXPERTS (Today) =====")
        print(pd.DataFrame(experts_data).to_string())

if __name__ == "__main__":
    main()
