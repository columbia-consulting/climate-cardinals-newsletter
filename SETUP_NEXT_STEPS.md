# SETUP GUIDE - After Code Changes

## ✅ Code Changes Complete

All critical fixes have been implemented! Here's what was changed:

### Files Modified:
1. ✅ `automated_newsletter.py` - Data accumulation, deduplication, Monday-only email, data clearing
2. ✅ `.github/workflows/newsletter.yml` - Removed cache, fixed data persistence
3. ✅ `README.md` - Updated workflow description
4. ✅ `.env.example` - Added WEB_REPORT_BASE_URL

### Files Created:
1. ✅ `netlify.toml` - Netlify deployment configuration
2. ✅ `validate_fixes.py` - Validation script for testing

---

## 🚀 Next Steps for Deployment

### Step 1: Test Locally (5 minutes)

```powershell
# Navigate to project directory
cd c:\Users\Pranav\OneDrive\Desktop\climate-cardinals-newsletter

# Run validation tests
python validate_fixes.py

# Test the script (will scrape data but not send email since it's not Monday)
python automated_newsletter.py
```

**Expected Results:**
- ✅ validate_fixes.py shows all tests passing
- ✅ automated_newsletter.py scrapes data and saves to CSVs
- ✅ State is tracked in state.json
- ✅ No email sent (not Monday)

---

### Step 2: Setup Netlify (10 minutes)

> [!IMPORTANT]
> This is required for the "View All Data" button in emails to work!

Follow the complete guide in [NETLIFY_SETUP.md](file:///c:/Users/Pranav/OneDrive/Desktop/climate-cardinals-newsletter/NETLIFY_SETUP.md)

**Quick Steps:**
1. Go to https://netlify.com and sign up/login
2. Click "Add new site" → "Import an existing project"
3. Connect to your GitHub repository
4. **Build settings:**
   - Build command: *(leave empty)*
   - Publish directory: `weekly_data`
5. Deploy!
6. **Copy your Netlify URL** (e.g., `https://your-site.netlify.app`)

---

### Step 3: Add GitHub Secret (2 minutes)

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. **Name:** `WEB_REPORT_BASE_URL`
5. **Value:** Your Netlify URL from Step 2
   - Example: `https://climate-cardinals-weekly.netlify.app`
6. Click "Add secret"

**Why this matters:** This URL is used in emails so recipients can click "View All Data" and see your Netlify-hosted reports.

---

### Step 4: Push Changes to GitHub (3 minutes)

```powershell
cd c:\Users\Pranav\OneDrive\Desktop\climate-cardinals-newsletter

# Check what changed
git status

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Fix: Add data accumulation, deduplication, and Netlify integration"

# Push to GitHub
git push
```

**What happens next:**
- GitHub Actions workflow runs automatically
- Scrapes data and saves to CSVs
- Commits data back to repo
- Netlify detects the commit and deploys your website
- Your site is live in 1-2 minutes!

---

### Step 5: Verify Everything Works (5 minutes)

#### Test 1: GitHub Actions
1. Go to your repo → Actions tab
2. You should see a workflow run from your push
3. Click on it and check the logs
4. Look for:
   - ✅ "Scraping new data..."
   - ✅ "Saved grants.csv (+X new, Y total after deduplication)"
   - ✅ "Not Monday, skipping email send"
   - ✅ Commit step succeeds

#### Test 2: Netlify Deployment
1. Go to Netlify dashboard
2. Your site should show "Published"
3. Click on the URL to visit your site
4. You should see an index page with your reports listed

#### Test 3: Weekly Data Persistence
1. Go back to your GitHub repo
2. Navigate to `weekly_data/` folder
3. You should see:
   - ✅ `grants.csv`
   - ✅ `events.csv`
   - ✅ `csr_reports.csv`
   - ✅ `experts.csv`
   - ✅ `state.json`
   - ✅ `index.html`
   - ✅ `climate_cardinals_report_YYYYMMDD.html`

---

## 📅 Understanding the Weekly Cycle

### Current Day (Saturday, Feb 8):
```
✅ Script runs → Scrapes data → Saves to CSV
✅ Data committed to GitHub
✅ Netlify deploys updated site
❌ No email sent (not Monday)
```

### Tomorrow (Sunday, Feb 9):
```
✅ Script runs → Scrapes data → APPENDS to CSV
✅ Data now has Saturday + Sunday combined
✅ Duplicates removed automatically
✅ Data committed to GitHub
✅ Netlify updates site
❌ No email sent (not Monday)
```

### Monday (Feb 10):
```
✅ Script runs → Scrapes data → APPENDS to CSV
✅ Data now has ALL WEEK's data (7 days)
✅ Generates HTML reports with all data
✅ Commits to GitHub → Netlify deploys
⏰ Waits 1-2 mins for Netlify
📧 SENDS EMAIL with links to Netlify site
🗑️ CLEARS all CSV files
🔄 Ready for next week
```

---

## 🛠️ Troubleshooting

### Problem: Validation tests fail

**Solution:** Check which test failed and fix accordingly:
- **Data Accumulation:** Run `python automated_newsletter.py` at least once
- **Deduplication:** Check CSV files have URL column
- **State Tracking:** Delete old state.json and re-run script
- **File Structure:** Ensure all files were committed
- **Netlify Config:** Verify netlify.toml was created

### Problem: GitHub Actions fails

**Solution:** Check the error in Actions logs:
1. Go to Actions tab → Click failed run
2. Click "Run newsletter script" step
3. Look for error messages
4. Common issues:
   - Missing WEB_REPORT_BASE_URL secret
   - Invalid SMTP credentials
   - Python dependency installation failure

### Problem: Netlify not deploying

**Solution:**
1. Check Netlify dashboard for deployment logs
2. Verify publish directory is set to `weekly_data`
3. Ensure GitHub connection is active
4. Try manual "Trigger deploy" in Netlify

### Problem: Email not sending on Monday

**Solution:**
1. Check GitHub Actions logs for Monday run
2. Verify email secrets are set correctly:
   - SENDER_EMAIL
   - SENDER_PASSWORD (Gmail app password, no spaces!)
   - RECIPIENT_EMAILS (comma-separated, no spaces)
3. Check spam folder for test emails

---

## ✨ You're All Set!

Your newsletter automation system is now fully fixed and ready to run! 

**What happens automatically:**
- ✅ Runs daily at 9 AM UTC
- ✅ Accumulates data Tuesday-Sunday
- ✅ Removes duplicates automatically
- ✅ Sends email every Monday with full week's data
- ✅ Clears data after Monday for fresh start
- ✅ Updates Netlify website before each email
- ✅ Costs $0 to operate

**No manual work needed!** Just monitor the first week to ensure everything works as expected.

---

## 📋 First Week Checklist

Monitor these on each day:

**Tuesday-Sunday:**
- [ ] GitHub Actions runs successfully
- [ ] CSV files grow with more data each day
- [ ] No duplicates in CSVs
- [ ] Netlify site updates daily
- [ ] state.json tracks last_scrape_date

**Monday:**
- [ ] GitHub Actions runs successfully
- [ ] Email arrives in inbox (check spam too!)
- [ ] Email contains preview of data
- [ ] "View All Data" button works and goes to Netlify
- [ ] Netlify shows complete weekly data
- [ ] CSV files are cleared after email
- [ ] Tuesday starts fresh accumulation

---

**Questions?** Review the full guides:
- [DEPLOYMENT_GUIDE.md](file:///c:/Users/Pranav/OneDrive/Desktop/climate-cardinals-newsletter/DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [NETLIFY_SETUP.md](file:///c:/Users/Pranav/OneDrive/Desktop/climate-cardinals-newsletter/NETLIFY_SETUP.md) - Netlify hosting setup
- [automation_review.md](file:///C:/Users/Pranav/.gemini/antigravity/brain/1703a778-7cb2-4187-9c41-429c588af906/automation_review.md) - Technical analysis of fixes
