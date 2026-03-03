#!/usr/bin/env python3
"""
Extract data from week 10 HTML report and send test email to columbia@climatecardinals.org
"""

import os
import re
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

def extract_data_from_html(html_path):
    """Extract grants, events, CSR reports, and experts from HTML report"""
    
    print(f"\n📄 Reading HTML report: {html_path.name}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find all sections
    sections = soup.find_all('div', class_='section')
    
    data = {
        'grants': [],
        'events': [],
        'csr_reports': [],
        'experts': []
    }
    
    for section in sections:
        section_title = section.find('h2', class_='section-title')
        if not section_title:
            continue
        
        title_text = section_title.get_text().strip()
        
        # Determine section type
        section_type = None
        if '💰' in title_text or 'Grant' in title_text:
            section_type = 'grants'
        elif '🎤' in title_text or 'Event' in title_text:
            section_type = 'events'
        elif '📊' in title_text or 'Report' in title_text or 'CSR' in title_text:
            section_type = 'csr_reports'
        elif '👤' in title_text or 'Expert' in title_text:
            section_type = 'experts'
        
        if not section_type:
            continue
        
        # Extract items from this section
        # Experts use expert-card, others use item-card
        if section_type == 'experts':
            items = section.find_all('div', class_='expert-card')
            
            for item in items:
                # Extract name
                name_elem = item.find('div', class_='expert-name')
                name = name_elem.get_text().strip() if name_elem else 'Unknown'
                
                # Extract role
                role_elem = item.find('div', class_='expert-role')
                role = role_elem.get_text().strip() if role_elem else '—'
                
                # Extract LinkedIn URL
                link_elem = item.find('a', class_='linkedin-btn')
                linkedin = link_elem.get('href', '—') if link_elem else '—'
                
                data[section_type].append({
                    'Name': name,
                    'Role': role,
                    'LinkedIn': linkedin,
                    'Scraped': datetime.now().strftime('%Y-%m-%d')
                })
        else:
            items = section.find_all('div', class_='item-card')
            
            for item in items:
                # Extract title
                title_elem = item.find('div', class_='item-title')
                title = title_elem.get_text().strip() if title_elem else 'Untitled'
                
                # Extract domain
                meta_elem = item.find('div', class_='item-meta')
                domain = '—'
                date_info = '—'
                
                if meta_elem:
                    # Look for domain
                    domain_match = meta_elem.find('span', string=re.compile('🌐'))
                    if domain_match:
                        domain = domain_match.get_text().replace('🌐', '').strip()
                    
                    # Look for date info
                    date_match = meta_elem.find('span', string=re.compile('⏰|📅'))
                    if date_match:
                        date_info = date_match.get_text().replace('⏰', '').replace('📅', '').strip()
                
                # Extract description
                desc_elem = item.find('div', class_='item-description')
                description = desc_elem.get_text().strip() if desc_elem else '—'
                
                # Extract URL
                link_elem = item.find('a', class_='item-link')
                url = link_elem.get('href', '—') if link_elem else '—'
                
                # For grants, events, CSR reports
                data[section_type].append({
                    'Title': title,
                    'Organization': domain,
                    'Date Info': date_info,
                    'Description': description,
                    'URL': url,
                    'Scraped': datetime.now().strftime('%Y-%m-%d')
                })
    
    return data

def save_to_csv(data, output_folder):
    """Save extracted data to CSV files"""
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    
    csv_mapping = {
        'grants': 'grants.csv',
        'events': 'events.csv',
        'csr_reports': 'csr_reports.csv',
        'experts': 'experts.csv'
    }
    
    for key, filename in csv_mapping.items():
        if data[key]:
            df = pd.DataFrame(data[key])
            csv_path = output_folder / filename
            df.to_csv(csv_path, index=False)
            print(f"✅ Saved {len(data[key])} items to {filename}")
        else:
            print(f"⚠️  No data for {key}")

def send_email_with_data(data):
    """Send email with extracted data"""
    
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    WEB_REPORT_BASE_URL = os.getenv("WEB_REPORT_BASE_URL", "")
    RECIPIENT_EMAIL = "columbia@climatecardinals.org"
    
    print("\n📧 Preparing to send email...")
    print(f"   From: {SENDER_EMAIL}")
    print(f"   To: {RECIPIENT_EMAIL}")
    
    # Import email template
    from email_template_condensed import generate_condensed_email_html
    
    # Prepare data as DataFrames
    grants_df = pd.DataFrame(data['grants']) if data['grants'] else pd.DataFrame()
    events_df = pd.DataFrame(data['events']) if data['events'] else pd.DataFrame()
    csr_df = pd.DataFrame(data['csr_reports']) if data['csr_reports'] else pd.DataFrame()
    experts_df = pd.DataFrame(data['experts']) if data['experts'] else pd.DataFrame()
    
    # Rename Organization to Domain for template compatibility
    for df in [grants_df, events_df, csr_df]:
        if not df.empty and 'Organization' in df.columns:
            df.rename(columns={'Organization': 'Domain'}, inplace=True)
    
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
    try:
        print(f"📤 Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print("🔐 Authenticating...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("📧 Sending email...")
            server.sendmail(SENDER_EMAIL, [RECIPIENT_EMAIL], msg.as_string())
        
        print("\n✅ WEEK 10 EMAIL SENT SUCCESSFULLY!")
        print(f"📧 Sent to: {RECIPIENT_EMAIL}")
        print(f"\n📊 Email contained:")
        print(f"   - {len(data['grants'])} grants")
        print(f"   - {len(data['events'])} events")
        print(f"   - {len(data['csr_reports'])} CSR reports")
        print(f"   - {len(data['experts'])} experts")
        return True
            
    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("📧 WEEK 10 DATA EXTRACTOR & EMAIL SENDER")
    print("="*70)
    print(f"📅 Current date: {datetime.now().strftime('%Y-%m-%d %A')}")
    print(f"🎯 Target: Extract week 10 data and send to columbia@climatecardinals.org")
    
    # Find the week 10 HTML report (March 2, 2026)
    html_path = Path("weekly_data/climate_cardinals_report_20260302.html")
    
    if not html_path.exists():
        print(f"\n❌ Week 10 report not found: {html_path}")
        return False
    
    # Extract data from HTML
    print("\n" + "="*70)
    print("STEP 1: Extracting data from HTML report")
    print("="*70)
    
    data = extract_data_from_html(html_path)
    
    total_items = sum(len(items) for items in data.values())
    print(f"\n📊 Extracted {total_items} total items:")
    print(f"   - {len(data['grants'])} grants")
    print(f"   - {len(data['events'])} events")
    print(f"   - {len(data['csr_reports'])} CSR reports")
    print(f"   - {len(data['experts'])} experts")
    
    # Save to CSV files
    print("\n" + "="*70)
    print("STEP 2: Saving data to CSV files")
    print("="*70)
    
    save_to_csv(data, "weekly_data")
    
    # Send email
    print("\n" + "="*70)
    print("STEP 3: Sending email")
    print("="*70)
    
    success = send_email_with_data(data)
    
    print("\n" + "="*70)
    
    if success:
        print("\n✅ ALL DONE! Check columbia@climatecardinals.org inbox")
    else:
        print("\n❌ Email sending failed, but data was extracted to CSV files")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
