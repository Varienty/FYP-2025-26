#!/bin/bash
# Override AWS EB's auto-generated Procfile with correct wsgi:application entry point
# This runs BEFORE the web service starts

cat > /var/app/current/Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:8000 --workers 4 --worker-class gthread --threads 2 --timeout 60 wsgi:application
EOF

echo "[predeploy] Procfile overridden with wsgi:application entry point"
