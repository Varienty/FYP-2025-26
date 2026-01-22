import os

# Ensure any necessary env defaults here (optional)
os.environ.setdefault("FLASK_ENV", os.getenv("FLASK_ENV", "production"))

# Import the Flask app as 'application' for Elastic Beanstalk
from main import app as application  # noqa: E402
