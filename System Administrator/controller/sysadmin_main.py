"""
System Administrator - Main Application
Runs all System Admin controllers on a single port (5009)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import time
import bcrypt
import requests
import threading
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=False)

# Camera monitoring configuration
FACIAL_RECOGNITION_URL = 'http://127.0.0.1:5011'
CAMERA_DEVICE_ID = 'facial-recognition-camera'
CAMERA_DEVICE_NAME = 'Facial Recognition Camera'
camera_monitor_thread = None
camera_monitor_running = False

# =============================================================================
# CAMERA MONITORING FUNCTIONS
# =============================================================================

def check_camera_status():
    """Check if facial recognition camera is actually active (webcam on)"""
    try:
        response = requests.get(f'{FACIAL_RECOGNITION_URL}/api/facial-recognition/camera/status', timeout=2)
        if response.status_code == 200:
            data = response.json()
            # Only report online if camera is actually active, not just server running
            if data.get('ok') and data.get('active'):
                return 'online'
        return 'offline'
    except requests.exceptions.RequestException:
        return 'offline'

def ensure_camera_device_exists():
    """Ensure the camera device exists in the devices table"""
    existing = db_utils.query_one(
        "SELECT id FROM devices WHERE id = %s",
        (CAMERA_DEVICE_ID,)
    )

    if not existing:
        # Create the device record
        db_utils.execute(
            """INSERT INTO devices (id, name, type, status, last_seen, latency_ms)
               VALUES (%s, %s, %s, %s, NOW(), %s)""",
            (CAMERA_DEVICE_ID, CAMERA_DEVICE_NAME, 'camera', 'offline', 0)
        )
        print(f"✓ Created camera device: {CAMERA_DEVICE_NAME}")

def update_camera_status(status):
    """Update camera status in the devices table"""
    latency = 0
    if status == 'online':
        # Measure actual latency
        try:
            start = time.time()
            requests.get(f'{FACIAL_RECOGNITION_URL}/health', timeout=2)
            latency = int((time.time() - start) * 1000)  # ms
        except:
            latency = 0

    db_utils.execute(
        """UPDATE devices
           SET status = %s, last_seen = NOW(), latency_ms = %s
           WHERE id = %s""",
        (status, latency, CAMERA_DEVICE_ID)
    )

def log_alert(alert_type, title, description, device_id=None):
    """Log an alert to the system_alerts table"""
    try:
        db_utils.execute(
            """INSERT INTO system_alerts
               (alert_type, severity, title, description, device_id, status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
            (alert_type, 'high', title, description, device_id, 'new')
        )
    except Exception as e:
        print(f"Error logging alert: {e}")

def resolve_alerts(device_id):
    """Mark all new/acknowledged alerts for a device as resolved"""
    try:
        db_utils.execute(
            """UPDATE system_alerts
               SET status = 'resolved', resolved_at = NOW()
               WHERE device_id = %s AND status IN ('new', 'acknowledged')""",
            (device_id,)
        )
    except Exception as e:
        print(f"Error resolving alerts: {e}")

def monitor_camera():
    """Background thread to monitor camera status"""
    global camera_monitor_running

    print(f"\n{'='*60}")
    print("Camera Monitor Thread Started")
    print(f"Monitoring: {FACIAL_RECOGNITION_URL}")
    print(f"{'='*60}\n")

    # Ensure device exists
    ensure_camera_device_exists()

    previous_status = None

    while camera_monitor_running:
        try:
            current_status = check_camera_status()

            # Update database
            update_camera_status(current_status)

            # Check for status change
            if previous_status is not None and previous_status != current_status:
                if current_status == 'offline':
                    print(f"⚠️  Camera went OFFLINE at {datetime.now().strftime('%H:%M:%S')}")
                    log_alert(
                        'camera_offline',
                        f'{CAMERA_DEVICE_NAME} is offline',
                        'The facial recognition camera is not responding. Please check the service on port 5011.',
                        CAMERA_DEVICE_ID
                    )
                elif current_status == 'online':
                    print(f"✓ Camera came back ONLINE at {datetime.now().strftime('%H:%M:%S')}")
                    resolve_alerts(CAMERA_DEVICE_ID)

            previous_status = current_status

        except Exception as e:
            print(f"Error monitoring camera: {e}")

        # Wait 5 seconds before next check
        time.sleep(5)

    print("Camera Monitor Thread Stopped")

def start_camera_monitoring():
    """Start the camera monitoring background thread"""
    global camera_monitor_thread, camera_monitor_running

    if camera_monitor_thread is None or not camera_monitor_thread.is_alive():
        camera_monitor_running = True
        camera_monitor_thread = threading.Thread(target=monitor_camera, daemon=True)
        camera_monitor_thread.start()

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """System admin login - authenticate against database"""
    payload = request.get_json() or {}
    email = payload.get('username') or payload.get('email')
    password = payload.get('password')
    
    if not email or not password:
        return jsonify({'ok': False, 'error': 'Email and password required'}), 400
    
    # Query system_admins table
    admin = db_utils.query_one(
        "SELECT id, admin_id, email, password, first_name, last_name, is_active FROM system_admins WHERE email = %s",
        (email,)
    )
    
    if not admin:
        return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401
    
    if not admin.get('is_active'):
        return jsonify({'ok': False, 'error': 'Account is disabled'}), 403
    
    # Verify password (bcrypt)
    stored_hash = admin['password'].encode('utf-8')
    # Handle PHP $2y$ hash compatibility
    if stored_hash.startswith(b'$2y$'):
        stored_hash = b'$2b$' + stored_hash[4:]
    
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return jsonify({'ok': False, 'error': 'Invalid credentials'}), 401
    
    # Update last_login
    db_utils.execute(
        "UPDATE system_admins SET last_login = NOW() WHERE id = %s",
        (admin['id'],)
    )
    
    return jsonify({
        'ok': True, 
        'user': {
            'id': admin['admin_id'],
            'username': admin['email'].split('@')[0],
            'role': 'system-admin',
            'email': admin['email'],
            'firstName': admin['first_name'],
            'lastName': admin['last_name']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """System admin logout"""
    return jsonify({'ok': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email to user"""
    payload = request.get_json() or {}
    role = payload.get('role', '').lower()
    email = payload.get('email', '').strip()

    if not email or not role:
        return jsonify({'ok': False, 'error': 'Email and role are required'}), 400

    # Determine which table to query based on role
    if role == 'system-admin' or role == 'system administrator':
        table = 'system_admins'
        id_col = 'admin_id'
    elif role == 'student-service-admin' or role == 'student service administrator':
        table = 'student_service_admins'
        id_col = 'admin_id'
    elif role == 'lecturer':
        table = 'lecturers'
        id_col = 'lecturer_id'
    else:
        return jsonify({'ok': False, 'error': 'Invalid role'}), 400

    # Check if user exists
    user = db_utils.query_one(
        f"SELECT {id_col} as id, email, first_name, last_name FROM {table} WHERE email = %s",
        (email,)
    )

    if not user:
        # For security, don't reveal if email exists or not
        return jsonify({
            'ok': True,
            'message': 'If an account exists with this email, a password reset link has been sent.'
        })

    # Import EmailService
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from common.email_service import EmailService

    # Generate reset token and code
    email_service = EmailService()
    reset_code = email_service.generate_reset_code(8)

    # Create reset link (pointing to a reset password page)
    reset_link = f"http://localhost/FYP-Team-15/common/reset_password.html?token={reset_code}&email={email}&role={role}"

    # Calculate expiry (5 minutes from now)
    from datetime import datetime, timedelta
    expiry = datetime.now() + timedelta(minutes=5)

    # Update database with reset token and expiry
    db_utils.execute(
        f"UPDATE {table} SET reset_token = %s, reset_token_expiry = %s WHERE {id_col} = %s",
        (reset_code, expiry, user['id'])
    )

    # Send email
    user_name = f"{user['first_name']} {user['last_name']}"
    result = email_service.send_password_reset_email(
        to_email=email,
        user_name=user_name,
        reset_code=reset_code,
        reset_link=reset_link
    )

    if result.get('ok'):
        return jsonify({
            'ok': True,
            'message': 'Password reset instructions have been sent to your email.'
        })
    else:
        return jsonify({
            'ok': False,
            'error': 'Failed to send email. Please try again later.'
        }), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user password using reset token"""
    payload = request.get_json() or {}
    token = payload.get('token', '').strip()
    email = payload.get('email', '').strip()
    role = payload.get('role', '').lower()
    new_password = payload.get('newPassword', '')

    if not token or not email or not role or not new_password:
        return jsonify({'ok': False, 'error': 'All fields are required'}), 400

    if len(new_password) < 8:
        return jsonify({'ok': False, 'error': 'Password must be at least 8 characters long'}), 400

    # Determine which table to query based on role
    if role == 'system-admin' or role == 'system administrator':
        table = 'system_admins'
        id_col = 'admin_id'
    elif role == 'student-service-admin' or role == 'student service administrator':
        table = 'student_service_admins'
        id_col = 'admin_id'
    elif role == 'lecturer':
        table = 'lecturers'
        id_col = 'lecturer_id'
    else:
        return jsonify({'ok': False, 'error': 'Invalid role'}), 400

    # Look up user and verify token
    user = db_utils.query_one(
        f"SELECT {id_col} as id, email, reset_token, reset_token_expiry FROM {table} WHERE email = %s",
        (email,)
    )

    if not user:
        return jsonify({'ok': False, 'error': 'Invalid reset link'}), 400

    # Verify token matches
    if user.get('reset_token') != token:
        return jsonify({'ok': False, 'error': 'Invalid or expired reset token'}), 400

    # Verify token hasn't expired
    from datetime import datetime
    if not user.get('reset_token_expiry'):
        return jsonify({'ok': False, 'error': 'Invalid reset token'}), 400

    if datetime.now() > user['reset_token_expiry']:
        return jsonify({'ok': False, 'error': 'Reset token has expired. Please request a new password reset.'}), 400

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update password and clear reset token
    db_utils.execute(
        f"UPDATE {table} SET password = %s, reset_token = NULL, reset_token_expiry = NULL WHERE {id_col} = %s",
        (hashed_password, user['id'])
    )

    return jsonify({
        'ok': True,
        'message': 'Password reset successful! You can now log in with your new password.'
    })

# =============================================================================
# POLICY MANAGEMENT ENDPOINTS (US20, US21)
# =============================================================================

@app.route('/api/policies', methods=['GET'])
def get_policies():
    """Get all attendance policies from database (US20)"""
    policies = db_utils.query_all(
        """SELECT id, entity_id as moduleId,
           grace_period_minutes as gracePeriod, late_threshold_minutes as lateThreshold,
           is_active, created_at as createdAt
           FROM attendance_policies
           ORDER BY created_at DESC"""
    )

    # Convert to expected format
    result = []
    for p in policies:
        result.append({
            'id': f"p_{p['id']}",
            'moduleId': p['moduleId'],
            'gracePeriod': p['gracePeriod'],
            'lateThreshold': p['lateThreshold'],
            'isActive': bool(p['is_active']),
            'createdAt': p['createdAt'].isoformat() if p['createdAt'] else None
        })

    return jsonify({"ok": True, "policies": result})

@app.route('/api/policies', methods=['POST'])
def add_policy():
    """Create new attendance policy in database (US20)"""
    payload = request.get_json() or {}
    module_id = payload.get('moduleId')
    grace_period = payload.get('gracePeriod', 10)
    late_threshold = payload.get('lateThreshold', 15)

    if not module_id:
        return jsonify({'ok': False, 'error': 'moduleId is required'}), 400

    # Check if policy already exists for this module
    existing = db_utils.query_one(
        "SELECT id FROM attendance_policies WHERE entity_id = %s",
        (module_id,)
    )

    if existing:
        return jsonify({'ok': False, 'error': 'Policy already exists for this module'}), 400

    db_utils.execute(
        """INSERT INTO attendance_policies
           (policy_name, entity_id, grace_period_minutes,
            late_threshold_minutes, applies_to, is_active)
           VALUES (%s, %s, %s, %s, %s, TRUE)""",
        ('Module Policy', module_id, grace_period, late_threshold, 'course')
    )

    # Get the newly created policy
    new_policy = db_utils.query_one(
        "SELECT id, entity_id, grace_period_minutes, late_threshold_minutes FROM attendance_policies ORDER BY id DESC LIMIT 1"
    )

    return jsonify({
        'ok': True,
        'policy': {
            'id': f"p_{new_policy['id']}",
            'moduleId': new_policy['entity_id'],
            'gracePeriod': new_policy['grace_period_minutes'],
            'lateThreshold': new_policy['late_threshold_minutes']
        }
    }), 201

@app.route('/api/policies/<policy_id>', methods=['PUT'])
def update_policy(policy_id):
    """Update existing policy in database (US21)"""
    payload = request.get_json() or {}

    # Extract numeric ID from policy_id (format: p_123 or just 123)
    numeric_id = int(policy_id.replace('p_', '')) if 'p_' in policy_id else int(policy_id)

    # Build update query dynamically
    updates = []
    params = []

    if 'moduleId' in payload:
        # Check if another policy already uses this module
        existing = db_utils.query_one(
            "SELECT id FROM attendance_policies WHERE entity_id = %s AND id != %s",
            (payload['moduleId'], numeric_id)
        )
        if existing:
            return jsonify({'ok': False, 'error': 'Policy already exists for this module'}), 400

        updates.append("entity_id = %s")
        params.append(payload['moduleId'])

    if 'gracePeriod' in payload:
        updates.append("grace_period_minutes = %s")
        params.append(payload['gracePeriod'])

    if 'lateThreshold' in payload:
        updates.append("late_threshold_minutes = %s")
        params.append(payload['lateThreshold'])

    if not updates:
        return jsonify({'ok': False, 'error': 'No fields to update'}), 400

    params.append(numeric_id)
    db_utils.execute(
        f"UPDATE attendance_policies SET {', '.join(updates)} WHERE id = %s",
        tuple(params)
    )

    # Return updated policy
    updated = db_utils.query_one(
        "SELECT id, entity_id, grace_period_minutes, late_threshold_minutes FROM attendance_policies WHERE id = %s",
        (numeric_id,)
    )

    if not updated:
        return jsonify({'ok': False, 'error': 'Policy not found'}), 404

    return jsonify({
        'ok': True,
        'policy': {
            'id': policy_id,
            'moduleId': updated['entity_id'],
            'gracePeriod': updated['grace_period_minutes'],
            'lateThreshold': updated['late_threshold_minutes']
        }
    })

@app.route('/api/policies/<policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    """Delete policy from database (US21)"""
    # Extract numeric ID
    numeric_id = int(policy_id.replace('p_', '')) if 'p_' in policy_id else int(policy_id)
    
    rows = db_utils.execute(
        "DELETE FROM attendance_policies WHERE id = %s",
        (numeric_id,)
    )
    
    if rows > 0:
        return jsonify({'ok': True, 'message': 'Policy deleted'})
    return jsonify({'ok': False, 'error': 'Policy not found'}), 404

# =============================================================================
# HARDWARE MONITORING ENDPOINTS (US22, US23)
# =============================================================================

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all hardware devices with status from database (US22)"""
    devices = db_utils.query_all(
        """SELECT id, name, type, status, last_seen as lastSeen, latency_ms as latencyMs, 
           created_at as createdAt
           FROM devices
           ORDER BY name"""
    )
    
    # Convert to expected format
    result = []
    for d in devices:
        # Determine location from name or use default
        location = d.get('name', '').split('-')[-1].strip() if '-' in d.get('name', '') else 'Unknown'
        
        result.append({
            'id': d['id'],
            'name': d['name'],
            'type': d['type'],
            'status': d['status'],
            'location': location,
            'lastSeen': d['lastSeen'].isoformat() if d['lastSeen'] else None,
            'latencyMs': d['latencyMs'] or 0
        })
    
    return jsonify({"ok": True, "devices": result})

@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device status in database (US23)"""
    payload = request.get_json() or {}
    
    # Build update query
    updates = []
    params = []
    
    if 'status' in payload:
        updates.append("status = %s")
        params.append(payload['status'])
        # Update last_seen if status is online
        if payload['status'] == 'online':
            updates.append("last_seen = NOW()")
    if 'name' in payload:
        updates.append("name = %s")
        params.append(payload['name'])
    
    if not updates:
        return jsonify({'ok': False, 'error': 'No fields to update'}), 400
    
    params.append(device_id)
    rows = db_utils.execute(
        f"UPDATE devices SET {', '.join(updates)} WHERE id = %s",
        tuple(params)
    )
    
    if rows == 0:
        return jsonify({'ok': False, 'error': 'Device not found'}), 404
    
    # Return updated device
    updated = db_utils.query_one(
        "SELECT id, name, type, status, last_seen, latency_ms FROM devices WHERE id = %s",
        (device_id,)
    )
    
    location = updated.get('name', '').split('-')[-1].strip() if '-' in updated.get('name', '') else 'Unknown'
    
    return jsonify({
        'ok': True,
        'device': {
            'id': updated['id'],
            'name': updated['name'],
            'type': updated['type'],
            'status': updated['status'],
            'location': location,
            'lastSeen': updated['last_seen'].isoformat() if updated['last_seen'] else None,
            'latencyMs': updated['latency_ms'] or 0
        }
    })

@app.route('/api/devices/stats', methods=['GET'])
def device_stats():
    """Get device statistics from database (US22)"""
    stats = db_utils.query_one(
        """SELECT 
           COUNT(*) as total,
           SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online,
           SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) as offline,
           SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
           FROM devices"""
    )
    
    total = stats['total'] or 0
    online = stats['online'] or 0
    
    return jsonify({
        'ok': True,
        'stats': {
            'total': total,
            'online': online,
            'offline': stats['offline'] or 0,
            'maintenance': stats['maintenance'] or 0,
            'uptime': round((online / total * 100), 1) if total > 0 else 0
        }
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get active system alerts from database"""
    alerts = db_utils.query_all(
        """SELECT id, alert_type, severity, title, description, device_id, status,
           created_at, acknowledged_by, acknowledged_at, resolved_at
           FROM system_alerts
           WHERE status IN ('new', 'acknowledged')
           ORDER BY created_at DESC
           LIMIT 50"""
    )

    result = []
    for alert in alerts:
        result.append({
            'id': alert['id'],
            'type': alert['alert_type'],
            'severity': alert['severity'],
            'title': alert['title'],
            'description': alert['description'],
            'deviceId': alert['device_id'],
            'status': alert['status'],
            'createdAt': alert['created_at'].isoformat() if alert['created_at'] else None,
            'acknowledgedBy': alert['acknowledged_by'],
            'acknowledgedAt': alert['acknowledged_at'].isoformat() if alert['acknowledged_at'] else None,
            'resolvedAt': alert['resolved_at'].isoformat() if alert['resolved_at'] else None
        })

    return jsonify({'ok': True, 'alerts': result})

# =============================================================================
# USER MANAGEMENT ENDPOINTS (US24, US25)
# =============================================================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users from database (US24)"""
    # Get users from all three tables
    lecturers = db_utils.query_all(
        """SELECT lecturer_id as id, CONCAT(first_name, ' ', last_name) as name, 
           email, 'lecturer' as role, is_active as isActive, 
           created_at as createdAt
           FROM lecturers
           ORDER BY created_at DESC"""
    )
    
    ssa = db_utils.query_all(
        """SELECT admin_id as id, CONCAT(first_name, ' ', last_name) as name, 
           email, 'student-service-admin' as role, is_active as isActive,
           created_at as createdAt
           FROM student_service_admins
           ORDER BY created_at DESC"""
    )
    
    sysadmins = db_utils.query_all(
        """SELECT admin_id as id, CONCAT(first_name, ' ', last_name) as name, 
           email, 'system-admin' as role, is_active as isActive,
           created_at as createdAt
           FROM system_admins
           ORDER BY created_at DESC"""
    )
    
    # Combine all users
    all_users = []
    for user in lecturers + ssa + sysadmins:
        all_users.append({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'isActive': bool(user['isActive']),
            'createdAt': user['createdAt'].strftime('%Y-%m-%d') if user['createdAt'] else None
        })
    
    return jsonify({"ok": True, "users": all_users})

@app.route('/api/users', methods=['POST'])
def add_user():
    """Create new user in database (US24)"""
    payload = request.get_json() or {}
    
    # Get first and last name from payload
    first_name = payload.get('firstName', '')
    last_name = payload.get('lastName', '')
    
    # Fallback: if 'name' field exists, split it
    if not first_name and 'name' in payload:
        name_parts = payload.get('name', '').split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
    email = payload.get('email', '')
    role = payload.get('role', 'lecturer')
    
    # Generate default password hash for 'password'
    default_password = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert into appropriate table based on role
    if role == 'lecturer':
        # Generate lecturer_id
        max_id = db_utils.query_one("SELECT MAX(CAST(SUBSTRING(lecturer_id, 4) AS UNSIGNED)) as max_id FROM lecturers")
        next_num = (max_id['max_id'] or 0) + 1
        user_id = f"LEC{str(next_num).zfill(3)}"
        
        db_utils.execute(
            """INSERT INTO lecturers (lecturer_id, email, password, first_name, last_name, is_active)
               VALUES (%s, %s, %s, %s, %s, TRUE)""",
            (user_id, email, default_password, first_name, last_name)
        )
    elif role == 'student-service-admin':
        max_id = db_utils.query_one("SELECT MAX(CAST(SUBSTRING(admin_id, 4) AS UNSIGNED)) as max_id FROM student_service_admins")
        next_num = (max_id['max_id'] or 0) + 1
        user_id = f"SSA{str(next_num).zfill(3)}"
        
        db_utils.execute(
            """INSERT INTO student_service_admins (admin_id, email, password, first_name, last_name, is_active)
               VALUES (%s, %s, %s, %s, %s, TRUE)""",
            (user_id, email, default_password, first_name, last_name)
        )
    else:  # system-admin
        max_id = db_utils.query_one("SELECT MAX(CAST(SUBSTRING(admin_id, 9) AS UNSIGNED)) as max_id FROM system_admins")
        next_num = (max_id['max_id'] or 0) + 1
        user_id = f"SYSADMIN{str(next_num).zfill(3)}"
        
        db_utils.execute(
            """INSERT INTO system_admins (admin_id, email, password, first_name, last_name, is_active)
               VALUES (%s, %s, %s, %s, %s, TRUE)""",
            (user_id, email, default_password, first_name, last_name)
        )
    
    return jsonify({
        'ok': True,
        'user': {
            'id': user_id,
            'name': f"{first_name} {last_name}",
            'email': email,
            'role': role,
            'isActive': True,
            'createdAt': time.strftime('%Y-%m-%d')
        }
    }), 201

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user in database (US24)"""
    payload = request.get_json() or {}
    
    # Determine current table based on user_id prefix
    if user_id.startswith('LEC'):
        old_table = 'lecturers'
        old_id_col = 'lecturer_id'
        old_role = 'lecturer'
    elif user_id.startswith('SSA'):
        old_table = 'student_service_admins'
        old_id_col = 'admin_id'
        old_role = 'student-service-admin'
    else:
        old_table = 'system_admins'
        old_id_col = 'admin_id'
        old_role = 'system-admin'
    
    # Get current user data
    current_user = db_utils.query_one(
        f"SELECT {old_id_col} as id, first_name, last_name, email, password, is_active FROM {old_table} WHERE {old_id_col} = %s",
        (user_id,)
    )
    
    if not current_user:
        return jsonify({'ok': False, 'error': 'User not found'}), 404
    
    # Parse name updates
    first_name = current_user['first_name']
    last_name = current_user['last_name']
    if 'firstName' in payload:
        first_name = payload['firstName']
    if 'lastName' in payload:
        last_name = payload['lastName']
    if 'name' in payload:
        name_parts = payload['name'].split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    email = payload.get('email', current_user['email'])
    is_active = payload.get('isActive', current_user['is_active'])
    password = current_user['password']
    new_role = payload.get('role', old_role)
    
    # Check if role changed - need to move user between tables
    if new_role != old_role:
        # Determine new table
        if new_role == 'lecturer':
            new_table = 'lecturers'
            new_id_col = 'lecturer_id'
            # Generate new lecturer ID
            new_id = f"LEC{int(time.time() * 1000) % 100000:05d}"
        elif new_role == 'student-service-admin':
            new_table = 'student_service_admins'
            new_id_col = 'admin_id'
            new_id = f"SSA{int(time.time() * 1000) % 100000:05d}"
        else:  # system-admin
            new_table = 'system_admins'
            new_id_col = 'admin_id'
            new_id = f"SYS{int(time.time() * 1000) % 100000:05d}"
        
        # Delete from old table
        db_utils.execute(
            f"DELETE FROM {old_table} WHERE {old_id_col} = %s",
            (user_id,)
        )
        
        # Insert into new table
        db_utils.execute(
            f"INSERT INTO {new_table} ({new_id_col}, first_name, last_name, email, password, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
            (new_id, first_name, last_name, email, password, is_active)
        )
        
        return jsonify({
            'ok': True,
            'user': {
                'id': new_id,
                'name': f"{first_name} {last_name}",
                'email': email,
                'role': new_role,
                'isActive': bool(is_active)
            }
        })
    else:
        # Same role - just update in place
        db_utils.execute(
            f"UPDATE {old_table} SET first_name = %s, last_name = %s, email = %s, is_active = %s WHERE {old_id_col} = %s",
            (first_name, last_name, email, is_active, user_id)
        )
        
        return jsonify({
            'ok': True,
            'user': {
                'id': user_id,
                'name': f"{first_name} {last_name}",
                'email': email,
                'role': old_role,
                'isActive': bool(is_active)
            }
        })

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user from database (US25)"""
    # Determine which table based on user_id prefix
    if user_id.startswith('LEC'):
        table = 'lecturers'
        id_col = 'lecturer_id'
    elif user_id.startswith('SSA'):
        table = 'student_service_admins'
        id_col = 'admin_id'
    else:
        table = 'system_admins'
        id_col = 'admin_id'
    
    # Delete the user from the database
    rows = db_utils.execute(
        f"DELETE FROM {table} WHERE {id_col} = %s",
        (user_id,)
    )
    
    if rows > 0:
        return jsonify({'ok': True, 'message': 'User deleted successfully'})
    return jsonify({'ok': False, 'error': 'User not found'}), 404

# =============================================================================
# PERMISSIONS MANAGEMENT ENDPOINTS (US26)
# =============================================================================

# Permissions are still managed in-memory as they're configuration-level
# In production, these would be stored in a permissions table
permissions = {
    'lecturer': ['view_schedule', 'mark_attendance', 'generate_reports', 'view_students'],
    'student-service-admin': ['mark_attendance', 'adjust_attendance', 'view_audit_log', 'generate_reports', 'upload_class_list'],
    'system-admin': ['all']
}

@app.route('/api/permissions', methods=['GET'])
def get_permissions():
    """Get all role permissions (US26)"""
    return jsonify({"ok": True, "permissions": permissions})

@app.route('/api/permissions/<role>', methods=['PUT'])
def update_permissions(role):
    """Update role permissions (US26)"""
    payload = request.get_json() or {}
    new_permissions = payload.get('permissions', [])
    
    if role in permissions:
        permissions[role] = new_permissions
        return jsonify({'ok': True, 'role': role, 'permissions': new_permissions})
    
    return jsonify({'ok': False, 'error': 'Role not found'}), 404

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'System Admin Controller running'}), 200

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("System Administrator Controller")
    print("=" * 60)
    print("Running on: http://127.0.0.1:5009")
    print("Endpoints:")
    print("  - Auth: /api/auth/*")
    print("  - Policies: /api/policies/*")
    print("  - Devices: /api/devices/*")
    print("  - Users: /api/users/*")
    print("  - Permissions: /api/permissions/*")
    print("=" * 60)

    # Start camera monitoring in background thread
    start_camera_monitoring()

    app.run(debug=True, port=5009, host='127.0.0.1', use_reloader=False)
