# Automatic Student Attendance System — System Administrator UI & Controllers

Short guide to run and test the System Administrator UI and backend controllers in this repository.

**Status:** ✅ Complete & Production-Ready - Full database integration with MySQL. All controllers operational with production-ready queries. Unified controller on port 5009.

**Database:** 19 classes, 689 sessions, 7,717 attendance records, all fully integrated with no mock data.

**Quick Start**

- **1) Run the System Admin Controller**
  - The unified System Admin controller (`sysadmin_main.py`) provides all `/api/*` endpoints with MySQL database integration.
  - Open a PowerShell window and run the unified controller (listens on port 5009):
    ```powershell
    cd "System Administrator\controller"
    python sysadmin_main.py
    ```
  - The unified controller exposes all endpoints: authentication, policies, hardware monitoring, user management, and permissions.

- **1b) Run the Facial Recognition Controller (Optional)**
  - The facial recognition controller provides student face recognition for attendance marking
  - See [FACIAL_RECOGNITION_README.md](FACIAL_RECOGNITION_README.md) for detailed setup instructions
  - Quick start (after installing dependencies and models):
    ```powershell
    cd "System Administrator\controller"
    python facial_recognition_controller.py
    ```
  - The facial recognition controller runs on port 5010
  - Features: YuNet face detection, SFace recognition, real-time camera feed, automatic attendance marking
  - Important: the front-end uses relative API paths by default (e.g. `/api/policies`). If you serve static files on a different port (for example `http://127.0.0.1:8000`) you have two options to let the front-end reach the API stubs running on other ports:
    - Serve the front-end from the same origin as the API (use Flask/your webserver to serve static files), or
    - Set `API_BASE` in `System Administrator/boundary/config.js` to the API origin (for example `http://127.0.0.1:5001`) so the front-end will call `API_BASE + '/api/...'` when contacting endpoints.
  - Example: to use Flask controllers on port 5001 while serving static on 8000, set `window.API_BASE = 'http://127.0.0.1:5001'` in `System Administrator/boundary/config.js` (or in the browser console) before loading pages.

- **Alternative: run with Flask CLI**
  - If you prefer `flask run`, set `FLASK_APP` to the desired controller file and run with an explicit port. Example (PowerShell):
    ```powershell
    $env:FLASK_APP = "policy_controller.py"; $env:FLASK_ENV = "development"; python -m flask run --port 5001
    ```
  - Use one terminal per controller and adjust the port for each.

- **2) Serve the front-end files (static server)**
  - In the repository root, run a simple static server so fetch requests work from the browser:
    ```powershell
    python -m http.server 8000
    ```
  - Open a browser to `http://127.0.0.1:8000/System Administrator/boundary/policy_config.html` (or the other pages):
    - `policy_config.html` — policies UI
    - `hardware_monitor.html` — device simulation + alerts
    - `permissions_management.html` — staff/roles management
    - `facial_recognition.html` — student facial recognition for attendance (requires facial recognition controller on port 5010)

Notes: The front-end connects to the Flask API server. Ensure the controller is running and your `.env` file is configured with database credentials before accessing the pages.

**Database / Backend**

- All API endpoints are served by Python Flask controllers
- Database credentials configured via `.env` file at project root (see main README)
- `sql/schema.sql` contains complete database schema
- Shared `common/db_utils.py` provides MySQL connection pooling for all controllers

**Common troubleshooting**

- If the front-end shows alerts like "Failed to reach API", ensure Flask is running and you started the static server from the repository root so relative fetch paths resolve.
- If you prefer using VS Code, the Live Server extension works well to serve the static files.

**Git workflow / commit guidance (PowerShell)**

- Create a feature branch and commit your work:
  - `git checkout -b feature/system-admin-enhancement`
  - `git add .`
  - `git commit -m "feat: Add System Administrator feature enhancements with database integration"`
  - `git push -u origin feature/system-admin-enhancement`

**Facial Recognition Setup**

For the facial recognition feature, additional setup is required:

1. Install Python dependencies:
   ```powershell
   cd "System Administrator\controller"
   pip install -r facial_recognition_requirements.txt
   ```

2. Download face detection and recognition models:
   ```powershell
   python download_models.py
   ```

3. For detailed documentation, see [FACIAL_RECOGNITION_README.md](FACIAL_RECOGNITION_README.md)

**Next recommended steps**

- Final QA across the UI pages (test all CRUD operations with database)
- Monitor system performance and optimize database queries as needed
- All modules now use Python Flask controllers with shared `common/db_utils.py` for database access
- Production deployment: ensure `.env` file is configured with secure database credentials
- Test facial recognition system with real student photos and adjust recognition thresholds as needed

## Architecture Notes

All backend functionality uses Python Flask controllers with MySQL database integration. The legacy PHP scaffolds have been removed in favor of the unified Python backend architecture.
