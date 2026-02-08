"""
Email template - reads email_template_email_safe.html and fills in data only
"""

import pandas as pd
from pathlib import Path
import re

def generate_email_html(experts_df, grants_df, events_df, csr_df):
    """Read email-safe HTML template and fill in data"""
    
    # Read email-safe template (with inline styles)
    template_path = Path(__file__).parent / "email_template_email_safe.html"
    with open(template_path, 'r') as f:
        html = f.read()
    
    # Get counts
    experts_count = len(experts_df) if not experts_df.empty else 0
    grants_count = len(grants_df) if not grants_df.empty else 0
    events_count = len(events_df) if not events_df.empty else 0
    csr_count = len(csr_df) if not csr_df.empty else 0
    
    today = pd.Timestamp.today()
    week_num = today.isocalendar()[1]
    date_str = today.strftime("%B %d, %Y")
    
    # Replace date and issue info
    html = html.replace("Issue #6", f"Issue #{week_num}")
    html = html.replace("February 06, 2026", date_str)
    
    # Replace counts - 4 sections, each with a 00 number
    count_pattern = '<div style="position: absolute; top: 0px; right: 30px; font-family: Georgia, serif; font-size: 100px; font-weight: bold; color: #e8ece9; line-height: 0.8; margin: 0; padding: 0;">00</div>'
    counts = [experts_count, grants_count, events_count, csr_count]
    for count in counts:
        html = html.replace(count_pattern, 
                           f'<div style="position: absolute; top: 0px; right: 30px; font-family: Georgia, serif; font-size: 100px; font-weight: bold; color: #e8ece9; line-height: 0.8; margin: 0; padding: 0;">{count:02d}</div>', 1)
    
    # Replace editorial text with actual counts
    html = html.replace(
        "0 new funding opportunities, 0 upcoming climate events, 0 expert connections, and 0 fresh sustainability reports",
        f"{grants_count} new funding opportunities, {events_count} upcoming climate events, {experts_count} expert connections, and {csr_count} fresh sustainability reports"
    )
    
    # Build expert cards HTML with inline styles
    experts_html = ""
    if not experts_df.empty:
        for idx, (_, row) in enumerate(experts_df.iterrows()):
            if idx >= 5:
                break
            name = row.get('Name', 'Unknown')
            role = row.get('Role', '')
            linkedin = row.get('LinkedIn', '')
            
            role_html = f'<div style="font-size: 14px; color: #1a5538; font-weight: 500; line-height: 1.5; font-family: Georgia, serif;">{role}</div>' if role and role != '—' else ''
            linkedin_html = f'<a href="{linkedin}" style="display: inline-block; color: #1a5538; text-decoration: none; font-size: 13px; font-weight: 600; padding: 10px 18px; background: #ffffff; border: 1px solid #9caf88; border-radius: 6px; margin-top: 10px; font-family: Georgia, serif;">View LinkedIn</a>' if linkedin and linkedin != '—' else ''
            
            experts_html += f'''<div style="background: #f5f7f5; border: 1px solid #9caf88; border-left: 4px solid #9caf88; padding: 20px; margin-bottom: 15px;">
                <div style="display: flex; gap: 15px; margin-bottom: 12px; align-items: flex-start;">
                    <div style="font-size: 32px;">👤</div>
                    <div style="flex: 1;">
                        <div style="font-size: 18px; font-weight: 700; color: #0a2f1f; margin: 0 0 4px 0; font-family: Georgia, serif;">{name}</div>
                        {role_html}
                    </div>
                </div>
                {linkedin_html}
            </div>
'''
    
    # Build grants cards HTML with inline styles
    grants_html = ""
    if not grants_df.empty:
        for idx, (_, row) in enumerate(grants_df.iterrows()):
            if idx >= 5:
                break
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            date_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; margin-right: 20px; font-family: Georgia, serif;">📅 {date_info}</div>' if date_info and date_info != '—' else ''
            domain_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; font-family: Georgia, serif;"><a href="{url}" style="color: #1a5538; text-decoration: none;">🌐 {domain}</a></div>' if domain and domain != '—' else ''
            url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 13px; font-weight: 600; padding: 11px 22px; border-radius: 6px; margin-top: 15px; font-family: Georgia, serif;">Read Full Article →</a>' if url and url != '—' else ''
            
            grants_html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 4px solid #0a2f1f; padding: 24px; margin-bottom: 18px;">
                <div style="font-size: 18px; font-weight: 700; color: #0a2f1f; margin: 0 0 12px 0; line-height: 1.4; font-family: Georgia, serif;">{title}</div>
                <div style="padding-bottom: 12px; border-bottom: 1px solid #e8ece9; margin-bottom: 12px;">
                    {date_html}
                    {domain_html}
                </div>
                <div style="font-size: 14px; color: #1a5538; line-height: 1.6; margin-bottom: 15px; font-family: Georgia, serif;">{description}</div>
                {url_html}
            </div>
'''
    
    # Build events cards HTML with inline styles
    events_html = ""
    if not events_df.empty:
        for idx, (_, row) in enumerate(events_df.iterrows()):
            if idx >= 5:
                break
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            date_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; margin-right: 20px; font-family: Georgia, serif;">📅 {date_info}</div>' if date_info and date_info != '—' else ''
            domain_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; font-family: Georgia, serif;"><a href="{url}" style="color: #1a5538; text-decoration: none;">🌐 {domain}</a></div>' if domain and domain != '—' else ''
            url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 13px; font-weight: 600; padding: 11px 22px; border-radius: 6px; margin-top: 15px; font-family: Georgia, serif;">Read Full Article →</a>' if url and url != '—' else ''
            
            events_html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 4px solid #0a2f1f; padding: 24px; margin-bottom: 18px;">
                <div style="font-size: 18px; font-weight: 700; color: #0a2f1f; margin: 0 0 12px 0; line-height: 1.4; font-family: Georgia, serif;">{title}</div>
                <div style="padding-bottom: 12px; border-bottom: 1px solid #e8ece9; margin-bottom: 12px;">
                    {date_html}
                    {domain_html}
                </div>
                <div style="font-size: 14px; color: #1a5538; line-height: 1.6; margin-bottom: 15px; font-family: Georgia, serif;">{description}</div>
                {url_html}
            </div>
'''
    
    # Build CSR cards HTML with inline styles
    csr_html = ""
    if not csr_df.empty:
        for idx, (_, row) in enumerate(csr_df.iterrows()):
            if idx >= 5:
                break
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            date_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; margin-right: 20px; font-family: Georgia, serif;">📅 {date_info}</div>' if date_info and date_info != '—' else ''
            domain_html = f'<div style="display: inline-block; font-size: 13px; color: #8b7355; font-weight: 500; font-family: Georgia, serif;"><a href="{url}" style="color: #1a5538; text-decoration: none;">🌐 {domain}</a></div>' if domain and domain != '—' else ''
            url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 13px; font-weight: 600; padding: 11px 22px; border-radius: 6px; margin-top: 15px; font-family: Georgia, serif;">Read Full Article →</a>' if url and url != '—' else ''
            
            csr_html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 4px solid #0a2f1f; padding: 24px; margin-bottom: 18px;">
                <div style="font-size: 18px; font-weight: 700; color: #0a2f1f; margin: 0 0 12px 0; line-height: 1.4; font-family: Georgia, serif;">{title}</div>
                <div style="padding-bottom: 12px; border-bottom: 1px solid #e8ece9; margin-bottom: 12px;">
                    {date_html}
                    {domain_html}
                </div>
                <div style="font-size: 14px; color: #1a5538; line-height: 1.6; margin-bottom: 15px; font-family: Georgia, serif;">{description}</div>
                {url_html}
            </div>
'''
    
    # Replace no-data sections with actual cards
    html = re.sub(
        r'(<!-- Climate Experts Section -->.*?)<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">.*?</div>\s*(<!-- Grants Section -->)',
        rf'\1{experts_html}\2',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    html = re.sub(
        r'(<!-- Grants Section -->.*?)<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">.*?</div>\s*(<!-- Events Section -->)',
        rf'\1{grants_html}\2',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    html = re.sub(
        r'(<!-- Events Section -->.*?)<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">.*?</div>\s*(<!-- ESG Reports Section -->)',
        rf'\1{events_html}\2',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    html = re.sub(
        r'(<!-- ESG Reports Section -->.*?)<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">.*?</div>\s*(<!-- Footer -->)',
        rf'\1{csr_html}\2',
        html,
        count=1,
        flags=re.DOTALL
    )
    
    return html
