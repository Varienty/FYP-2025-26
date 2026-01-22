# AWS Deployment Guide

**Complete guide for deploying the FYP Attendance System to AWS Elastic Beanstalk**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Users (Browser/Frontend)            │
└──────────────────┬──────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────┐
│  AWS Elastic Beanstalk (Python 3.11)        │
│  - Unified Flask Backend (main.py)          │
│  - Port: 5000 (internal via Gunicorn)       │
│  - Instance: t2.micro (Free Tier)           │
│  - Region: ap-southeast-1 (Singapore)       │
└──────────────────┬──────────────────────────┘
                   │ Internal VPC
                   ▼
┌─────────────────────────────────────────────┐
│   AWS RDS MySQL 8.0                         │
│   - Database: studentattendance             │
│   - Port: 3306 (internal)                   │
│   - Credentials: admin / iamtrying          │
└─────────────────────────────────────────────┘
```

---

## 📋 Current Deployment Status

| Component | Status | Details |
|-----------|--------|---------|
| **Environment** | ✅ Ready | fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com |
| **Health** | ✅ Green | All instances healthy |
| **Platform** | ✅ Active | Python 3.11 on Amazon Linux 2023 |
| **Database** | ✅ Connected | RDS MySQL with 750+ records |
| **Authentication** | ✅ Working | All 4 roles tested and verified |

**Live URL:** http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com

---

## 🚀 Quick Deploy

### Deploy Code Changes
```powershell
# 1. Commit your changes
git add .
git commit -m "Description of changes"

# 2. Deploy to Elastic Beanstalk
eb deploy

# 3. Monitor deployment
eb logs --stream
```

### Check Status
```powershell
eb status              # Environment status
eb health              # Health monitoring
eb logs                # View recent logs
```

---

## 🔧 Configuration Files

### Required Files
- **`Procfile`** - Defines how to start the application
  ```
  web: gunicorn --bind :5000 --workers 3 --timeout 120 wsgi:application
  ```

- **`wsgi.py`** - WSGI entry point
  ```python
  from main import app as application
  ```

- **`requirements.txt`** - Python dependencies
  ```
  Flask==3.0.0
  Flask-Cors==4.0.0
  gunicorn==21.2.0
  mysql-connector-python==8.2.0
  python-dotenv==1.0.0
  bcrypt==4.1.1
  PyJWT==2.8.0
  ```

- **`.ebextensions/01_flask.config`** - EB configuration
  ```yaml
  option_settings:
    aws:elasticbeanstalk:application:environment:
      PYTHONPATH: "/var/app/current:$PYTHONPATH"
    aws:elasticbeanstalk:container:python:
      WSGIPath: wsgi:application
  ```

---

## 🗄️ Database Configuration

### Environment Variables

Set these in Elastic Beanstalk Console → Configuration → Software:

```env
# RDS Database (Required)
RDS_HOSTNAME=studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com
RDS_PORT=3306
RDS_DB_NAME=studentattendance
RDS_USERNAME=admin
RDS_PASSWORD=iamtrying

# Application Settings
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DOMAIN_NAME=fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com
```

### Database Connection

The app automatically uses RDS environment variables:
- `common/db_utils.py` handles both RDS and local MySQL
- Connection pooling for performance
- Automatic fallback to localhost for development

---

## 🔑 Demo Credentials

**Password for all accounts:** `password`

### System Administrator
- Email: `admin@attendance.com`

### Student Service Administrator
- Email: `studentservice@attendance.com`
- Email: `registry@university.com`

### Lecturer
- Email: `john.smith@university.com`
- Email: `jane.doe@university.com`
- Email: `mike.johnson@university.com`

### Student
- Email: `alice.wong@student.edu`
- Email: `bob.tan@student.edu`
- Email: `charlie.lee@student.edu`

**📄 Full credentials list:** [DEMO_CREDENTIALS.md](DEMO_CREDENTIALS.md)

---

## 📊 Data Summary

### Imported Records
- **Students:** 20
- **Lecturers:** 3
- **System Admins:** 2
- **Student Service Admins:** 2
- **Classes:** 5
- **Attendance Records:** 717
- **Total Records:** 750+ across 14 tables

---

## 🧪 Testing & Verification

### Test All Roles (PowerShell)
```powershell
# System health check
Invoke-WebRequest "http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/health/db"

# Test login
$headers = @{"Content-Type"="application/json"}
$body = '{"email":"admin@attendance.com","password":"password"}'
Invoke-WebRequest -Uri "http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/api/auth/login" -Method POST -Headers $headers -Body $body -UseBasicParsing
```

### Expected Results
- ✅ Health endpoint returns: `{"db":"ok"}`
- ✅ Login returns: `{"success":true,"user":{...},"token":"..."}`
- ✅ All 9 test accounts login successfully

---

## 🔍 Troubleshooting

### Check Logs
```powershell
eb logs                    # Recent logs
eb logs --stream           # Live log streaming
eb ssh                     # SSH into instance
```

### Common Issues

**Issue:** 502 Bad Gateway
- **Cause:** Application crashed or not starting
- **Fix:** Check logs with `eb logs`, verify Procfile and wsgi.py

**Issue:** Database connection failed
- **Cause:** Wrong RDS credentials or security group
- **Fix:** Verify environment variables, check RDS security group allows EB

**Issue:** Import errors
- **Cause:** Missing dependencies
- **Fix:** Update requirements.txt and redeploy

---

## 📝 Maintenance

### Update Database
```powershell
# Create SQL script
echo "UPDATE students SET email='new@email.com' WHERE id=1;" > update.sql

# Run on RDS (from allowed IP)
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -piamtrying studentattendance < update.sql
```

### Scale Application
```powershell
# Scale instances
eb scale 2                 # Set to 2 instances

# Change instance type
eb config                  # Edit configuration file
```

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain
1. Register domain (Route 53 or external)
2. Create CNAME record pointing to EB CNAME
3. Update `DOMAIN_NAME` environment variable
4. Enable SSL via AWS Certificate Manager

---

## 📚 Additional Resources

- **[DEMO_CREDENTIALS.md](DEMO_CREDENTIALS.md)** - Complete credentials reference
- **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)** - Current deployment status
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Local development setup
- **[README.md](README.md)** - Project overview

---

## 🎯 Key Commands Reference

| Action | Command |
|--------|---------|
| Deploy | `eb deploy` |
| Check status | `eb status` |
| View logs | `eb logs` |
| Stream logs | `eb logs --stream` |
| SSH to instance | `eb ssh` |
| Check health | `eb health` |
| Terminate environment | `eb terminate` |
| Restart application | `eb restart` |

---

*Last Updated: January 22, 2026*
*Status: Production Ready ✅*
