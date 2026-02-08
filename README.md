# Climate Cardinals - Automated Weekly Newsletter

🌍 **100% FREE automated climate intelligence newsletter** using DuckDuckGo (no API keys needed)

---

## ⚡ Quick Start

1. **Setup Gmail** (5 min) - Enable 2FA and generate app password
2. **Deploy to GitHub** (10 min) - Upload files and add 3 secrets
3. **Done!** - Runs automatically forever

**Full guide**: See `DEPLOYMENT_GUIDE.md`

---

## 📋 What You Need

- ✅ Gmail account (free)
- ✅ GitHub account (free)
- ✅ 15 minutes of time

**Total Cost: $0/month forever**

---

## 🚀 Features

- ✅ **Runs daily** - Collects data Tuesday-Sunday
- ✅ **Sends Monday** - Beautiful email every Monday morning
- ✅ **Auto-clears** - Fresh data each week
- ✅ **100% FREE** - No API keys required
- ✅ **Unlimited searches** - DuckDuckGo has no rate limits
- ✅ **Premium design** - Magazine-quality email template

---

## 📊 What It Collects

Each week gathers:
- 💰 **Grants & Funding** - Climate/sustainability opportunities
- 📅 **Events & Conferences** - Upcoming climate events
- 👥 **Climate Experts** - LinkedIn profiles of leaders
- 📊 **ESG Reports** - Corporate sustainability disclosures

---

## 🔑 Required Secrets (GitHub)

Add these 3 secrets to GitHub Actions:

1. **SENDER_EMAIL** - Your Gmail address  
2. **SENDER_PASSWORD** - Gmail app password (16 chars, no spaces)
3. **RECIPIENT_EMAILS** - Client emails (comma-separated, no spaces)

---

## 📁 Project Structure

```
climate-cardinals-newsletter/
├── automated_newsletter.py    # Main automation script
├── email_template.py          # Premium HTML email generator
├── requirements.txt           # Python dependencies
├── .env.example              # Config template
├── .github/workflows/
│   └── newsletter.yml        # GitHub Actions workflow
├── DEPLOYMENT_GUIDE.md       # Step-by-step deployment
└── test_setup.py             # Verify your setup
```

---

## 🗓️ How It Works

### Tuesday - Sunday (Days 2-7)
- Script runs at 9 AM UTC
- Scrapes new climate data via DuckDuckGo
- **Appends** new data to existing CSV files
- **Removes duplicates** by URL (keeps first occurrence)
- Commits to GitHub → Triggers Netlify deployment
- Website shows latest accumulated data

### Monday (Day 1)
- Script runs at 9 AM UTC
- Scrapes Monday's data
- Adds to accumulated weekly data (now 7 days of data)
- Generates complete HTML reports
- Commits to GitHub → Triggers Netlify deployment
- **Sends email** with links to updated website
- **Clears all CSV files** for fresh week start

---

## 🔧 Setup Instructions

### Option 1: Quick Deploy (Recommended)

```bash
# 1. Setup Gmail (see DEPLOYMENT_GUIDE.md)

# 2. Upload to GitHub
# - Create new repository
# - Upload all files

# 3. Add 3 secrets in Settings → Secrets → Actions

# 4. Enable workflow in Actions tab

# Done! Runs automatically
```

### Option 2: Local Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env with your keys

# 3. Test setup
python test_setup.py

# 4. Run manually
python automated_newsletter.py
```

---

## ✅ Verification

After deployment:

1. **Test run** - Go to Actions → Run workflow
2. **Check logs** - Should see data collection
3. **Wait for Monday** - First email sends
4. **Check inbox** - Verify email received
5. **Check spam** - First email may go to spam

---

## 📊 Search System

### DuckDuckGo
- **Unlimited searches** - No rate limits
- **No API key needed** - Just works
- **Reliable** - Fallback for any API issues
- **Fast** - Results in seconds

---

## 🛠️ Troubleshooting

### No email received
- Check spam folder
- Verify SENDER_PASSWORD has no spaces
- Check RECIPIENT_EMAILS format: `email1@x.com,email2@y.com`

### No data collected
- Check workflow logs in Actions tab
- Verify Gmail credentials are correct
- DuckDuckGo should always work

### Workflow not running
- Check Actions tab is enabled
- Verify `.github/workflows/newsletter.yml` exists
- GitHub Actions can have 5-15 minute delays

---

## 📞 Support Files

- **`DEPLOYMENT_GUIDE.md`** - Complete deployment instructions
- **`test_setup.py`** - Verify your configuration

---

## 💰 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| GitHub Actions | ~70 min/month | $0 (free tier: 2,000 min) |
| DuckDuckGo | Unlimited | $0 |
| Gmail | Email sending | $0 |
| **Total** | | **$0/month** |

---

## 🎉 You're All Set!

After deployment, the system:
- ✅ Runs automatically daily
- ✅ Sends beautiful emails every Monday
- ✅ Costs nothing to operate
- ✅ Requires zero maintenance

**Just set it and forget it!** 🚀

---

## 📝 License

MIT License - Free to use and modify

---

**Made with 🌍 for Climate Cardinals**

*Questions? Check DEPLOYMENT_GUIDE.md*
