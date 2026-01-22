# Elastic Beanstalk + RDS Configuration Diagnostic

## Issue: Data not being retrieved from RDS database

Your code is correctly configured for production with Elastic Beanstalk and RDS. The problem is likely in the **environment variable configuration**. Here's how to fix it:

---

## Step 1: Check Current EB Environment Variables

Run this command to see what environment variables are currently set:

```bash
eb printenv
```

**You should see:**
```
RDS_HOSTNAME=your-rds-endpoint.ap-southeast-1.rds.amazonaws.com
RDS_USERNAME=admin
RDS_PASSWORD=your-password
RDS_DB_NAME=student_attendance
RDS_PORT=3306

# OR:
DATABASE_URL=mysql://admin:password@your-rds-endpoint.ap-southeast-1.rds.amazonaws.com:3306/student_attendance
```

**If you see neither of these → This is your problem!**

---

## Step 2: Set Environment Variables in EB

### Option A: Set DATABASE_URL (Recommended)

```bash
# Get your RDS endpoint from AWS Console > RDS > Databases > your-instance
# Format: mysql://username:password@endpoint:port/database

eb setenv DATABASE_URL="mysql://admin:YOUR_PASSWORD@your-rds-endpoint.ap-southeast-1.rds.amazonaws.com:3306/student_attendance"
```

### Option B: Set Individual RDS Variables

```bash
eb setenv \
  RDS_HOSTNAME="your-rds-endpoint.ap-southeast-1.rds.amazonaws.com" \
  RDS_PORT="3306" \
  RDS_DB_NAME="student_attendance" \
  RDS_USERNAME="admin" \
  RDS_PASSWORD="YOUR_PASSWORD"
```

---

## Step 3: Verify RDS Connection Works

### Option 1: SSH into EB Instance
```bash
eb ssh
# Inside the instance:
python3
>>> from common.db_utils import get_connection
>>> conn = get_connection()
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT * FROM lecturers LIMIT 1;")
>>> print(cursor.fetchall())
```

### Option 2: Create Health Check Endpoint

Add this to your `main.py`:

```python
@app.route('/health/detailed', methods=['GET'])
def health_detailed():
    """Detailed health check including database and environment"""
    try:
        # Check environment
        import os
        env_vars = {
            'has_database_url': bool(os.getenv('DATABASE_URL')),
            'has_rds_hostname': bool(os.getenv('RDS_HOSTNAME')),
            'flask_env': os.getenv('FLASK_ENV', 'not set'),
        }
        
        # Check database
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM lecturers")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'lecturers_count': result['count'] if result else 0,
            'environment': env_vars
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
```

Then test:
```bash
curl https://your-eb-url/health/detailed
```

---

## Step 4: Check RDS Database Configuration

### In AWS Console:
1. Go to RDS > Databases
2. Find your database instance
3. Check:
   - ✅ Status: **Available**
   - ✅ Security Groups: **Allow inbound port 3306 from EB security group**
   - ✅ Public Accessibility: Check if needed
   - ✅ Endpoint: Copy the endpoint
   - ✅ Master username: Usually `admin`

### From EB Instance, test RDS connectivity:

```bash
eb ssh
# Test connection
telnet your-rds-endpoint.ap-southeast-1.rds.amazonaws.com 3306

# Or use mysql client:
mysql -h your-rds-endpoint.ap-southeast-1.rds.amazonaws.com -u admin -p student_attendance
```

---

## Step 5: Check Database Schema Exists

The database `student_attendance` must exist and have all tables. If not, you need to initialize it:

### Option 1: Run on EB Instance

```bash
# SSH into instance
eb ssh

# Run initialization script
cd /var/app/current
python init_db.py
```

### Option 2: Create tables directly in RDS

```bash
mysql -h your-rds-endpoint.ap-southeast-1.rds.amazonaws.com -u admin -p student_attendance < sql/schema.sql
```

---

## Step 6: Check EB Instance Logs

```bash
# View recent logs
eb logs

# Or SSH in and check:
eb ssh
tail -f /var/log/eb-activity.log
tail -f /var/log/eb-engine.log
```

Look for errors like:
- `Connection refused`
- `Unknown host`
- `Access denied`
- `Table doesn't exist`

---

## Step 7: Verify Code is Using Environment Variables Correctly

Your `db_utils.py` checks for environment variables in this order:

1. ✅ `DATABASE_URL` (Railway format)
2. ✅ `RDS_HOSTNAME` + RDS_* variables (AWS RDS)
3. ❌ Fallback to localhost (development only)

**This is correct!** The fallback to localhost should NOT be used in production.

---

## Quick Troubleshooting Checklist

| Issue | Check |
|-------|-------|
| "Connection refused" | EB can't reach RDS - check security groups |
| "Unknown host" | RDS endpoint typo - verify in AWS Console |
| "Access denied" | Wrong RDS username/password - verify in AWS Console |
| "Table doesn't exist" | Database schema not initialized - run `sql/schema.sql` |
| "No data showing" | Data not in RDS - check if schema was created |
| "Localhost only works" | Environment variables not set - use `eb setenv` |

---

## Common Issues

### Issue 1: Security Group Not Configured
```
Error: Connection refused
Cause: EB security group not allowed to access RDS
Solution:
1. Get EB security group ID
2. In RDS security group, add inbound rule:
   Type: MySQL/Aurora
   Port: 3306
   Source: <EB security group ID>
```

### Issue 2: Database URL Format Wrong
```
# WRONG:
DATABASE_URL=your-rds-endpoint:3306/student_attendance

# CORRECT:
DATABASE_URL=mysql://admin:password@your-rds-endpoint.ap-southeast-1.rds.amazonaws.com:3306/student_attendance
```

### Issue 3: Schema Not Initialized
```bash
# Check if tables exist
mysql -h your-endpoint -u admin -p student_attendance
mysql> SHOW TABLES;

# If empty, run:
mysql -h your-endpoint -u admin -p student_attendance < sql/schema.sql
```

---

## What Your Code Does (Production Path)

When a request comes in:

```
User Browser
     ↓
[HTTPS Request] → EB Instance
     ↓
Flask (main.py)
     ↓
db_utils.py → _get_db_config()
     ↓
Check: Is DATABASE_URL set? YES
     ↓
Parse DATABASE_URL
     ↓
Connect to RDS
     ↓
Execute Query
     ↓
Return Data
```

**The key is that DATABASE_URL or RDS_HOSTNAME must be set!**

---

## Verification Commands

```bash
# 1. Check environment variables are set
eb printenv | grep -E "DATABASE_URL|RDS_"

# 2. Check EB logs for connection errors
eb logs --zip

# 3. Test health endpoint
curl https://your-eb-domain/health/db

# 4. Check database connectivity from EB
eb ssh
python3 -c "from common.db_utils import get_connection; print(get_connection())"

# 5. List database tables
eb ssh
python3
>>> from common.db_utils import get_connection
>>> conn = get_connection()
>>> cursor = conn.cursor()
>>> cursor.execute("SHOW TABLES;")
>>> print(cursor.fetchall())
```

---

## Next Steps

1. **Set environment variables** with `eb setenv` (Step 2)
2. **Verify connection** with health endpoint (Step 3)
3. **Check RDS security groups** (Step 4)
4. **Initialize database** if needed (Step 5)
5. **Deploy and test** with `eb deploy`

**After setting environment variables, you MUST deploy for changes to take effect:**

```bash
git add .
git commit -m "RDS configuration"
eb deploy
```

---

## Your Code is Correct! ✅

The problem is **not** in your code. Your code properly:
- ✅ Reads from environment variables
- ✅ Supports DATABASE_URL (Railway format)
- ✅ Supports RDS variables (AWS format)
- ✅ Has connection pooling
- ✅ No hardcoded localhost in production code

The issue is that **environment variables are not set** in your EB environment.

Fix this with `eb setenv` and your API will start returning real data from RDS!
