import os

# Ensure any necessary env defaults here (optional)
os.environ.setdefault("FLASK_ENV", os.getenv("FLASK_ENV", "production"))

# Import the Flask app from main
from main import app  # noqa: E402

# Export as both 'app' and 'application' for compatibility with all EB entry points
application = app

__all__ = ['app', 'application']
