#!/usr/bin/env python3
"""
Check current IP and provide AWS CLI commands to update RDS Security Group
"""
import requests

# Get your current public IP
try:
    response = requests.get('https://api.ipify.org?format=json')
    your_ip = response.json()['ip']
    print(f"Your current public IP: {your_ip}")
    print("\n" + "="*60)
    print("To allow your IP to access RDS, run these AWS CLI commands:")
    print("="*60)
    print(f"""
# 1. Find your RDS security group ID
aws rds describe-db-instances --db-instance-identifier studentattendance --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' --output text

# 2. Add your IP to security group (replace <SECURITY-GROUP-ID> with result from step 1)
aws ec2 authorize-security-group-ingress --group-id <SECURITY-GROUP-ID> --protocol tcp --port 3306 --cidr {your_ip}/32
""")
    print("\nOR manually in AWS Console:")
    print(f"1. Go to RDS → Databases → studentattendance")
    print(f"2. Click on VPC security group")
    print(f"3. Edit inbound rules → Add rule")
    print(f"4. Type: MySQL/Aurora, Port: 3306, Source: {your_ip}/32")
    print(f"5. Save rules")
except Exception as e:
    print(f"Error: {e}")
    print("\nManually check your IP at: https://whatismyipaddress.com/")
