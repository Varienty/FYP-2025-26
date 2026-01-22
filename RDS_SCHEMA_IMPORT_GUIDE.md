# 🔴 CRITICAL: Import Database Schema to AWS RDS

## The Problem
Your AWS RDS database is **completely empty** - no tables exist. That's why you're getting "Table doesn't exist" errors.

Your local MySQL has the schema (so it works locally), but you never imported it to RDS.

## Solution: Import schema.sql to RDS

### Option 1: Using MySQL Workbench (Easiest)

**Step 1: Connect to RDS**
1. Open MySQL Workbench
2. Click **Database** → **Manage Connections**
3. Create new connection with:
   - **Connection Name:** `FYP AWS RDS`
   - **Hostname:** `studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com`
   - **Port:** `3306`
   - **Username:** `admin` (or your RDS master username)
   - **Password:** (your RDS password)
4. Click **Test Connection** → Should say "Connection successful"
5. Click **OK**

**Step 2: Import Schema**
1. Double-click the new connection to open it
2. Click **File** → **Open SQL Script**
3. Navigate to: `C:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26\sql\schema.sql`
4. Click **Open**
5. Review the script (shows creating database & tables)
6. Click the **Execute** button (⚡ lightning bolt icon) or press `Ctrl+Shift+Enter`
7. Wait for completion (should show "X rows affected" at bottom)
8. You should see message: **"All statements executed successfully"**

**Step 3: Verify**
1. In the left sidebar, you should now see:
   ```
   ├─ student_attendance (database)
     ├─ classes
     ├─ students
     ├─ lecturers
     ├─ attendance
     ├─ timetable
     ├─ student_enrollments
     ├─ attendance_policies
     └─ ... (other tables)
   ```
2. If you see these tables, the schema is imported! ✅

**Step 4: Import Sample Data (Optional but Recommended)**
1. Click **File** → **Open SQL Script**
2. Select `additional_data.sql`
3. Click **Execute**
4. This populates your database with 750+ student records

---

### Option 2: Using MySQL Command Line

**Step 1: Open Terminal/PowerShell**

**Step 2: Run this command:**
```powershell
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com `
       -u admin -p student_attendance < "C:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26\sql\schema.sql"
```

When prompted, enter your RDS password.

**Step 3: For sample data:**
```powershell
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com `
       -u admin -p student_attendance < "C:\Users\amosy\OneDrive\Documents\GitHub\FYP-2025-26\sql\additional_data.sql"
```

---

### Option 3: Using phpMyAdmin (If Available)

If your hosting has phpMyAdmin:
1. Log in to phpMyAdmin
2. Click **Databases** → **student_attendance** (or create it)
3. Click **Import**
4. Select `schema.sql`
5. Click **Go**
6. Repeat for `additional_data.sql`

---

## ✅ How to Verify It Worked

After importing, go back to your application:

1. **Open Debug Page:** http://fyp-flask-env.eba-8ev8txxm.ap-southeast-1.elasticbeanstalk.com/debug

2. **Section 6: Database Data Loading Test** - Click each button:
   - Should see: ✓ Users - 7 records returned
   - Should see: ✓ Modules - X records returned
   - Should see: ✓ Lecturers - 3 records returned
   - Should see: ✓ Students - 750+ records returned
   - etc.

3. **Test Application Pages:**
   - System Admin → Attendance Policies (should load with data)
   - SSA → Modules, Students (should load)
   - Lecturer → Classes, Attendance (should load)

**If all show data:** ✅ Schema imported successfully!

---

## 📋 What Gets Imported

The `schema.sql` file creates:

**User Tables:**
- `system_admins` (3 admin accounts)
- `student_service_admins` (1 SSA account)
- `lecturers` (9 lecturer accounts)
- `students` (will have 750+ after additional_data.sql)

**Academic Tables:**
- `classes` (15 course sections)
- `timetable` (45 class schedules)
- `student_enrollments` (student enrollment records)
- `intake_periods` (intake management)

**Attendance Tables:**
- `attendance` (717+ attendance records)
- `attendance_sessions` (class session tracking)
- `attendance_policies` (10 system policies)
- `medical_certificates` (medical documentation)

**System Tables:**
- `system_config` (system settings)
- `audit_log` (system audit trail)

---

## 🚨 Important Notes

1. **RDS Credentials Needed:**
   - Host: `studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com`
   - Username: `admin`
   - Password: (the one you set when creating RDS)
   - Port: `3306`

2. **Database Name:**
   - The schema creates a database named `student_attendance`
   - Don't create it manually - the schema.sql will create it

3. **Drop Warning:**
   - The schema starts with `DROP DATABASE IF EXISTS student_attendance;`
   - This is safe - it only drops if it exists
   - If you already have data in RDS, back it up first!

4. **Time Required:**
   - Schema import: ~5 seconds
   - Sample data import: ~30 seconds
   - Total: ~1 minute

---

## 📞 Next Steps

1. **Import the schema** using Option 1, 2, or 3 above
2. **Wait for completion** and verify tables exist
3. **Test the debug page** to confirm data is accessible
4. **Take screenshot** of debug page Section 6 showing all tests passing
5. **Report back** with results

Once schema is in RDS, all your endpoints will work because the tables will exist! 🎉

---

## ❓ Troubleshooting

**Error: "Access Denied"**
- Check RDS username/password
- Verify RDS security group allows port 3306

**Error: "Connection Refused"**
- Check RDS endpoint is correct
- Verify RDS instance is running (AWS Console)

**Error: "Unknown Database"**
- This is OK on first run - schema.sql creates it

**Error: "Table already exists"**
- Drop the database first in MySQL, or
- Edit schema.sql to remove the `DROP DATABASE` line

**Application still shows errors after import:**
- Restart your Elastic Beanstalk environment
- Or redeploy the application: `eb deploy`

---

**This is the last missing piece! Once you import the schema, everything will work! 💪**
