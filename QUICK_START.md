# 🚂 Railway Deployment - Quick Checklist

## ✅ Pre-Deployment Setup (5 minutes)

### 1. Download All Files
Download all files from Claude to your computer:
- ✅ All Python files (complete_backend.py, multi_platform_scraper.py, etc.)
- ✅ requirements.txt
- ✅ Procfile
- ✅ railway.json
- ✅ runtime.txt
- ✅ .gitignore

Put them all in one folder called `milo-tracker`

### 2. Create GitHub Repo (2 minutes)

```bash
# In your milo-tracker folder
git init
git add .
git commit -m "Initial commit"
```

Go to https://github.com/new
- Repository name: `milo-price-tracker`
- Public or Private: Your choice
- Don't add README, .gitignore (we have them)
- Click "Create repository"

Then:
```bash
# Replace YOUR-USERNAME
git remote add origin https://github.com/YOUR-USERNAME/milo-price-tracker.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Railway (2 minutes)

1. Go to https://railway.app
2. Click "Login with GitHub"
3. Click "New Project"
4. Choose "Deploy from GitHub repo"
5. Select `milo-price-tracker`
6. Wait 3-5 minutes for build
7. Done! 🎉

### 4. Get Your URL

1. Click on your project
2. Go to "Settings" → "Domains"
3. Click "Generate Domain"
4. Copy your URL (like: `milo-tracker-production.up.railway.app`)

### 5. Test Your API

```bash
# Replace with your URL
curl https://your-url.up.railway.app/api/status

# Should return:
{
  "status": "running",
  "cache_status": "active",
  ...
}
```

## 🎨 Update Frontend

In your `milo-tracker.html`, change:

```javascript
// OLD:
const API_URL = 'http://localhost:5000';

// NEW (use your Railway URL):
const API_URL = 'https://your-url.up.railway.app';
```

Deploy frontend to Vercel (optional):
1. Create new repo for frontend
2. Push milo-tracker.html
3. Connect to Vercel
4. Done!

## 💰 Cost Estimate

**Free tier:** $5 credit/month
- Enough for ~500 hours of uptime
- Perfect for personal use

**If you exceed:**
- ~$5-10/month for this project
- Set spending limit in Railway settings

## 🐛 If Something Goes Wrong

**Build fails:**
1. Check Railway logs
2. Look for error message
3. Common fixes:
   - Add missing package to requirements.txt
   - Check Python version in runtime.txt

**App crashes:**
1. Check logs for errors
2. Usually timeout issues with scraping
3. Increase timeouts in scrapers

**Can't access API:**
1. Check if domain is generated
2. Try triggering new deployment
3. Check CORS settings

## 📞 Get Help

**Railway:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**This Project:**
- Read RAILWAY_DEPLOY.md for detailed guide
- Check error logs first
- Test locally before pushing

## ✨ That's It!

You should now have:
- ✅ Code on GitHub
- ✅ App running on Railway
- ✅ Public API URL
- ✅ Auto-scraping every hour

Total time: ~10 minutes
Total cost: $0 (free tier)

Enjoy your Milo price tracker! 🥤
