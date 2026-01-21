# Facial Recognition System - System Administrator

A lightweight and efficient facial recognition system for student attendance marking using **YuNet** for face detection and **SFace** (lightweight alternative to GhostFaceNet) for face recognition.

## Features

- **Real-time Face Detection**: Uses YuNet, a lightweight and accurate face detector
- **Face Recognition**: Uses SFace for efficient face recognition (similar performance to GhostFaceNet-0.5)
- **Live Camera Feed**: Real-time video streaming with face detection overlays
- **Attendance Tracking**: Automatic attendance marking with confidence scores
- **Liveness Detection**: Basic liveness scoring to prevent spoofing
- **Student Management**: Register and manage student face encodings
- **Session Management**: Track attendance sessions with date, time, and room information

## Architecture

### Backend (Python Flask)
- **Controller**: `controller/facial_recognition_controller.py`
- **Port**: 5010
- **Database**: MySQL (uses shared `common/db_utils.py`)

### Frontend (HTML/JavaScript)
- **UI**: `boundary/facial_recognition.html`
- **Features**: Live camera feed, control buttons, attendance display

### Models
- **YuNet**: Lightweight face detection (ONNX format)
  - Size: ~200KB
  - Speed: Real-time on CPU
  - Accuracy: High precision for face detection

- **SFace**: Lightweight face recognition (ONNX format)
  - Size: ~40MB
  - Speed: Real-time on CPU
  - Accuracy: Comparable to GhostFaceNet-0.5

## Installation

### 1. Install Python Dependencies

```bash
cd "System Administrator/controller"
pip install -r facial_recognition_requirements.txt
```

### 2. Download Face Recognition Models

Run the automatic model downloader:

```bash
python download_models.py
```

This will create a `models/` directory and download:
- `face_detection_yunet_2023mar.onnx` (~200KB)
- `face_recognition_sface_2021dec.onnx` (~40MB)

**Manual Download** (if automatic download fails):
1. Visit: https://github.com/opencv/opencv_zoo
2. Download models from:
   - `models/face_detection_yunet/face_detection_yunet_2023mar.onnx`
   - `models/face_recognition_sface/face_recognition_sface_2021dec.onnx`
3. Place them in `System Administrator/controller/models/`

### 3. Verify Database Setup

Ensure your `.env` file at the project root has database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_attendance
```

The `students` table must have a `face_data` column (TEXT type) to store face encodings.

## Running the System

### 1. Start the Facial Recognition Controller

```bash
cd "System Administrator/controller"
python facial_recognition_controller.py
```

The controller will start on `http://127.0.0.1:5010`

### 2. Serve the Frontend

From the project root:

```bash
python -m http.server 8000
```

### 3. Access the UI

Open your browser to:
```
http://127.0.0.1:8000/System%20Administrator/boundary/facial_recognition.html
```

## Usage Guide

### Initial Setup

1. **Check Server Status**: Ensure the green "Server Online" indicator shows at the top
2. **Refresh Faces**: Click "Refresh Faces" to load student face encodings from the database
3. **Verify Models**: The server status should show the number of faces loaded

### Marking Attendance

1. **Start Camera**: Click "Start Camera" to activate the webcam
2. **Start Scanning**: Click "Start Scanning" to enable face recognition
3. **Position Students**: Students should face the camera
4. **Automatic Recognition**: The system will automatically detect and recognize faces
5. **View Results**: Recognized students appear in the "Today's Attendance" panel
6. **Stop Scanning**: Click "Stop Scanning" when done

### Registering New Faces

To register a student's face encoding, you can use the API endpoint:

```python
import requests
import base64

# Read student image
with open('student_photo.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Register face
response = requests.post('http://127.0.0.1:5010/api/facial-recognition/faces/register', json={
    'student_id': 'STU2025001',
    'image': f'data:image/jpeg;base64,{image_data}'
})

print(response.json())
```

Alternatively, you can create a separate enrollment interface.

## API Endpoints

### Camera Management
- `POST /api/facial-recognition/camera/start` - Start camera
- `POST /api/facial-recognition/camera/stop` - Stop camera
- `GET /api/facial-recognition/camera/feed` - Video stream
- `GET /api/facial-recognition/camera/status` - Camera status

### Scanning
- `POST /api/facial-recognition/scanning/start` - Start face recognition
- `POST /api/facial-recognition/scanning/stop` - Stop face recognition

### Face Management
- `POST /api/facial-recognition/faces/refresh` - Reload face encodings
- `POST /api/facial-recognition/faces/register` - Register new face

### Session & Attendance
- `GET /api/facial-recognition/session` - Get current session data
- `POST /api/facial-recognition/attendance/save` - Save attendance to database

### Health Check
- `GET /health` - Server health and model status

## Configuration

Edit `facial_recognition_controller.py` to adjust recognition parameters:

```python
RECOGNITION_THRESHOLD = 0.5  # Cosine similarity threshold (0.0-1.0)
LIVENESS_THRESHOLD = 0.7     # Liveness detection threshold
CONFIDENCE_THRESHOLD = 0.8   # Face detection confidence
```

**Recommendations**:
- **Higher RECOGNITION_THRESHOLD** (0.6-0.7): More strict, fewer false positives
- **Lower RECOGNITION_THRESHOLD** (0.3-0.5): More lenient, may have false positives
- Start with 0.5 and adjust based on your environment

## Database Schema

The system uses the existing `students` and `attendance` tables:

```sql
-- Students table with face_data column
CREATE TABLE students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(50) UNIQUE NOT NULL,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  face_data TEXT,  -- Base64 encoded face embedding
  ...
);

-- Attendance table with face_confidence
CREATE TABLE attendance (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  class_id INT,
  check_in_time TIMESTAMP,
  status ENUM('present', 'late', 'absent'),
  face_confidence DECIMAL(5,2),  -- Recognition confidence
  ...
);
```

## Performance Optimization

### CPU Optimization
- YuNet and SFace are optimized for CPU inference
- Expect 20-30 FPS on modern laptops
- Frame processing: ~30-50ms per frame

### GPU Acceleration (Optional)
To use GPU acceleration, install CUDA-enabled OpenCV:

```bash
pip install opencv-contrib-python-headless
# Ensure CUDA and cuDNN are installed
```

### Memory Usage
- YuNet model: ~5MB RAM
- SFace model: ~50MB RAM
- Per-student encoding: ~512 bytes
- 1000 students: ~500KB total

## Troubleshooting

### Camera Not Starting
- **Issue**: "Failed to open camera"
- **Solution**: Ensure no other application is using the camera
- **macOS**: Grant camera permissions in System Preferences > Security & Privacy

### Models Not Loading
- **Issue**: "Model not found" error
- **Solution**: Run `python download_models.py` to download models
- **Verify**: Check that `controller/models/` contains both `.onnx` files

### Low Recognition Accuracy
- **Issue**: Students not recognized or wrong matches
- **Solutions**:
  - Ensure good lighting conditions
  - Students should face the camera directly
  - Adjust `RECOGNITION_THRESHOLD` in the controller
  - Re-register face encodings with better quality photos

### Database Connection Errors
- **Issue**: "Database connection failed"
- **Solution**:
  - Verify `.env` file has correct credentials
  - Ensure MySQL server is running
  - Check that `student_attendance` database exists

### High CPU Usage
- **Issue**: CPU usage at 100%
- **Solutions**:
  - Reduce frame rate by increasing sleep time in `generate_frames()`
  - Lower camera resolution
  - Process every 2nd or 3rd frame instead of all frames

## Security Considerations

1. **Face Data Storage**: Face encodings are stored as base64 in the database (not actual photos)
2. **HTTPS**: Use HTTPS in production to encrypt video streams
3. **Access Control**: Implement authentication for the facial recognition interface
4. **Privacy**: Inform students about facial recognition usage and data storage
5. **Liveness Detection**: The basic liveness check helps prevent photo spoofing

## Future Enhancements

- [ ] Anti-spoofing with advanced liveness detection
- [ ] Multi-camera support for large classrooms
- [ ] Face enrollment interface in the UI
- [ ] Batch face registration from CSV
- [ ] Real-time attendance notifications
- [ ] Integration with class schedules
- [ ] Attendance reports and analytics
- [ ] Mobile app support

## Technical Details

### Face Encoding Process
1. **Detection**: YuNet detects face bounding boxes and landmarks
2. **Alignment**: Face is aligned using detected landmarks
3. **Feature Extraction**: SFace extracts 128-dimensional embedding
4. **Storage**: Embedding is base64-encoded and stored in database

### Recognition Process
1. **Detect**: Find faces in the frame
2. **Extract**: Generate embedding for each detected face
3. **Compare**: Calculate cosine similarity with all known faces
4. **Match**: If similarity > threshold, identify as that student
5. **Record**: Add to recognized students list with confidence score

### Why SFace Instead of GhostFaceNet?
- **Availability**: SFace is readily available in OpenCV Zoo
- **Performance**: Similar accuracy to GhostFaceNet-0.5 with better CPU optimization
- **Size**: Compact model (~40MB) suitable for lightweight deployment
- **Support**: Well-maintained by OpenCV team

## References

- [OpenCV Zoo](https://github.com/opencv/opencv_zoo)
- [YuNet Paper](https://arxiv.org/abs/2203.10043)
- [Face Recognition with OpenCV](https://docs.opencv.org/4.x/d0/dd4/tutorial_dnn_face.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API endpoint documentation
3. Check server logs for error messages
4. Verify model files are correctly downloaded

## License

This facial recognition module is part of the Student Attendance System project.
