# Attendance System - Login & Database Guide

## Quick Start

### 1. Login Credentials (Demo)

Use these credentials to test each role:

| Role | Email | Password |
|------|-------|----------|
| System Administrator | `admin@example.com` | `password` |
| Student Service Admin | `ssa@example.com` | `password` |
| Lecturer | `lecturer@example.com` | `password` |
| Student | `student@example.com` | `password` |

### 2. Start the System

```bash
# Navigate to project directory
cd "c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26"

# Start Flask server
python main.py
```

The server will start on: `http://localhost:5000`

### 3. Access the Login Page

Open your browser and go to: `http://localhost:5000/`

This will show the unified login page.

---

## How It Works

### Database Connection

The system uses **MySQL** for data storage. It will try to connect in this order:

1. **Railway** - `DATABASE_URL` environment variable (for deployment)
2. **AWS RDS** - `RDS_HOSTNAME`, `RDS_USERNAME`, etc. (for AWS deployment)
3. **Local MySQL** - Default connection to `127.0.0.1` (development)

#### Local Development Setup

If you don't have MySQL running, install it or use Docker:

```bash
# Docker - Start MySQL container
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=student_attendance mysql:8.0

# Or use local MySQL
# Make sure MySQL service is running
net start MySQL80  # Windows
```

### Database Schema

The system uses these main tables:

```
lecturers
├── id (primary key)
├── lecturer_id
├── email
├── password (bcrypt hashed)
├── first_name
└── last_name

student_service_admins
├── id (primary key)
├── admin_id
├── email
├── password (bcrypt hashed)
├── first_name
└── last_name

system_admins
├── id (primary key)
├── admin_id
├── email
├── password (bcrypt hashed)
├── first_name
└── last_name

students
├── id (primary key)
├── student_id
├── email
├── password (bcrypt hashed)
├── first_name
└── last_name

modules
├── id (primary key)
├── code
├── name
├── lecturer_id (foreign key)

attendance
├── id (primary key)
├── student_id (foreign key)
├── module_id (foreign key)
├── attendance_date
├── status ('Present', 'Absent', 'Late')

timetable
├── id (primary key)
├── module_id (foreign key)
├── day
├── start_time
├── end_time
├── room
```

---

## API Endpoints

All endpoints use the unified backend on port 5000.

### Authentication
- `POST /api/auth/login` - Login with email & password
- `POST /api/auth/logout` - Logout

### System Admin Endpoints
- `GET /api/policies` - Get all attendance policies
- `GET /api/devices/stats` - Get device statistics
- `GET /api/alerts` - Get system alerts
- `GET /api/users` - Get all users
- `POST /api/users` - Create new user

### Student Service Admin Endpoints
- `GET /api/ssa/modules` - Get all modules
- `GET /api/ssa/lecturers` - Get all lecturers
- `GET /api/ssa/students` - Get all students
- `GET /api/ssa/modules/<id>/students` - Get students in module
- `POST /api/ssa/modules/<id>/assign-lecturer` - Assign lecturer
- `POST /api/ssa/modules/<id>/enroll` - Enroll students
- `GET /api/ssa/timetable` - Get timetable
- `POST /api/ssa/timetable` - Create timetable entry
- `DELETE /api/ssa/timetable/<id>` - Delete timetable entry

### Lecturer Endpoints
- `GET /api/lecturer/classes` - Get lecturer's classes
- `GET /api/lecturer/attendance` - Get attendance records
- `GET /api/lecturer/reports` - Get attendance reports
- `GET /api/lecturer/notifications` - Get notifications
- `GET /api/lecturer/dashboard/stats` - Get dashboard statistics

### Common Endpoints
- `GET /api/attendance/classes` - Get classes for attendance
- `GET /api/attendance/daily-summary` - Get daily summary

---

## Accessing Different Dashboards

After login, you'll be redirected to your role-specific dashboard:

1. **System Admin Dashboard**
   - URL: `http://localhost:5000/System Administrator/boundary/dashboard.html`
   - Features: Manage policies, hardware, permissions, facial recognition

2. **Student Service Admin Dashboard**
   - URL: `http://localhost:5000/Student Service Administrator/boundary/dashboard.html`
   - Features: Manage students, modules, lecturers, timetables

3. **Lecturer Dashboard**
   - URL: `http://localhost:5000/Lecturer/boundary/dashboard.html`
   - Features: View classes, attendance records, reports, notifications

---

## Troubleshooting

### Issue: "Unable to connect to database"

**Solution**: Make sure MySQL is running
```bash
# Check if MySQL is running
mysql -u root

# If not running, start it
net start MySQL80  # Windows
brew services start mysql  # Mac
sudo systemctl start mysql  # Linux
```

### Issue: "Invalid email or password"

**Cause**: User doesn't exist in database or password is wrong

**Solution**: Use demo credentials:
- `admin@example.com` / `password`
- `ssa@example.com` / `password`
- `lecturer@example.com` / `password`

### Issue: "Database doesn't exist"

**Solution**: Create database from SQL files:
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < student_attendance < sql/additional_data.sql
```

### Issue: Dashboard shows no data

**Cause**: API endpoints can't connect to database

**Solution**:
1. Check Flask server logs
2. Verify database connection in `common/db_utils.py`
3. Check that tables exist: `SHOW TABLES;`

---

## Session Management

When you login, the system stores:

```javascript
// In sessionStorage
auth_user: {
  id: "user_id",
  email: "user@example.com",
  role: "lecturer",  // or "system-admin", "student-service-admin"
  first_name: "John",
  last_name: "Doe"
}
isAuthenticated: "true"
```

This is used by `auth.js` to:
- Check if user is logged in
- Verify user role permissions
- Redirect to login if not authenticated
- Display user name in headers

---

## Creating New Users

Use the System Admin dashboard or API:

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "userRole": "Lecturer",
    "email": "new.lecturer@example.com",
    "password": "password123",
    "name": "John Smith",
    "userID": "LEC001"
  }'
```

---

## Environment Variables

Create `.env` file in project root:

```env
# Local MySQL
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_attendance
DB_PORT=3306

# Or Railway
DATABASE_URL=mysql://user:password@host:3306/database

# Or AWS RDS
RDS_HOSTNAME=your-rds-endpoint.amazonaws.com
RDS_USERNAME=admin
RDS_PASSWORD=your_password
RDS_DB_NAME=student_attendance
RDS_PORT=3306
```

---

## Next Steps

1. ✅ Start the server: `python main.py`
2. ✅ Login with demo credentials
3. ✅ Explore each dashboard
4. ✅ Check API endpoints in Postman/curl
5. ✅ Set up your own database with real data

Happy testing! 🎉
