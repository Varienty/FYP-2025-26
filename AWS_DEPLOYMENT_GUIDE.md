# 🚀 AWS Elastic Beanstalk Deployment Guide

**Complete step-by-step guide to deploy your FYP on AWS in 30 minutes**

---

## 📋 Prerequisites

✅ **AWS Account** (free tier eligible)
- [Sign up here](https://aws.amazon.com/free/)
- Free tier includes: 750 hrs/month EC2 `t2.micro` + MySQL RDS

✅ **AWS CLI installed**
```powershell
# Install AWS CLI
choco install awscli  # If using Chocolatey
# Or download from https://aws.amazon.com/cli/

# Verify
aws --version
```

✅ **EB CLI installed**
```powershell
pip install awsebcli
eb --version
```

✅ **Git installed**
```powershell
git --version
```

✅ **AWS IAM User with programmatic access**
- [Create here](https://console.aws.amazon.com/iam/home#/users)
- Save your **Access Key ID** and **Secret Access Key**

---

## 🔐 Step 1: Configure AWS Credentials

Store your AWS credentials locally:

```powershell
# Configure AWS CLI
aws configure

# When prompted, enter:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
# Should return your AWS account info
```

---

## 📦 Step 2: Prepare Your Repository

Navigate to your project root:

```powershell
cd c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26

# Verify files are in place
ls main.py                    # ✓ New unified Flask app
ls .ebextensions\            # ✓ AWS config files
ls common\db_utils.py        # ✓ Updated for RDS
ls common\config.js          # ✓ Updated for AWS
ls requirements.txt          # ✓ Python dependencies
ls sql\schema.sql            # ✓ Database schema
```

### Create `.gitignore` (if not exists)

```powershell
# Add to your .gitignore
Add-Content .gitignore @"
.ebignore
.elasticbeanstalk/
*.pyc
__pycache__/
.env
venv/
.DS_Store
"@
```

### Verify Git repository

```powershell
git status

# If not a git repo yet:
git init
git add .
git commit -m "Prepare for AWS deployment"
```

---

## 🌐 Step 3: Initialize Elastic Beanstalk

```powershell
# Navigate to project root
cd c:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26

# Initialize EB for your project
eb init -p python-3.11 attendance-system --region us-east-1

# When prompted:
# - Select your AWS region (recommend us-east-1 for free tier)
# - Select platform: Python 3.11
# - Do NOT set up CodeCommit (use GitHub instead)
```

This creates `.elasticbeanstalk/config.yml`:

```yaml
branch-defaults:
  main:
    environment: attendance-prod
    group_suffix: null
environment-defaults:
  attendance-prod:
    branch: main
global:
  application_name: attendance-system
  default_platform: Python 3.11
  default_region: us-east-1
  sc: git
```

---

## 🏗️ Step 4: Create Elastic Beanstalk Environment with RDS

### Option A: Using EB CLI (Recommended - Easiest)

```powershell
# Create environment with RDS database
eb create attendance-prod `
  --instance-type t2.micro `
  --database `
  --db.engine mysql `
  --db.version 8.0 `
  --db.instance db.t2.micro `
  --db.user admin `
  --envvars FLASK_ENV=production,PYTHONUNBUFFERED=true

# This will:
# ✓ Create EC2 instance (t2.micro - free tier)
# ✓ Create RDS MySQL database (free tier)
# ✓ Deploy your application
# ✓ Takes about 5-10 minutes

# Monitor creation
eb status
```

### Option B: Using AWS Console (Manual)

1. Go to [AWS Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk)
2. Click **Create Application**
3. Fill in:
   - Application name: `attendance-system`
   - Platform: Python 3.11
   - Code: Upload ZIP of your repository
4. Click **Create application**
5. Once created, go to **Configuration**
6. Click **Edit** under Database
7. Configure MySQL with `db.t2.micro`

---

## ✅ Step 5: Verify Deployment

```powershell
# Check environment status
eb status

# View environment details
eb info

# Get your application URL
eb open

# You should see:
# ✓ Health: Green
# ✓ URL: https://attendance-prod.elasticbeanstalk.com
# ✓ Instances: 1 running (t2.micro)
```

### Test the API

```powershell
# Get your environment URL
$url = (eb open --print-url).Trim()

# Test health endpoint
curl "$url/health"
# Should return: {"status": "healthy", "service": "attendance-system"}

# Test root endpoint
curl "$url/"
# Should return endpoint information
```

---

## 🗄️ Step 6: Initialize Database

```powershell
# SSH into your EC2 instance
eb ssh

# Once connected:
# Load the database schema
mysql -h $RDS_HOSTNAME -u $RDS_USERNAME -p$RDS_PASSWORD < sql/schema.sql

# Verify database created
mysql -h $RDS_HOSTNAME -u $RDS_USERNAME -p$RDS_PASSWORD -e "USE student_attendance; SHOW TABLES;"

# Exit SSH
exit
```

### Alternative: Use AWS Systems Manager Session Manager

```powershell
# No need to set up SSH keys
eb ssh --method=ssm
```

---

## 🌍 Step 7: Configure Your Frontend

Your HTML files now point to the correct API:

1. **Local development** (`localhost`):
   - Frontend: `http://localhost:8000` (your local server)
   - API: `http://localhost:5000` (unified backend)

2. **AWS Production**:
   - Frontend: `https://attendance-prod.elasticbeanstalk.com`
   - API: `https://attendance-prod.elasticbeanstalk.com` (same domain - CORS-friendly!)

The `config.js` automatically detects and uses the correct endpoint.

---

## 🚀 Step 8: Test Your Application

1. Open your EB app URL in browser
2. Navigate to login page
3. Test login with demo credentials
4. Verify attendance marking works
5. Check Reports generation

### Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| 502 Bad Gateway | App not running - check logs: `eb logs` |
| Database connection failed | RDS not initialized - run schema.sql manually |
| CORS errors | Check `main.py` CORS configuration |
| Long deploy time | Normal for first deploy (5-10 mins) |

---

## 📊 Step 9: Monitor Your Application

```powershell
# View application logs
eb logs

# View recent deployments
eb appversion

# Check environment health
eb health

# Monitor CPU/Memory usage
eb open-console  # Opens AWS Console
```

---

## 💰 Step 10: Manage Costs

### Free Tier Usage (per month)
- **750 hours** EC2 `t2.micro`
- **750 hours** RDS `db.t2.micro`
- **1GB** data transfer out
- **Total: ~$0**

### To Monitor Costs

```powershell
# Set up billing alarm in AWS Console
# AWS Billing → Billing Alerts → Create billing alert

# Or use AWS Budgets
# AWS Budgets → Create budget → Set limit ($5)
```

### If You Need to Stop/Delete

```powershell
# Terminate environment (STOPS CHARGES)
eb terminate attendance-prod

# This deletes:
# ✓ EC2 instance
# ✓ RDS database
# ✓ Load balancer
# ⚠️ Data is deleted (save backups first!)
```

---

## 🔄 Step 11: Deploy Updates

After making code changes:

```powershell
# Commit your changes
git add .
git commit -m "Update attendance logic"

# Deploy to Elastic Beanstalk
eb deploy

# Monitor deployment
eb status
```

---

## 🔗 Step 12: Custom Domain (Optional)

To use your own domain (e.g., `attendance.youruni.edu`):

1. In AWS Route 53, create A record pointing to your EB URL
2. Or use your domain registrar's CNAME settings
3. Update frontend `config.js` if needed

---

## 📋 Deployment Checklist

- [ ] AWS account created with free tier
- [ ] AWS CLI and EB CLI installed
- [ ] AWS credentials configured
- [ ] Git repository initialized
- [ ] Files in place: `main.py`, `.ebextensions/`, updated `db_utils.py`, `config.js`
- [ ] Environment created with RDS
- [ ] Database schema loaded
- [ ] Health check passing
- [ ] Login page accessible
- [ ] API endpoints responding
- [ ] Billing alerts set up

---

## 🆘 Troubleshooting

### App doesn't deploy
```powershell
eb logs
# Check error messages in logs
```

### Database won't connect
```powershell
# Check RDS endpoint in EB config
eb config

# Manually connect and test
mysql -h <RDS_HOSTNAME> -u admin -p
```

### CORS errors
```powershell
# Verify CORS headers in main.py
# They're already configured in the provided main.py
```

### 502 Bad Gateway
```powershell
# Usually means Flask app crashed
eb logs
# Look for Python errors in error log
```

---

## 📚 Additional Resources

- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS Free Tier](https://aws.amazon.com/free/)

---

## 🎓 Summary for Your FYP

**What You Get:**
- ✅ Live application on AWS (free!)
- ✅ Auto-scaling infrastructure
- ✅ Managed MySQL database
- ✅ Automatic backups
- ✅ Professional deployment for your CV

**Time Required:** ~30 minutes
**Cost:** ~$0 (within free tier)
**Difficulty:** Easy with this guide

---

**Questions?** Refer back to the troubleshooting section or check the AWS documentation.

Good luck with your FYP! 🎉
