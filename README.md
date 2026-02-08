# Climate Cardinals Newsletter Automation

Automated weekly climate intelligence newsletter system.

## Features
- Daily scraping (Tuesday-Sunday)
- Weekly email digest (Monday)
- Automatic Netlify deployment
- Zero maintenance required

## Setup
1. Add GitHub Secrets:
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAILS`
   - `WEB_REPORT_BASE_URL`

2. Connect Netlify to this repo
3. Push to GitHub - automation runs daily at 9 AM UTC

## Files
- `automated_newsletter.py` - Main script
- `email_template_condensed.py` - Email generator
- `web_report_generator.py` - HTML report generator
- `.github/workflows/newsletter.yml` - GitHub Actions workflow
- `netlify.toml` - Netlify configuration
