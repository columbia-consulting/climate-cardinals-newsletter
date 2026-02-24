"""
Web page generator for complete weekly intelligence report
Creates a standalone HTML page with all data when users want to see everything
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from dateutil import parser
import json
import glob
import re

def calculate_event_countdown(date_str):
    """Convert a date string into a countdown format like 'In 4 weeks'"""
    if not date_str or date_str == "—":
        return None
    
    if "rolling" in date_str.lower() or "ongoing" in date_str.lower():
        return "Ongoing"
    
    try:
        # Parse the date
        event_date = parser.parse(date_str, fuzzy=True)
        today = datetime.now()
        
        # Calculate difference
        days_until = (event_date - today).days
        
        if days_until < 0:
            return None  # Don't show past events
        elif days_until == 0:
            return "Today"
        elif days_until == 1:
            return "Tomorrow"
        elif days_until < 7:
            return f"In {days_until} days"
        elif days_until < 30:
            weeks = days_until // 7
            return f"In {weeks} week{'s' if weeks > 1 else ''}"
        elif days_until < 365:
            months = days_until // 30
            return f"In {months} month{'s' if months > 1 else ''}"
        else:
            return date_str  # Far future, just show the date
    except:
        return date_str  # If parsing fails, return original date

def generate_full_report_html(experts_df, grants_df, events_df, csr_df, output_dir="weekly_data"):
    """Generate a complete HTML report with all data"""
    
    today = datetime.now()
    week_num = today.isocalendar()[1]
    date_str = today.strftime("%B %d, %Y")
    
    # Get counts
    experts_count = len(experts_df) if not experts_df.empty else 0
    grants_count = len(grants_df) if not grants_df.empty else 0
    events_count = len(events_df) if not events_df.empty else 0
    csr_count = len(csr_df) if not csr_df.empty else 0
    
    # Start building the HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Climate Cardinals - Complete Weekly Intelligence Report</title>
    <style>
        @import url('https://fonts.cdnfonts.com/css/fk-screamer');
        @import url('https://fonts.cdnfonts.com/css/athletics');

        body {{
            font-family: 'Athletics', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #192928;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #ffffff;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }}

        .header {{
            padding: 50px 40px;
            background: linear-gradient(135deg, #3154ff 0%, #253292 100%);
            color: #ffffff;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0;
            margin: 0;
            background: #ff082c;
        }}

        .stat-card {{
            text-align: center;
            padding: 40px 25px;
            background: #ff082c;
            border-right: 2px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            text-decoration: none;
            display: block;
            cursor: pointer;
        }}

        .stat-card:last-child {{
            border-right: none;
        }}

        .stat-card:hover {{
            background: #f95208;
            transform: scale(1.05);
        }}

        .stat-number {{
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 48px;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 10px;
            line-height: 1;
        }}

        .stat-label {{
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 12px;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 700;
        }}

        .section {{
            padding: 50px 40px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .section-header {{
            margin-bottom: 30px;
        }}

        .section-title {{
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 36px;
            font-weight: 900;
            color: #192928;
            margin: 0 0 10px 0;
            display: flex;
            align-items: center;
            gap: 15px;
            text-transform: uppercase;
            letter-spacing: -1px;
        }}

        .section-subtitle {{
            font-family: 'Athletics', Arial, sans-serif;
            font-size: 15px;
            color: #666666;
            margin: 0;
            font-weight: 600;
        }}

        .item-card {{
            background: #ffffff;
            border: 2px solid #e0e0e0;
            border-left: 5px solid #ff082c;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }}

        .item-card:hover {{
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
            border-left-color: #3154ff;
        }}

        .item-title {{
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 20px;
            font-weight: 900;
            color: #192928;
            margin: 0 0 15px 0;
            line-height: 1.3;
        }}

        .item-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
            flex-wrap: wrap;
        }}

        .meta-item {{
            font-size: 13px;
            color: #3154ff;
            font-weight: 600;
        }}

        .item-description {{
            font-family: 'Athletics', Arial, sans-serif;
            font-size: 15px;
            color: #192928;
            line-height: 1.6;
            margin-bottom: 20px;
            opacity: 0.9;
        }}

        .item-link {{
            display: inline-block;
            background: #ff082c;
            color: #ffffff;
            text-decoration: none;
            font-size: 14px;
            font-weight: 700;
            padding: 14px 30px;
            border-radius: 50px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .item-link:hover {{
            background: #3154ff;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(49, 84, 255, 0.4);
        }}

        .expert-card {{
            background: #ffffff;
            border: 2px solid #e0e0e0;
            border-left: 5px solid #3154ff;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            transition: all 0.3s ease;
        }}

        .expert-card:hover {{
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
            border-left-color: #ff082c;
        }}

        .expert-name {{
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 22px;
            font-weight: 900;
            color: #192928;
            margin: 0 0 10px 0;
        }}

        .expert-role {{
            font-family: 'Athletics', Arial, sans-serif;
            font-size: 15px;
            color: #666666;
            font-weight: 600;
            margin-bottom: 15px;
        }}

        .linkedin-btn {{
            display: inline-block;
            background: #3154ff;
            color: #ffffff;
            text-decoration: none;
            font-size: 13px;
            font-weight: 700;
            padding: 12px 24px;
            border-radius: 50px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .linkedin-btn:hover {{
            background: #ff082c;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 8, 44, 0.4);
        }}

        .no-data {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #f0f7ff 0%, #e8f5fe 100%);
            border: 2px dashed #9fdfff;
            border-radius: 12px;
            color: #192928;
            opacity: 0.7;
        }}

        .footer {{
            padding: 60px 40px;
            background: #000000;
            color: #ffffff;
            text-align: center;
        }}

        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #ff082c;
            color: #ffffff;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(255, 8, 44, 0.5);
            transition: all 0.3s ease;
            font-weight: bold;
        }}

        .back-to-top:hover {{
            background: #3154ff;
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 8px 25px rgba(49, 84, 255, 0.5);
        }}

        .toggle-btn {{
            display: block;
            margin: 40px auto 0;
            background: linear-gradient(135deg, #3154ff 0%, #253292 100%);
            color: #ffffff;
            border: none;
            font-family: 'FK Screamer', Arial, sans-serif;
            font-size: 14px;
            font-weight: 900;
            padding: 16px 40px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(49, 84, 255, 0.3);
        }}

        .toggle-btn:hover {{
            background: linear-gradient(135deg, #ff082c 0%, #f95208 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 8, 44, 0.4);
        }}

        .toggle-btn:active {{
            transform: translateY(0);
        }}

        .item-hidden {{
            display: none;
        }}

        /* Print styles - show all content when printing */
        @media print {{
            .item-hidden {{
                display: block !important;
            }}

            .toggle-btn,
            .back-to-top {{
                display: none !important;
            }}

            .item-card,
            .expert-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>

<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div
                style="font-family: 'FK Screamer', Arial, sans-serif; font-size: 11px; font-weight: 900; letter-spacing: 3px; text-transform: uppercase; color: #ffffff; margin-bottom: 20px; opacity: 0.9;">
                Complete Weekly Intelligence • Issue #{week_num}</div>
            <h1
                style="font-family: 'FK Screamer', Arial, sans-serif; font-size: 56px; font-weight: 900; color: #ffffff; margin: 0 0 15px 0; line-height: 1; letter-spacing: -2px;">
                🌍 CLIMATE CARDINALS</h1>
            <p
                style="font-family: 'Athletics', Arial, sans-serif; font-size: 20px; color: #ffffff; margin: 0 0 30px 0; opacity: 0.95; font-weight: 600;">
                Complete
                Weekly Intelligence Report</p>
            <div
                style="display: flex; justify-content: space-between; align-items: center; padding-top: 20px; padding-bottom: 10px; border-top: 2px solid rgba(255,255,255,0.3);">
                <div
                    style="font-family: 'Athletics', Arial, sans-serif; font-size: 15px; font-weight: 700; color: #ffffff; opacity: 0.95;">
                    📅 {date_str}</div>
                <div
                    style="font-family: 'FK Screamer', Arial, sans-serif; font-size: 11px; color: #ffffff; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; opacity: 0.9;">
                    Complete Dataset</div>
            </div>

            <!-- Stats Overview -->
            <div class="stats-grid">
                <a href="#experts" class="stat-card">
                    <div class="stat-number">{experts_count}</div>
                    <div class="stat-label">Climate Experts</div>
                </a>
                <a href="#grants" class="stat-card">
                    <div class="stat-number">{grants_count}</div>
                    <div class="stat-label">Grant Opportunities</div>
                </a>
                <a href="#events" class="stat-card">
                    <div class="stat-number">{events_count}</div>
                    <div class="stat-label">Upcoming Events</div>
                </a>
                <a href="#reports" class="stat-card">
                    <div class="stat-number">{csr_count}</div>
                    <div class="stat-label">ESG Reports</div>
                </a>
            </div>
        </div>
"""

    # Climate Experts Section
    html_content += f"""
        <div class="section" id="experts">
            <div class="section-header">
                <h2 class="section-title">👤 Climate Experts</h2>
                <p class="section-subtitle">Climate leaders and decision-makers actively seeking partnerships and collaboration</p>
            </div>
"""
    
    if not experts_df.empty:
        for idx, (_, row) in enumerate(experts_df.iterrows()):
            name = row.get('Name', 'Unknown')
            role = row.get('Role', '')  
            linkedin = row.get('LinkedIn', '')
            
            linkedin_btn = f'<a href="{linkedin}" class="linkedin-btn">View LinkedIn Profile</a>' if linkedin and linkedin != '—' else ''
            
            html_content += f"""
            <div class="expert-card">
                <div class="expert-name">{name}</div>
                <div class="expert-role">{role}</div>
                {linkedin_btn}
            </div>
"""
    else:
        html_content += '<div class="no-data"><div style="font-size: 40px; margin-bottom: 15px;">👥</div><p>No climate experts curated this week</p></div>'
    
    html_content += "</div>"

    # Grants Section
    html_content += f"""
        <div class="section" id="grants">
            <div class="section-header">
                <h2 class="section-title">💰 Grants & Funding</h2>
                <p class="section-subtitle">Active grant programs and funding opportunities to accelerate climate initiatives</p>
            </div>
"""
    
    if not grants_df.empty:
        for idx, (_, row) in enumerate(grants_df.iterrows()):
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            deadline = row.get('Deadline', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            meta_items = []
            has_deadline = False
            
            # Show deadline countdown prominently if available
            if deadline and deadline != '—':
                has_deadline = True
                if deadline != date_info:
                    # Show the human-readable countdown with highlighted styling
                    meta_items.append(f'<span class="meta-item" style="background: #ffe8ec; padding: 6px 12px; border-radius: 6px; color: #ff082c; font-weight: 700;">⏰ {deadline}</span>')
                elif date_info and date_info != '—':
                    # Show raw date if that's all we have
                    meta_items.append(f'<span class="meta-item" style="background: #ffe8ec; padding: 6px 12px; border-radius: 6px; color: #ff082c; font-weight: 700;">📅 {date_info}</span>')
            elif date_info and date_info != '—':
                has_deadline = True
                # Show raw date if no deadline countdown
                meta_items.append(f'<span class="meta-item" style="background: #ffe8ec; padding: 6px 12px; border-radius: 6px; color: #ff082c; font-weight: 700;">📅 {date_info}</span>')
            
            if domain and domain != '—':
                meta_items.append(f'<span class="meta-item">🌐 {domain}</span>')
            
            meta_html = '<div class="item-meta">' + ''.join(meta_items) + '</div>' if meta_items else ''
            
            # Add deadline note if not available
            deadline_note = '' if has_deadline else '<div style="font-size: 13px; color: #666; margin-top: 12px; font-style: italic;">💡 Visit grant page for deadline and eligibility details</div>'
            
            link_html = f'<a href="{url}" class="item-link">View Grant Details →</a>' if url and url != '—' else ''
            
            html_content += f"""
            <div class="item-card">
                <div class="item-title">{title}</div>
                {meta_html}
                <div class="item-description">{description}</div>
                {deadline_note}
                {link_html}
            </div>
"""
    else:
        html_content += '<div class="no-data"><div style="font-size: 40px; margin-bottom: 15px;">💰</div><p>No grant opportunities curated this week</p></div>'
    
    html_content += "</div>"

    # Events Section
    html_content += f"""
        <div class="section" id="events">
            <div class="section-header">
                <h2 class="section-title">🎤 Events & Conferences</h2>
                <p class="section-subtitle">Premier gatherings where climate leaders convene to share insights and forge partnerships</p>
            </div>
"""
    
    if not events_df.empty:
        for idx, (_, row) in enumerate(events_df.iterrows()):
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            meta_items = []
            
            # Show event countdown prominently if available
            if date_info and date_info != '—':
                countdown = calculate_event_countdown(date_info)
                if countdown:
                    # Show countdown with highlighted styling
                    meta_items.append(f'<span class="meta-item" style="background: #e8f4ff; padding: 6px 12px; border-radius: 6px; color: #0066cc; font-weight: 700;">📅 {countdown}</span>')
                    # Also show the actual date if countdown is relative
                    if countdown not in [date_info, "Ongoing", "Today", "Tomorrow"] and "In " in countdown:
                        meta_items.append(f'<span class="meta-item">🗓️ {date_info}</span>')
            
            if domain and domain != '—':
                meta_items.append(f'<span class="meta-item">🌐 {domain}</span>')
            
            meta_html = '<div class="item-meta">' + ''.join(meta_items) + '</div>' if meta_items else ''
            link_html = f'<a href="{url}" class="item-link">Read Full Article →</a>' if url and url != '—' else ''
            
            html_content += f"""
            <div class="item-card">
                <div class="item-title">{title}</div>
                {meta_html}
                <div class="item-description">{description}</div>
                {link_html}
            </div>
"""
    else:
        html_content += '<div class="no-data"><div style="font-size: 40px; margin-bottom: 15px;">🎤</div><p>No events curated this week</p></div>'
    
    html_content += "</div>"

    # CSR Reports Section
    html_content += f"""
        <div class="section" id="reports">
            <div class="section-header">
                <h2 class="section-title">📊 ESG & Sustainability Reports</h2>
                <p class="section-subtitle">Latest corporate sustainability disclosures and environmental impact assessments</p>
            </div>
"""
    
    if not csr_df.empty:
        for idx, (_, row) in enumerate(csr_df.iterrows()):
            title = row.get('Title', 'Untitled')
            domain = row.get('Domain', row.get('Organization', ''))
            date_info = row.get('Date Info', '')
            url = row.get('URL', '')
            description = row.get('Description', '')
            
            meta_items = []
            if date_info and date_info != '—':
                meta_items.append(f'<span class="meta-item">📅 {date_info}</span>')
            if domain and domain != '—':
                meta_items.append(f'<span class="meta-item">🌐 {domain}</span>')
            
            meta_html = '<div class="item-meta">' + ''.join(meta_items) + '</div>' if meta_items else ''
            link_html = f'<a href="{url}" class="item-link">Read Full Article →</a>' if url and url != '—' else ''
            
            html_content += f"""
            <div class="item-card">
                <div class="item-title">{title}</div>
                {meta_html}
                <div class="item-description">{description}</div>
                {link_html}
            </div>
"""
    else:
        html_content += '<div class="no-data"><div style="font-size: 40px; margin-bottom: 15px;">📊</div><p>No ESG reports curated this week</p></div>'
    
    html_content += "</div>"

    # Footer
    html_content += f"""
        <div class="footer">
            <div style="font-size: 48px; margin-bottom: 20px;">🌍</div>
            <h3
                style="font-family: 'FK Screamer', Arial, sans-serif; font-size: 28px; font-weight: 900; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 2px;">
                CLIMATE CARDINALS</h3>
            <p
                style="font-family: 'Athletics', Arial, sans-serif; font-size: 15px; opacity: 0.9; margin: 0 0 20px 0; font-weight: 600;">
                Complete Weekly Intelligence Report</p>
            <div style="width: 60px; height: 3px; background: #ffffff; margin: 20px auto;"></div>
            <p style="font-family: 'Athletics', Arial, sans-serif; font-size: 12px; opacity: 0.7; margin: 12px 0 0 0;">©
                2026 Climate Cardinals • Generated on {date_str}</p>
        </div>
    </div>
    
    <!-- Back to top button -->
    <button class="back-to-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" title="Back to top">↑</button>
    
    <script>
        // Show/hide back to top button
        window.addEventListener('scroll', function() {{
            const backToTop = document.querySelector('.back-to-top');
            if (window.pageYOffset > 300) {{
                backToTop.style.display = 'block';
            }} else {{
                backToTop.style.display = 'none';
            }}
        }});
        
        // Initially hide the button
        document.querySelector('.back-to-top').style.display = 'none';
        
        // Read More/Show Less functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const sections = document.querySelectorAll('.section');
            
            sections.forEach(section => {{
                // Get all cards in this section (both expert-card and item-card)
                const cards = section.querySelectorAll('.expert-card, .item-card');
                
                // Only add toggle functionality if there are more than 3 cards
                if (cards.length > 3) {{
                    // Hide cards after the first 3
                    cards.forEach((card, index) => {{
                        if (index >= 3) {{
                            card.classList.add('item-hidden');
                        }}
                    }});
                    
                    // Create toggle button
                    const toggleBtn = document.createElement('button');
                    toggleBtn.className = 'toggle-btn';
                    toggleBtn.textContent = `Read More (${{cards.length - 3}} more)`;
                    toggleBtn.setAttribute('aria-expanded', 'false');
                    toggleBtn.setAttribute('aria-label', `Show ${{cards.length - 3}} more items`);
                    
                    // Add click handler
                    let isExpanded = false;
                    toggleBtn.addEventListener('click', function() {{
                        isExpanded = !isExpanded;
                        
                        cards.forEach((card, index) => {{
                            if (index >= 3) {{
                                if (isExpanded) {{
                                    card.classList.remove('item-hidden');
                                }} else {{
                                    card.classList.add('item-hidden');
                                }}
                            }}
                        }});
                        
                        // Update button text and accessibility
                        if (isExpanded) {{
                            toggleBtn.textContent = 'Show Less';
                            toggleBtn.setAttribute('aria-expanded', 'true');
                            toggleBtn.setAttribute('aria-label', 'Show fewer items');
                        }} else {{
                            toggleBtn.textContent = `Read More (${{cards.length - 3}} more)`;
                            toggleBtn.setAttribute('aria-expanded', 'false');
                            toggleBtn.setAttribute('aria-label', `Show ${{cards.length - 3}} more items`);
                            
                            // Scroll to section header when collapsing
                            const sectionHeader = section.querySelector('.section-header');
                            if (sectionHeader) {{
                                sectionHeader.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                            }}
                        }}
                    }});
                    
                    // Append button to section
                    section.appendChild(toggleBtn);
                }}
            }});
        }});
    </script>
</body>
</html>"""

    # Save the HTML file
    output_path = Path(output_dir) / f"climate_cardinals_report_{today.strftime('%Y%m%d')}.html"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Full report saved: {output_path.resolve()}")
    
    # Update index.html with all reports
    update_index_html(output_dir)
    
    return output_path.resolve()

def generate_report_metadata(experts_df, grants_df, events_df, csr_df, report_url):
    """Generate metadata about the report for use in email templates"""
    
    today = datetime.now()
    
    metadata = {
        'date': today.strftime('%Y-%m-%d'),
        'week_number': today.isocalendar()[1],
        'report_url': str(report_url),
        'counts': {
            'experts': len(experts_df) if not experts_df.empty else 0,
            'grants': len(grants_df) if not grants_df.empty else 0,
            'events': len(events_df) if not events_df.empty else 0,
            'csr': len(csr_df) if not csr_df.empty else 0
        }
    }
    
    # Save metadata
    metadata_path = Path("weekly_data") / "report_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata


def update_index_html(output_dir="weekly_data"):
    """
    Update index.html with all available reports listed in reverse chronological order
    """
    # Find all report files
    report_pattern = str(Path(output_dir) / "climate_cardinals_report_*.html")
    report_files = glob.glob(report_pattern)
    
    # Extract dates and sort (newest first)
    reports_data = []
    for report_file in report_files:
        filename = Path(report_file).name
        # Extract date from filename: climate_cardinals_report_YYYYMMDD.html
        match = re.search(r'climate_cardinals_report_(\d{8})\.html', filename)
        if match:
            date_str = match.group(1)
            try:
                report_date = datetime.strptime(date_str, '%Y%m%d')
                reports_data.append({
                    'filename': filename,
                    'date': report_date,
                    'date_str': date_str
                })
            except ValueError:
                continue
    
    # Sort by date (newest first)
    reports_data.sort(key=lambda x: x['date'], reverse=True)
    
    # Remove any reports dated in the future (e.g. test files or mistakes)
    today = datetime.now()
    reports_data = [r for r in reports_data if r['date'] <= today]
    
    # Get the latest report for the main button
    latest_report = reports_data[0]['filename'] if reports_data else None
    
    # Generate report links HTML
    report_links_html = ""
    for report in reports_data:
        formatted_date = report['date'].strftime("%B %d, %Y")
        week_num = report['date'].isocalendar()[1]
        report_links_html += f'''            <a href="{report['filename']}" class="report-link">
                📅 Week {week_num} - {formatted_date}
            </a>
'''
    
    if not report_links_html:
        report_links_html = '''            <p style="color: #8b7355; font-style: italic;">No reports available yet.</p>
'''
    
    # Generate the complete index.html
    index_html = f'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Climate Cardinals Weekly Reports</title>
    <style>
        body {{
            font-family: Georgia, serif;
            background: linear-gradient(135deg, #0a2f1f 0%, #1a5538 100%);
            margin: 0;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .container {{
            max-width: 600px;
            background: #ffffff;
            border-radius: 12px;
            padding: 50px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            text-align: center;
        }}

        .logo {{
            font-size: 72px;
            margin-bottom: 20px;
        }}

        h1 {{
            color: #0a2f1f;
            font-size: 36px;
            margin: 0 0 15px 0;
        }}

        p {{
            color: #1a5538;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}

        .btn {{
            display: inline-block;
            background: #0a2f1f;
            color: #ffffff;
            text-decoration: none;
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 10px;
        }}

        .btn:hover {{
            background: #1a5538;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}

        .secondary {{
            background: #9caf88;
            color: #0a2f1f;
        }}

        .secondary:hover {{
            background: #7d9270;
        }}

        .reports-list {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #e8ece9;
        }}

        .report-link {{
            display: block;
            padding: 15px;
            margin: 10px 0;
            background: #f5f7f5;
            border: 1px solid #9caf88;
            border-radius: 6px;
            color: #0a2f1f;
            text-decoration: none;
            transition: all 0.3s ease;
        }}

        .report-link:hover {{
            background: #e8ece9;
            transform: translateX(5px);
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e8ece9;
            color: #8b7355;
            font-size: 14px;
        }}
    </style>
</head>

<body>
    <div class="container">
        <div class="logo">🌍</div>
        <h1>Climate Cardinals</h1>
        <p>Weekly Intelligence Reports for Climate Action Leaders</p>

        <div>
            {f'<a href="{latest_report}" class="btn">View Latest Report</a>' if latest_report else '<span class="btn" style="opacity: 0.5; cursor: not-allowed;">No Reports Yet</span>'}
            <a href="#reports" class="btn secondary">All Reports</a>
        </div>

        <div id="reports" class="reports-list">
            <h3 style="color: #0a2f1f; margin-bottom: 20px;">📊 Available Reports</h3>
{report_links_html}        </div>

        <div class="footer">
            <p>© 2026 Climate Cardinals<br>
                Empowering the next generation of climate leaders</p>
        </div>
    </div>
</body>

</html>'''
    
    # Save index.html
    index_path = Path(output_dir) / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"🏠 Index page updated with {len(reports_data)} report(s)")
    return index_path