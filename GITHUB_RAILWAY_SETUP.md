# 🚀 GitHub → Railway Deployment Guide

## 📁 Step 1: Set Up on Your Desktop

### 1.1 Create Project Folder

```bash
# On your desktop, create a new folder
mkdir milo-price-tracker
cd milo-price-tracker
```

### 1.2 Download Files from Claude

Download ALL files from Claude outputs to this folder:

**Core Files (MUST HAVE):**
- ✅ `complete_backend.py` - Your main backend
- ✅ `multi_platform_scraper.py` - All platform scrapers
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway start command
- ✅ `railway.json` - Railway build config
- ✅ `runtime.txt` - Python version
- ✅ `.gitignore` - Git exclusions

**Optional (but recommended):**
- 📚 `TESTING_GUIDE.md`
- 📚 `FLASH_SALE_GUIDE.md`
- 📚 `COMPLETE_GUIDE.md`
- 📚 `RAILWAY_DEPLOY.md`
- 📚 `QUICK_START.md`
- 📚 `README.md`
- 🎨 `milo-tracker.html` - Frontend (optional, can deploy separately)
- 🧪 `test_all_features.py` - Test suite (optional)

### 1.3 Verify Your Folder Structure

Your folder should look like this:

```
milo-price-tracker/
├── complete_backend.py          ← Main backend
├── multi_platform_scraper.py    ← Scrapers
├── requirements.txt             ← Dependencies
├── Procfile                     ← Railway start
├── railway.json                 ← Railway config
├── runtime.txt                  ← Python version
├── .gitignore                   ← Git ignore
├── README.md                    ← Documentation
├── TESTING_GUIDE.md
├── FLASH_SALE_GUIDE.md
├── COMPLETE_GUIDE.md
└── RAILWAY_DEPLOY.md
```

## 📝 Step 2: GitHub Repository Name

### Recommended Names:

**Option 1: Descriptive**
```
milo-price-tracker-sg
```
✅ Clear purpose
✅ Includes location
✅ Professional

**Option 2: Short & Sweet**
```
milo-tracker
```
✅ Simple
✅ Easy to remember
✅ Clean URL

**Option 3: Branded**
```
milocompare-singapore
```
✅ Unique
✅ Marketable
✅ Professional

**My Recommendation:** `milo-price-tracker-sg`
- Clear what it does
- Singapore-specific
- SEO-friendly
- Professional for portfolio

### What NOT to Name It:
❌ `test-project`
❌ `my-scraper`
❌ `untitled`
❌ Names with spaces (GitHub doesn't allow)

## 🔧 Step 3: Initialize Git

```bash
# In your milo-price-tracker folder
git init
git add .
git commit -m "Initial commit: Milo price tracker with flash sale detection"
```

## 🌐 Step 4: Create GitHub Repository

### Option A: Using GitHub Website (Easiest)

1. Go to https://github.com/new
2. Repository name: `milo-price-tracker-sg`
3. Description: `Multi-platform price tracker for Milo products in Singapore with flash sale detection (FairPrice, Shopee, Lazada, Sheng Siong, Giant)`
4. **Public** or **Private**: Your choice
   - Public: Good for portfolio, others can see
   - Private: Keep it personal
5. ❌ **DO NOT** check "Initialize with README"
6. ❌ **DO NOT** add .gitignore
7. ❌ **DO NOT** choose a license (yet)
8. Click **"Create repository"**

### Option B: Using GitHub CLI (Advanced)

```bash
# If you have GitHub CLI installed
gh repo create milo-price-tracker-sg --public --source=. --remote=origin
```

## 🔗 Step 5: Link Local to GitHub

After creating the repo on GitHub, you'll see commands like this:

```bash
# Copy your actual URL from GitHub
git remote add origin https://github.com/YOUR-USERNAME/milo-price-tracker-sg.git
git branch -M main
git push -u origin main
```

**Replace `YOUR-USERNAME`** with your actual GitHub username!

## ✅ Step 6: Verify Push

Go to your GitHub repo:
```
https://github.com/YOUR-USERNAME/milo-price-tracker-sg
```

You should see all your files! ✅

## 🚂 Step 7: Deploy to Railway

### 7.1 Sign Up for Railway

1. Go to https://railway.app
2. Click **"Login with GitHub"**
3. Authorize Railway to access your GitHub

### 7.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **`milo-price-tracker-sg`**
4. Railway will automatically:
   - ✅ Detect Python
   - ✅ Read `railway.json`
   - ✅ Install from `requirements.txt`
   - ✅ Install Playwright + Chromium
   - ✅ Start your server

### 7.3 Wait for Build

First deployment takes **3-5 minutes**:
- Installing Python
- Installing dependencies
- Installing Playwright & Chromium
- Starting server

Watch the logs - you should see:
```
✅ Installing Python 3.11.6
✅ Installing dependencies
✅ Installing Playwright
✅ Starting server...
🥤 Milo Price Tracker API
Server: http://0.0.0.0:XXXX
```

### 7.4 Get Your Public URL

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy your URL (like: `milo-tracker-production.up.railway.app`)

### 7.5 Test Your API

```bash
# Replace with your Railway URL
curl https://your-app.up.railway.app/api/status

# Should return:
{
  "status": "running",
  "cache_status": "active",
  ...
}
```

## 🎨 Step 8: Update Frontend (Optional)

If you want to deploy the frontend:

### Option A: Update HTML to Use Railway API

```javascript
// In milo-tracker.html, change:
const API_URL = 'https://your-app.up.railway.app';
```

### Option B: Deploy Frontend Separately to Vercel

```bash
# Create separate repo for frontend
mkdir milo-tracker-frontend
cd milo-tracker-frontend
# Copy milo-tracker.html here
# Push to GitHub
# Deploy to Vercel (free)
```

## 🔄 Step 9: Future Updates

Whenever you make changes:

```bash
# Make your changes
git add .
git commit -m "Added feature X"
git push

# Railway automatically redeploys! 🎉
```

## 📊 Step 10: Monitor Your Deployment

### Railway Dashboard Shows:
- 🔴 Build status
- 📊 CPU/Memory usage
- 📝 Logs (live)
- 💰 Cost (free tier: $5/month credit)

### Check Logs:
1. Go to Railway project
2. Click on service
3. View **"Deployments"** tab
4. See real-time logs

## ⚠️ Common Issues & Solutions

### Issue 1: Git Push Fails
```bash
# If you get authentication error:
# Use GitHub personal access token
git remote set-url origin https://YOUR-TOKEN@github.com/YOUR-USERNAME/milo-price-tracker-sg.git
```

### Issue 2: Railway Build Fails
**Check:**
- `requirements.txt` is present
- `Procfile` is present
- `railway.json` is present
- All file names are correct (case-sensitive!)

### Issue 3: App Crashes on Railway
**Check logs for:**
- Port binding issues (Railway sets PORT env var)
- Missing dependencies
- Scraper timeouts

**Fix:** Already handled in `complete_backend.py`:
```python
port = int(os.environ.get('PORT', 5000))  # ✅ Already done
```

### Issue 4: Playwright Fails to Install
**Solution:** Already in `railway.json`:
```json
"buildCommand": "pip install -r requirements.txt && playwright install chromium --with-deps"
```

## 🎯 Quick Reference Commands

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Create GitHub repo (on website)
# Then link it:
git remote add origin https://github.com/YOUR-USERNAME/milo-price-tracker-sg.git
git branch -M main
git push -u origin main

# Future updates:
git add .
git commit -m "Your message"
git push

# Railway deploys automatically after push! ✨
```

## 📋 Pre-Flight Checklist

Before pushing to GitHub:

- [ ] All files downloaded to `milo-price-tracker` folder
- [ ] `.gitignore` file present
- [ ] `requirements.txt` has all dependencies
- [ ] `Procfile` exists
- [ ] `railway.json` exists
- [ ] No sensitive data (API keys, passwords) in files
- [ ] README.md explains the project

Before deploying to Railway:

- [ ] GitHub repo created and pushed
- [ ] Railway account created with GitHub
- [ ] Railway has access to your repo
- [ ] Ready to wait 3-5 minutes for first build

## 🎉 Success Criteria

You'll know it worked when:

- ✅ GitHub shows all your files
- ✅ Railway build completes (green checkmark)
- ✅ Railway gives you a public URL
- ✅ `curl https://your-app/api/status` returns JSON
- ✅ `curl https://your-app/api/products` returns product data

## 💡 Pro Tips

1. **Use descriptive commit messages**
   ```bash
   git commit -m "Added Lazada flash sale detection"
   # Better than: git commit -m "update"
   ```

2. **Create a good README**
   - What it does
   - How to run locally
   - API endpoints
   - Technologies used

3. **Add a .env.example file** (for future features)
   ```
   # .env.example
   PORT=5000
   CACHE_DURATION=3600
   ```

4. **Tag releases**
   ```bash
   git tag -a v1.0.0 -m "First release"
   git push origin v1.0.0
   ```

5. **Monitor Railway costs**
   - Check usage in Railway dashboard
   - Set spending limit if needed
   - Free tier usually enough for personal projects

## 📞 Need Help?

**GitHub Issues:**
- Can't push: Check authentication
- Wrong URL: Verify remote URL
- Permission denied: Check GitHub access

**Railway Issues:**
- Build fails: Check logs
- App crashes: Check environment variables
- Timeout: Increase scraper wait times

**Discord/Community:**
- Railway: https://discord.gg/railway
- GitHub: https://github.community

---

## 🚀 Ready to Deploy?

Follow these steps in order:

1. ✅ Create `milo-price-tracker` folder
2. ✅ Download all files
3. ✅ `git init` and commit
4. ✅ Create GitHub repo: `milo-price-tracker-sg`
5. ✅ Push to GitHub
6. ✅ Deploy to Railway
7. ✅ Get public URL
8. ✅ Test API
9. 🎉 You're live!

**Time estimate:** 15-20 minutes total

Good luck! 🥤
