# 🚀 FINAL DEPLOYMENT GUIDE - Climate Cardinals Newsletter

## Complete Step-by-Step Instructions (DuckDuckGo - No API Keys)

### 📋 What You'll Need (3 items total)

- [ ] GitHub account (free)
- [ ] Gmail account (for sending emails)
- [ ] Client's recipient email addresses
- [ ] 15 minutes of time

---

## 📧 STEP 1: Setup Gmail for Sending (5 minutes)

### 1.1 Enable 2-Factor Authentication

1. Go to **https://myaccount.google.com/security**
2. Under "Signing in to Google", click **"2-Step Verification"**
3. Follow the setup process
4. Verify your phone number

### 1.2 Generate App Password

1. Go back to **https://myaccount.google.com/security**
2. Under "Signing in to Google", click **"2-Step Verification"**
3. Scroll down to **"App passwords"**
4. Click **"App passwords"**
5. You may need to sign in again
6. Select:
   - **App**: Mail
   - **Device**: Other (Custom name)
   - **Name it**: "Climate Cardinals Newsletter"
7. Click **"Generate"**
8. Copy the **16-character password** (example: `abcd efgh ijkl mnop`)
9. **Remove all spaces**: `abcdefghijklmnop`
10. **SAVE THIS PASSWORD** - you'll need it in Step 3

**✅ You should now have your Gmail app password!**

---

## 📁 STEP 2: Setup GitHub Repository (10 minutes)

### 2.1 Download the Project Files

1. **Download** the ZIP file: `climate-cardinals-newsletter.zip`
2. **Extract** it to a folder on your computer
3. You should see these files:
   ```
   climate-cardinals-newsletter/
   ├── automated_newsletter.py
   ├── email_template.py
   ├── requirements.txt
   ├── .env.example
   ├── .gitignore
   ├── README.md
   ├── DEPLOYMENT_GUIDE.md
   ├── test_setup.py
   └── .github/
       └── workflows/
           └── newsletter.yml
   ```

### 2.2 Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name**: `climate-cardinals-newsletter`
   - **Description**: "Automated weekly climate intelligence newsletter"
   - **Privacy**: Choose **Private** (recommended for client projects)
   - **Initialize**: ❌ Do NOT check "Add README file"
3. Click **"Create repository"**

### 2.3 Upload Files to GitHub

**Option A - Web Upload (Easier):**

1. On your new repository page, click **"uploading an existing file"**
2. **Drag and drop ALL files** from the extracted folder
3. Make sure to include the `.github` folder with the `workflows` subfolder
4. Scroll down and click **"Commit changes"**

**Option B - Command Line (Advanced):**

```bash
cd path/to/climate-cardinals-newsletter
git init
git add .
git commit -m "Initial commit - automated newsletter"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/climate-cardinals-newsletter.git
git push -u origin main
```

**✅ Your code should now be on GitHub!**

---

## 🔒 STEP 3: Configure GitHub Secrets (5 minutes)

This is **CRITICAL** - without these secrets, the newsletter won't work!

1. Go to your repository on GitHub
2. Click **"Settings"** tab (top menu)
3. In left sidebar, click **"Secrets and variables"** → **"Actions"**
4. Click **"New repository secret"** button

### Add These 3 Secrets (one at a time):

#### Secret 1: SENDER_EMAIL
- **Name**: `SENDER_EMAIL`
- **Value**: Your Gmail address
  - Example: `yourname@gmail.com`
- Click **"Add secret"**

#### Secret 2: SENDER_PASSWORD
- **Name**: `SENDER_PASSWORD`
- **Value**: Your 16-character Gmail App Password from Step 1.2 (NO SPACES)
  - Example: `abcdefghijklmnop`
- Click **"Add secret"**

#### Secret 3: RECIPIENT_EMAILS
- **Name**: `RECIPIENT_EMAILS`
- **Value**: Client email addresses separated by commas (NO SPACES between emails)
  - Example: `client@company.com,manager@company.com,team@company.com`
- Click **"Add secret"**

### ✅ Verify All 3 Secrets Are Added

You should see 3 secrets listed:
- ✅ SENDER_EMAIL
- ✅ SENDER_PASSWORD
- ✅ RECIPIENT_EMAILS

---

## ✅ STEP 4: Enable GitHub Actions (2 minutes)

1. Go to **"Actions"** tab in your repository
2. If you see "Workflows aren't being run on this repository":
   - Click **"I understand my workflows, go ahead and enable them"**
3. You should see **"Climate Cardinals Weekly Newsletter"** workflow
4. If it says "This workflow has a workflow_dispatch event trigger":
   - Click **"Enable workflow"**

**✅ GitHub Actions is now enabled!**

---

## 🧪 STEP 5: Test the System (3 minutes)

### 5.1 Run Manual Test

1. Stay on the **"Actions"** tab
2. Click **"Climate Cardinals Weekly Newsletter"** (on the left)
3. Click **"Run workflow"** button (right side)
4. Select **"Branch: main"**
5. Click the green **"Run workflow"** button
6. Wait 10-20 seconds, then refresh the page
7. You should see a workflow run appear (yellow/orange circle = running)

### 5.2 Check the Results

1. Click on the running workflow
2. Click **"collect-and-send"**
3. Click **"Run newsletter script"**
4. You should see output like:
   ```
   🌍 CLIMATE CARDINALS - FREE AUTOMATED NEWSLETTER
   📅 Date: Saturday, February 07, 2026
   📥 Collecting data for the week (Day 6/7)
   💰 Collecting Grants...
     ✓ DuckDuckGo: 8 results
   ```

### 5.3 What to Expect

**If it's NOT Monday:**
- ✅ Script collects data
- ✅ Saves to CSV files
- ✅ No email sent (waits for Monday)

**If it IS Monday:**
- ✅ Script loads all weekly data
- ✅ Generates beautiful HTML email
- ✅ Sends to all recipient emails
- ✅ Clears data for fresh week

**✅ If you see green checkmarks, it's working!**

---

## 🗓️ STEP 6: Understand the Weekly Cycle

### How the Automation Works:

```
TUESDAY - SUNDAY (Days 2-7)
├─ 9:00 AM UTC - Script runs automatically
├─ Collects climate data via DuckDuckGo
├─ Appends to weekly CSV files
├─ Removes duplicates
└─ Waits for Monday

MONDAY (Day 1)
├─ 9:00 AM UTC - Script runs automatically
├─ Detects it's Monday
├─ Loads ALL accumulated data from the week
├─ Generates premium HTML email
├─ Sends to all recipients
├─ CLEARS all CSV files
└─ Ready to start fresh week
```

### Daily Schedule:
- **Runs at**: 9:00 AM UTC every day
- **UTC to your timezone**:
  - 9 AM UTC = 4 AM EST (New York)
  - 9 AM UTC = 1 AM PST (Los Angeles)
  - 9 AM UTC = 2:30 PM IST (India)

### To Change the Schedule:

1. Edit `.github/workflows/newsletter.yml`
2. Change the cron line:
   ```yaml
   - cron: '0 14 * * *'  # 2 PM UTC = 9 AM EST
   ```
3. Cron format: `minute hour day month dayofweek`
   - `0 9 * * *` = 9 AM UTC every day
   - `0 14 * * 1` = 2 PM UTC every Monday only

---

## 📊 STEP 7: Monitor & Verify

### Check First Email (Monday)

**After first Monday at 9 AM UTC:**

1. **Check recipient inboxes** for the email
2. **Check spam folder** if not in inbox
3. **Verify email looks correct** (premium design)

### View Collection Progress (Any Day)

1. Go to **"Actions"** tab
2. Click on latest workflow run
3. Click **"Run newsletter script"**
4. See what data was collected

### Check for Errors

If something fails:
1. Go to **"Actions"** tab
2. Look for **red X** next to workflow run
3. Click on it to see error messages
4. Common fixes:
   - Re-check all 3 secrets are correct
   - Verify Gmail app password (no spaces)
   - Check recipient emails format (no spaces after commas)

---

## 🎯 VERIFICATION CHECKLIST

Before considering deployment complete:

- [ ] Gmail app password generated
- [ ] GitHub repository created
- [ ] All project files uploaded
- [ ] 3 GitHub secrets configured correctly
- [ ] GitHub Actions enabled
- [ ] Test workflow run completed successfully
- [ ] Understand Monday = email day
- [ ] Client email addresses added
- [ ] Spam folder checked (first email)

---

## 🛠️ TROUBLESHOOTING

### Email Not Sending

**Symptoms**: It's Monday but no email received

**Solutions**:
1. Check Gmail hasn't blocked automated sending:
   - Go to Gmail → Check for security alerts
   - Verify "Less secure app access" or "App passwords" is working
2. Verify SENDER_PASSWORD has no spaces
3. Check RECIPIENT_EMAILS format: `email1@domain.com,email2@domain.com`
4. Look at workflow logs for error messages

### No Data Collected

**Symptoms**: CSV files are empty or email has no items

**Solutions**:
1. Check workflow logs for errors
2. Verify DuckDuckGo is accessible
3. Try running workflow manually again

### Workflow Not Running

**Symptoms**: No automatic runs appearing

**Solutions**:
1. Check Actions tab is enabled
2. Verify `.github/workflows/newsletter.yml` exists
3. GitHub Actions can have 5-15 minute delays
4. Check repository isn't disabled

---

## 💰 COST BREAKDOWN

### Current Setup (100% FREE)

| Service | Cost | Usage |
|---------|------|-------|
| GitHub Actions | $0 | 2-3 min/day = ~70 min/month (free tier: 2,000 min) |
| DuckDuckGo | $0 | Unlimited, free |
| Gmail | $0 | Free sending |
| **TOTAL** | **$0/month** | ✅ |

---

## 📝 FINAL CHECKLIST

- [ ] Downloaded ZIP and extracted files
- [ ] Created GitHub repository
- [ ] Uploaded all files to GitHub
- [ ] Added 3 secrets to GitHub
- [ ] Enabled GitHub Actions
- [ ] Ran test workflow successfully
- [ ] Understand weekly cycle (Monday = email)
- [ ] Client emails configured
- [ ] First Monday verified

---

## 🎉 YOU'RE DONE!

The system is now **fully automated**:

✅ **Runs automatically** every day at 9 AM UTC
✅ **Collects data** Tuesday-Sunday
✅ **Sends email** every Monday
✅ **Clears data** after sending
✅ **Costs $0** to run
✅ **No manual work** required ever

### To Disable Later:
1. Actions tab → Climate Cardinals Weekly Newsletter
2. Click "..." menu → Disable workflow

### To Re-enable:
1. Same steps → Enable workflow

---

## 📞 SUPPORT

If something goes wrong:

1. **Check workflow logs** in Actions tab
2. **Review troubleshooting** section above
3. **Verify all 3 secrets** are correct
4. **Check spam folder** for emails
5. **Contact technical support** if needed

---

## 🚀 NEXT STEPS

After deployment:
1. **Monitor first week** of data collection
2. **Verify first Monday email** arrives
3. **Check spam folders** initially
4. **Confirm with client** email looks good
5. **Set it and forget it!**

---

**Made with 🌍 for Climate Cardinals**

*Last Updated: February 2026*
