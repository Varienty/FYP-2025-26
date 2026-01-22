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

# Serve static files (CSS, JS, images, etc.)
@app.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    """Serve static files from common folder"""
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

@app.route('/api/sysadmin/dashboard', methods=['GET'])
def sysadmin_dashboard():
    """Placeholder for system admin dashboard"""
    return jsonify({'message': 'System admin dashboard'}), 200

@app.route('/api/sysadmin/users', methods=['GET'])
def sysadmin_users():
    """Placeholder for user management"""
    return jsonify({'message': 'User management endpoint'}), 200

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
def serve_sysadmin_page(filename='dashboard.html'):
    """Serve System Admin pages"""
    try:
        return send_from_directory('System Administrator/boundary', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404

# Student Service Administrator pages (literal spaces)
@app.route('/Student Service Administrator/boundary/<path:filename>', methods=['GET'])
@app.route('/Student Service Administrator/boundary', methods=['GET'], defaults={'filename': 'dashboard.html'})
def serve_ssa_page(filename='dashboard.html'):
    """Serve SSA pages"""
    try:
        return send_from_directory('Student Service Administrator/boundary', filename)
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404

# Lecturer pages
@app.route('/Lecturer/boundary/<path:filename>', methods=['GET'])
@app.route('/Lecturer/boundary', methods=['GET'], defaults={'filename': 'dashboard.html'})
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


