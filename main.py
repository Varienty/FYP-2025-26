#!/usr/bin/env python3
"""
Unified Attendance Management System Backend
Simple Flask app for Railway.app deployment

Usage:
  Local: python main.py
  Railway: gunicorn main:app
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
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
    """Root endpoint"""
    return jsonify({
        'message': 'Student Attendance Management System',
        'version': '1.0.0',
        'status': 'running',
        'environment': os.getenv('ENVIRONMENT', 'production')
    }), 200

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

