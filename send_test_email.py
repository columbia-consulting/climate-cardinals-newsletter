#!/usr/bin/env python3
"""
Quick test email sender to columbia@climatecardinals.org
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from web_report_generator import generate_full_report_html

# Load environment variables
load_dotenv()

def send_test_to_columbia(recipient_email=None):
    """Send test email to columbia@climatecardinals.org"""
    
    print("="*60)
    if recipient_email:
        print(f"📧 SENDING TEST EMAIL TO {recipient_email}")
    else:
        print("📧 SENDING TEST EMAIL TO columbia@climatecardinals.org")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Get email credentials
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    WEB_REPORT_BASE_URL = os.getenv("WEB_REPORT_BASE_URL", "")
    
    # Override recipient to provided email or default to columbia@climatecardinals.org
    RECIPIENT_EMAIL = recipient_email or "columbia@climatecardinals.org"
    
    print("\n🔍 Checking configuration...")
    
    if not SENDER_EMAIL:
        print("❌ SENDER_EMAIL not set")
        print("\n💡 Please set the following in your .env file:")
        print("   SENDER_EMAIL=your-email@gmail.com")
        print("   SENDER_PASSWORD=your-app-password")
        return False
    else:
        print(f"✅ SENDER_EMAIL: {SENDER_EMAIL}")
    
    if not SENDER_PASSWORD:
        print("❌ SENDER_PASSWORD not set")
        return False
    else:
        print(f"✅ SENDER_PASSWORD: {'*' * min(16, len(SENDER_PASSWORD))} (hidden)")
    
    print(f"✅ RECIPIENT: {RECIPIENT_EMAIL}")
    print(f"✅ SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    
    if WEB_REPORT_BASE_URL:
        print(f"✅ WEB_REPORT_BASE_URL: {WEB_REPORT_BASE_URL}")
    else:
        print(f"⚠️  WEB_REPORT_BASE_URL: Not set (will use placeholder)")
    
    # Try to load data from CSV files
    weekly_data = Path("weekly_data")
    data_files = {
        "grants.csv": weekly_data / "grants.csv",
        "events.csv": weekly_data / "events.csv",
        "csr_reports.csv": weekly_data / "csr_reports.csv",
        "experts.csv": weekly_data / "experts.csv"
    }
    
    all_data = {}
    total_items = 0
    
    print("\n📁 Loading data...")
    for name, filepath in data_files.items():
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                all_data[name] = df.to_dict('records')
                count = len(df)
                total_items += count
                print(f"✅ {name}: {count} items")
            except Exception as e:
                all_data[name] = []
                print(f"⚠️  {name}: Error reading ({e})")
        else:
            all_data[name] = []
            print(f"⚠️  {name}: Not found")
    
    if total_items == 0:
        print("\n⚠️  No data found in CSV files - will send email with empty/sample data")
    
    # Send email
    print("\n📨 Sending email...")
    
    try:
        from email_template_condensed import generate_condensed_email_html
        
        # Prepare data as DataFrames
        grants_df = pd.DataFrame(all_data.get("grants.csv", [])) if all_data.get("grants.csv") else pd.DataFrame()
        events_df = pd.DataFrame(all_data.get("events.csv", [])) if all_data.get("events.csv") else pd.DataFrame()
        csr_df = pd.DataFrame(all_data.get("csr_reports.csv", [])) if all_data.get("csr_reports.csv") else pd.DataFrame()
        experts_df = pd.DataFrame(all_data.get("experts.csv", [])) if all_data.get("experts.csv") else pd.DataFrame()
        
        # Rename Organization to Domain for template compatibility
        for df in [grants_df, events_df, csr_df]:
            if not df.empty and 'Organization' in df.columns:
                df.rename(columns={'Organization': 'Domain'}, inplace=True)
        
        # Generate HTML email
        report_path = generate_full_report_html(experts_df, grants_df, events_df, csr_df)
        html_content = generate_condensed_email_html(
            experts_df, 
            grants_df, 
            events_df, 
            csr_df, 
            base_url=WEB_REPORT_BASE_URL,
            report_filename=Path(report_path).name,
        )
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🌍 Climate Cardinals Newsletter - TEST - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        
        msg.attach(MIMEText(html_content, "html"))
        
        # Send via SMTP
        print(f"📤 Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("📧 Sending email...")
            server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        
        print("\n✅ TEST EMAIL SENT SUCCESSFULLY!")
        print(f"📧 Sent to: {RECIPIENT_EMAIL}")
        print(f"\n📊 Email contained:")
        print(f"   - {len(all_data.get('grants.csv', []))} grants")
        print(f"   - {len(all_data.get('events.csv', []))} events")
        print(f"   - {len(all_data.get('csr_reports.csv', []))} CSR reports")
        print(f"   - {len(all_data.get('experts.csv', []))} experts")
        print("\n📋 Next steps:")
        print("1. Check inbox at columbia@climatecardinals.org")
        print("2. Check spam folder if not in inbox")
        print("3. Verify email formatting looks correct")
        return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Common issues:")
        print("   - Gmail App Password incorrect (must be 16 chars, no spaces)")
        print("   - 2-Step Verification not enabled in Google Account")
        print("   - SMTP server/port incorrect")
        print("   - Wrong sender email address")
        return False

if __name__ == "__main__":
    recipient = None
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    success = send_test_to_columbia(recipient)
    exit(0 if success else 1)
