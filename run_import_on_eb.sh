#!/bin/bash

# Legacy Data Import Script for EB Instance
# This runs on the EB instance which has VPC access to RDS

set -e

RDS_HOST="studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com"
RDS_USER="admin"
RDS_PASS="iamtrying"
RDS_DB="student_attendance"

STAGING_DB="student_attendance_legacy"
CURRENT_DIR="/var/app/current"
DUMP_FILE="$CURRENT_DIR/student_attendance.sql"
IMPORT_SCRIPT="$CURRENT_DIR/sql/import_from_legacy.sql"

echo "======================================================================"
echo "LEGACY DATA IMPORT - Running on EB Instance"
echo "======================================================================"
echo ""

# Step 1: Create staging schema
echo "[STEP 1] Creating staging schema '$STAGING_DB'..."
mysql -h "$RDS_HOST" -u "$RDS_USER" -p"$RDS_PASS" -e "CREATE DATABASE IF NOT EXISTS $STAGING_DB;" 2>/dev/null || {
  echo "✗ Failed to create staging schema"
  exit 1
}
echo "✓ Staging schema created"
echo ""

# Step 2: Import legacy dump into staging
echo "[STEP 2] Importing legacy dump into staging schema..."
if [ -f "$DUMP_FILE" ]; then
  mysql -h "$RDS_HOST" -u "$RDS_USER" -p"$RDS_PASS" "$STAGING_DB" < "$DUMP_FILE" 2>/dev/null || {
    echo "✗ Failed to import legacy dump"
    exit 1
  }
  echo "✓ Legacy dump imported into $STAGING_DB"
else
  echo "⚠️  Legacy dump file not found at $DUMP_FILE"
  echo "   Attempting to continue with existing staging schema..."
fi
echo ""

# Step 3: Import users from staging to live
echo "[STEP 3] Importing user data from staging to live schema..."
if [ -f "$IMPORT_SCRIPT" ]; then
  mysql -h "$RDS_HOST" -u "$RDS_USER" -p"$RDS_PASS" "$RDS_DB" < "$IMPORT_SCRIPT" 2>/dev/null || {
    echo "✗ Failed to import user data"
    exit 1
  }
  echo "✓ User data imported successfully"
else
  echo "⚠️  Import script not found at $IMPORT_SCRIPT"
  echo "   Skipping user import"
fi
echo ""

# Step 4: Verify import
echo "[STEP 4] Verifying import..."
mysql -h "$RDS_HOST" -u "$RDS_USER" -p"$RDS_PASS" "$RDS_DB" << EOF 2>/dev/null
SELECT 'system_admins' as table_name, COUNT(*) as count FROM system_admins
UNION ALL
SELECT 'student_service_admins', COUNT(*) FROM student_service_admins
UNION ALL
SELECT 'lecturers', COUNT(*) FROM lecturers
UNION ALL
SELECT 'students', COUNT(*) FROM students;
EOF

echo ""
echo "======================================================================"
echo "✓ IMPORT COMPLETE"
echo "======================================================================"
