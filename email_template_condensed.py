"""
Condensed email template - generates digest format emails with top 3 items per section
and links to full report for users who want complete data
"""

import pandas as pd
from pathlib import Path
import re
from web_report_generator import generate_full_report_html, generate_report_metadata

def generate_condensed_email_html(experts_df, grants_df, events_df, csr_df, base_url=""):
    """Generate condensed email with top 3 items per section and links to full report
    
    Args:
        experts_df: DataFrame with expert data
        grants_df: DataFrame with grant data
        events_df: DataFrame with event data
        csr_df: DataFrame with CSR report data
        base_url: Base URL for hosted reports (e.g., "https://yourusername.github.io/reports")
                  Leave empty to use local file:// URLs (only works on your computer)
    """
    
    # Generate full web report first
    report_path = generate_full_report_html(experts_df, grants_df, events_df, csr_df)
    metadata = generate_report_metadata(experts_df, grants_df, events_df, csr_df, report_path)
    
    # Read condensed email template
    template_path = Path(__file__).parent / "email_template_condensed.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Get counts
    experts_count = len(experts_df) if not experts_df.empty else 0
    grants_count = len(grants_df) if not grants_df.empty else 0
    events_count = len(events_df) if not events_df.empty else 0
    csr_count = len(csr_df) if not csr_df.empty else 0
    
    today = pd.Timestamp.today()
    week_num = today.isocalendar()[1]
    date_str = today.strftime("%B %d, %Y")
    
    # Replace date, issue info and counts in stats cards
    html = html.replace("Issue #6", f"Issue #{week_num}")
    html = html.replace("February 06, 2026", date_str)
    
    # Replace count placeholders in stats grid
    html = html.replace("COUNT_EXPERTS", str(experts_count))
    html = html.replace("COUNT_GRANTS", str(grants_count))
    html = html.replace("COUNT_EVENTS", str(events_count))
    html = html.replace("COUNT_REPORTS", str(csr_count))
    
    # Replace total counts in section headers
    html = html.replace("TOTAL_EXPERTS_COUNT", str(experts_count))
    html = html.replace("TOTAL_GRANTS_COUNT", str(grants_count))
    html = html.replace("TOTAL_EVENTS_COUNT", str(events_count))
    html = html.replace("TOTAL_CSR_COUNT", str(csr_count))
    
    # Generate report URL based on hosting configuration
    report_filename = f"climate_cardinals_report_{today.strftime('%Y%m%d')}.html"
    
    if base_url:
        # Use hosted URL (production)
        base_url = base_url.rstrip('/')  # Remove trailing slash if present
        report_url = f"{base_url}/{report_filename}"
        print(f"📡 Report URLs will use: {report_url}")
    else:
        # Use local file:// URL (local testing only)
        report_url = f"file:///{str(report_path).replace(chr(92), '/')}"  # Replace backslashes
        print(f"⚠️  Warning: Using local file:// URLs - users won't be able to access links!")
        print(f"   Set WEB_REPORT_BASE_URL to your hosted URL before sending to users.")
    
    # Replace all URL placeholders with the actual report URL
    html = html.replace("FULL_REPORT_URL", report_url)
    html = html.replace("FULL_EXPERTS_URL", f"{report_url}#experts")
    html = html.replace("FULL_GRANTS_URL", f"{report_url}#grants")  
    html = html.replace("FULL_EVENTS_URL", f"{report_url}#events")
    html = html.replace("FULL_CSR_URL", f"{report_url}#reports")
    
    # Generate condensed content for each section (top 3 items)
    experts_html = generate_condensed_experts_html(experts_df)
    grants_html = generate_condensed_grants_html(grants_df)
    events_html = generate_condensed_events_html(events_df)
    csr_html = generate_condensed_csr_html(csr_df)
    
    # Replace content placeholders
    html = html.replace("<!-- EXPERTS_CONTENT_PLACEHOLDER -->", experts_html)
    html = html.replace("<!-- GRANTS_CONTENT_PLACEHOLDER -->", grants_html)
    html = html.replace("<!-- EVENTS_CONTENT_PLACEHOLDER -->", events_html)
    html = html.replace("<!-- CSR_CONTENT_PLACEHOLDER -->", csr_html)
    
    return html

def generate_condensed_experts_html(experts_df):
    """Generate condensed HTML for top 3 experts"""
    if experts_df.empty:
        return '''<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">
            <div style="font-size: 40px; margin-bottom: 12px;">👥</div>
            <div style="font-size: 14px; color: #8b7355; font-style: italic; font-family: Georgia, serif;">No experts curated this week</div>
        </div>'''
    
    html = ""
    for idx, (_, row) in enumerate(experts_df.iterrows()):
        if idx >= 3:  # Only show top 3
            break
            
        name = row.get('Name', 'Unknown')
        role = row.get('Role', '')
        linkedin = row.get('LinkedIn', '')
        
        # Truncate role if too long
        if role and len(role) > 80:
            role = role[:77] + "..."
            
        role_html = f'<div style="font-size: 13px; color: #1a5538; margin-bottom: 12px; font-family: Georgia, serif;">{role}</div>' if role and role != '—' else ''
        linkedin_html = f'<a href="{linkedin}" style="display: inline-block; color: #0077b5; text-decoration: none; font-size: 12px; font-weight: 600; padding: 8px 16px; background: #ffffff; border: 1px solid #0077b5; border-radius: 4px; font-family: Georgia, serif;">LinkedIn →</a>' if linkedin and linkedin != '—' else ''
        
        html += f'''<div style="background: #f5f7f5; border: 1px solid #9caf88; padding: 18px; margin-bottom: 12px; border-radius: 6px;">
            <div style="font-size: 16px; font-weight: 700; color: #0a2f1f; margin: 0 0 6px 0; font-family: Georgia, serif;">{name}</div>
            {role_html}
            {linkedin_html}
        </div>'''
    
    return html

def generate_condensed_grants_html(grants_df):
    """Generate condensed HTML for top 3 grants"""
    if grants_df.empty:
        return '''<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">
            <div style="font-size: 40px; margin-bottom: 12px;">💰</div>
            <div style="font-size: 14px; color: #8b7355; font-style: italic; font-family: Georgia, serif;">No grants curated this week</div>
        </div>'''
    
    html = ""
    for idx, (_, row) in enumerate(grants_df.iterrows()):
        if idx >= 3:  # Only show top 3
            break
            
        title = row.get('Title', 'Untitled')
        domain = row.get('Domain', row.get('Organization', ''))
        date_info = row.get('Date Info', '')
        url = row.get('URL', '')
        description = row.get('Description', '')
        
        # Truncate title and description for condensed view
        if title and len(title) > 90:
            title = title[:87] + "..."
        if description and len(description) > 120:
            description = description[:117] + "..."
            
        meta_parts = []
        if date_info and date_info != '—':
            meta_parts.append(f'📅 {date_info}')
        if domain and domain != '—':
            meta_parts.append(f'🌐 {domain}')
        
        meta_html = f'<div style="font-size: 11px; color: #8b7355; margin-bottom: 10px; font-family: Georgia, serif;">{" • ".join(meta_parts)}</div>' if meta_parts else ''
        url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 11px; font-weight: 600; padding: 8px 16px; border-radius: 4px; margin-top: 10px; font-family: Georgia, serif;">Read More →</a>' if url and url != '—' else ''
        
        html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 3px solid #0a2f1f; padding: 18px; margin-bottom: 12px; border-radius: 6px;">
            <div style="font-size: 15px; font-weight: 700; color: #0a2f1f; margin: 0 0 8px 0; line-height: 1.3; font-family: Georgia, serif;">{title}</div>
            {meta_html}
            <div style="font-size: 13px; color: #1a5538; line-height: 1.5; margin-bottom: 12px; font-family: Georgia, serif;">{description}</div>
            {url_html}
        </div>'''
    
    return html

def generate_condensed_events_html(events_df):
    """Generate condensed HTML for top 3 events"""
    if events_df.empty:
        return '''<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">
            <div style="font-size: 40px; margin-bottom: 12px;">🎤</div>
            <div style="font-size: 14px; color: #8b7355; font-style: italic; font-family: Georgia, serif;">No events curated this week</div>
        </div>'''
    
    html = ""
    for idx, (_, row) in enumerate(events_df.iterrows()):
        if idx >= 3:  # Only show top 3
            break
            
        title = row.get('Title', 'Untitled')
        domain = row.get('Domain', row.get('Organization', ''))
        date_info = row.get('Date Info', '')
        url = row.get('URL', '')
        description = row.get('Description', '')
        
        # Truncate title and description for condensed view
        if title and len(title) > 90:
            title = title[:87] + "..."
        if description and len(description) > 120:
            description = description[:117] + "..."
            
        meta_parts = []
        if date_info and date_info != '—':
            meta_parts.append(f'📅 {date_info}')
        if domain and domain != '—':
            meta_parts.append(f'🌐 {domain}')
        
        meta_html = f'<div style="font-size: 11px; color: #8b7355; margin-bottom: 10px; font-family: Georgia, serif;">{" • ".join(meta_parts)}</div>' if meta_parts else ''
        url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 11px; font-weight: 600; padding: 8px 16px; border-radius: 4px; margin-top: 10px; font-family: Georgia, serif;">View Event →</a>' if url and url != '—' else ''
        
        html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 3px solid #0a2f1f; padding: 18px; margin-bottom: 12px; border-radius: 6px;">
            <div style="font-size: 15px; font-weight: 700; color: #0a2f1f; margin: 0 0 8px 0; line-height: 1.3; font-family: Georgia, serif;">{title}</div>
            {meta_html}
            <div style="font-size: 13px; color: #1a5538; line-height: 1.5; margin-bottom: 12px; font-family: Georgia, serif;">{description}</div>
            {url_html}
        </div>'''
    
    return html

def generate_condensed_csr_html(csr_df):
    """Generate condensed HTML for top 3 CSR reports"""
    if csr_df.empty:
        return '''<div style="text-align: center; padding: 40px 20px; background: #f5f7f5; border: 2px dashed #9caf88; border-radius: 8px;">
            <div style="font-size: 40px; margin-bottom: 12px;">📊</div>
            <div style="font-size: 14px; color: #8b7355; font-style: italic; font-family: Georgia, serif;">No reports curated this week</div>
        </div>'''
    
    html = ""
    for idx, (_, row) in enumerate(csr_df.iterrows()):
        if idx >= 3:  # Only show top 3
            break
            
        title = row.get('Title', 'Untitled')
        domain = row.get('Domain', row.get('Organization', ''))
        date_info = row.get('Date Info', '')
        url = row.get('URL', '')
        description = row.get('Description', '')
        
        # Truncate title and description for condensed view
        if title and len(title) > 90:
            title = title[:87] + "..."
        if description and len(description) > 120:
            description = description[:117] + "..."
            
        meta_parts = []
        if date_info and date_info != '—':
            meta_parts.append(f'📅 {date_info}')
        if domain and domain != '—':
            meta_parts.append(f'🌐 {domain}')
        
        meta_html = f'<div style="font-size: 11px; color: #8b7355; margin-bottom: 10px; font-family: Georgia, serif;">{" • ".join(meta_parts)}</div>' if meta_parts else ''
        url_html = f'<a href="{url}" style="display: inline-block; color: #ffffff; background: #0a2f1f; text-decoration: none; font-size: 11px; font-weight: 600; padding: 8px 16px; border-radius: 4px; margin-top: 10px; font-family: Georgia, serif;">View Report →</a>' if url and url != '—' else ''
        
        html += f'''<div style="background: #ffffff; border: 1px solid #e8ece9; border-left: 3px solid #0a2f1f; padding: 18px; margin-bottom: 12px; border-radius: 6px;">
            <div style="font-size: 15px; font-weight: 700; color: #0a2f1f; margin: 0 0 8px 0; line-height: 1.3; font-family: Georgia, serif;">{title}</div>
            {meta_html}
            <div style="font-size: 13px; color: #1a5538; line-height: 1.5; margin-bottom: 12px; font-family: Georgia, serif;">{description}</div>
            {url_html}
        </div>'''
    
    return html