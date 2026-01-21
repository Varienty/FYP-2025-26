# 🚀 Railway.app Quick Start (5 Minutes)

## Overview
Your code is ready for Railway! Follow these 5 simple steps to go live.

## What's Changed
✅ `main.py` - Production Flask app (Procfile-ready)
✅ `Procfile` - Tells Railway how to run your app
✅ `requirements.txt` - Added gunicorn for production
✅ `.env.example` - Environment variable template
✅ `common/db_utils.py` - Auto-connects to Railway MySQL

## 5-Minute Deploy

### 1. GitHub (2 min)
```powershell
# In your project folder
git init
git add .
git commit -m "Deploy to Railway"
git remote add origin https://github.com/YOUR_USERNAME/FYP-2025-26.git
git branch -M main
git push -u origin main
```

### 2. Railway Account (1 min)
- Go to [railway.app](https://railway.app)
- Click "Login with GitHub"
- Authorize Railway

### 3. Create Project (1 min)
- Click "Create New Project"
- Select "Deploy from GitHub repo"
- Choose `FYP-2025-26`
- Railway detects `Procfile` automatically ✓

### 4. Add MySQL (1 min)
- Click "Add" → "MySQL"
- Railway auto-creates database
- Sets `DATABASE_URL` environment variable ✓

### 5. Deploy & Get URL (0 min)
- Railway deploys automatically
- Go to "Settings" → "Domains"
- Copy your live URL!

## Your Live URL
```
https://yourapp-production.up.railway.app
```

## Load Database (One-time)
```bash
# Get MySQL details from Railway dashboard
# Click MySQL plugin → Connect tab
mysql -h HOST -u USER -p PASSWORD -D student_attendance < sql/schema.sql
```

## Test It
```
https://yourapp-production.up.railway.app/health
→ Should see: {"status": "ok", ...}
```

## That's It! 🎉
Your app is now live and accessible from anywhere!

For detailed guide: See [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)
