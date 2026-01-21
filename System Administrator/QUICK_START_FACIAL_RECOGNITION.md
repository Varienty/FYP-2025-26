# Quick Start Guide - Facial Recognition System

Get the facial recognition system up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Working webcam
- MySQL database running with `student_attendance` database
- `.env` file configured at project root

## Setup Steps

### Option 1: Automated Setup (Recommended)

**Windows:**
```powershell
cd "System Administrator\controller"
.\setup_facial_recognition.bat
```

**macOS/Linux:**
```bash
cd "System Administrator/controller"
./setup_facial_recognition.sh
```

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r facial_recognition_requirements.txt
   ```

2. **Download models:**
   ```bash
   python download_models.py
   ```

3. **Verify installation:**
   ```bash
   python test_facial_recognition.py
   ```

## Running the System

### Step 1: Start the Backend

```bash
cd "System Administrator/controller"
python facial_recognition_controller.py
```

You should see:
```
============================================================
Facial Recognition Controller
============================================================

Initializing models...
✓ YuNet face detector loaded successfully
✓ Face recognizer loaded successfully

Loading known faces...
✓ Loaded X student face encodings

Running on: http://127.0.0.1:5010
============================================================
```

### Step 2: Serve the Frontend

Open a new terminal and run from project root:

```bash
python -m http.server 8000
```

### Step 3: Access the UI

Open your browser to:
```
http://127.0.0.1:8000/System%20Administrator/boundary/facial_recognition.html
```

## Using the System

### First Time Use

1. **Check Status**: Verify "Server Online" indicator is green
2. **Refresh Faces**: Click "Refresh Faces" button to load student data
3. **Start Camera**: Click "Start Camera" to activate webcam
4. **Start Scanning**: Click "Start Scanning" to enable face recognition

### Marking Attendance

1. Have students face the camera one at a time
2. System automatically detects and recognizes faces
3. Recognized students appear in "Today's Attendance" panel
4. View confidence and liveness scores for each recognition

### Stopping

1. Click "Stop Scanning" to stop recognition
2. Click "Stop Camera" to turn off webcam
3. Close browser tab when done

## Troubleshooting

### Camera won't start
- Close other apps using the camera (Zoom, Skype, etc.)
- On macOS: Grant camera permissions in System Preferences

### Models not loading
```bash
cd "System Administrator/controller"
python download_models.py
```

### No students recognized
- Ensure students have face_data in database
- Check lighting (good lighting needed)
- Students should face camera directly
- Try adjusting `RECOGNITION_THRESHOLD` in controller

### Database errors
- Verify `.env` has correct database credentials
- Ensure MySQL is running
- Check that `student_attendance` database exists

## Testing Installation

Run the test script to verify everything is working:

```bash
python test_facial_recognition.py
```

This will check:
- ✓ Model files exist and can be loaded
- ✓ Camera is accessible
- ✓ Database connection works
- ✓ Student data is available

## Next Steps

- **Register student faces**: See FACIAL_RECOGNITION_README.md for face enrollment
- **Adjust settings**: Edit `facial_recognition_controller.py` to tune recognition parameters
- **Integration**: Connect with class schedules and attendance records

## Architecture

```
Browser (Port 8000)
    ↓ HTTP
Frontend (facial_recognition.html)
    ↓ WebSocket/HTTP
Backend (Port 5010)
    ├── YuNet (Face Detection)
    ├── SFace (Face Recognition)
    └── MySQL Database
```

## Support

- **Detailed docs**: [FACIAL_RECOGNITION_README.md](FACIAL_RECOGNITION_README.md)
- **Test script**: `python test_facial_recognition.py`
- **Check logs**: Look at terminal output for error messages

## Performance Tips

- **CPU**: System runs efficiently on CPU (20-30 FPS)
- **Lighting**: Ensure good, even lighting for best recognition
- **Distance**: Students should be 1-2 meters from camera
- **Quality**: Use HD webcam for better detection accuracy

---

**Ready to go!** Start the backend, open the UI, and begin recognizing students.
