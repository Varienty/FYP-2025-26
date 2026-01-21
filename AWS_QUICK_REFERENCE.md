# 🚀 AWS Elastic Beanstalk - Quick Reference Card

## One-Time Setup (First Time Only)

```powershell
# 1. Install required tools
pip install awsebcli
# Download AWS CLI from https://aws.amazon.com/cli/

# 2. Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# 3. Navigate to project
cd c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26

# 4. Initialize Elastic Beanstalk
eb init -p python-3.11 attendance-system --region us-east-1

# 5. Create environment (EC2 only)
eb create attendance-prod --instance-type t2.micro

# 6. Wait for deployment (5-10 minutes)
eb status

# 7. THEN add database via AWS Console:
#    - Go to Elastic Beanstalk console
#    - Click attendance-prod environment
#    - Configuration → Edit Database
#    - Enable RDS: MySQL, db.t2.micro
#    - Save and apply
#    OR use: eb config (then uncomment RDS section)

# 8. Get your URL
eb open
```

---

## Regular Deployment (Every Update)

```powershell
# 1. Commit your changes
git add .
git commit -m "Your commit message"

# 2. Deploy to AWS
eb deploy

# 3. Monitor
eb status

# 4. View logs if needed
eb logs
```

---

## Useful Commands

```powershell
# Open your live application
eb open

# View current environment status
eb status

# View environment details
eb info

# View recent logs
eb logs

# SSH into the EC2 instance
eb ssh

# Check environment health
eb health

# View configuration
eb config

# Scale up/down
eb scale 2          # 2 instances
eb scale 1          # 1 instance

# Terminate environment (STOPS CHARGES)
eb terminate attendance-prod

# List all environments
eb list
```

---

## Database Access

```powershell
# SSH into instance first
eb ssh

# Once logged in:
# Check environment variables
echo $RDS_HOSTNAME
echo $RDS_USERNAME
echo $RDS_PASSWORD

# Connect to database
mysql -h $RDS_HOSTNAME -u $RDS_USERNAME -p$RDS_PASSWORD student_attendance

# In MySQL:
SHOW TABLES;
SELECT * FROM lecturers LIMIT 5;
EXIT;
```

---

## File Structure (What We Created)

```
FYP-2025-26/
├── main.py                          # ✨ NEW - Unified Flask app
├── .ebextensions/                   # ✨ NEW - AWS config
│   ├── python.config                # Python & app setup
│   └── rds.config                   # Database setup
├── .ebignore                        # ✨ NEW - Exclude from deployment
├── common/
│   ├── db_utils.py                  # ✏️ UPDATED - AWS RDS support
│   ├── config.js                    # ✏️ UPDATED - Dynamic endpoints
│   ├── auth.js
│   ├── email_service.py
│   └── ...
├── Lecturer/                        # Unchanged
├── Student Service Administrator/   # Unchanged
├── System Administrator/            # Unchanged
├── sql/                             # Unchanged
├── AWS_DEPLOYMENT_GUIDE.md          # ✨ NEW - Full guide
├── AWS_DEPLOYMENT_SUMMARY.md        # ✨ NEW - Quick summary
└── requirements.txt                 # Unchanged
```

---

## Cost Tracking

```powershell
# Set billing alarm in AWS Console:
# 1. Go to https://console.aws.amazon.com/billing
# 2. Billing Alerts → Create billing alert
# 3. Set threshold to $5/month

# Or use AWS Budgets:
# 1. AWS Budgets → Create budget
# 2. Set limit and notification email
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **502 Bad Gateway** | `eb logs` - check Flask errors |
| **Database error** | SSH into instance, verify RDS connection |
| **CORS error** | Verify origin in `main.py` CORS config |
| **Deployment slow** | Normal for first deploy (10-15 mins) |
| **High bills** | Check AWS billing, terminate unused resources |

---

## Testing Your Deployment

```powershell
# Get your URL
$url = eb open --print-url

# Test health
curl "$url/health"

# Test root endpoint
curl "$url/"

# Test login endpoint
curl -X POST "$url/api/lecturer/auth/login" `
  -Header "Content-Type: application/json" `
  -Body '{"email":"test@test.com","password":"test123"}'
```

---

## Important Notes

⚠️ **Before Deleting Environment:**
- Backup your database
- Download any generated reports
- Save important logs

```powershell
# Take RDS snapshot before deletion
# AWS Console → RDS → Instances → attendance-prod-db → Create snapshot
```

---

## Environment Variables (Auto-Set by EB)

When deployed, these are automatically available:

```
RDS_HOSTNAME=attendance-prod-db.xxxxx.us-east-1.rds.amazonaws.com
RDS_PORT=3306
RDS_DB_NAME=student_attendance
RDS_USERNAME=admin
RDS_PASSWORD=[automatically generated]
```

Your `db_utils.py` reads these automatically!

---

## Next Steps

1. ✅ Files are created
2. 📖 Read [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)
3. 🔐 Configure AWS credentials
4. 🌐 Run `eb init` and `eb create`
5. 🎉 Your app is live!

---

## Support Resources

- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Commands](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Python on Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)
- [RDS Documentation](https://docs.aws.amazon.com/rds/)

---

**Good luck with your FYP! 🎓**
