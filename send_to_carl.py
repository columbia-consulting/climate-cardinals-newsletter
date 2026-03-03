#!/usr/bin/env python3
"""
Send test email to carldybwad@climatecardinals.org with week 10 data
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

def send_to_carl():
    """Send email to carldybwad@climatecardinals.org with existing data"""
    
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    WEB_REPORT_BASE_URL = os.getenv("WEB_REPORT_BASE_URL", "")
    RECIPIENT_EMAIL = "carldybwad@climatecardinals.org"
    
    print("="*60)
    print("📧 SENDING EMAIL TO carldybwad@climatecardinals.org")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"📧 To: {RECIPIENT_EMAIL}")
    
    # Load data from CSV files
    weekly_data = Path("weekly_data")
    
    try:
        grants_df = pd.read_csv(weekly_data / "grants.csv") if (weekly_data / "grants.csv").exists() else pd.DataFrame()
        events_df = pd.read_csv(weekly_data / "events.csv") if (weekly_data / "events.csv").exists() else pd.DataFrame()
        csr_df = pd.read_csv(weekly_data / "csr_reports.csv") if (weekly_data / "csr_reports.csv").exists() else pd.DataFrame()
        experts_df = pd.read_csv(weekly_data / "experts.csv") if (weekly_data / "experts.csv").exists() else pd.DataFrame()
        
        # Rename Organization to Domain for template compatibility
        for df in [grants_df, events_df, csr_df]:
            if not df.empty and 'Organization' in df.columns:
                df.rename(columns={'Organization': 'Domain'}, inplace=True)
        
        print(f"\n📊 Data loaded:")
        print(f"   - {len(grants_df)} grants")
        print(f"   - {len(events_df)} events")
        print(f"   - {len(csr_df)} CSR reports")
        print(f"   - {len(experts_df)} experts")
        
        # Import email template
        from email_template_condensed import generate_condensed_email_html
        
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
        msg["Subject"] = f"🌍 Climate Cardinals Newsletter - Week 10 - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        
        msg.attach(MIMEText(html_content, "html"))
        
        # Send via SMTP
        print(f"\n📤 Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("📧 Sending email...")
            server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        
        print("\n✅ EMAIL SENT SUCCESSFULLY!")
        print(f"📧 Sent to: {RECIPIENT_EMAIL}")
        return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = send_to_carl()
    sys.exit(0 if success else 1)
