#!/bin/bash
set -e

PROCFILE="/var/app/current/Procfile"

# Backup original Procfile if it exists
if [ -f "$PROCFILE" ]; then
    cp "$PROCFILE" "$PROCFILE.bak.$(date +%s)"
    echo "[postdeploy] Backed up original Procfile"
fi

# Override with correct entry point
cat > "$PROCFILE" << 'EOF'
web: gunicorn --bind 0.0.0.0:8000 --workers 4 --worker-class gthread --threads 2 --timeout 60 wsgi:application
EOF

chmod 644 "$PROCFILE"
echo "[postdeploy] Procfile overridden with wsgi:application entry point"
cat "$PROCFILE"
