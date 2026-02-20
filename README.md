# Climate Cardinals Newsletter Automation

Automated weekly climate intelligence newsletter system.

## Features
- Daily scraping (Tuesday–Sunday)
- Weekly email digest (Monday)
- Weekly static site deployed with GitHub Pages
- Zero maintenance required after initial setup

## Setup
1. Add GitHub Secrets:
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAILS`
   - `WEB_REPORT_BASE_URL`

2. (Optional) if you still have a Netlify site, go to the dashboard and disable automatic builds or delete the site entirely. The repo no longer needs Netlify and there are no build credits required.

3. Push to GitHub – the existing `newsletter.yml` workflow will continue sending emails; the new `weekly-report.yml` workflow will regenerate and publish static HTML every Monday.

4. Enable GitHub Pages
   - In your repository settings, go to **Pages**.
   - Under **Build and deployment**, select the **gh-pages** branch and **/ (root)** folder.
   - Save; the site will be available at `https://<your‑user>.github.io/<repo>` or your custom domain.
   - If you previously pointed a custom domain to Netlify, update the DNS records to point at GitHub Pages instead (or remove them to let the default URL work).

## Files
- `automated_newsletter.py` - Main script
- `email_template_condensed.py` - Email generator
- `web_report_generator.py` - HTML report generator
- `.github/workflows/newsletter.yml` - GitHub Actions workflow
- `netlify.toml` - Netlify configuration
