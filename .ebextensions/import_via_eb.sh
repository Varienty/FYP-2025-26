#!/bin/bash
# Import SQL files to RDS from within EB environment
# This script runs on the EB EC2 instance which already has RDS access

echo "Installing MySQL client if not present..."
sudo yum install -y mysql

echo "Creating import directory..."
mkdir -p /tmp/sql_import

echo "SQL files will be uploaded to /tmp/sql_import/"
echo ""
echo "Run these commands on your LOCAL machine to upload files:"
echo "eb ssh -e 'scp sql/schema.sql ec2-user@instance:/tmp/sql_import/'"
echo "eb ssh -e 'scp sql/additional_data.sql ec2-user@instance:/tmp/sql_import/'"
echo "eb ssh -e 'scp student_attendance.sql ec2-user@instance:/tmp/sql_import/'"
echo ""
echo "Then execute import:"
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < /tmp/sql_import/schema.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < /tmp/sql_import/additional_data.sql
mysql -h studentattendance.cxyigemqkv6k.ap-southeast-1.rds.amazonaws.com -u admin -p studentattendance < /tmp/sql_import/student_attendance.sql

echo "Import complete!"
