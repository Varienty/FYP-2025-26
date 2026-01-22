# System Status & Quick Reference

## ✅ System is READY

### Server Status
- **Flask Backend**: Running on `http://localhost:5000`
- **Database**: MySQL (connection configured)
- **Unified Backend**: All 3 roles on same port (5000)

---

## 🔐 LOGIN INSTRUCTIONS

### Step 1: Open Browser
```
http://localhost:5000/
```

### Step 2: Enter Credentials

Choose your role and login:

#### System Administrator
```
Email: admin@example.com
Password: password
```
**Access**: Hardware monitoring, policies, facial recognition, permissions

#### Student Service Administrator  
```
Email: ssa@example.com
Password: password
```
**Access**: Module management, student enrollment, timetable, daily reports

#### Lecturer
```
Email: lecturer@example.com
Password: password
```
**Access**: Attendance records, class schedule, reports, notifications

---

## 🎯 What Each Dashboard Does

### System Admin Dashboard
```
Features:
✓ View attendance policies
✓ Monitor hardware/devices
✓ Configure facial recognition
✓ Manage user permissions
✓ System alerts & monitoring
```
**URL**: `http://localhost:5000/System Administrator/boundary/dashboard.html`

---

### Student Service Admin Dashboard
```
Features:
✓ Manage modules/courses
✓ View/assign lecturers
✓ Enroll students
✓ Create timetables
✓ View daily attendance summary
✓ Upload class lists
✓ Compliance reports
```
**URL**: `http://localhost:5000/Student Service Administrator/boundary/dashboard.html`

---

### Lecturer Dashboard
```
Features:
✓ View assigned classes
✓ Start/end attendance sessions
✓ View real-time attendance
✓ Check attendance records
✓ Generate reports
✓ Receive notifications
✓ View class schedule
```
**URL**: `http://localhost:5000/Lecturer/boundary/dashboard.html`

---

## 📊 Key API Endpoints (for testing)

### Test with Postman or curl:

**Login**
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "lecturer@example.com",
  "password": "password"
}
```

**Get Modules** (SSA)
```
GET http://localhost:5000/api/ssa/modules
```

**Get Lecturers** (SSA)
```
GET http://localhost:5000/api/ssa/lecturers
```

**Get Attendance Records** (Lecturer)
```
GET http://localhost:5000/api/lecturer/attendance
```

**Get Dashboard Stats** (Lecturer)
```
GET http://localhost:5000/api/lecturer/dashboard/stats
```

---

## 🗄️ Database Tables

### User Tables
- `lecturers` - Lecturer accounts
- `student_service_admins` - SSA accounts  
- `system_admins` - Admin accounts
- `students` - Student accounts

### Academic Data
- `modules` - Courses/Classes
- `timetable` - Class schedule
- `module_enrollments` - Student enrollments

### Attendance Data
- `attendance` - Attendance records
- `attendance_policies` - System policies

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process using port 5000
taskkill /PID <PID> /F
```

### Database connection failed
```bash
# Start MySQL
net start MySQL80

# Test connection
mysql -u root -p
```

### Login shows "Invalid email or password"
- Database might not have the demo users
- Check MySQL is running
- Verify user exists: `SELECT * FROM lecturers WHERE email='lecturer@example.com';`

### Dashboard shows no data
- API endpoints need database to have data
- Check database tables are not empty
- Review Flask server logs for SQL errors

---

## 📝 File Structure

```
project/
├── main.py (Flask backend - port 5000)
├── common/
│   ├── config.js (API configuration)
│   ├── auth.js (Authentication)
│   ├── login.html (Login page)
│   └── db_utils.py (Database utilities)
├── Lecturer/boundary/ (Lecturer dashboards)
├── Student Service Administrator/boundary/ (SSA dashboards)
├── System Administrator/boundary/ (Admin dashboards)
└── LOGIN_AND_DATABASE_GUIDE.md (Detailed guide)
```

---

## ✨ What's Fixed

✅ Fixed all script paths from `/static/` to `../../common/`
✅ Unified backend on single port (5000)
✅ Fixed login.html script loading
✅ Added API endpoints for dashboard data
✅ Fixed lecturer dashboard to use unified backend
✅ Added missing notification endpoints
✅ All 3 roles use same authentication

---

## 🚀 Next Steps

1. **Start Server** (if not already running):
   ```bash
   python main.py
   ```

2. **Open Login Page**:
   ```
   http://localhost:5000/
   ```

3. **Test Login** with demo credentials

4. **Explore Dashboard** for your role

5. **Test API Endpoints** with Postman

---

**Need Help?** Check `LOGIN_AND_DATABASE_GUIDE.md` for detailed troubleshooting
