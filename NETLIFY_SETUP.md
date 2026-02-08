# Netlify Auto-Deployment Setup Guide

## 🎯 Overview
This guide sets up automatic deployment to Netlify whenever new data is scraped. Your workflow will be:
1. Run script → Scrapes data → Generates reports → Sends email
2. Commits changes to GitHub
3. GitHub triggers Netlify → Site updates automatically

---

## 📋 Prerequisites
- GitHub account
- Netlify account (free at netlify.com)
- Git installed on your computer

---

## 🚀 Setup Steps

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `climate-cardinals-newsletter`
3. Set as **Public** (required for free Netlify)
4. Don't add README, .gitignore, or license (we have files already)
5. Click "Create repository"

### Step 2: Connect Local Project to GitHub

Open PowerShell in your project folder and run:

```powershell
# Initialize Git (if not already done)
git init

# Create .gitignore to exclude sensitive files
@"
__pycache__/
*.pyc
.env
*.log
.DS_Store
"@ | Out-File -FilePath .gitignore -Encoding utf8

# Stage all files
git add .

# First commit
git commit -m "Initial commit - Climate Cardinals Newsletter"

# Rename branch to main
git branch -M main

# Add your GitHub repository (REPLACE with your username!)
git remote add origin https://github.com/YOUR_USERNAME/climate-cardinals-newsletter.git

# Push to GitHub
git push -u origin main
```

**🔐 If GitHub asks for authentication:**
- Use Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens
- Select scope: `repo` (full repository access)

### Step 3: Connect Netlify to GitHub

1. Go to https://netlify.com and login
2. Click "Add new site" → "Import an existing project"
3. Choose **GitHub**
4. Authorize Netlify to access your repositories
5. Select: `climate-cardinals-newsletter`
6. **Build settings:**
   - Build command: *(leave empty)*
   - Publish directory: `weekly_data`
7. Click **Deploy site**

### Step 4: Get Your Netlify URL

After deployment completes (1-2 minutes):
1. Copy your Netlify URL (e.g., `https://YOUR-SITE-NAME.netlify.app`)
2. Update your environment variable:

```powershell
# Set permanently (add to your PowerShell profile)
$env:WEB_REPORT_BASE_URL="https://YOUR-SITE-NAME.netlify.app"

# Or edit automated_newsletter.py and set:
# WEB_REPORT_BASE_URL = "https://YOUR-SITE-NAME.netlify.app"
```

### Step 5: Configure Auto-Deploy

Netlify is now watching your GitHub repository! Every time you push changes, it auto-deploys.

**Enable continuous deployment:**
- Already enabled by default! ✅
- Every `git push` triggers a new deployment
- Check deployment status at: netlify.com/sites/YOUR-SITE-NAME/deploys

---

## 🔄 Weekly Workflow

### Option A: Automated Script (Recommended)

Run the all-in-one script:

```powershell
python run_and_deploy.py
```

This automatically:
1. ✅ Scrapes new data
2. ✅ Generates reports  
3. ✅ Updates index.html
4. ✅ Sends email
5. ✅ Commits to Git
6. ✅ Pushes to GitHub → Triggers Netlify deployment

### Option B: Manual Commands

```powershell
# 1. Scrape data and send email
python automated_newsletter.py

# 2. Commit and push
git add .
git commit -m "Weekly update: $(Get-Date -Format 'yyyy-MM-dd')"
git push

# Netlify auto-deploys in 1-2 minutes!
```

---

## 🔧 Customization

### Change Netlify Site Name

1. Go to Netlify dashboard
2. Site settings → Domain management → Options
3. Change site name to something memorable
4. Update `WEB_REPORT_BASE_URL` environment variable

### Schedule Automatic Runs

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task → "Climate Cardinals Weekly"
3. Trigger: Weekly, Monday 9:00 AM
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File "C:\path\to\run_and_deploy.py"`

---

## 📊 Monitoring

### Check Deployment Status

**Netlify Dashboard:**
- URL: https://app.netlify.com/sites/YOUR-SITE-NAME/deploys
- Shows: Deploy log, status, preview URL

**GitHub:**
- Your commits appear immediately
- Check: https://github.com/YOUR_USERNAME/climate-cardinals-newsletter/commits

### Verify Live Site

After deployment:
1. Visit: `https://YOUR-SITE-NAME.netlify.app`
2. Should see all weekly reports listed
3. Click "View Latest Report" to see newest data

---

## 🛠️ Troubleshooting

### Problem: Netlify shows 404 "Page Not Found"

**Solution:** Publish directory is wrong
- Go to Site settings → Build & deploy → Continuous deployment
- Set "Publish directory" to: `weekly_data`
- Click "Save" and trigger manual deploy

### Problem: Git push fails "permission denied"

**Solution:** Set up authentication
```powershell
# Use GitHub CLI (recommended)
winget install GitHub.cli
gh auth login

# Or use Personal Access Token
# Generate at: https://github.com/settings/tokens
```

### Problem: Index.html not updating

**Solution:** Run web report generator
```powershell
python -c "from web_report_generator import update_index_html; update_index_html()"
```

### Problem: Old reports not showing

**Solution:** All reports are auto-scanned from `weekly_data/` folder
- Check files exist: `ls weekly_data/*.html`
- Regenerate index: Run command above

---

## ✅ Verification Checklist

After setup, verify:
- [ ] GitHub repository created and pushed
- [ ] Netlify connected to GitHub repo
- [ ] Netlify publish directory = `weekly_data`
- [ ] Can access site at Netlify URL
- [ ] Index page shows all reports
- [ ] Latest report link works
- [ ] `WEB_REPORT_BASE_URL` environment variable set
- [ ] Email contains correct Netlify URLs
- [ ] Git push triggers Netlify deployment

---

## 🎉 You're Done!

Your automated workflow:
1. Run `python run_and_deploy.py` every Monday
2. New data → Reports generated → Email sent
3. GitHub updated → Netlify deploys automatically
4. Live site updated with latest reports in 2 minutes!

**Next time:** Just run the script and everything updates automatically! 🚀
