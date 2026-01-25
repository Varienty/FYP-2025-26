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
import base64
from datetime import date, datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from common.db_utils import get_connection
import bcrypt

# Lazy imports for heavy dependencies (OpenCV, NumPy)
cv2 = None
np = None

# Facial recognition imports (now relocated to a space-free package path)
FACIAL_RECOGNITION_AVAILABLE = False
FaceDetector = None
FaceRecognizer = None
FaceDatabase = None

try:
    from facerec.facial_recognition_controller import FaceDetector, FaceRecognizer, FaceDatabase
    FACIAL_RECOGNITION_AVAILABLE = True
    print("✓ Facial recognition modules imported from package 'facerec'")
except Exception as e:
    print(f"⚠ Facial recognition not available: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    # Dummy classes to prevent crashes when FR is unavailable
    class FaceDetector: pass
    class FaceRecognizer: pass
    class FaceDatabase: pass

# Create Flask app with static and template folders
app = Flask(__name__, 
            static_folder='common',
            static_url_path='/static',
            template_folder='common')
CORS(app, origins="*", supports_credentials=True, allow_headers="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

# ============================================================================
# FACIAL RECOGNITION INITIALIZATION
# ============================================================================

# Initialize facial recognition system on startup
face_detector = None
face_recognizer = None
student_faces = None

def init_facial_recognition():
    """Initialize facial recognition system"""
    global face_detector, face_recognizer, student_faces
    
    if not FACIAL_RECOGNITION_AVAILABLE:
        print("⚠ Facial recognition module not available - will use demo mode")
        return False
    
    try:
        model_dir = os.path.join(os.path.dirname(__file__), 'facerec', 'models')
        print(f"[FR-INIT] Using model directory: {model_dir}")
        print(f"[FR-INIT] Directory exists: {os.path.exists(model_dir)}")
        
        if not os.path.exists(model_dir):
            print("⚠ Model directory not found - facial recognition cannot start")
            return False
        
        # Initialize face detector
        face_detection_model = os.path.join(model_dir, 'face_detection_yunet_2023mar.onnx')
        print(f"[FR-INIT] Face detector model exists: {os.path.exists(face_detection_model)}")
        try:
            if os.path.exists(face_detection_model):
                face_detector = FaceDetector(face_detection_model)
                print("✓ Face detector initialized")
            else:
                print(f"⚠ Face detection model not found: {face_detection_model}")
        except Exception as e:
            print(f"✗ Failed to initialize face detector: {e}")
            import traceback
            traceback.print_exc()
        
        # Initialize face recognizer
        face_recognition_model = os.path.join(model_dir, 'face_recognition_sface_2021dec.onnx')
        print(f"[FR-INIT] Face recognizer model exists: {os.path.exists(face_recognition_model)}")
        try:
            if os.path.exists(face_recognition_model):
                face_recognizer = FaceRecognizer(face_recognition_model)
                print("✓ Face recognizer initialized")
            else:
                print(f"⚠ Face recognition model not found: {face_recognition_model}")
        except Exception as e:
            print(f"✗ Failed to initialize face recognizer: {e}")
            import traceback
            traceback.print_exc()
        
        # Initialize student face database
        try:
            if face_recognizer:
                print("[FR-INIT] Loading student faces from database...")
                student_faces = FaceDatabase(face_recognizer)
                loaded_count = student_faces.load_from_database()
                if loaded_count:
                    print(f"✓ Loaded {student_faces.get_count()} student faces from database")
                else:
                    print("⚠ No student faces loaded from database (may be empty)")
        except Exception as e:
            print(f"✗ Failed to load student face database: {e}")
            import traceback
            traceback.print_exc()
        
        return face_detector is not None and face_recognizer is not None
    except Exception as e:
        print(f"✗ Unexpected error initializing facial recognition: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# HEALTH CHECK & STATUS ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint for load balancer"""
    return jsonify({'status': 'ok', 'service': 'attendance-system'}), 200

# Ensure facial recognition initializes under WSGI (e.g., gunicorn/EB)
try:
    print("[Startup] Initializing facial recognition (import time)...")
    init_facial_recognition()
except Exception as e:
    print(f"⚠ Facial recognition init error: {e}")

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
        raw_policies = cursor.fetchall()
        cursor.close()
        
        # Transform to camelCase for frontend consistency
        policies = []
        for p in raw_policies:
            policies.append({
                'id': p['id'],
                'policyId': p['id'],
                'moduleId': p['entity_id'],
                'policyName': p['policy_name'],
                'appliesTo': p['applies_to'],
                'gracePeriod': p['grace_period_minutes'],
                'lateThreshold': p['late_threshold_minutes'],
                'minAttendance': float(p['minimum_attendance_percentage']) if p['minimum_attendance_percentage'] else None,
                'isActive': bool(p['is_active']),
                'createdAt': p['created_at'].isoformat() if p.get('created_at') else None,
                'updatedAt': p['updated_at'].isoformat() if p.get('updated_at') else None
            })
        
        return jsonify({'ok': True, 'policies': policies}), 200
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
        devices = cursor.fetchall() or []
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
        # Return empty devices list on error instead of 500
        import sys
        print(f"Error loading devices: {str(e)}", file=sys.stderr)
        return jsonify({'ok': True, 'devices': []}), 200
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
        # Return zero stats on error instead of 500
        import sys
        print(f"Error loading device stats: {str(e)}", file=sys.stderr)
        return jsonify({
            'ok': True,
            'stats': {
                'total': 0,
                'online': 0,
                'offline': 0,
                'maintenance': 0,
                'uptime': 0
            }
        }), 200
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
        # Return empty alerts on error instead of 500
        import sys
        print(f"Error loading alerts: {str(e)}", file=sys.stderr)
        return jsonify({'ok': True, 'alerts': []}), 200
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
        cursor.execute("""
            SELECT m.id, m.module_code, m.module_name, m.description, 
                   m.lecturer_id, l.first_name as lecturer_first_name, l.last_name as lecturer_last_name,
                   COALESCE(se.enrolled_count, 0) as enrolled_count,
                   m.academic_year, m.semester, m.credits, m.is_active
            FROM modules m
            LEFT JOIN lecturers l ON m.lecturer_id = l.id
            LEFT JOIN (
                SELECT
                    module_id AS module_id,
                    COUNT(DISTINCT student_id) AS enrolled_count
                FROM student_enrollments
                GROUP BY module_id
            ) se ON se.module_id = m.id
            GROUP BY m.id
            LIMIT 50
        """)
        raw_modules = cursor.fetchall()
        cursor.close()

        # Return both snake_case (for older pages) and camelCase (for newer pages)
        modules = []
        for m in raw_modules:
            enrolled_count = int(m['enrolled_count'] or 0)
            modules.append({
                # Original snake_case fields
                'id': m['id'],
                'module_code': m['module_code'],
                'module_name': m['module_name'],
                'description': m['description'],
                'lecturer_id': m['lecturer_id'],
                'lecturer_first_name': m['lecturer_first_name'],
                'lecturer_last_name': m['lecturer_last_name'],
                'enrolled_count': enrolled_count,
                'semester': m['semester'],
                'credits': m['credits'],
                'is_active': m['is_active'],
                # CamelCase aliases for frontend convenience
                'moduleCode': m['module_code'],
                'moduleName': m['module_name'],
                'lecturerId': m['lecturer_id'],
                'lecturerFirstName': m['lecturer_first_name'],
                'lecturerLastName': m['lecturer_last_name'],
                'enrolledCount': enrolled_count,
                'isActive': bool(m['is_active']) if m['is_active'] is not None else None
            })

        return jsonify({'ok': True, 'modules': modules}), 200
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
        cursor.execute("""
            SELECT id, lecturer_id, email, first_name, last_name, department, 
                   phone, is_active, created_at
            FROM lecturers 
            LIMIT 50
        """)
        raw_lecturers = cursor.fetchall()
        cursor.close()

        lecturers = []
        for l in raw_lecturers:
            lecturers.append({
                'id': l['id'],
                'lecturer_id': l['lecturer_id'],
                'email': l['email'],
                'first_name': l['first_name'],
                'last_name': l['last_name'],
                'department': l['department'],
                'phone': l['phone'],
                'is_active': l['is_active'],
                'created_at': l['created_at'].isoformat() if l.get('created_at') else None,
                # CamelCase aliases
                'lecturerId': l['lecturer_id'],
                'firstName': l['first_name'],
                'lastName': l['last_name'],
                'isActive': bool(l['is_active']) if l['is_active'] is not None else None,
                'createdAt': l['created_at'].isoformat() if l.get('created_at') else None
            })

        return jsonify({'ok': True, 'lecturers': lecturers}), 200
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
        cursor.execute("""
            SELECT id, student_id, email, first_name, last_name, phone, 
                   program, intake_period, intake_year, academic_year, level, is_active, created_at
            FROM students 
            LIMIT 100
        """)
        raw_students = cursor.fetchall()
        cursor.close()

        students = []
        for s in raw_students:
            students.append({
                'id': s['id'],
                'student_id': s['student_id'],
                'email': s['email'],
                'first_name': s['first_name'],
                'last_name': s['last_name'],
                'phone': s['phone'],
                'program': s['program'],
                'intake_period': s['intake_period'],
                'intake_year': s['intake_year'],
                'academic_year': s['academic_year'],
                'level': s['level'],
                'is_active': s['is_active'],
                'created_at': s['created_at'].isoformat() if s.get('created_at') else None,
                # CamelCase aliases
                'studentId': s['student_id'],
                'firstName': s['first_name'],
                'lastName': s['last_name'],
                'intakePeriod': s['intake_period'],
                'intakeYear': s['intake_year'],
                'academicYear': s['academic_year'],
                'isActive': bool(s['is_active']) if s['is_active'] is not None else None,
                'createdAt': s['created_at'].isoformat() if s.get('created_at') else None
            })

        return jsonify({'ok': True, 'students': students}), 200
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
            SELECT s.id, s.student_id, s.email, s.first_name, s.last_name, s.phone,
                   s.program, s.intake_period, s.intake_year, s.academic_year, s.level, s.is_active,
                   se.enrollment_date, se.status
            FROM students s
            INNER JOIN student_enrollments se ON s.id = se.student_id
            WHERE se.module_id = %s
            ORDER BY s.student_id
        """, (module_id,))
        raw_students = cursor.fetchall()
        cursor.close()

        students = []
        for s in raw_students:
            students.append({
                'id': s['id'],
                'student_id': s['student_id'],
                'email': s['email'],
                'first_name': s['first_name'],
                'last_name': s['last_name'],
                'phone': s['phone'],
                'program': s['program'],
                'intake_period': s['intake_period'],
                'intake_year': s['intake_year'],
                'academic_year': s['academic_year'],
                'level': s['level'],
                'is_active': s['is_active'],
                'enrollment_date': s['enrollment_date'].isoformat() if s.get('enrollment_date') else None,
                'status': s['status'],
                # CamelCase aliases
                'studentId': s['student_id'],
                'firstName': s['first_name'],
                'lastName': s['last_name'],
                'intakePeriod': s['intake_period'],
                'intakeYear': s['intake_year'],
                'academicYear': s['academic_year'],
                'isActive': bool(s['is_active']) if s['is_active'] is not None else None,
                'enrollmentDate': s['enrollment_date'].isoformat() if s.get('enrollment_date') else None
            })

        return jsonify({'ok': True, 'students': students}), 200
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
                    "INSERT INTO student_enrollments (module_id, student_id) VALUES (%s, %s)",
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
        cursor.execute("DELETE FROM student_enrollments WHERE module_id = %s AND student_id = %s", (module_id, student_id))
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
        cursor.execute("""
            SELECT id, module_id, day_of_week, 
                   TIME_FORMAT(start_time, '%H:%i') as start_time,
                   TIME_FORMAT(end_time, '%H:%i') as end_time,
                   room, is_active
            FROM timetable 
            LIMIT 50
        """)
        raw_timetable = cursor.fetchall()
        cursor.close()

        timetable = []
        for t in raw_timetable:
            timetable.append({
                'id': t['id'],
                'module_id': t['module_id'],
                'day_of_week': t['day_of_week'],
                'start_time': t['start_time'],
                'end_time': t['end_time'],
                'room': t['room'],
                'is_active': t['is_active'],
                # CamelCase aliases
                'moduleId': t['module_id'],
                'dayOfWeek': t['day_of_week'],
                'startTime': t['start_time'],
                'endTime': t['end_time'],
                'isActive': bool(t['is_active']) if t['is_active'] is not None else None
            })

        return jsonify({'ok': True, 'timetable': timetable}), 200
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
        cursor.execute("SELECT id, module_code as code, module_name as name FROM modules LIMIT 50")
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
            SELECT DATE(check_in_time) as date, COUNT(*) as total_records,
                   SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                   SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent
            FROM attendance
            WHERE check_in_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(check_in_time)
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
        cursor.execute("SELECT id, module_code as code, module_name as name FROM modules LIMIT 20")
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
                   m.module_code as class_code, a.status, a.check_in_time
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            INNER JOIN modules m ON a.module_id = m.id
            WHERE a.check_in_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY a.check_in_time DESC
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
            SELECT m.id, m.module_code as code, m.module_name as name,
                   COUNT(a.id) as total_attendance_records,
                   SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count
            FROM modules m
            LEFT JOIN attendance a ON m.id = a.module_id
            GROUP BY m.id, m.module_code, m.module_name
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
                ROUND(SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as avg
            FROM attendance
            WHERE check_in_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
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
# FACIAL RECOGNITION STUB ENDPOINTS (For System Admin page compatibility)
# ============================================================================
# These endpoints provide graceful degradation for the facial recognition UI
# Full facial recognition requires OpenCV and camera hardware setup on the server

@app.route('/api/facial-recognition/camera/start', methods=['POST'])
def facial_recognition_camera_start():
    """Stub: Start camera feed"""
    return jsonify({'ok': False, 'error': 'Facial recognition not available in this deployment. System requires OpenCV and camera hardware setup.'}), 503

@app.route('/api/facial-recognition/camera/stop', methods=['POST'])
def facial_recognition_camera_stop():
    """Stub: Stop camera feed"""
    return jsonify({'ok': True, 'message': 'Camera stopped'}), 200

@app.route('/api/facial-recognition/camera/status', methods=['GET'])
def facial_recognition_camera_status():
    """Stub: Get camera status"""
    return jsonify({'ok': True, 'status': 'offline', 'message': 'Camera not available'}), 200

@app.route('/api/facial-recognition/camera/feed')
def facial_recognition_camera_feed():
    """Stub: Camera feed stream"""
    return jsonify({'error': 'Facial recognition not available'}), 503

@app.route('/api/facial-recognition/scanning/start', methods=['POST'])
def facial_recognition_scanning_start():
    """Stub: Start scanning"""
    return jsonify({'ok': False, 'error': 'Facial recognition not available'}), 503

@app.route('/api/facial-recognition/scanning/stop', methods=['POST'])
def facial_recognition_scanning_stop():
    """Stub: Stop scanning"""
    return jsonify({'ok': True, 'message': 'Scanning stopped'}), 200

@app.route('/api/facial-recognition/faces/refresh', methods=['POST'])
def facial_recognition_faces_refresh():
    """Stub: Refresh face database"""
    return jsonify({'ok': False, 'error': 'Facial recognition not available'}), 503

@app.route('/api/facial-recognition/faces/list', methods=['GET'])
def facial_recognition_faces_list():
    """Stub: List recognized faces"""
    return jsonify({'ok': True, 'faces': []}), 200

def _get_current_timetable():
    """Get today's first active timetable entry with module metadata."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Determine today's weekday name (e.g., 'Monday')
        from datetime import datetime
        today = datetime.now()
        weekday = today.strftime('%A')

        cursor.execute(
            """
            SELECT t.id AS timetable_id,
                   t.module_id,
                   m.module_code,
                   m.module_name,
                   m.description,
                   t.day_of_week,
                   t.start_time,
                   t.end_time,
                   t.room,
                   (
                       SELECT COUNT(*)
                       FROM student_enrollments se
                       WHERE se.module_id = t.module_id
                   ) AS enrolled_count
            FROM timetable t
            JOIN modules m ON t.module_id = m.id
            WHERE t.is_active = 1 AND m.is_active = 1 AND t.day_of_week = %s
            ORDER BY t.start_time ASC
            LIMIT 1
            """,
            (weekday,),
        )
        row = cursor.fetchone()
        cursor.close()
        return row
    except Exception:
        # Graceful fallback when DB is unreachable or schema mismatch
        return None
    finally:
        if conn:
            conn.close()


@app.route('/api/facial-recognition/session', methods=['GET'])
def facial_recognition_session():
    """Return current session snapshot used by polling UI."""
    session = _get_current_timetable()
    if not session:
        return jsonify({'ok': False, 'error': 'No active session today'}), 404

    return jsonify({
        'ok': True,
        'session': {
            'session_id': session['timetable_id'],
            'timetable_id': session['timetable_id'],
            'module_id': session['module_id'],
            'class_id': session['module_id'],  # Backward compatibility
            'module_code': session['module_code'],
            'module_name': session['module_name'],
            'date': str(date.today()),
            'time': str(session['start_time']) if session['start_time'] else None,
            'end_time': str(session['end_time']) if session['end_time'] else None,
            'room': session['room'],
            'enrolled_count': int(session['enrolled_count'] or 0),
            'recognized_students': [],
            'is_live': True,
        },
    }), 200


@app.route('/api/facial-recognition/sessions/current', methods=['GET'])
def facial_recognition_sessions_current():
    """Return the current (or next) timetable session for today."""
    try:
        session = _get_current_timetable()
        if not session:
            return jsonify({'ok': False, 'message': 'No sessions scheduled for today'}), 200

        return jsonify({
            'ok': True,
            'session': {
                'session_id': session['timetable_id'],
                'timetable_id': session['timetable_id'],
                'module_id': session['module_id'],
                'class_id': session['module_id'],  # Backward compatibility
                'module_code': session['module_code'],
                'module_name': session['module_name'],
                'date': str(date.today()),
                'time': str(session['start_time']) if session['start_time'] else None,
                'end_time': str(session['end_time']) if session['end_time'] else None,
                'room': session['room'],
                'enrolled_count': int(session['enrolled_count'] or 0),
                'is_live': True,
            },
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'message': 'Session lookup failed', 'error': str(e)}), 200


@app.route('/api/facial-recognition/attendance/save-one', methods=['POST'])
def facial_recognition_attendance_save_one():
    """Persist a single attendance record linked to timetable/module."""
    conn = None
    try:
        data = request.get_json() or {}
        student_code = data.get('student_id')
        timetable_id = data.get('timetable_id') or data.get('session_id')
        module_id = data.get('module_id') or data.get('class_id')
        confidence = data.get('confidence')

        if not student_code or not module_id:
            return jsonify({'ok': False, 'error': 'student_id and module_id are required'}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM students WHERE student_id = %s", (student_code,))
        student_row = cursor.fetchone()
        if not student_row:
            return jsonify({'ok': False, 'error': 'Student not found'}), 404

        student_pk = student_row['id']

        # Ensure module exists
        cursor.execute("SELECT id FROM modules WHERE id = %s", (module_id,))
        module_row = cursor.fetchone()
        if not module_row:
            return jsonify({'ok': False, 'error': 'Module not found'}), 404

        # Insert attendance
        cursor.execute(
            """
            INSERT INTO attendance (student_id, module_id, timetable_id, status, face_confidence, is_manual)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (student_pk, module_id, timetable_id, 'present', confidence, False),
        )
        conn.commit()

        return jsonify({'ok': True, 'status': 'present'}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/facial-recognition/attendance/today', methods=['GET'])
def facial_recognition_attendance_today():
    """Return today's attendance for a given class (class_id query param)."""
    class_id = request.args.get('class_id', type=int)
    if not class_id:
        return jsonify({'ok': False, 'error': 'class_id is required'}), 400

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.id, s.student_id, CONCAT(s.first_name, ' ', s.last_name) AS name,
                   a.status, a.face_confidence, a.check_in_time
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.class_id = %s AND DATE(a.check_in_time) = CURDATE()
            ORDER BY a.check_in_time DESC
            """,
            (class_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return jsonify({'ok': True, 'students': rows}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/facial-recognition/attendance/reset', methods=['POST'])
def facial_recognition_attendance_reset():
    """Delete today's attendance for a class (for testing)."""
    data = request.get_json() or {}
    class_id = data.get('class_id') or data.get('module_id')
    if not class_id:
        return jsonify({'ok': False, 'error': 'class_id is required'}), 400

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM attendance WHERE class_id = %s AND DATE(check_in_time) = CURDATE()",
            (class_id,),
        )
        conn.commit()
        cursor.close()
        return jsonify({'ok': True}), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/facial-recognition/attendance/session', methods=['GET'])
def facial_recognition_attendance_session():
    """Return attendance for a specific timetable session."""
    timetable_id = request.args.get('timetable_id', type=int)
    if not timetable_id:
        return jsonify({'ok': False, 'error': 'timetable_id is required'}), 400

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.id, s.student_id, CONCAT(s.first_name, ' ', s.last_name) AS name,
                   a.status, a.face_confidence, a.check_in_time
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.timetable_id = %s
            ORDER BY a.check_in_time DESC
            """,
            (timetable_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return jsonify({'ok': True, 'students': rows}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/facial-recognition/timetable/all', methods=['GET'])
def facial_recognition_timetable_all():
    """Stub: Get all timetable entries"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.class_id, c.class_code, c.class_name, 
                   t.day_of_week, t.start_time, t.end_time, t.room
            FROM timetable t
            JOIN classes c ON t.class_id = c.id
            ORDER BY t.day_of_week, t.start_time
        """)
        timetables = cursor.fetchall()
        cursor.close()
        
        result = []
        for t in timetables:
            result.append({
                'id': t['id'],
                'classId': t['class_id'],
                'classCode': t['class_code'],
                'className': t['class_name'],
                'dayOfWeek': t['day_of_week'],
                'startTime': str(t['start_time']) if t['start_time'] else None,
                'endTime': str(t['end_time']) if t['end_time'] else None,
                'room': t['room']
            })
        
        return jsonify({'ok': True, 'timetables': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/facial-recognition/identify', methods=['POST'])
def facial_recognition_identify():
    """Identify student from face image using AI facial recognition"""
    global cv2, np
    
    # Lazy load OpenCV and NumPy only when needed
    if cv2 is None:
        try:
            import cv2 as cv2_module
            cv2 = cv2_module
        except ImportError:
            cv2 = None
    
    if np is None:
        try:
            import numpy as np_module
            np = np_module
        except ImportError:
            np = None
    
    try:
        data = request.get_json()
        image_data = data.get('image')
        confidence_threshold = data.get('confidence', 0.5)
        
        if not image_data:
            return jsonify({'ok': False, 'error': 'No image provided'}), 400
        
        # Check if facial recognition is available
        if not FACIAL_RECOGNITION_AVAILABLE or not all([face_detector, face_recognizer, student_faces]):
            print(f"[IDENTIFY] FR check - FACIAL_RECOGNITION_AVAILABLE={FACIAL_RECOGNITION_AVAILABLE}, detector={face_detector}, recognizer={face_recognizer}, student_faces={student_faces}")
            return jsonify({
                'ok': False,
                'error': 'Facial recognition not initialized on server',
                'faces_found': 0,
                'debug': {
                    'FR_AVAILABLE': FACIAL_RECOGNITION_AVAILABLE,
                    'detector': 'loaded' if face_detector else 'None',
                    'recognizer': 'loaded' if face_recognizer else 'None',
                    'student_faces': f'loaded:{student_faces.get_count()}' if student_faces else 'None'
                }
            }), 200
        
        # Check if OpenCV is available
        if cv2 is None or np is None:
            print("⚠ OpenCV/NumPy not available, returning demo data")
            if confidence_threshold > 0.7:
                demo_students = [
                    {'student_id': 'S9001', 'name': 'Alice Tester'},
                    {'student_id': 'S9002', 'name': 'Bob Tester'},
                ]
                import random
                return jsonify({
                    'ok': True,
                    'student': random.choice(demo_students),
                    'message': 'Demo mode - OpenCV not available'
                }), 200
        
        print("[IDENTIFY] Processing frame...")
        # Decode base64 image
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return jsonify({'ok': False, 'error': 'Invalid image data'}), 400
            
            print(f"[IDENTIFY] Frame decoded: {frame.shape}")
        except Exception as e:
            print(f"[IDENTIFY] Error decoding image: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'ok': False, 'error': 'Failed to decode image'}), 400
        
        # Detect faces in the image
        print(f"[IDENTIFY] Detecting faces...")
        faces = face_detector.detect(frame)
        print(f"[IDENTIFY] Faces detected: {len(faces) if faces else 0}")
        
        if faces is None or len(faces) == 0:
            return jsonify({
                'ok': False,
                'error': 'No face detected in image',
                'faces_found': 0
            }), 400
        
        # Get the largest/clearest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])  # By area (width * height)
        x, y, w, h = map(int, largest_face[:4])
        
        # Extract face region
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return jsonify({
                'ok': False,
                'error': 'Could not extract face region'
            }), 400
        
        # Get face feature/encoding using pre-cropped face image (works without landmarks)
        face_feature = face_recognizer.extract_features_from_image(face_roi)
        
        if face_feature is None:
            return jsonify({
                'ok': False,
                'error': 'Could not extract face features'
            }), 400
        
        # Find matching student
        # Use tuned thresholds from controller: threshold=0.25 for better matching
        match = student_faces.find_match(face_feature, threshold=0.25, min_confidence_gap=0.02)
        
        if match:
            student_id, name, similarity = match
            return jsonify({
                'ok': True,
                'student': {
                    'student_id': student_id,
                    'name': name
                },
                'confidence': float(similarity),
                'message': 'Face matched successfully'
            }), 200
        else:
            return jsonify({
                'ok': False,
                'error': 'No matching student found',
                'message': 'Face not recognized in database'
            }), 400
    
    except Exception as e:
        print(f"Error in facial recognition identify: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Initialize facial recognition system (optional - won't crash if it fails)
    try:
        print("\n" + "="*60)
        print("Initializing facial recognition system...")
        init_facial_recognition()
        print("="*60 + "\n")
    except Exception as e:
        print(f"⚠ Facial recognition initialization error (continuing anyway): {e}")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    print(f"Starting Flask app on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)


