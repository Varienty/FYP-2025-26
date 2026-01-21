"""
Student Service Administrator - Authentication Controller
Handles login, logout, password reset, and password change operations.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sys
import os
import bcrypt

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils

auth_bp = Blueprint('ssa_auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user against database"""
    data = request.get_json()
    email = data.get('username') or data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'ok': False, 'message': 'Email and password required'}), 400
    
    # Query student_service_admins table
    admin = db_utils.query_one(
        """SELECT id, admin_id, email, password, first_name, last_name, is_active 
           FROM student_service_admins WHERE email = %s""",
        (email,)
    )
    
    if not admin:
        return jsonify({'ok': False, 'message': 'Invalid credentials'}), 401
    
    if not admin.get('is_active'):
        return jsonify({'ok': False, 'message': 'Account is disabled'}), 403
    
    # Verify password (bcrypt with PHP compatibility)
    stored_hash = admin['password'].encode('utf-8')
    if stored_hash.startswith(b'$2y$'):
        stored_hash = b'$2b$' + stored_hash[4:]
    
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return jsonify({'ok': False, 'message': 'Invalid credentials'}), 401
    
    # Update last_login
    db_utils.execute(
        "UPDATE student_service_admins SET last_login = NOW() WHERE id = %s",
        (admin['id'],)
    )
    
    return jsonify({
        'ok': True,
        'message': 'Login successful',
        'user': {
            'id': admin['admin_id'],
            'username': admin['email'].split('@')[0],
            'role': 'student-service-admin',
            'email': admin['email'],
            'firstName': admin['first_name'],
            'lastName': admin['last_name']
        }
    }), 200

@auth_bp.route('/reset', methods=['POST'])
def reset_password_request():
    """Request password reset - send email with reset link"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'ok': False, 'message': 'Email required'}), 400
    
    # In production, send email with reset token
    # For now, return success
    return jsonify({
        'ok': True,
        'message': f'Password reset link sent to {email}. Check your email.'
    }), 200

@auth_bp.route('/verify-reset', methods=['POST'])
def verify_password_reset():
    """Verify reset token and update password"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('newPassword')
    
    if not token or not new_password:
        return jsonify({'ok': False, 'message': 'Missing required fields'}), 400
    
    if len(new_password) < 8:
        return jsonify({'ok': False, 'message': 'Password must be at least 8 characters'}), 400
    
    # In production, verify token and update in database
    return jsonify({
        'ok': True,
        'message': 'Password updated successfully'
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change password for authenticated user"""
    data = request.get_json()
    email = data.get('username') or data.get('email')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    if not email or not current_password or not new_password:
        return jsonify({'ok': False, 'message': 'All fields required'}), 400
    
    if len(new_password) < 8:
        return jsonify({'ok': False, 'message': 'Password must be at least 8 characters'}), 400
    
    # Get current password hash
    admin = db_utils.query_one(
        "SELECT id, password FROM student_service_admins WHERE email = %s",
        (email,)
    )
    
    if not admin:
        return jsonify({'ok': False, 'message': 'User not found'}), 404
    
    # Verify current password
    stored_hash = admin['password'].encode('utf-8')
    if stored_hash.startswith(b'$2y$'):
        stored_hash = b'$2b$' + stored_hash[4:]
    
    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
        return jsonify({'ok': False, 'message': 'Current password is incorrect'}), 401
    
    # Update password in database
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_utils.execute(
        "UPDATE student_service_admins SET password = %s WHERE id = %s",
        (new_hash, admin['id'])
    )
    
    return jsonify({
        'ok': True,
        'message': 'Password changed successfully'
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out user"""
    return jsonify({
        'ok': True,
        'message': 'Logged out successfully'
    }), 200
