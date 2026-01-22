# AWS Elastic Beanstalk Deployment Checklist

## Overview
This project uses **AWS Elastic Beanstalk** for backend hosting and **AWS RDS MySQL** for the database. The application is a unified Flask backend serving all roles (System Admin, SSA, Lecturer, Student).

---

## Architecture
```
┌─────────────────────────────────────────────┐
│         Users (Browser/Frontend)            │
└──────────────────┬──────────────────────────┘
                   │
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────┐
│  AWS Elastic Beanstalk (main.py)            │
│  - port: 5000 (internal)                    │
│  - gunicorn + Flask                         │
│  - t2/t3.micro (free tier)                  │
└──────────────────┬──────────────────────────┘
                   │
                   │ Internal VPC connection
                   ▼
┌─────────────────────────────────────────────┐
│   AWS RDS MySQL (student_attendance)        │
│   - ap-southeast-1 region                   │
│   - port: 3306                              │
│   - user: admin                             │
└─────────────────────────────────────────────┘
```

---

## Initial Setup (One-Time)

### 1. Prerequisites
- AWS Account with EB, RDS, EC2, and security group permissions
- EB CLI installed: `pip install awsebcli`
- Git repository initialized

### 2. Create Elastic Beanstalk Environment
```powershell
# Initialize EB project
eb init -p "Python 3.11 running on 64bit Amazon Linux 2" --region ap-southeast-1

# Create environment (single instance, free tier eligible)
eb create fyp-flask-env --single --instance-type t2.micro --region ap-southeast-1
```

### 3. Create RDS MySQL Instance
```
RDS Console → Create database
- Engine: MySQL 8.0
- Instance identifier: student-attendance
- DB name: student_attendance
- Region: ap-southeast-1
- Instance class: db.t3.micro (free tier eligible)
- Storage: 20 GB SSD
- Backup: 7 days
- Public accessibility: No (only accessed from EB instance)
```

### 4. Configure Security Groups
**RDS Security Group:**
- Inbound: Port 3306 from EB instance security group

**EB Security Group:**
- Inbound: Port 80, 443 from anywhere
- Outbound: Port 3306 to RDS instance

### 5. Initialize Database
```powershell
# SSH into EB instance
eb ssh

# Inside the instance, run the init script
python init_db.py
```

---

## Deployment

### Before Each Deployment
1. Ensure all changes are committed to git
2. Update version numbers if applicable
3. Test locally if possible

### Deploy Using EB CLI
```powershell
# Deploy latest code
eb deploy

# Deploy and create new EB environment
eb create [env-name]

# Deploy to specific environment
eb deploy [env-name]
```

### Monitor Deployment
```powershell
# View real-time logs
eb logs --stream

# Check environment health
eb health --refresh

# View recent events
eb events -f
```

---

## Environment Variables Setup

### Set Database Connection
```powershell
# Option 1: Using DATABASE_URL (recommended)
eb setenv DATABASE_URL="mysql://admin:PASSWORD@rds-endpoint.ap-southeast-1.rds.amazonaws.com:3306/student_attendance"

# Option 2: Using individual RDS variables
eb setenv RDS_HOSTNAME="rds-endpoint.ap-southeast-1.rds.amazonaws.com"
eb setenv RDS_PORT="3306"
eb setenv RDS_DB_NAME="student_attendance"
eb setenv RDS_USERNAME="admin"
eb setenv RDS_PASSWORD="PASSWORD"
```

### Set Deployment Environment
```powershell
eb setenv ENVIRONMENT="production"
eb setenv URL_PROTOCOL="https"
eb setenv DOMAIN_NAME="fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com"
```

### View Current Environment Variables
```powershell
eb printenv
```

### Update Specific Variables
```powershell
# Database password changed
eb setenv RDS_PASSWORD="new-password"

# Domain name changed
eb setenv DOMAIN_NAME="new-domain.elasticbeanstalk.com"
```

---

## Testing After Deployment

### 1. Test Health Endpoints
```bash
# Health check
curl https://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/health

# Database connectivity
curl https://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/health/db
```

### 2. Test Login
```bash
curl -X POST https://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'
```

### 3. Test Page Serving
- Navigate to https://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/
- Should see login page
- After login, should redirect to role-specific dashboard

---

## Troubleshooting

### Database Connection Issues

**Symptom:** `/health/db` returns 500 error

**Solutions:**
1. Check DATABASE_URL is correctly set
   ```powershell
   eb printenv | grep DATABASE_URL
   ```

2. Verify RDS security group allows EB instance
   - EB instance security group ID must be in RDS inbound rules

3. Check RDS instance is available
   - RDS Console → Databases → Check status (should be "available")

4. Test connection from EB instance
   ```bash
   eb ssh
   python -c "from common.db_utils import get_connection; conn = get_connection(); print('Connected!')"
   ```

### Login Issues

**Symptom:** Login returns 401

**Solutions:**
1. Verify test users exist in database
   ```bash
   eb ssh
   python verify_users.py
   ```

2. Check credentials in database match what you're sending
   - Passwords should be bcrypt hashes starting with `$2`

3. Verify login.html is sending email field (not username)
   - Check browser DevTools Network tab

### Page Not Found (404)

**Symptom:** Dashboard pages return 404

**Solutions:**
1. Check main.py has routes for all pages
   - System Admin: `/System%20Administrator/boundary/<path>`
   - SSA: `/Student%20Service%20Administrator/boundary/<path>`
   - Lecturer: `/Lecturer/boundary/<path>`

2. Check file paths are correct (spaces encoded as `%20`)

3. Check catch-all route is at END of file (after all API routes)

### Email Issues

**Symptom:** Password reset emails not sent

**Solutions:**
1. Check EMAIL_* environment variables are set
   ```powershell
   eb printenv | grep EMAIL
   ```

2. Verify Gmail SMTP credentials
   - Must use App Password (not regular password)
   - Enable 2FA on Gmail account

3. Check logs for SMTP errors
   ```powershell
   eb logs --stream
   ```

---

## Common Commands Reference

```powershell
# Environment Management
eb init              # Initialize EB project
eb create            # Create new environment
eb open              # Open app in browser
eb list              # List environments
eb use [env-name]    # Switch to environment

# Deployment
eb deploy            # Deploy current code
eb deploy [env-name] # Deploy to specific environment
eb abort              # Abort current deployment

# Configuration
eb setenv KEY=VALUE  # Set environment variable
eb printenv          # View environment variables
eb config            # View/edit EB configuration

# Monitoring
eb health            # View environment health
eb health --refresh  # Continuous health monitoring
eb logs              # View recent logs
eb logs --stream     # Stream logs in real-time
eb events -f         # Stream events
eb status            # View environment status
eb open              # Open app in browser

# SSH & Debugging
eb ssh               # SSH into instance
eb local run         # Run app locally with EB config
eb local open        # Open locally running app

# Cleanup
eb terminate         # Delete environment
eb delete            # Delete application
```

---

## Best Practices

### 1. Always Use Environment Variables
- ❌ Don't hardcode URLs, passwords, or configuration
- ✅ Use `os.getenv('VAR_NAME', 'default_value')`

### 2. Version Control
- ✅ Commit code changes to git
- ❌ Don't commit `.env` files with secrets
- ✅ Use `.env.example` for documentation

### 3. Database Backups
- ✅ Enable RDS automated backups (7+ days)
- ✅ Create manual snapshots before major changes
- ❌ Don't rely on default 1-day backup period

### 4. Monitoring
- ✅ Check CloudWatch logs regularly
- ✅ Set up CloudWatch alarms for errors
- ✅ Monitor disk space and CPU usage

### 5. Security
- ✅ Use bcrypt for password hashing (already implemented)
- ✅ Enable HTTPS (EB handles this with default certificate)
- ✅ Restrict RDS to VPC only (no public access)
- ✅ Use strong passwords for RDS master user

### 6. Cost Optimization
- ✅ Use t2/t3.micro instances (free tier eligible)
- ✅ Stop environments when not in use
- ✅ Use RDS Reserved Instances for production
- ❌ Don't use larger instances than needed

---

## File Structure
```
.
├── main.py                          # Unified Flask backend (entry point)
├── wsgi.py                          # WSGI wrapper for EB
├── Procfile                         # EB process configuration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .ebignore                        # Files to exclude from EB deployment
├── .elasticbeanstalk/               # EB configuration files
│   └── config.yml                   # EB environment config
├── common/                          # Shared utilities
│   ├── db_utils.py                  # Database connection pooling
│   ├── config.js                    # Frontend API configuration
│   ├── auth.js                      # Frontend authentication
│   ├── login.html                   # Login page (served at /)
│   ├── reset_password.html          # Password reset page
│   ├── forgot_password.html         # Forgot password page
│   ├── email_service.py             # Email service for notifications
│   └── ... (other shared files)
├── System Administrator/boundary/   # System admin UI pages (served via Flask routes)
├── Student Service Administrator/   # SSA UI pages (served via Flask routes)
├── Lecturer/boundary/               # Lecturer UI pages (served via Flask routes)
└── sql/                             # Database schemas and migrations
```

---

## Performance Optimization

### 1. Connection Pooling
- ✅ Already implemented in `common/db_utils.py`
- Default pool size: 5 connections
- Adjust with environment variables if needed

### 2. Caching
- Consider adding Redis for session caching
- CloudFront can cache static files

### 3. Database Optimization
- Create indexes on frequently queried columns (email, student_id, etc.)
- Monitor slow query logs

### 4. Frontend Optimization
- Minify CSS/JS for production
- Use CDN for static assets
- Enable gzip compression (EB default)

---

## Post-Deployment Checklist

- [ ] Login page loads at root URL (/)
- [ ] Login works with test credentials
- [ ] Dashboard pages load after login
- [ ] Health endpoints return 200 OK
- [ ] Database connectivity confirmed (/health/db)
- [ ] Email notifications send correctly
- [ ] No 404 errors in CloudWatch logs
- [ ] Environment variables correctly set (eb printenv)
- [ ] HTTPS certificate is valid
- [ ] Mobile responsive design works

---

## Support & Debugging

### View Logs
```powershell
# Recent logs
eb logs

# Stream logs in real-time
eb logs --stream

# SSH and check logs manually
eb ssh
tail -f /var/log/eb-activity.log
tail -f /var/log/eb-engine.log
```

### Check Application Status
```powershell
# Environment health
eb health

# Continuous health monitoring
eb health --refresh

# Environment details
eb status
```

### Manual Testing
```powershell
# SSH into instance
eb ssh

# Test database connection
python
>>> from common.db_utils import get_connection
>>> conn = get_connection()
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT 1")
>>> print(cursor.fetchone())
```

---

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Last Updated:** January 22, 2026
**Deployment Region:** ap-southeast-1 (Singapore)
**Status:** ✅ Ready for production
