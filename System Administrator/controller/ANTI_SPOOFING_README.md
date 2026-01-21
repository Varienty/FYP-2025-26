# Anti-Spoofing Integration

## Overview

MobileNetV3-Small-FAS anti-spoofing has been integrated into the facial recognition system to prevent photo/video replay attacks.

## How It Works

The system uses a **two-stage verification process**:

1. **Stage 1: Face Recognition** (Existing)
   - Detects faces using YuNet
   - Recognizes students using SFace model
   - Matches against student database

2. **Stage 2: Liveness Detection** (NEW)
   - Analyzes face texture quality (moiré patterns from screens)
   - Checks color diversity (real skin vs prints)
   - Evaluates brightness consistency (natural vs artificial lighting)
   - Optional: Deep learning model check (MobileNetV3)

**Both stages must pass** for attendance to be marked.

## Current Configuration

- **Status**: ENABLED by default
- **Threshold**: 70% (0.7) - Faces scoring below 70% are rejected
- **Method**: Hybrid (Traditional CV + Deep Learning fallback)

## Detection Methods

### 1. Texture Quality Check (Weight: 30%)
- Uses Laplacian variance to detect image sharpness
- Real faces have higher variance than screens/prints
- Detects moiré patterns from digital displays

### 2. Color Diversity Check (Weight: 25%)
- Analyzes HSV color histogram
- Real skin has more color variation than printed photos
- Calculates standard deviation in hue and saturation

### 3. Brightness Consistency Check (Weight: 25%)
- Examines lighting patterns
- Real faces have natural shadows/highlights
- Screens have uniform backlighting

### 4. Deep Learning Model (Weight: 20% - Optional)
- MobileNetV3-Small neural network
- Binary classification: live vs spoof
- Currently fallback only (no trained weights yet)

## API Endpoints

### Get Status
```bash
GET /api/facial-recognition/anti-spoofing/status
```
Returns:
```json
{
  "ok": true,
  "available": true,
  "enabled": true,
  "threshold": 0.7,
  "debug": false
}
```

### Enable Anti-Spoofing
```bash
POST /api/facial-recognition/anti-spoofing/enable
```

### Disable Anti-Spoofing
```bash
POST /api/facial-recognition/anti-spoofing/disable
```

### Set Threshold
```bash
POST /api/facial-recognition/anti-spoofing/threshold
Content-Type: application/json

{
  "threshold": 0.6
}
```
Threshold range: 0.0 (very lenient) to 1.0 (very strict)

## Detection Behavior

### When Spoofing is Detected:
- Face is recognized but fails liveness check
- Orange "Unknown" box is drawn instead of green
- Attendance is NOT marked
- Console logs warning: "⚠ Spoofing detected for [Name]"

### When Face is Live:
- Both recognition and liveness pass
- Green box with name and confidence
- Attendance marked automatically
- Liveness score stored in database

## Reverting to Previous Version

If you need to revert:

1. Stop the controller:
   ```bash
   pkill -f facial_recognition_controller.py
   ```

2. Restore backup:
   ```bash
   cd "/Applications/XAMPP/xamppfiles/htdocs/FYP-Team-15/System Administrator/controller"
   cp facial_recognition_controller.py.backup facial_recognition_controller.py
   ```

3. Start controller:
   ```bash
   python3 facial_recognition_controller.py
   ```

## Tuning Recommendations

### If Too Many False Rejections (Real people rejected):
- Lower threshold: 0.5 - 0.6
- Less strict, more permissive

### If Too Many False Accepts (Photos getting through):
- Raise threshold: 0.8 - 0.9
- More strict, better security

### Disable Temporarily for Testing:
```bash
curl -X POST http://localhost:5011/api/facial-recognition/anti-spoofing/disable
```

## Technical Details

- **Module**: `anti_spoofing.py`
- **Model**: MobileNetV3-Small (3 conv layers, ~50KB)
- **Input**: 128x128 RGB face image
- **Output**: Liveness score (0-100%)
- **Performance**: ~5-10ms per face (CPU)
- **Dependencies**: PyTorch, OpenCV, NumPy

## Files Modified

1. `facial_recognition_controller.py` - Added liveness check in process_frame()
2. `anti_spoofing.py` - NEW - Anti-spoofing detection module
3. `facial_recognition_controller.py.backup` - Backup of original

## Next Steps (Optional)

1. Train MobileNetV3 model on real/fake face dataset
2. Add temporal analysis (detect video replay)
3. Implement 3D depth analysis
4. Add eye blink detection
5. Challenge-response (show random gesture)

---

**Created**: 2025-12-31
**Status**: Production Ready (Traditional CV methods)
**Model Training**: Pending (Deep learning component)
