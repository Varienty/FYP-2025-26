# 🔑 Demo Credentials Reference

**Quick reference guide for all test accounts in the FYP Attendance System**

---

## Password for All Accounts
**`password`** (all lowercase)

---

## 👤 System Administrator

### Account 1 (Primary)
- **Email:** `admin@attendance.com`
- **User ID:** SYSADMIN001
- **Name:** System Administrator
- **Role:** sysadmin
- **Access:** Full system administration

### Use for:
- System configuration
- User management
- Hardware monitoring
- Policy configuration
- Permission management

---

## 📝 Student Service Administrator (SSA)

### Account 1
- **Email:** `studentservice@attendance.com`
- **User ID:** SSA001
- **Name:** Student Service Administrator
- **Department:** Student Affairs
- **Role:** ssa

### Account 2
- **Email:** `registry@university.com`
- **User ID:** SSA002
- **Name:** Registry Officer
- **Department:** Registrar Office
- **Role:** ssa

### Use for:
- Manual attendance marking
- Student record management
- Compliance reports
- Audit log viewing
- Class list uploads
- Daily summaries

---

## 👨‍🏫 Lecturer

### Account 1
- **Email:** `john.smith@university.com`
- **User ID:** LEC001
- **Name:** John Smith
- **Department:** Computer Science
- **Role:** lecturer

### Account 2
- **Email:** `jane.doe@university.com`
- **User ID:** LEC002
- **Name:** Jane Doe
- **Department:** Computer Science
- **Role:** lecturer

### Account 3
- **Email:** `mike.johnson@university.com`
- **User ID:** LEC003
- **Name:** Mike Johnson
- **Department:** Computer Science
- **Role:** lecturer

### Use for:
- Real-time attendance tracking
- Class schedule viewing
- Attendance report generation
- Notification management
- Facial recognition attendance

---

## 🎓 Student

### Account 1
- **Email:** `alice.wong@student.edu`
- **User ID:** STU2025001
- **Name:** Alice Wong
- **Program:** Computer Science
- **Level:** Degree
- **Intake:** April 2025
- **Role:** student

### Account 2
- **Email:** `bob.tan@student.edu`
- **User ID:** STU2025002
- **Name:** Bob Tan
- **Program:** Computer Science
- **Level:** Degree
- **Intake:** April 2025
- **Role:** student

### Account 3
- **Email:** `charlie.lee@student.edu`
- **User ID:** STU2024003
- **Name:** Charlie Lee
- **Program:** Information Technology
- **Level:** Diploma
- **Intake:** July 2024
- **Role:** student

### Account 4
- **Email:** `diana.kumar@student.edu`
- **User ID:** STU2024004
- **Name:** Diana Kumar
- **Program:** Software Engineering
- **Level:** Degree
- **Intake:** July 2024
- **Role:** student

### Use for:
- Viewing personal attendance records
- Checking attendance reports
- Viewing class schedules
- Submitting medical certificates

---

## 🌐 Access URLs

### Production (AWS Elastic Beanstalk)
```
http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com
```

### Local Development
```
http://localhost:5000
```
*(Or the port specified by your Flask app)*

---

## 📝 Quick Test Commands

### Test All Role Logins (PowerShell)
```powershell
.\test_correct_credentials.ps1
```

### Expected Result
```
✓ SUCCESS  System Admin
✓ SUCCESS  Student #1
✓ SUCCESS  Student #2
✓ SUCCESS  Student #3
✓ SUCCESS  Lecturer #1
✓ SUCCESS  Lecturer #2
✓ SUCCESS  Lecturer #3
✓ SUCCESS  SSA #1
✓ SUCCESS  SSA #2

Result: 9 / 9 credentials working
```

---

## 🔒 Security Notes

- ⚠️ These are **demo/test credentials only**
- 🚫 **Never use in production**
- 🔐 All passwords are bcrypt hashed in database
- 🎯 Hash: `$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi`
- 📊 This hash decodes to: `password`

---

## 📚 Additional Resources

- **Main README:** [README.md](README.md)
- **Getting Started:** [GETTING_STARTED.md](GETTING_STARTED.md)
- **Deployment Status:** [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)
- **Lecturer Module:** [Lecturer/README.md](Lecturer/README.md)
- **SSA Module:** [Student Service Administrator/README.md](Student Service Administrator/README.md)
- **System Admin Module:** [System Administrator/README.md](System Administrator/README.md)

---

*Last Updated: January 22, 2026*
*Status: All credentials verified and tested ✅*
