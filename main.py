#!/usr/bin/env python3
"""
Unified Attendance Management System Backend
Simple Flask app for Railway.app deployment

Usage:
  Local: python main.py
  Railway: gunicorn main:app
"""

import os
from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS

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

@app.route('/', methods=['GET'])
def index():
    """Serve login page"""
    try:
        return send_file('login.html')
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
# LECTURER API ENDPOINTS
# ============================================================================

@app.route('/api/lecturer/auth/login', methods=['POST'])
def login():
    """Placeholder for lecturer login"""
    return jsonify({'error': 'API backend configured'}), 200

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
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

