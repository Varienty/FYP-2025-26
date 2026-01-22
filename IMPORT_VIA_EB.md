# Import Database via Elastic Beanstalk

Since your local machine cannot connect to RDS (likely firewall blocking port 3306), we'll import through your EB environment which **already has RDS access**.

## Method 1: SSH into EB and Import

### Step 1: Initialize EB CLI
```powershell
eb init --region ap-southeast-1
```
Select your application: **fyp-flask-app**
Select your environment: **fyp-flask-env**

### Step 2: SSH into EB Instance
```powershell
eb ssh
```

### Step 3: Once Inside EB Instance, Run:
```bash
# Install MySQL client
sudo yum install -y mysql

# Create import directory
mkdir -p ~/sql_import
```

### Step 4: On Your LOCAL Machine (in another PowerShell), Upload SQL Files:
```powershell
# Get instance ID first
eb ssh --setup

# Upload files (adjust path if needed)
scp -i "your-keypair.pem" sql/schema.sql ec2-user@your-eb-instance-ip:~/sql_import/
scp -i "your-keypair.pem" sql/additional_data.sql ec2-user@your-eb-instance-ip:~/sql_import/
scp -i "your-keypair.pem" student_attendance.sql ec2-user@your-eb-instance-ip:~/sql_import/
```

### Step 5: Back in EB SSH Session, Import:
```bash
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < ~/sql_import/schema.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < ~/sql_import/additional_data.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < ~/sql_import/student_attendance.sql
```
Enter password: **Shashasha12345678**

---

## Method 2: EASIEST - AWS CloudShell (No SSH Required)

### Step 1: Open AWS CloudShell
1. Go to AWS Console: https://console.aws.amazon.com/
2. Click **CloudShell** icon (top right, looks like `>_`)
3. Wait for it to load

### Step 2: Upload SQL Files
Click **Actions** → **Upload file**
Upload these 3 files:
- `sql/schema.sql`
- `sql/additional_data.sql`
- `student_attendance.sql`

### Step 3: Import to RDS
```bash
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -pShashasha12345678 studentattendance < schema.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -pShashasha12345678 studentattendance < additional_data.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -pShashasha12345678 studentattendance < student_attendance.sql
```

**Note:** CloudShell has MySQL client pre-installed and has direct AWS network access.

---

## Method 3: Combine SQL Files First (Faster)

Create a single SQL file to import:

```powershell
# On your local machine
Get-Content sql\schema.sql, sql\additional_data.sql, student_attendance.sql | Set-Content combined_import.sql
```

Then upload just `combined_import.sql` using Method 2 (CloudShell) and run:
```bash
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -pShashasha12345678 studentattendance < combined_import.sql
```

---

## After Import - Verify

Visit your debug page:
https://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug_test.html

**Section 6** should now show data from all endpoints instead of "Table doesn't exist" errors.

---

## Why Local Connection Failed

Your security group is correct, but:
- Windows Firewall or corporate network blocking outbound MySQL port 3306
- ISP might block MySQL connections
- VPN or proxy interfering

**CloudShell is the easiest workaround** - it has direct AWS VPC access.
