#!/usr/bin/env python3
"""
Test script to send newsletter email immediately (bypasses Monday check)
Use this to test your email configuration with real data
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_email():
    """Send test email with current accumulated data"""
    
    print("="*60)
    print("📧 EMAIL TEST SCRIPT")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check environment variables
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "")
    WEB_REPORT_BASE_URL = os.getenv("WEB_REPORT_BASE_URL", "")
    
    print("\n🔍 Checking configuration...")
    
    if not SENDER_EMAIL:
        print("❌ SENDER_EMAIL not set in .env")
        return False
    else:
        print(f"✅ SENDER_EMAIL: {SENDER_EMAIL}")
    
    if not SENDER_PASSWORD:
        print("❌ SENDER_PASSWORD not set in .env")
        return False
    else:
        print(f"✅ SENDER_PASSWORD: {'*' * len(SENDER_PASSWORD)} (hidden)")
    
    if not RECIPIENT_EMAILS:
        print("❌ RECIPIENT_EMAILS not set in .env")
        return False
    else:
        recipients = [e.strip() for e in RECIPIENT_EMAILS.split(",")]
        print(f"✅ RECIPIENT_EMAILS: {len(recipients)} recipient(s)")
        for email in recipients:
            print(f"   - {email}")
    
    if WEB_REPORT_BASE_URL:
        print(f"✅ WEB_REPORT_BASE_URL: {WEB_REPORT_BASE_URL}")
    else:
        print(f"⚠️  WEB_REPORT_BASE_URL: Not set (will use local file:// URLs)")
    
    # Check for data files
    weekly_data = Path("weekly_data")
    print("\n📁 Checking data files...")
    
    data_files = {
        "grants.csv": weekly_data / "grants.csv",
        "events.csv": weekly_data / "events.csv",
        "csr_reports.csv": weekly_data / "csr_reports.csv",
        "experts.csv": weekly_data / "experts.csv"
    }
    
    all_data = {}
    total_items = 0
    
    for name, filepath in data_files.items():
        if filepath.exists():
            df = pd.read_csv(filepath)
            all_data[name] = df.to_dict('records')
            count = len(df)
            total_items += count
            print(f"✅ {name}: {count} items")
        else:
            all_data[name] = []
            print(f"⚠️  {name}: Not found (will send empty)")
    
    if total_items == 0:
        print("\n⚠️  Warning: No data found in CSV files!")
        print("   Run 'python automated_newsletter.py' first to generate data")
        response = input("\nSend email anyway with empty data? (y/n): ")
        if response.lower() != 'y':
            print("❌ Test cancelled")
            return False
    
    # Confirm sending
    print(f"\n📊 Total items to send: {total_items}")
    print(f"📧 Email will be sent to: {', '.join(recipients)}")
    confirm = input("\n⚠️  Send test email now? (y/n): ")
    
    if confirm.lower() != 'y':
        print("❌ Test cancelled")
        return False
    
    # Send email directly without Monday check
    print("\n📨 Sending email...")
    
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        # Import email template
        from email_template_condensed import generate_condensed_email_html
        
        # Prepare data as DataFrames
        grants_df = pd.DataFrame(all_data["grants.csv"]) if all_data["grants.csv"] else pd.DataFrame()
        events_df = pd.DataFrame(all_data["events.csv"]) if all_data["events.csv"] else pd.DataFrame()
        csr_df = pd.DataFrame(all_data["csr_reports.csv"]) if all_data["csr_reports.csv"] else pd.DataFrame()
        experts_df = pd.DataFrame(all_data["experts.csv"]) if all_data["experts.csv"] else pd.DataFrame()
        
        # Rename Organization to Domain for template compatibility
        if not grants_df.empty and 'Organization' in grants_df.columns:
            grants_df = grants_df.rename(columns={'Organization': 'Domain'})
        if not events_df.empty and 'Organization' in events_df.columns:
            events_df = events_df.rename(columns={'Organization': 'Domain'})
        if not csr_df.empty and 'Organization' in csr_df.columns:
            csr_df = csr_df.rename(columns={'Organization': 'Domain'})
        
        # Generate HTML email
        html_content = generate_condensed_email_html(
            experts_df, 
            grants_df, 
            events_df, 
            csr_df, 
            base_url=WEB_REPORT_BASE_URL
        )
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🌍 Climate Cardinals Newsletter - TEST EMAIL - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAILS
        
        msg.attach(MIMEText(html_content, "html"))
        
        # Send email via SMTP
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        
        print(f"📤 Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("📧 Sending email...")
            
            recipients = [e.strip() for e in RECIPIENT_EMAILS.split(",")]
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        
        print("\n✅ TEST EMAIL SENT SUCCESSFULLY!")
        print("\n📋 Next steps:")
        print("1. Check recipient inbox(es)")
        print("2. Check spam folder if not in inbox")
        print("3. Verify email formatting looks correct")
        print("4. Click 'View All Data' button to test Netlify link")
        print(f"\n📊 Email contained:")
        print(f"   - {len(all_data['grants.csv'])} grants")
        print(f"   - {len(all_data['events.csv'])} events")
        print(f"   - {len(all_data['csr_reports.csv'])} CSR reports")
        print(f"   - {len(all_data['experts.csv'])} experts")
        return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Common issues:")
        print("   - Gmail App Password incorrect (must be 16 chars, no spaces)")
        print("   - 2-Step Verification not enabled in Google Account")
        print("   - Wrong email address")
        return False

if __name__ == "__main__":
    print("\n⚠️  This script bypasses the Monday check for testing purposes")
    print("It will send an email immediately with whatever data exists in weekly_data/\n")
    
    success = test_email()
    sys.exit(0 if success else 1)
