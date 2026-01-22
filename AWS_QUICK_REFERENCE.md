# AWS EB Quick Reference

## Key Facts

| Item | Value |
|------|-------|
| **Backend** | Flask 3.0 (main.py) on Elastic Beanstalk |
| **Database** | AWS RDS MySQL 8.0 |
| **Region** | ap-southeast-1 (Singapore) |
| **Instance Type** | t2.micro (free tier) |
| **Entry Point** | wsgi:application (Gunicorn) |
| **Port (Internal)** | 5000 |
| **Port (Public)** | 80/443 (EB Load Balancer) |
| **Login Page Route** | GET / → serves login.html |

---

## Deploy Code Changes

```powershell
# 1. Commit changes
git add .
git commit -m "Description of changes"

# 2. Deploy to EB
eb deploy

# 3. Monitor
eb logs --stream
```

---

## Set Environment Variables

```powershell
# Database (Required)
eb setenv DATABASE_URL="mysql://admin:PASSWORD@rds-host:3306/student_attendance"

# Domain (Required)
eb setenv DOMAIN_NAME="your-eb-domain.elasticbeanstalk.com"

# View all
eb printenv
```

---

## Test Endpoints

```bash
# Login page
curl https://your-domain/

# Health check
curl https://your-domain/health

# Database check
curl https://your-domain/health/db

# Login
curl -X POST https://your-domain/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'
```

---

## Troubleshoot

```powershell
# View environment
eb printenv

# SSH into instance
eb ssh

# Stream logs
eb logs --stream

# Health status
eb health --refresh

# Recent events
eb events -f
```

---

## Environment Variables Needed

```
DATABASE_URL              # Required: MySQL connection string
DOMAIN_NAME              # Required: Your EB domain
ENVIRONMENT              # Optional: "production" or "development"
URL_PROTOCOL             # Optional: "https" or "http"
PORT                     # Optional: Default 5000
EMAIL_HOST               # Optional: For password reset emails
EMAIL_USER               # Optional: Email sender address
EMAIL_PASSWORD           # Optional: Email app password
```

---

## File Locations

| What | Where |
|------|-------|
| **Backend Code** | main.py, wsgi.py |
| **Login Page** | common/login.html |
| **Dashboard Pages** | System Administrator/boundary/, etc. |
| **Database Code** | common/db_utils.py |
| **Config** | .env.example, .ebignore, Procfile |
| **Docs** | AWS_DEPLOYMENT_CHECKLIST.md |

---

## Login Flow

1. User visits `/` → **login.html** loads
2. User enters email + password + role
3. Frontend sends POST to `/api/auth/login`
4. Backend validates in database
5. On success → redirect to role dashboard
6. On failure → show error message

---

## Important Notes

✅ **Login page ALWAYS comes first** - root route `/` serves it  
✅ **Environment variables in EB, not in .env file**  
✅ **Old controller files are excluded** - only main.py runs  
✅ **All dashboards use same backend** - one Flask app for all roles  
✅ **Database uses RDS connection pooling** - safe for multiple requests  

---

## Common Issues

| Issue | Fix |
|-------|-----|
| Database won't connect | Check `eb printenv`, verify RDS endpoint |
| Login fails | Verify test users exist: `python verify_users.py` |
| Dashboard returns 404 | Check main.py has page routes, file paths correct |
| Domain name changes | Run `eb setenv DOMAIN_NAME="new-domain"` |
| Email not sending | Verify EMAIL_* vars, check logs |

---

**Last Updated:** January 22, 2026  
**Status:** ✅ All AWS components verified and ready
