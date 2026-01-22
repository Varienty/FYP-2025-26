# Legacy Data Import Runbook (RDS MySQL)

This runbook walks you through snapshotting RDS, staging the legacy dump, and safely importing only user accounts into the live schema.

## Prerequisites

- RDS endpoint, username, and password for the MySQL instance.
- AWS access (Console or AWS CLI configured with `ap-southeast-1`).
- The legacy dump file available locally: `student_attendance.sql`.

## 1) Take an RDS Snapshot (Safety First)

### AWS Console
- Go to RDS > Databases > select your DB instance.
- Actions > Take snapshot > name: `pre-legacy-import-<YYYYMMDD-HHMM>`.
- Wait until snapshot status is `available`.

### AWS CLI (optional)
```bash
aws rds create-db-snapshot \
  --region ap-southeast-1 \
  --db-snapshot-identifier pre-legacy-import-$(date +%Y%m%d-%H%M) \
  --db-instance-identifier <YOUR_DB_INSTANCE_ID>

aws rds wait db-snapshot-available \
  --region ap-southeast-1 \
  --db-snapshot-identifier pre-legacy-import-<SNAPSHOT_ID>
```

## 2) Stage the Legacy Dump on RDS

Create a separate schema and import the dump so we can selectively copy data:

```bash
# Create staging schema
mysql -h <RDS_HOST> -u <USER> -p -e "CREATE DATABASE IF NOT EXISTS student_attendance_legacy;"

# Import the legacy dump into the staging schema
mysql -h <RDS_HOST> -u <USER> -p student_attendance_legacy < student_attendance.sql
```

Tip: If connecting from Windows PowerShell, you can run the same commands; you will be prompted for the password.

## 3) Import Users Safely into Live Schema

Run the provided SQL script against the live database (`student_attendance`). This only imports users (system admins, SSAs, lecturers, students) and de-duplicates by email.

```bash
mysql -h <RDS_HOST> -u <USER> -p student_attendance < sql/import_from_legacy.sql
```

What it does:
- Inserts only rows whose `email` does not already exist.
- Excludes legacy `id` values to avoid primary key collisions.
- Does NOT import classes, enrollments, or attendance records (phase 2 needed).

## 4) Verify

- Attempt login using one of the imported emails (e.g., `admin@attendance.com`, `studentservice@attendance.com`, `john.smith@university.com`).
- Passwords are bcrypt hashes in the dump. Our app supports `$2y$`/`$2b$` formats; use the known demo password `password` if applicable.
- Check `/health/db` and basic pages still load.

## 5) Rollback (If Needed)

If anything looks wrong, restore from the snapshot:
- AWS Console: RDS > Snapshots > select the snapshot > Restore.
- Or use AWS CLI: `aws rds restore-db-instance-from-db-snapshot ...`

## Phase 2 (Optional)

To import `classes`, `student_enrollments`, `timetable`, and `attendance`, we will:
- Build mapping tables to translate legacy IDs to newly assigned IDs.
- Reinsert relational data using the mappings to preserve referential integrity.
- Provide a separate script once approved.
