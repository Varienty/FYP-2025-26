#!/usr/bin/env python3
"""
Unified Attendance Management System Backend
Merges all 7 Flask controllers into a single application
Designed for AWS Elastic Beanstalk deployment

Local Development:
  python main.py

AWS Elastic Beanstalk:
  Automatically runs via WSGIPath: main:app in .ebextensions/python.config
"""

import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main Flask app
app = Flask(__name__)

# Configure CORS - allow all origins
CORS(app, 
     origins="*", 
     supports_credentials=True, 
     allow_headers="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

# Health check endpoint for AWS load balancer
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'attendance-system'}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Student Attendance Management System API',
        'version': '1.0.0',
        'endpoints': {
            'lecturer': '/api/lecturer/*',
            'student_service_admin': '/api/ssa/*',
            'system_admin': '/api/sysadmin/*'
        }
    }), 200

# ============================================================================
# Import and register Lecturer controllers (Port 5003-5007)
# ============================================================================
logger.info("Loading Lecturer Controllers...")

try:
    # Import each lecturer controller as Flask app
    from Lecturer.controller.lecturer_auth_controller import app as lecturer_auth_app
    from Lecturer.controller.lecturer_attendance_controller import app as lecturer_attendance_app
    from Lecturer.controller.lecturer_report_controller import app as lecturer_report_app
    from Lecturer.controller.lecturer_schedule_controller import app as lecturer_schedule_app
    from Lecturer.controller.lecturer_notification_controller import app as lecturer_notification_app
    
    # Register routes from lecturer controllers
    @app.route('/api/lecturer/auth/login', methods=['POST'])
    def lecturer_login():
        with app.app_context():
            return lecturer_auth_app.dispatch_request()
    
    # Copy all routes from lecturer auth app
    for rule in lecturer_auth_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func = lecturer_auth_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    app.add_url_rule(rule.rule, rule.endpoint, func, methods=[method])
    
    # Copy routes from other lecturer controllers
    for lecturer_app in [lecturer_attendance_app, lecturer_report_app, 
                         lecturer_schedule_app, lecturer_notification_app]:
        for rule in lecturer_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func = lecturer_app.view_functions[rule.endpoint]
                for method in rule.methods:
                    if method not in ['HEAD', 'OPTIONS']:
                        # Avoid duplicate endpoint names
                        endpoint_name = f"{rule.endpoint}_{id(func)}"
                        try:
                            app.add_url_rule(rule.rule, endpoint_name, func, methods=[method])
                        except Exception as e:
                            logger.warning(f"Could not register {rule.rule}: {e}")
    
    logger.info("✓ Lecturer Controllers loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load Lecturer Controllers: {e}")
    logger.exception(e)

# ============================================================================
# Import and register Student Service Admin controllers (Port 5008)
# ============================================================================
logger.info("Loading Student Service Admin Controllers...")

try:
    # Import SSA main app
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     'Student Service Administrator/controller')))
    from ssa_main import app as ssa_app
    
    # Copy all routes from SSA app
    for rule in ssa_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func = ssa_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    endpoint_name = f"ssa_{rule.endpoint}_{id(func)}"
                    try:
                        app.add_url_rule(rule.rule, endpoint_name, func, methods=[method])
                    except Exception as e:
                        logger.warning(f"Could not register SSA {rule.rule}: {e}")
    
    logger.info("✓ Student Service Admin Controllers loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load Student Service Admin Controllers: {e}")
    logger.exception(e)

# ============================================================================
# Import and register System Admin controllers (Port 5009)
# ============================================================================
logger.info("Loading System Admin Controllers...")

try:
    # Import System Admin main app
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                     'System Administrator/controller')))
    from sysadmin_main import app as sysadmin_app
    
    # Copy all routes from System Admin app
    for rule in sysadmin_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func = sysadmin_app.view_functions[rule.endpoint]
            for method in rule.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    endpoint_name = f"sysadmin_{rule.endpoint}_{id(func)}"
                    try:
                        app.add_url_rule(rule.rule, endpoint_name, func, methods=[method])
                    except Exception as e:
                        logger.warning(f"Could not register System Admin {rule.rule}: {e}")
    
    logger.info("✓ System Admin Controllers loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load System Admin Controllers: {e}")
    logger.exception(e)

# ============================================================================
# Error handlers
# ============================================================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# Main entry point
# ============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Attendance Management System on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Database: {os.getenv('DB_HOST', 'localhost')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )
