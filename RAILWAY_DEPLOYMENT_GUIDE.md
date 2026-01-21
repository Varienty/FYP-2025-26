# Railway.app Deployment Guide

Student Attendance Management System on Railway.app

## Prerequisites

- GitHub account (for code hosting)
- Railway account (free at [railway.app](https://railway.app))
- MySQL database on Railway (free tier available)

## Step-by-Step Deployment

### Step 1: Prepare Your Code

Your code is already configured! The following files have been created:

✅ **Procfile** - Tells Railway how to run your Flask app
✅ **main.py** - Production-ready Flask entry point
✅ **.env.example** - Environment variable template
✅ **common/db_utils.py** - Handles Railway's DATABASE_URL automatically

### Step 2: Push Code to GitHub

1. Open terminal in your project directory
2. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Attendance system for Railway deployment"
   ```

3. Create a new repository on GitHub and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/FYP-2025-26.git
   git push -u origin main
   ```

### Step 3: Create Railway Account & Login

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "GitHub" (authenticate with your GitHub account)
3. Click "Create Project" → "Deploy from GitHub repo"

### Step 4: Create MySQL Database on Railway

1. In Railway dashboard, click "Create" button
2. Select "MySQL" (not PostgreSQL)
3. Railway will generate a `DATABASE_URL` environment variable automatically

### Step 5: Add Flask Application

1. Click "Create" → "Deploy from GitHub repo"
2. Select your `FYP-2025-26` repository
3. Railway auto-detects the Procfile and knows how to run your app

### Step 6: Configure Environment Variables

1. Go to "Variables" tab in Railway dashboard
2. Verify `DATABASE_URL` is already set (from MySQL step)
3. Add optional:
   ```
   FLASK_ENV=production
   PYTHON_VERSION=3.11
   ```

### Step 7: Deploy

1. Railway auto-deploys when you:
   - Push code to GitHub, OR
   - Use CLI: `railway up`
   
2. Watch deployment logs in Railway dashboard:
   - Should see "pip install -r requirements.txt"
   - Then "gunicorn main:app" starting
   - Look for "Running on http://0.0.0.0:5000"

### Step 8: Load Database Schema

1. Get MySQL connection details from Railway MySQL plugin:
   - Host, Port, Username, Password, Database name

2. Connect with your MySQL client:
   ```bash
   mysql -h <host> -u <user> -p <password> -D student_attendance < sql/schema.sql
   ```

3. Or use Railway's web terminal:
   - Click MySQL plugin → "Connect"
   - Paste contents of `sql/schema.sql`

### Step 9: Get Your Live URL

1. In Railway dashboard, go to "Settings" → "Domains"
2. Copy the public URL (e.g., `https://yourapp-production.up.railway.app`)
3. This is your live website URL!

### Step 10: Test Your Deployment

1. Open live URL in browser → should see:
   ```json
   {
     "message": "Student Attendance Management System",
     "version": "1.0.0",
     "status": "running"
   }
   ```

2. Test health endpoint: `https://yourapp-production.up.railway.app/health`
3. Test API endpoints: Configure `config.js` with your live URL if needed

## Connecting Your Frontend

Your HTML files (in `Lecturer/boundary/`, `Student Service Administrator/boundary/`, etc.) use `config.js` to auto-detect the API base URL.

For local development:
```javascript
// config.js - auto-detects
getApiBase() // returns http://localhost:5000
```

On Railway:
```javascript
// config.js - auto-detects
getApiBase() // returns https://yourapp-production.up.railway.app
```

**No changes needed!** The `config.js` automatically uses the current domain.

## Database Connection Flow

```
Local Dev:
  main.py → db_utils.py → localhost:3306 (your local MySQL)

Railway:
  main.py → db_utils.py → DATABASE_URL (Railway MySQL) ✓ Automatic
```

The `db_utils.py` prioritizes:
1. `DATABASE_URL` environment variable (Railway's automatic setting)
2. `RDS_*` environment variables (if using AWS RDS)
3. Local defaults (localhost:3306)

## Troubleshooting

### Build Failed
- Check Railway logs: "Deployment" → "Build" log
- Common issues:
  - Missing `requirements.txt` dependencies
  - Python version mismatch
  - Invalid `Procfile` syntax

### Can't Connect to Database
- Verify `DATABASE_URL` is set in Railway dashboard
- Check MySQL plugin is provisioned
- Confirm `sql/schema.sql` has been loaded

### 502 Bad Gateway Error
- Flask app crashed on startup
- Check Railway logs for error messages
- Common causes:
  - Database connection failed
  - Import errors in Python files
  - Missing dependencies in `requirements.txt`

### Slow Loading / Timeouts
- Cold start on free tier (~30 seconds first request)
- Check Railway CPU/Memory usage in dashboard
- Upgrade plan if needed (minimal cost)

## Updating Your App

Simply push new code to GitHub:
```bash
git add .
git commit -m "Fix: Updated attendance logic"
git push origin main
```

Railway auto-deploys within 1-2 minutes!

## Next Steps

1. ✅ Push code to GitHub (Step 2)
2. ✅ Create Railway account (Step 3)
3. ✅ Create MySQL database (Step 4)
4. ✅ Deploy Flask app (Step 5-7)
5. ✅ Load database schema (Step 8)
6. ✅ Get live URL (Step 9)
7. ✅ Test deployment (Step 10)

## Support

- Railway docs: https://docs.railway.app
- Flask docs: https://flask.palletsprojects.com
- GitHub docs: https://docs.github.com

---

**Need help?**
- Check Railway dashboard logs
- Review this guide's troubleshooting section
- Reference `DEPLOYMENT_INSTRUCTIONS.md` for alternative options
