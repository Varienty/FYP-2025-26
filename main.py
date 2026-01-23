#!/usr/bin/env python3
"""
Unified Attendance Management System Backend
Simple Flask app for Railway.app deployment

Usage:
  Local: python main.py
  Railway: gunicorn main:app
"""

import os
import json
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from common.db_utils import get_connection
import bcrypt

# Create Flask app with static and template folders
app = Flask(__name__, 
            static_folder='common',
            static_url_path='/static',
            template_folder='common')
CORS(app, origins="*", supports_credentials=True, allow_headers="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

# ============================================================================
# HEALTH CHECK & STATUS ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint for load balancer"""
    return jsonify({'status': 'ok', 'service': 'attendance-system'}), 200

@app.route('/health/db', methods=['GET'])
def health_db():
    """Check database connectivity and basic status"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'db': 'ok'}), 200
    except Exception as e:
        return jsonify({'db': 'error', 'message': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Serve login page"""
    try:
        return send_from_directory('common', 'login.html')
    except FileNotFoundError:
        return jsonify({
            'message': 'Student Attendance Management System',
            'version': '1.0.0',
            'status': 'running',
            'note': 'login.html not found'
        }), 200

@app.route('/debug', methods=['GET'])
def debug_page():
    """Serve debug test page"""
    try:
        return send_from_directory('.', 'debug_test.html')
    except FileNotFoundError:
        return jsonify({'error': 'Debug page not found'}), 404

# Serve static files (CSS, JS, images, etc.)
@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files from common folder"""
    return send_from_directory('common', filename)

# Serve common files at /common/ path (for scripts loaded by HTML pages)
@app.route('/common/<path:filename>', methods=['GET'])
def serve_common(filename):
    """Serve common files from common folder"""
    return send_from_directory('common', filename)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user - check all user types"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Try Student Service Admin
        cursor.execute("SELECT id, admin_id as user_id, 'ssa' as role, password, first_name, last_name FROM student_service_admins WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            # Try System Admin
            cursor.execute("SELECT id, admin_id as user_id, 'sysadmin' as role, password, first_name, last_name FROM system_admins WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if not user:
            # Try Lecturer
            cursor.execute("SELECT id, lecturer_id as user_id, 'lecturer' as role, password, first_name, last_name FROM lecturers WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        if not user:
            # Try Student
            cursor.execute("SELECT id, student_id as user_id, 'student' as role, password, first_name, last_name FROM students WHERE email = %s", (email,))
            user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password (bcrypt hash comparison)
        # Note: The sample data uses bcrypt hashes. For testing, you can use plain 'password' 
        # or properly hash new passwords with bcrypt
        stored_hash = user.get('password', '')
        
        # Check if it's a bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if stored_hash.startswith('$2'):
            # Verify bcrypt hash
            password_match = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        else:
            # Fallback: plain text comparison (for testing)
            password_match = password == stored_hash
        
        if not password_match:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Return user info
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'user_id': user['user_id'],
                'role': user['role'],
                'email': email,
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    return jsonify({'success': True, 'message': 'Logged out'}), 200

# ============================================================================
# LECTURER API ENDPOINTS
# ============================================================================

@app.route('/api/lecturer/dashboard', methods=['GET'])
def lecturer_dashboard():
    """Placeholder for lecturer dashboard"""
    return jsonify({'message': 'Lecturer dashboard'}), 200

@app.route('/api/lecturer/attendance', methods=['GET'])
def lecturer_attendance():
    """Get attendance for lecturer's classes"""
    return jsonify({'message': 'Lecturer attendance'}), 200

# ============================================================================
# STUDENT SERVICE ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/ssa/attendance', methods=['GET'])
def ssa_attendance():
    """Placeholder for SSA attendance"""
    return jsonify({'message': 'SSA attendance endpoint'}), 200

@app.route('/api/ssa/reports', methods=['GET'])
def ssa_reports():
    """Placeholder for SSA reports"""
    return jsonify({'message': 'SSA reports endpoint'}), 200

# ============================================================================
# SYSTEM ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/policies', methods=['GET'])
def get_policies():
    """Get all attendance policies"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attendance_policies ORDER BY id LIMIT 100")
        policies = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'policies': policies or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all hardware devices with status from database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, type, status, last_seen as lastSeen, latency_ms as latencyMs, 
                   created_at as createdAt
            FROM devices
            ORDER BY name
        """)
        devices = cursor.fetchall()
        cursor.close()
        
        # Convert to expected format
        result = []
        for d in devices:
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
        
        return jsonify({'ok': True, 'devices': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device status in database"""
    conn = None
    try:
        payload = request.get_json() or {}
        
        # Build update query
        updates = []
        params = []
        
        if 'status' in payload:
            updates.append("status = %s")
            params.append(payload['status'])
            if payload['status'] == 'online':
                updates.append("last_seen = NOW()")
        if 'name' in payload:
            updates.append("name = %s")
            params.append(payload['name'])
        
        if not updates:
            return jsonify({'ok': False, 'error': 'No fields to update'}), 400
        
        params.append(device_id)
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"UPDATE devices SET {', '.join(updates)} WHERE id = %s", tuple(params))
        conn.commit()
        rows = cursor.rowcount
        
        if rows == 0:
            cursor.close()
            return jsonify({'ok': False, 'error': 'Device not found'}), 404
        
        # Return updated device
        cursor.execute(
            "SELECT id, name, type, status, last_seen, latency_ms FROM devices WHERE id = %s",
            (device_id,)
        )
        updated = cursor.fetchone()
        cursor.close()
        
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
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/devices/stats', methods=['GET'])
def get_device_stats():
    """Get device/hardware statistics"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
               COUNT(*) as total,
               SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online,
               SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) as offline,
               SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
            FROM devices
        """)
        stats = cursor.fetchone()
        cursor.close()
        
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
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get active system alerts from database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, alert_type, severity, title, description, device_id, status,
                   created_at, acknowledged_by, acknowledged_at, resolved_at
            FROM system_alerts
            WHERE status IN ('new', 'acknowledged')
            ORDER BY created_at DESC
            LIMIT 50
        """)
        alerts = cursor.fetchall()
        cursor.close()
        
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
        
        return jsonify({'ok': True, 'alerts': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all staff/admin users"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get system admins and SSAs
        cursor.execute("""
            SELECT id, first_name, last_name, email, 'system_admin' as role, 1 as isActive 
            FROM system_admins
            UNION ALL
            SELECT id, first_name, last_name, email, 'ssa' as role, 1 as isActive
            FROM student_service_admins
            UNION ALL
            SELECT id, first_name, last_name, email, 'lecturer' as role, 1 as isActive
            FROM lecturers
            LIMIT 50
        """)
        users = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'users': users or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user account"""
    conn = None
    try:
        data = request.get_json()
        userRole = data.get('userRole', '')
        email = data.get('email', '')
        first_name = data.get('name', '').split()[0] if data.get('name') else ''
        last_name = data.get('name', '').split()[-1] if data.get('name') else ''
        password = data.get('password', '')
        user_id = data.get('userID', '')
        
        if not all([userRole, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if userRole == 'Lecturer':
            cursor.execute(
                "INSERT INTO lecturers (lecturer_id, email, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s)",
                (user_id, email, password_hash, first_name, last_name)
            )
        elif userRole == 'StudentServiceAdmin':
            cursor.execute(
                "INSERT INTO student_service_admins (admin_id, email, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s)",
                (user_id, email, password_hash, first_name, last_name)
            )
        elif userRole == 'SystemAdministrator':
            cursor.execute(
                "INSERT INTO system_admins (admin_id, email, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s)",
                (user_id, email, password_hash, first_name, last_name)
            )
        
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# STUDENT SERVICE ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/ssa/modules', methods=['GET'])
def get_ssa_modules():
    """Get all modules for SSA"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, class_code as code, class_name as name FROM modules LIMIT 50")
        modules = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'modules': modules or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/lecturers', methods=['GET'])
def get_ssa_lecturers():
    """Get all lecturers for SSA"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, lecturer_id, email, first_name, last_name FROM lecturers LIMIT 50")
        lecturers = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'lecturers': lecturers or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/students', methods=['GET'])
def get_ssa_students():
    """Get all students for SSA"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, student_id, email, first_name, last_name FROM students LIMIT 100")
        students = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'students': students or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/ssa/modules/<int:module_id>/students', methods=['GET'])
def get_module_students(module_id):
    """Get students enrolled in a specific module"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.student_id, s.email, s.first_name, s.last_name
            FROM students s
            INNER JOIN module_enrollments me ON s.id = me.student_id
            WHERE me.module_id = %s
        """, (module_id,))
        students = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'students': students or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/modules/<int:module_id>/assign-lecturer', methods=['POST'])
def assign_lecturer_to_module(module_id):
    """Assign lecturer to a module"""
    conn = None
    try:
        data = request.get_json()
        lecturer_id = data.get('lecturer_id')
        
        if not lecturer_id:
            return jsonify({'error': 'lecturer_id required'}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE modules SET lecturer_id = %s WHERE id = %s", (lecturer_id, module_id))
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': 'Lecturer assigned'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/modules/<int:module_id>/enroll', methods=['POST'])
def enroll_students(module_id):
    """Enroll students in a module"""
    conn = None
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'error': 'student_ids required'}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        for student_id in student_ids:
            try:
                cursor.execute(
                    "INSERT INTO module_enrollments (module_id, student_id) VALUES (%s, %s)",
                    (module_id, student_id)
                )
            except:
                pass  # Skip if already enrolled
        
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': f'{len(student_ids)} students enrolled'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/modules/<int:module_id>/unenroll/<int:student_id>', methods=['POST', 'DELETE'])
def unenroll_student(module_id, student_id):
    """Remove student from a module"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM module_enrollments WHERE module_id = %s AND student_id = %s", (module_id, student_id))
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': 'Student unenrolled'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/timetable', methods=['GET'])
def get_timetable():
    """Get timetable"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM timetable LIMIT 50")
        timetable = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'timetable': timetable or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/timetable', methods=['POST'])
def create_timetable_entry():
    """Create timetable entry"""
    conn = None
    try:
        data = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO timetable (module_id, day, start_time, end_time, room)
            VALUES (%s, %s, %s, %s, %s)
        """, (data.get('module_id'), data.get('day'), data.get('start_time'), data.get('end_time'), data.get('room')))
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': 'Timetable entry created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/ssa/timetable/<int:entry_id>', methods=['DELETE'])
def delete_timetable_entry(entry_id):
    """Delete timetable entry"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timetable WHERE id = %s", (entry_id,))
        conn.commit()
        cursor.close()
        return jsonify({'ok': True, 'message': 'Timetable entry deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/attendance/classes', methods=['GET'])
def get_attendance_classes():
    """Get classes for attendance tracking"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, class_code as code, class_name as name FROM modules LIMIT 50")
        classes = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'classes': classes or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/attendance/daily-summary', methods=['GET'])
def get_daily_summary():
    """Get daily attendance summary"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DATE(attendance_date) as date, COUNT(*) as total_records,
                   SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
            FROM attendance
            WHERE attendance_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(attendance_date)
            ORDER BY date DESC
            LIMIT 30
        """)
        summary = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'summary': summary or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# LECTURER ENDPOINTS
# ============================================================================

@app.route('/api/lecturer/classes', methods=['GET'])
def get_lecturer_classes():
    """Get classes assigned to the lecturer"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, class_code as code, class_name as name FROM modules LIMIT 20")
        classes = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'classes': classes or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/lecturer/attendance', methods=['GET'])
def get_lecturer_attendance():
    """Get attendance records for lecturer's classes"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id, s.student_id, s.first_name, s.last_name, 
                   m.code as class_code, a.status, a.attendance_date
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            INNER JOIN modules m ON a.module_id = m.id
            WHERE a.attendance_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY a.attendance_date DESC
            LIMIT 100
        """)
        records = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'records': records or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/lecturer/reports', methods=['GET'])
def get_lecturer_reports():
    """Get attendance reports"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.id, m.class_code as code, m.class_name as name,
                   COUNT(a.id) as total_attendance_records,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count
            FROM modules m
            LEFT JOIN attendance a ON m.id = a.class_id
            GROUP BY m.id, m.class_code, m.class_name
            LIMIT 20
        """)
        reports = cursor.fetchall()
        cursor.close()
        return jsonify({'ok': True, 'reports': reports or []}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/lecturer/notifications', methods=['GET'])
def get_lecturer_notifications():
    """Get notifications for lecturer"""
    try:
        # Return mock data for now
        return jsonify({
            'ok': True,
            'notifications': [
                {'id': 1, 'message': 'Your attendance session has ended', 'date': '2026-01-22'},
                {'id': 2, 'message': 'Weekly attendance report ready', 'date': '2026-01-20'}
            ]
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/lecturer/dashboard/stats', methods=['GET'])
def get_lecturer_dashboard_stats():
    """Get dashboard statistics for lecturer"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total classes
        cursor.execute("SELECT COUNT(*) as total FROM modules")
        total_classes = cursor.fetchone()['total'] or 0
        
        # Get today's classes
        cursor.execute("""
            SELECT COUNT(*) as total FROM timetable 
            WHERE DAYNAME(NOW()) LIKE day
        """)
        today_classes = cursor.fetchone()['total'] or 0
        
        # Get average attendance
        cursor.execute("""
            SELECT 
                ROUND(SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as avg
            FROM attendance
            WHERE attendance_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        result = cursor.fetchone()
        avg_attendance = result['avg'] or 0 if result and result['avg'] else 0
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'totalClasses': total_classes,
                'todayClasses': today_classes,
                'avgAttendance': avg_attendance,
                'activeSessions': 0
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/lecturer/notifications/subscribe', methods=['POST'])
def subscribe_notifications():
    """Subscribe to notifications"""
    try:
        data = request.get_json()
        return jsonify({'ok': True, 'message': 'Subscribed to notifications'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lecturer/notifications/generate-reminders', methods=['POST'])
def generate_notification_reminders():
    """Generate class reminders"""
    try:
        return jsonify({'ok': True, 'message': 'Reminders generated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# SERVE DASHBOARD PAGES & BOUNDARY FILES (MUST BE AFTER API ROUTES)
# ============================================================================

# System Administrator pages (use literal spaces; Flask matches URL-encoded '%20' too)
@app.route('/System Administrator/boundary/<path:filename>', methods=['GET'])
@app.route('/System Administrator/boundary', methods=['GET'], defaults={'filename': 'dashboard.html'})
# Also support links without '/boundary' prefix
@app.route('/System Administrator/<path:filename>', methods=['GET'])
def serve_sysadmin_page(filename='dashboard.html'):
    """Serve System Admin pages"""
    try:
        return send_from_directory('System Administrator/boundary', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404

# Student Service Administrator pages (literal spaces)
@app.route('/Student Service Administrator/boundary/<path:filename>', methods=['GET'])
@app.route('/Student Service Administrator/boundary', methods=['GET'], defaults={'filename': 'dashboard.html'})
# Also support links without '/boundary' prefix
@app.route('/Student Service Administrator/<path:filename>', methods=['GET'])
def serve_ssa_page(filename='dashboard.html'):
    """Serve SSA pages"""
    try:
        return send_from_directory('Student Service Administrator/boundary', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404

# Lecturer pages
@app.route('/Lecturer/boundary/<path:filename>', methods=['GET'])
@app.route('/Lecturer/boundary', methods=['GET'], defaults={'filename': 'dashboard.html'})
# Also support links without '/boundary' prefix
@app.route('/Lecturer/<path:filename>', methods=['GET'])
def serve_lecturer_page(filename='dashboard.html'):
    """Serve Lecturer pages"""
    try:
        return send_from_directory('Lecturer/boundary', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404

# Common auth pages (forgot_password, reset_password) - CATCH-ALL FOR HTML
@app.route('/<path:filename>', methods=['GET'])
def serve_common_page(filename):
    """Serve common pages (forgot_password.html, reset_password.html, etc.)"""
    if filename.endswith('.html'):
        try:
            return send_from_directory('common', filename)
        except FileNotFoundError:
            return jsonify({'error': 'Page not found'}), 404
    return jsonify({'error': 'Not found'}), 404

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)


