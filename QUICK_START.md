# QUICK START - 30 Seconds

## 1. Server Running ✅
The Flask server is **already running** on `http://localhost:5000`

## 2. Open Login
```
http://localhost:5000/
```

## 3. Pick Your Role & Login

**System Admin:**
- Email: `admin@example.com`
- Password: `password`

**Student Service Admin:**
- Email: `ssa@example.com`
- Password: `password`

**Lecturer:**
- Email: `lecturer@example.com`
- Password: `password`

---

## What Happens Next

1. You enter credentials → Click "Sign In"
2. System validates against database
3. You're redirected to your dashboard
4. Dashboard loads your data from the API

---

## How It Works (Behind the Scenes)

```
Browser (Login Page)
        ↓
[POST /api/auth/login]
        ↓
Flask Backend (main.py)
        ↓
[Query MySQL Database]
        ↓
[Return User Data + Role]
        ↓
Browser Sets sessionStorage
        ↓
Redirect to Dashboard
        ↓
Dashboard fetches data via API
[GET /api/lecturer/dashboard/stats]
[GET /api/ssa/modules]
[GET /api/attendance/classes]
        ↓
Display Data in Dashboard
```

---

## All Endpoints in ONE Place

Everything runs on **localhost:5000**

No more port 5004, 5005, 5006, 5007!

---

## If Server Stops

Restart it:
```bash
cd "c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26"
python main.py
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| "Unable to connect" | Make sure MySQL is running: `net start MySQL80` |
| "Invalid email/password" | Check database has users: `SELECT * FROM lecturers;` |
| "No data in dashboard" | Check API endpoints: `GET http://localhost:5000/api/ssa/modules` |
| "Scripts not loading" | Clear browser cache or use Ctrl+Shift+Delete |

---

**Now go to:** `http://localhost:5000/`

**Login and enjoy! 🎉**
