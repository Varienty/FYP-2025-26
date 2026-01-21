#!/usr/bin/env python3
"""
Lecturer Authentication Controller
Handles login, logout, and password reset for lecturers
Corresponds to US12 (Login), US13 (Reset Password), US19 (Logout)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import uuid
import bcrypt as bcrypt_lib

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from common.db_utils import query_one, execute

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

RESET_TOKEN_EXPIRY_MINUTES = 60


@app.route('/api/lecturer/auth/login', methods=['POST'])
def login():
    """
    US12 - Lecturer Login (Sequence Diagram #12)
    Authenticates lecturer using email and password
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validate input
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        # Check if lecturer exists in DB
        lecturer = query_one(
            """
            SELECT id, lecturer_id, email, password, first_name, last_name, department, is_active
            FROM lecturers
            WHERE email = %s
            """,
            (email,),
        )
        if not lecturer:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        # Verify password (bcrypt from PHP uses $2y$, convert to $2b$ for Python compatibility)
        try:
            stored_hash = lecturer['password'].encode('utf-8')
            # PHP bcrypt uses $2y$, Python uses $2b$ - they're compatible
            if stored_hash.startswith(b'$2y$'):
                stored_hash = b'$2b$' + stored_hash[4:]
            
            if not bcrypt_lib.checkpw(password.encode('utf-8'), stored_hash):
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 401
        except Exception:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        # Check if account is active
        if not lecturer.get('is_active', True):
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 403

        # Generate session token (mock)
        token = f"lecturer_token_{lecturer['lecturer_id']}_{datetime.now().timestamp()}"

        # Return lecturer data
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': lecturer['id'],
                'lecturer_id': lecturer['lecturer_id'],
                'email': lecturer['email'],
                'first_name': lecturer['first_name'],
                'last_name': lecturer['last_name'],
                'department': lecturer['department'],
                'role': 'lecturer'
            },
            'token': token
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/auth/reset-request', methods=['POST'])
def request_password_reset():
    """
    US13 - Request Password Reset (Sequence Diagram #13)
    Sends password reset email to lecturer
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400

        # Check if lecturer exists in DB
        lecturer = query_one(
            "SELECT id, lecturer_id FROM lecturers WHERE email = %s",
            (email,),
        )
        # Always return success to avoid user enumeration
        token = None
        if lecturer:
            token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)
            execute(
                """
                UPDATE lecturers
                SET reset_token = %s,
                    reset_token_expiry = %s
                WHERE id = %s
                """,
                (token, expires_at, lecturer['id']),
            )
            print(f"[RESET] Token for {email}: {token} (expires {expires_at})")

        return jsonify({
            'success': True,
            'message': 'If the email exists, a reset link has been sent',
            'token': token  # Included for demo/testing convenience
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/auth/reset-confirm', methods=['POST'])
def confirm_password_reset():
    """
    US13 - Confirm Password Reset (Sequence Diagram #13)
    Verifies token and updates password
    """
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('newPassword', '')
        verify_only = data.get('verifyOnly', False)

        if not token:
            return jsonify({
                'success': False,
                'message': 'Reset token is required'
            }), 400

        # Verify token in DB
        lecturer = query_one(
            """
            SELECT id, email, reset_token_expiry
            FROM lecturers
            WHERE reset_token = %s
            """,
            (token,),
        )
        if not lecturer:
            return jsonify({'success': False, 'message': 'Invalid or expired reset token'}), 401

        # Check expiry
        expiry = lecturer['reset_token_expiry']
        if expiry is None or datetime.now() > expiry:
            # Invalidate token if expired
            execute(
                "UPDATE lecturers SET reset_token = NULL, reset_token_expiry = NULL WHERE id = %s",
                (lecturer['id'],),
            )
            return jsonify({'success': False, 'message': 'Reset token has expired'}), 401

        if verify_only:
            return jsonify({'success': True, 'message': 'Token is valid', 'email': lecturer['email']}), 200

        # Update password
        if not new_password or len(new_password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters'
            }), 400

        # Hash password and update
        hashed = bcrypt_lib.hashpw(new_password.encode('utf-8'), bcrypt_lib.gensalt()).decode('utf-8')
        # Convert $2b$ to $2y$ for PHP compatibility
        if hashed.startswith('$2b$'):
            hashed = '$2y$' + hashed[4:]
        execute(
            "UPDATE lecturers SET password = %s, reset_token = NULL, reset_token_expiry = NULL WHERE id = %s",
            (hashed, lecturer['id']),
        )

        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/lecturer/auth/logout', methods=['POST'])
def logout():
    """
    US19 - Lecturer Logout (Sequence Diagram #19)
    Logs out lecturer and invalidates session
    """
    try:
        # In production, invalidate session token here
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Lecturer Auth Controller running on http://localhost:5003")
    print("Available endpoints:")
    print("  POST /api/lecturer/auth/login")
    print("  POST /api/lecturer/auth/reset-request")
    print("  POST /api/lecturer/auth/reset-confirm")
    print("  POST /api/lecturer/auth/logout")
    app.run(host='0.0.0.0', port=5003, debug=True)
