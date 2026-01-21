# Test Suite Documentation

Comprehensive testing suite for the Student Attendance Management System. All tests are organized by role and functionality.

**System Status:** ✅ Production-Ready
- 19 active classes
- 20 enrolled students
- 689 attendance sessions
- 7,717 complete attendance records
- 87-96% attendance rates (realistic)

## 📁 Directory Structure

```
tests/
├── database/           # Database connection and data integrity tests
├── lecturer/           # Lecturer module tests (US12-19) ✓ Complete
├── student_service_admin/  # SSA module tests (US27-36) ✓ Complete
├── system_admin/       # System admin tests (US20-26) ✓ Complete
└── README.md          # This file
```

## ⚡ Quick Start

### Prerequisites Checklist

- [ ] MySQL server running
- [ ] Database created and imported
- [ ] `.env` file configured
- [ ] Python dependencies installed
- [ ] Required controllers running (for module tests)

### 1. Database Setup

```powershell
# Create database
mysql -u root -p
CREATE DATABASE student_attendance;
USE student_attendance;
source sql/schema.sql;
source sql/additional_data.sql;
exit;
```

### 2. Environment Configuration

Create `.env` file in project root:
```env
DB_HOST=localhost
DB_USER=app_user
DB_PASSWORD=your_password
DB_NAME=student_attendance
DB_PORT=3306
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
# OR
pip install requests flask flask-cors mysql-connector-python python-dotenv bcrypt
```

## Running Tests

### Database Tests
Test database connectivity and data integrity first:
```powershell
cd tests/database
python test_db_connection.py       # Basic connection test
python test_database_data.py       # Comprehensive data verification
python test_password_hash.py       # Password hash compatibility
```

### Lecturer Module Tests

**Step 1: Start Controllers** (in separate terminals)
```powershell
# Terminal 1 - Auth Controller
python Lecturer/controller/lecturer_auth_controller.py          # Port 5003

# Terminal 2 - Schedule Controller
python Lecturer/controller/lecturer_schedule_controller.py      # Port 5006

# Terminal 3 - Attendance Controller
python Lecturer/controller/lecturer_attendance_controller.py    # Port 5004

# Terminal 4 - Report Controller
python Lecturer/controller/lecturer_report_controller.py        # Port 5005

# Terminal 5 - Notification Controller
python Lecturer/controller/lecturer_notification_controller.py  # Port 5007
```

**Step 2: Run Tests**
```powershell
cd tests/lecturer

# Quick health check (all controllers)
python test_controllers_status.py

# Authentication tests
python test_lecturer_auth.py

# Comprehensive feature tests
python test_lecturer_features.py

# Quick login/logout test
python quick_test.py
```

## Test Files Reference

| Test File | Purpose | Prerequisites |
|-----------|---------|---------------|
| **Database Tests** | | |
| `test_db_connection.py` | Basic DB connectivity | MySQL running, `.env` configured |
| `test_database_data.py` | Full data verification | Database imported with `additional_data.sql` |
| `test_password_hash.py` | Bcrypt hash testing | Database with lecturer data |
| **Lecturer Tests** | | |
| `test_controllers_status.py` | Quick health check of all 5 controllers | All controllers running |
| `test_lecturer_auth.py` | Authentication & login tests | Auth controller (port 5003) |
| `test_lecturer_features.py` | Schedule, attendance, reports, notifications | All controllers running |
| `quick_test.py` | Fast login/logout check | Auth controller (port 5003) |
| **Student Service Admin Tests** | | |
| `quick_test.py` | Quick health check | SSA controller (port 5008) |
| `test_ssa_auth.py` | Authentication & password reset tests | SSA controller (port 5008) |
| `test_ssa_attendance.py` | Attendance management tests | SSA controller (port 5008) |
| `test_ssa_reports.py` | Reports & file upload tests | SSA controller (port 5008) |
| **System Admin Tests** | | |
| `quick_test.py` | Quick health check + 6 endpoints | System Admin controller (port 5009) |
| `test_sysadmin_auth.py` | Authentication tests | System Admin controller (port 5009) |
| `test_sysadmin_policies.py` | Policy management tests (US20, US21) | System Admin controller (port 5009) |
| `test_sysadmin_hardware.py` | Hardware monitoring tests (US22, US23) | System Admin controller (port 5009) |
| `test_sysadmin_users.py` | User & permissions tests (US24, US25, US26) | System Admin controller (port 5009) |

## Test Credentials

### Lecturer Accounts
- **LEC001**: john.smith@university.com / password
- **LEC002**: jane.doe@university.com / password
- **LEC003**: mike.johnson@university.com / password

### Student Service Admin Accounts
- **SSA001**: studentservice@attendance.com / password
- **SSA002**: registry@university.com / password

### System Admin Accounts
- **SYSADMIN001**: admin@attendance.com / password
- **SYSADMIN002**: sysadmin@university.com / password

## Expected Results

### Database Tests
- ✓ Connection successful
- ✓ 20 students found (STU2025001-020)
- ✓ 3 lecturers, 2 SSAs, 2 system admins
- ✓ 89+ attendance records
- ✓ Foreign key integrity verified

### Lecturer Tests
- ✓ All 5 controllers operational
- ✓ Login/logout functional
- ✓ Schedule displays Monday/Wednesday CS101 classes
- ✓ Attendance records retrieved (48 for CS101)
- ✓ Reports generated successfully
- ✓ Notifications displayed (3 for LEC001)

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
```
Error: Access denied for user 'root'@'localhost'
Solution: Create dedicated app_user account or update .env credentials
```

**2. Controller Not Running**
```
Error: Connection refused on port 5003
Solution: Run `.\start_all_controllers.ps1` to start all controllers
```

**3. Import Error: No module named 'requests'**
```
Solution: pip install requests
```

**4. Password Hash Error**
```
Error: password cannot be longer than 72 bytes
Solution: Already fixed in lecturer_auth_controller.py (bcrypt compatibility)
```

---

## 🗄️ Database Tests

Tests for connectivity, data integrity, and schema verification.

### Test Files

| File | Purpose | Runtime |
|------|---------|---------|
| `test_db_connection.py` | Basic connection test | ~5s |
| `test_database_data.py` | Comprehensive verification (18 tables) | ~10s |
| `test_password_hash.py` | Bcrypt compatibility test | ~3s |

### Running Database Tests

```powershell
cd tests/database
python test_db_connection.py       # Run first to verify connectivity
python test_database_data.py       # Full data verification
python test_password_hash.py       # Hash compatibility check
```

### Expected Results

**test_db_connection.py**:
```
✓ Database connection successful!
✓ Found 3 lecturers
✓ Found 20 students
✓ Found 3 classes
```

**test_database_data.py**:
```
✓ 18 tables verified
✓ 20 students (STU2025001-020)
✓ 89+ attendance records
✓ 0 orphaned records (FK integrity)
✓ All 21 checks passed
```

**test_password_hash.py**:
```
✓ PHP $2y$ hash compatibility verified
✓ Python $2b$ conversion working
```

---

## 👨‍🏫 Lecturer Module Tests

Tests for authentication, schedule, attendance tracking, reports, and notifications (US12-19).

### Test Files

| File | Purpose | Controllers Required | Runtime |
|------|---------|---------------------|---------|
| `test_controllers_status.py` | Quick health check | All 5 (5003-5007) | ~3s |
| `test_lecturer_auth.py` | Login/logout (US12, US19) | 5003 (auth) | ~15s |
| `test_lecturer_features.py` | All features (US14-18) | 5004-5007 | ~30s |
| `quick_test.py` | Fast login check | 5003 (auth) | ~5s |

### Starting Controllers

Open 5 separate PowerShell terminals:

```powershell
# Terminal 1 - Auth Controller (Port 5003)
python Lecturer/controller/lecturer_auth_controller.py

# Terminal 2 - Attendance Controller (Port 5004)
python Lecturer/controller/lecturer_attendance_controller.py

# Terminal 3 - Reports Controller (Port 5005)
python Lecturer/controller/lecturer_report_controller.py

# Terminal 4 - Schedule Controller (Port 5006)
python Lecturer/controller/lecturer_schedule_controller.py

# Terminal 5 - Notifications Controller (Port 5007)
python Lecturer/controller/lecturer_notification_controller.py
```

### Running Lecturer Tests

```powershell
cd tests/lecturer

# Step 1: Verify all controllers are running
python test_controllers_status.py

# Step 2: Test authentication
python test_lecturer_auth.py

# Step 3: Test all features
python test_lecturer_features.py

# Quick check
python quick_test.py
```

### Expected Results

**test_controllers_status.py**:
```
✓ Auth Controller (5003): WORKING
✓ Schedule Controller (5006): WORKING
✓ Attendance Controller (5004): WORKING
✓ Report Controller (5005): WORKING
✓ Notification Controller (5007): WORKING
RESULT: 5/5 controllers (100%)
```

**test_lecturer_auth.py**:
```
✓ Lecturer Login (US12)
✓ Invalid Login Attempts (4/4)
✓ Database Verification
✓ Lecturer Logout (US19)
Total: 4/4 tests passed
```

**test_lecturer_features.py**:
```
✓ Schedule (US16) - 2 entries
✓ Attendance (US14, US18) - 48 records
✓ Reports (US15) - 2 reports
✓ Notifications (US17) - 3 notifications
Total: 8/8 tests passed
```

### User Story Coverage

| US | Feature | Status |
|----|---------|--------|
| US12 | Lecturer Login | ✓ Tested |
| US13 | Password Reset | ✓ Tested |
| US14 | Real-Time Attendance | ✓ Tested |
| US15 | Attendance Reports | ✓ Tested |
| US16 | Class Schedule | ✓ Tested |
| US17 | Notifications | ✓ Tested |
| US18 | Filter Records | ✓ Tested |
| US19 | Logout | ✓ Tested |

---

## 📋 Student Service Admin Tests

Tests for attendance management, audit logging, compliance reports, and file uploads (US27-36).

### Test Files

| File | Purpose | Controller Required | Runtime |
|------|---------|---------------------|---------|
| `quick_test.py` | Quick health check | 5008 (SSA main) | ~3s |
| `test_ssa_auth.py` | Login/logout (US27, US28, US30) | 5008 (SSA main) | ~10s |
| `test_ssa_attendance.py` | Attendance & audit (US29, US31, US33, US34) | 5008 (SSA main) | ~15s |
| `test_ssa_reports.py` | Reports & uploads (US32, US35, US36) | 5008 (SSA main) | ~15s |

### Starting Controller

**Recommended: Use the startup script**

```powershell
.\start_all_controllers.ps1
```

**Alternative: Manual start**

```powershell
# Start SSA unified controller (Port 5008)
cd 'Student Service Administrator\controller'
python ssa_main.py
```

### Running SSA Tests

```powershell
cd tests/student_service_admin

# Step 1: Verify controller is running
python quick_test.py

# Step 2: Test authentication
python test_ssa_auth.py

# Step 3: Test attendance management
python test_ssa_attendance.py

# Step 4: Test reports & uploads
python test_ssa_reports.py
```

### Expected Results

**quick_test.py**:
```
✓ SSA Controller (5008): WORKING
✓ All 6 endpoints accessible
```

**test_ssa_auth.py**:
```
✓ SSA Login (US27)
✓ Invalid Login Attempts (4/4)
✓ Password Reset (US30)
✓ Change Password (US30)
✓ SSA Logout (US28)
Total: 5/5 tests passed
```

**test_ssa_attendance.py**:
```
✓ Daily Summary (US34) - 87.5% attendance rate
✓ Get Students (US31) - 25 students retrieved
✓ Mark Attendance (US31) - 5 records saved
✓ Adjust Attendance (US33) - Record adjusted
✓ Search Attendance - Record found
✓ Audit Log (US29) - 2 entries logged
Total: 6/6 tests passed
```

**test_ssa_reports.py**:
```
✓ Compliance Report (US32) - 3 students below threshold
✓ Student History (US36) - Full history retrieved
✓ Upload Class List (US35) - 35 students uploaded
✓ Upload Photos (US35) - 3 photos uploaded
Total: 4/4 tests passed
```

### User Story Coverage

| US | Feature | Status |
|----|---------|--------|
| US27 | SSA Login | ✓ Tested |
| US28 | SSA Logout | ✓ Tested |
| US29 | Audit Log | ✓ Tested |
| US30 | Password Reset | ✓ Tested |
| US31 | Mark Attendance | ✓ Tested |
| US32 | Compliance Report | ✓ Tested |
| US33 | Adjust Attendance | ✓ Tested |
| US34 | Daily Summary | ✓ Tested |
| US35 | Upload Class List/Photos | ✓ Tested |
| US36 | Student History | ✓ Tested |

---

## 🔧 System Administrator Tests

Tests for policy management, hardware monitoring, user management, and permissions (US20-26).

### Test Files

| File | Purpose | Controller Required | Runtime |
|------|---------|---------------------|---------|
| `quick_test.py` | Quick health check | 5009 (System Admin main) | ~3s |
| `test_sysadmin_auth.py` | Login/logout | 5009 (System Admin main) | ~5s |
| `test_sysadmin_policies.py` | Policy CRUD (US20, US21) | 5009 (System Admin main) | ~10s |
| `test_sysadmin_hardware.py` | Hardware monitoring (US22, US23) | 5009 (System Admin main) | ~10s |
| `test_sysadmin_users.py` | Users & permissions (US24, US25, US26) | 5009 (System Admin main) | ~15s |

### Starting Controller

**Recommended: Use the startup script**

```powershell
.\start_all_controllers.ps1
```

**Alternative: Manual start**

```powershell
# Start System Admin unified controller (Port 5009)
cd 'System Administrator\controller'
python sysadmin_main.py
```

### Running System Admin Tests

```powershell
cd tests/system_admin

# Step 1: Verify controller is running
python quick_test.py

# Step 2: Test authentication
python test_sysadmin_auth.py

# Step 3: Test policy management
python test_sysadmin_policies.py

# Step 4: Test hardware monitoring
python test_sysadmin_hardware.py

# Step 5: Test user & permissions management
python test_sysadmin_users.py
```

### Expected Results

**quick_test.py**:
```
✓ System Admin Controller (5009): WORKING
✓ All 6 endpoints accessible
```

**test_sysadmin_auth.py**:
```
✓ System Admin Login
✓ Invalid Login Attempts (4/4)
✓ System Admin Logout
Total: 3/3 tests passed
```

**test_sysadmin_policies.py**:
```
✓ Get Policies (US20) - 2 policies retrieved
✓ Create Policy (US20) - New policy created
✓ Update Policy (US21) - Policy updated
✓ Delete Policy (US21) - Policy deleted
Total: 4/4 tests passed
```

**test_sysadmin_hardware.py**:
```
✓ Get Devices (US22) - 6 devices retrieved
✓ Device Statistics (US22) - Stats retrieved
✓ Update Device (US23) - Device updated
✓ Update Non-existent Device (US23) - Correctly rejected
Total: 4/4 tests passed
```

**test_sysadmin_users.py**:
```
✓ Get Users (US24) - 4 users retrieved
✓ Create User (US24) - New user created
✓ Update User (US24) - User updated
✓ Deactivate User (US25) - User deactivated
✓ Get Permissions (US26) - 3 roles retrieved
✓ Update Permissions (US26) - Permissions updated
Total: 6/6 tests passed
```

### User Story Coverage

| US | Feature | Status |
|----|---------|--------|
| US20 | View/Create Attendance Policies | ✓ Tested |
| US21 | Update/Delete Attendance Policies | ✓ Tested |
| US22 | Monitor Hardware Devices | ✓ Tested |
| US23 | Update Device Status | ✓ Tested |
| US24 | Create/Update/View Users | ✓ Tested |
| US25 | Deactivate User Accounts | ✓ Tested |
| US26 | Manage Role Permissions | ✓ Tested |

---

## 📊 Test Credentials

### Lecturer Accounts
```
LEC001: john.smith@university.com / password
LEC002: jane.doe@university.com / password
LEC003: mike.johnson@university.com / password
```

### Student Service Admin Accounts
```
SSA001: studentservice@attendance.com / password
SSA002: registry@university.com / password
```

### System Admin Accounts
```
SYSADMIN001: admin@attendance.com / password
SYSADMIN002: sysadmin@university.com / password
```

---

## 🔧 Troubleshooting

### Database Connection Failed
```
Error: Access denied for user 'root'@'localhost'
```
**Solution**: 
1. Create dedicated app_user account:
   ```sql
   CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON student_attendance.* TO 'app_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
2. Update `.env` with app_user credentials

### Controller Not Running
```
Error: Connection refused on port 5003
```
**Solution**: Ensure all controllers are running
```powershell
.\start_all_controllers.ps1
```

### Import Error
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Install missing dependencies
```powershell
pip install requests
```

### Password Hash Error
```
ValueError: password cannot be longer than 72 bytes
```
**Solution**: Already fixed in `lecturer_auth_controller.py` (bcrypt compatibility)

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Kill existing process
```powershell
Get-Process python | Where-Object {$_.MainWindowTitle -like "*lecturer*"} | Stop-Process
```

---

## 📝 Contributing Tests

When adding new test files:

1. **Organize by role**:
   - `tests/database/` - Infrastructure tests
   - `tests/lecturer/` - Lecturer features
   - `tests/student_service_admin/` - SSA features
   - `tests/system_admin/` - System admin features

2. **Naming convention**: `test_<feature>_<aspect>.py`
   - Good: `test_lecturer_auth.py`, `test_ssa_attendance.py`
   - Avoid: `test1.py`, `lecturer_test.py`

3. **Include header docstring**:
   ```python
   """
   Test script for [Feature Name]
   Tests: [what it tests]
   User Stories: [US numbers]
   """
   ```

4. **Update this README** with new test coverage

---

## 🚀 CI/CD Integration (Future)

Tests are designed for automated pipeline integration:
- GitHub Actions workflows
- Pre-commit hooks
- Continuous integration checks
- Coverage reporting

---

## 📈 Test Status

| Module | Tests | Status | Updated |
|--------|-------|--------|---------|
| Database | 3/3 | ✓ Complete | Dec 5, 2025 |
| Lecturer | 4/4 | ✓ Complete | Dec 5, 2025 |
| Student Service Admin | 4/4 | ✓ Complete | Dec 5, 2025 |
| System Admin | 5/5 | ✓ Complete | Dec 5, 2025 |

**Overall Coverage**: 
- Lecturer module: 8 user stories (US12-19) - 100% tested ✓
- SSA module: 10 user stories (US27-36) - 100% tested ✓
- System Admin module: 7 user stories (US20-26) - 100% tested ✓

---

**Last Updated**: December 5, 2025  
**Maintained by**: FYP Team 15
