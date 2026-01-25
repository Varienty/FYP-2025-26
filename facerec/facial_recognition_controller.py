"""
Facial Recognition Controller - OOP Version
Object-Oriented implementation for student facial recognition and attendance marking
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import sys
import os
import cv2
import numpy as np
import base64
from datetime import datetime, date, timedelta
import threading
import time
from typing import Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import errors as mysql_errors

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from common import db_utils


class FaceDetector:
    """Handles face detection using YuNet"""

    def __init__(self, model_path: str, score_threshold: float = 0.6):
        self.model_path = model_path
        self.score_threshold = score_threshold
        self.detector = None
        self.initialize()

    def initialize(self) -> bool:
        """Initialize the YuNet face detector"""
        try:
            if os.path.exists(self.model_path):
                self.detector = cv2.FaceDetectorYN.create(
                    self.model_path,
                    "",
                    (640, 640),  # Increased input size for better small face detection
                    self.score_threshold,
                    0.3,  # NMS threshold
                    5000,  # Top K
                    cv2.dnn.DNN_BACKEND_DEFAULT,
                    cv2.dnn.DNN_TARGET_CPU
                )
                print("✓ YuNet face detector loaded successfully")
                return True
            else:
                print(f"⚠ YuNet model not found at {self.model_path}")
                return False
        except Exception as e:
            print(f"✗ Error initializing face detector: {e}")
            return False

    def detect(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Detect faces in a frame with multi-scale detection for far distances"""
        if self.detector is None:
            return None

        height, width = frame.shape[:2]

        # Preprocess: Sharpen image for better far detection
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(frame, -1, kernel)

        # Primary detection on original frame
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(sharpened)

        # Multi-scale detection: Try upscaled frame for far/small faces
        # This helps detect faces that are too small in the original resolution
        if faces is None or len(faces) == 0:
            # Upscale by 1.5x for better small face detection
            scale_factor = 1.5
            upscaled = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor,
                                interpolation=cv2.INTER_CUBIC)
            upscaled_sharp = cv2.filter2D(upscaled, -1, kernel)

            h_up, w_up = upscaled.shape[:2]
            self.detector.setInputSize((w_up, h_up))
            _, faces_upscaled = self.detector.detect(upscaled_sharp)

            # Scale coordinates back to original frame size
            if faces_upscaled is not None and len(faces_upscaled) > 0:
                faces_upscaled[:, :4] /= scale_factor  # Scale x, y, w, h
                faces = faces_upscaled

        return faces

    @staticmethod
    def is_valid_face(face_box: np.ndarray, frame_width: int, frame_height: int) -> bool:
        """
        Validate if detected box is likely a real face (not hand, arm, etc.)

        Args:
            face_box: Detected face coordinates [x, y, w, h, ...]
            frame_width: Frame width for relative size check
            frame_height: Frame height for relative size check

        Returns:
            True if detection passes face validation criteria
        """
        x, y, w, h = face_box[:4].astype(int)

        # Check aspect ratio: faces are typically 0.6 to 1.6 (height/width)
        # Very relaxed for different angles, distances, and head positions
        aspect_ratio = h / max(w, 1)
        if aspect_ratio < 0.6 or aspect_ratio > 1.6:
            return False

        # Check relative size: face should be reasonable size of frame
        # Very wide range for near (large faces) and far (small faces) detection
        face_area = w * h
        frame_area = frame_width * frame_height
        relative_size = face_area / frame_area

        # Allow 0.4% to 85% of frame (very wide range for far distance detection)
        # 0.4% = person standing 5-7 meters away
        # 85% = person very close to camera
        if relative_size < 0.004 or relative_size > 0.85:
            return False

        # Very small minimum for far detection (30x30 pixels)
        # This allows detection of faces much farther away
        if w < 30 or h < 30:
            return False

        return True


class FaceRecognizer:
    """Handles face recognition and feature extraction"""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.recognizer = None
        self.initialize()

    def initialize(self) -> bool:
        """Initialize the face recognition model"""
        try:
            if os.path.exists(self.model_path):
                self.recognizer = cv2.FaceRecognizerSF.create(
                    self.model_path,
                    ""
                )
                print("✓ Face recognizer loaded successfully")
                return True
            else:
                print(f"⚠ Face recognition model not found at {self.model_path}")
                return False
        except Exception as e:
            print(f"✗ Error initializing face recognizer: {e}")
            return False

    def extract_features(self, frame: np.ndarray, face_coords: np.ndarray) -> Optional[np.ndarray]:
        """Extract face features from detected face with preprocessing for better accuracy"""
        if self.recognizer is None:
            return None

        try:
            aligned_face = self.recognizer.alignCrop(frame, face_coords)

            # Enhance image quality for better feature extraction
            aligned_face = self._enhance_face_image(aligned_face)

            feature = self.recognizer.feature(aligned_face)
            feature_vector = feature.flatten()

            # L2 normalization for better matching consistency
            norm = np.linalg.norm(feature_vector)
            if norm > 0:
                feature_vector = feature_vector / norm

            return feature_vector
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None

    @staticmethod
    def _enhance_face_image(face_img: np.ndarray) -> np.ndarray:
        """
        Enhance face image quality for better feature extraction
        Uses CLAHE to improve contrast and normalize lighting
        """
        try:
            # Convert to LAB color space for better lighting normalization
            lab = cv2.cvtColor(face_img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge channels and convert back to BGR
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

            return enhanced
        except Exception as e:
            # If enhancement fails, return original
            return face_img

    def extract_features_from_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract features from a pre-cropped face image with preprocessing"""
        if self.recognizer is None:
            return None

        try:
            # Resize to expected input size
            img_resized = cv2.resize(image, (112, 112))

            # Enhance image quality for better feature extraction
            img_resized = self._enhance_face_image(img_resized)

            feature = self.recognizer.feature(img_resized)
            feature_vector = feature.flatten()

            # L2 normalization for better matching consistency
            norm = np.linalg.norm(feature_vector)
            if norm > 0:
                feature_vector = feature_vector / norm

            return feature_vector
        except Exception as e:
            print(f"Error extracting features from image: {e}")
            return None

    @staticmethod
    def cosine_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Calculate cosine similarity between two feature vectors"""
        feat1 = feat1.flatten()
        feat2 = feat2.flatten()
        return np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2))


class FaceDatabase:
    """Manages the database of known faces"""

    def __init__(self, face_recognizer: FaceRecognizer):
        self.face_recognizer = face_recognizer
        self.known_faces: Dict[str, Dict] = {}

    def _ensure_face_images_table(self) -> None:
        """Create face_images table if it does not exist to prevent init failures."""
        try:
            db_utils.execute(
                """
                CREATE TABLE IF NOT EXISTS face_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    image_data LONGBLOB NOT NULL,
                    image_number INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    KEY idx_student_id (student_id),
                    CONSTRAINT fk_face_images_student FOREIGN KEY (student_id)
                        REFERENCES students(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
        except Exception as e:
            print(f"✗ Failed to ensure face_images table exists: {e}")

    def load_from_database(self) -> bool:
        """Load all student face encodings from database"""
        try:
            # Ensure the face_images table exists so initialization does not crash on fresh DBs
            self._ensure_face_images_table()

            # Get all active students
            students = db_utils.query_all(
                """SELECT id, student_id, first_name, last_name
                   FROM students
                   WHERE is_active = TRUE"""
            )

            print(f"\n{'='*60}")
            print(f"Loading student faces from database")
            print(f"Total students in database: {len(students)}")
            print(f"{'='*60}")

            self.known_faces = {}
            loaded_count = 0
            failed_students = []

            for student in students:
                student_internal_id = student['id']
                student_id = student['student_id']
                first_name = student['first_name']
                last_name = student['last_name']

                print(f"\n[{student_id}] {first_name} {last_name}")

                # Get face images from database
                try:
                    face_images = db_utils.query_all(
                        """SELECT image_data, image_number
                               FROM face_images
                               WHERE student_id = %s
                               ORDER BY image_number""",
                        (student_internal_id,)
                    )
                except mysql_errors.ProgrammingError as e:
                    if getattr(e, 'errno', None) == 1146:
                        print("  ⚠ face_images table missing, creating now...")
                        self._ensure_face_images_table()
                        face_images = db_utils.query_all(
                            """SELECT image_data, image_number
                                   FROM face_images
                                   WHERE student_id = %s
                                   ORDER BY image_number""",
                            (student_internal_id,)
                        )
                    else:
                        print(f"  ✗ DB error loading face_images: {e}")
                        continue

                if not face_images:
                    failed_students.append(f"{student_id} ({first_name} {last_name}) - no face images in database")
                    print(f"  ✗ No face images found in database")
                    continue

                print(f"  → Processing {len(face_images)} face image(s) from database")

                face_encodings = []

                for face_img in face_images:
                    try:
                        img_data = face_img['image_data']
                        image_number = face_img['image_number']

                        # Check if it's a base64 string or raw bytes
                        if isinstance(img_data, str):
                            img_data = base64.b64decode(img_data)

                        # Convert bytes to numpy array
                        nparr = np.frombuffer(img_data, np.uint8)
                        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                        if img is None:
                            print(f"    ✗ Image {image_number} - could not decode")
                            continue

                        # Extract features from pre-cropped face image
                        feature = self.face_recognizer.extract_features_from_image(img)
                        if feature is not None:
                            face_encodings.append(feature)
                            print(f"    ✓ Image {image_number} - feature extracted")

                    except Exception as e:
                        print(f"    ✗ Image {image_number} - error: {e}")

                if not face_encodings:
                    failed_students.append(f"{student_id} ({first_name} {last_name}) - no faces detected in images")
                    print(f"  ✗ No valid face encodings extracted")
                else:
                    # Average all encodings for this student and normalize
                    avg_encoding = np.mean(face_encodings, axis=0)

                    # L2 normalization of averaged encoding for better matching
                    norm = np.linalg.norm(avg_encoding)
                    if norm > 0:
                        avg_encoding = avg_encoding / norm

                    self.known_faces[student_id] = {
                        'name': f"{first_name} {last_name}",
                        'encoding': avg_encoding,
                        'num_samples': len(face_encodings)
                    }
                    loaded_count += 1
                    print(f"  ✓ SUCCESS - Loaded {len(face_encodings)} face encoding(s)")

            print(f"\n{'='*60}")
            print(f"SUMMARY")
            print(f"{'='*60}")
            print(f"✓ Successfully loaded: {loaded_count}/{len(students)} students")

            if failed_students:
                print(f"\n✗ Failed to load {len(failed_students)} student(s):")
                for failure in failed_students:
                    print(f"  - {failure}")

            print(f"{'='*60}\n")
            return True

        except Exception as e:
            print(f"✗ Error loading known faces: {e}")
            import traceback
            traceback.print_exc()
            return False

    def find_match(self, feature: np.ndarray, threshold: float = 0.28, min_confidence_gap: float = 0.020) -> Optional[Tuple[str, str, float]]:
        """
        Find the best matching student for a given face feature.

        Args:
            feature: Face feature vector to match
            threshold: Minimum similarity threshold (0.28 - lowered slightly for better detection)
            min_confidence_gap: Minimum gap between best and second-best match (0.020 - balanced for stability)

        Returns:
            Tuple of (student_id, name, similarity) if confident match found, None otherwise
        """
        if not self.known_faces:
            return None

        # Calculate similarity scores for all students
        similarities = []
        for student_id, data in self.known_faces.items():
            similarity = self.face_recognizer.cosine_similarity(feature, data['encoding'])
            similarities.append((student_id, data['name'], similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[2], reverse=True)

        if not similarities:
            return None

        best_match = similarities[0]
        best_similarity = best_match[2]

        # Log top matches for debugging
        print(f"  Top match: {best_match[1]} ({best_match[0]}) - similarity: {best_similarity:.4f}")
        if len(similarities) > 1:
            print(f"  2nd match: {similarities[1][1]} ({similarities[1][0]}) - similarity: {similarities[1][2]:.4f}")

        # Check if best match meets threshold
        if best_similarity < threshold:
            print(f"  ✗ Below threshold ({threshold})")
            return None

        # Check confidence gap: best match should be significantly better than second-best
        # This prevents false positives when face is ambiguous
        if len(similarities) > 1:
            second_best_similarity = similarities[1][2]
            confidence_gap = best_similarity - second_best_similarity

            if confidence_gap < min_confidence_gap:
                # Too close between two students - not confident enough
                print(f"  ✗ Confidence gap too small: {confidence_gap:.4f} < {min_confidence_gap}")
                return None

        print(f"  ✓ Match confirmed!")
        return best_match

    def get_count(self) -> int:
        """Get the number of known faces"""
        return len(self.known_faces)

    def get_all_faces(self) -> List[Dict]:
        """Get list of all loaded faces"""
        faces_list = []
        for student_id, data in self.known_faces.items():
            faces_list.append({
                'student_id': student_id,
                'name': data['name'],
                'num_samples': data.get('num_samples', 1)
            })
        return sorted(faces_list, key=lambda x: x['student_id'])


class AttendanceSession:
    """Manages the current attendance session"""

    def __init__(self):
        self.session_data = {
            'date': None,
            'time': None,
            'room': None,
            'module_id': None,
            'enrolled_count': 0,
            'recognized_students': []
        }
        self.lock = threading.Lock()

    def start(self, **kwargs):
        """Start a new session"""
        with self.lock:
            self.session_data.update(kwargs)
            self.session_data['recognized_students'] = []

    def add_student(self, student_id: str, name: str, confidence: float, liveness: float):
        """Add a recognized student to the session"""
        with self.lock:
            # Check if student already recognized
            if student_id not in [s['student_id'] for s in self.session_data['recognized_students']]:
                self.session_data['recognized_students'].append({
                    'student_id': student_id,
                    'name': name,
                    'confidence': float(confidence),
                    'liveness': float(liveness),
                    'timestamp': datetime.now().isoformat()
                })
                return True
            return False

    def get_data(self) -> Dict:
        """Get current session data"""
        with self.lock:
            return self.session_data.copy()

    def reset(self):
        """Reset the session"""
        with self.lock:
            self.session_data['recognized_students'] = []


class FaceTracker:
    """
    Tracks faces across frames to maintain temporal consistency.
    Prevents identity switching when the same face moves or changes angle.
    """

    def __init__(self, max_age: int = 10):
        """
        Args:
            max_age: Maximum frames to keep tracking a face without detection
        """
        self.tracks = {}  # track_id -> {student_id, last_seen, position, confirmation_count, similarity_history}
        self.next_track_id = 0
        self.max_age = max_age
        self.confirmation_threshold = 2  # Require 2 consecutive detections for stable recognition
        self.history_size = 5  # Keep last 5 similarity scores for smoothing

    def update(self, detections: List[Tuple[Tuple[int, int, int, int], str, str, float]]) -> List[Tuple[str, str, float, bool]]:
        """
        Update tracks with new detections.

        Args:
            detections: List of (bbox, student_id, name, confidence) tuples

        Returns:
            List of (student_id, name, confidence, is_confirmed) for stable tracks
        """
        current_frame_tracks = []

        # Age existing tracks
        for track_id in list(self.tracks.keys()):
            self.tracks[track_id]['last_seen'] += 1
            if self.tracks[track_id]['last_seen'] > self.max_age:
                del self.tracks[track_id]

        # Match new detections to existing tracks
        for bbox, student_id, name, confidence in detections:
            x, y, w, h = bbox
            center = (x + w // 2, y + h // 2)

            # Find closest existing track for this student
            best_track_id = None
            best_distance = float('inf')

            for track_id, track_data in self.tracks.items():
                if track_data['student_id'] == student_id:
                    track_center = track_data['position']
                    distance = np.sqrt((center[0] - track_center[0])**2 + (center[1] - track_center[1])**2)

                    if distance < 100 and distance < best_distance:  # Within 100 pixels
                        best_distance = distance
                        best_track_id = track_id

            if best_track_id is not None:
                # Update existing track
                track = self.tracks[best_track_id]
                track['last_seen'] = 0
                track['position'] = center

                # Add to similarity history for smoothing
                if 'similarity_history' not in track:
                    track['similarity_history'] = []
                track['similarity_history'].append(confidence)

                # Keep only recent history
                if len(track['similarity_history']) > self.history_size:
                    track['similarity_history'].pop(0)

                # Use average of recent similarities for stability
                avg_confidence = np.mean(track['similarity_history'])
                track['confidence'] = avg_confidence

                # Increment confirmation count only if consistent
                if len(track['similarity_history']) >= 2:
                    # Check if recent detections are consistent (not fluctuating wildly)
                    recent = track['similarity_history'][-3:] if len(track['similarity_history']) >= 3 else track['similarity_history']
                    std_dev = np.std(recent)

                    if std_dev < 0.08:  # Low variation = stable recognition (relaxed from 0.05 to 0.08)
                        track['confirmation_count'] = min(
                            track['confirmation_count'] + 1,
                            self.confirmation_threshold + 5
                        )
                    else:
                        # Even if variation is higher, still increment slowly
                        track['confirmation_count'] += 0.5
                else:
                    track['confirmation_count'] += 1
            else:
                # Create new track
                self.tracks[self.next_track_id] = {
                    'student_id': student_id,
                    'name': name,
                    'position': center,
                    'last_seen': 0,
                    'confirmation_count': 1,
                    'confidence': confidence,
                    'similarity_history': [confidence]
                }
                self.next_track_id += 1

        # Return confirmed tracks only
        confirmed_tracks = []
        for track_data in self.tracks.values():
            if track_data['confirmation_count'] >= self.confirmation_threshold:
                confirmed_tracks.append((
                    track_data['student_id'],
                    track_data['name'],
                    track_data['confidence'],
                    True
                ))

        return confirmed_tracks

    def reset(self):
        """Clear all tracks"""
        self.tracks = {}
        self.next_track_id = 0


class CameraManager:
    """Manages camera operations"""

    def __init__(self):
        self.camera = None
        self.active = False
        self.lock = threading.Lock()

    def start(self) -> bool:
        """Start the camera"""
        with self.lock:
            if self.active:
                self.stop()

            try:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    return False

                self.active = True
                return True
            except Exception as e:
                print(f"Error starting camera: {e}")
                return False

    def stop(self):
        """Stop the camera"""
        with self.lock:
            self.active = False
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                # Force cleanup on macOS
                cv2.destroyAllWindows()
                # Small delay to ensure camera is fully released
                time.sleep(0.1)

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera"""
        with self.lock:
            if not self.active or self.camera is None:
                return None

            success, frame = self.camera.read()
            return frame if success else None

    def is_active(self) -> bool:
        """Check if camera is active"""
        return self.active


class FacialRecognitionSystem:
    """Main facial recognition system orchestrator"""

    def __init__(self, config: Dict):
        self.config = config
        self.face_detector = FaceDetector(
            config['yunet_model_path'],
            config['detection_score_threshold']
        )
        self.face_recognizer = FaceRecognizer(config['face_recognition_model_path'])
        self.face_database = FaceDatabase(self.face_recognizer)
        self.session = AttendanceSession()
        self.camera_manager = CameraManager()
        self.face_tracker = FaceTracker(max_age=10)  # Track faces for up to 10 frames
        self.scanning_active = False

        # Recognition thresholds (optimized for uploaded photos)
        self.recognition_threshold = config.get('recognition_threshold', 0.25)  # Lowered for better matching
        self.confidence_threshold = config.get('confidence_threshold', 0.4)  # Lowered for easier detection

        # Face quality thresholds
        self.min_face_size = 40  # Minimum face width/height in pixels (further relaxed)
        self.min_sharpness = 20  # Minimum Laplacian variance for sharpness (relaxed, not used in process_frame)

    def initialize(self) -> bool:
        """Initialize all components"""
        print("=" * 60)
        print("Facial Recognition System")
        print("=" * 60)

        print("\nInitializing models...")
        if not self.face_detector.detector or not self.face_recognizer.recognizer:
            return False

        print("\nLoading known faces...")
        return self.face_database.load_from_database()

    def _check_face_quality(self, frame: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[bool, str]:
        """
        Check if face meets quality requirements.

        Returns:
            (is_good_quality, reason) tuple
        """
        x, y, w, h = bbox

        # Check minimum face size
        if w < self.min_face_size or h < self.min_face_size:
            return False, "too_small"

        # Extract face region for sharpness check
        face_region = frame[max(0, y):min(frame.shape[0], y+h), max(0, x):min(frame.shape[1], x+w)]

        if face_region.size == 0:
            return False, "invalid_region"

        # Check sharpness using Laplacian variance
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY) if len(face_region.shape) == 3 else face_region
        laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()

        if laplacian_var < self.min_sharpness:
            return False, "too_blurry"

        return True, "good"

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame with face detection and recognition.
        Includes quality filtering and temporal tracking for improved accuracy.
        """
        if not self.scanning_active:
            return frame

        # Detect faces
        faces = self.face_detector.detect(frame)

        detections = []  # Store (bbox, student_id, name, confidence) for tracking
        unmatched_faces = []  # Store unmatched face bboxes

        if faces is not None:
            # Filter and sort faces by detection confidence
            valid_faces = []
            frame_height, frame_width = frame.shape[:2]

            for face in faces:
                detection_confidence = face[14]

                # Skip low-confidence detections
                if detection_confidence <= self.confidence_threshold:
                    continue

                # Validate face geometry (filter out hands, arms, etc.)
                if not self.face_detector.is_valid_face(face, frame_width, frame_height):
                    continue

                valid_faces.append((face, detection_confidence))

            # Sort by confidence and only process the best detection
            # This prevents false positives from multiple weak detections
            valid_faces.sort(key=lambda x: x[1], reverse=True)

            # Process only the top detection (highest confidence face)
            for face, detection_confidence in valid_faces[:1]:  # Only process best match
                x, y, w, h = face[:4].astype(int)

                # Extract features
                feature = self.face_recognizer.extract_features(frame, face)

                if feature is not None:
                    # Find matching student
                    match = self.face_database.find_match(feature, self.recognition_threshold)

                    if match:
                        student_id, name, similarity = match
                        confidence_pct = self._normalize_confidence(similarity)

                        # Add to detections for tracking
                        detections.append(((x, y, w, h), student_id, name, confidence_pct))
                    else:
                        # No match - store for "Unknown" box
                        unmatched_faces.append((x, y, w, h))

        # Update tracker with current frame detections
        confirmed_tracks = self.face_tracker.update(detections)

        # Build a map of student_id -> bbox from current detections
        detection_map = {det_id: det_bbox for det_bbox, det_id, _, _ in detections}

        # Draw boxes for ALL detections immediately (don't wait for confirmation)
        drawn_student_ids = set()
        for det_bbox, student_id, name, confidence_pct in detections:
            x, y, w, h = det_bbox

            # Check if this student is confirmed by tracker
            is_confirmed = any(sid == student_id for sid, _, _, _ in confirmed_tracks)

            # Draw green box for recognized student
            box_color = (0, 255, 0)
            label = f"{name} ({confidence_pct:.1f}%)"

            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            cv2.putText(frame, label, (x, y-10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

            # Add to session ONLY if confirmed by tracker
            if is_confirmed:
                self.session.add_student(
                    student_id, name,
                    confidence_pct,
                    100  # liveness - not used currently
                )

            drawn_student_ids.add(student_id)

        # Draw orange boxes for unmatched faces
        for x, y, w, h in unmatched_faces:
            box_color = (0, 165, 255)  # Orange
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            cv2.putText(frame, "Unknown", (x, y-10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        return frame

    @staticmethod
    def _normalize_confidence(similarity: float) -> float:
        """
        Normalize cosine similarity to meaningful percentage (75-100%)
        Improved granularity for better confidence representation
        """
        if similarity >= 0.50:
            # Excellent match: 95-100%
            return 95 + min((similarity - 0.50) / 0.20, 1.0) * 5
        elif similarity >= 0.40:
            # Very good match: 88-95%
            return 88 + ((similarity - 0.40) / 0.10) * 7
        elif similarity >= 0.30:
            # Good match: 80-88%
            return 80 + ((similarity - 0.30) / 0.10) * 8
        else:
            # Acceptable match: 75-80%
            return 75 + ((similarity - 0.25) / 0.05) * 5

    def generate_video_stream(self):
        """Generate video frames for streaming"""
        while self.camera_manager.is_active():
            frame = self.camera_manager.read_frame()
            if frame is None:
                break

            # Process frame with recognition if scanning is active
            if self.scanning_active:
                frame = self.process_frame(frame)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            time.sleep(0.033)  # ~30 FPS


# =============================================================================
# FLASK APPLICATION
# =============================================================================

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    'yunet_model_path': os.path.join(os.path.dirname(__file__), 'models', 'face_detection_yunet_2023mar.onnx'),
    'face_recognition_model_path': os.path.join(os.path.dirname(__file__), 'models', 'face_recognition_sface_2021dec.onnx'),
    'detection_score_threshold': 0.5,  # Lowered from 0.6 for better face detection
    'recognition_threshold': 0.25,  # Lowered from 0.30 for better matching with uploaded photos
    'confidence_threshold': 0.4  # Lowered from 0.5 to detect faces more easily
}

# Initialize the facial recognition system
recognition_system = FacialRecognitionSystem(CONFIG)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Facial Recognition Controller running',
        'models_initialized': recognition_system.face_detector.detector is not None,
        'known_faces': recognition_system.face_database.get_count()
    }), 200


def update_camera_device_status(status: str):
    """Update camera device status in devices table"""
    try:
        device_id = 'facial-recognition-camera'
        now = datetime.now()

        # Check if device exists
        existing = db_utils.query_one(
            "SELECT id FROM devices WHERE id = %s",
            (device_id,)
        )

        if existing:
            # Update existing device
            db_utils.execute_update(
                """UPDATE devices
                   SET status = %s, last_seen = %s
                   WHERE id = %s""",
                (status, now, device_id)
            )
        else:
            # Insert new device
            db_utils.execute_update(
                """INSERT INTO devices (id, name, type, status, last_seen, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (device_id, 'Facial Recognition Camera', 'camera', status, now, now)
            )
    except Exception as e:
        print(f"Error updating camera device status: {e}")


@app.route('/api/facial-recognition/camera/start', methods=['POST'])
def start_camera():
    """Start the camera feed"""
    if recognition_system.camera_manager.start():
        update_camera_device_status('online')
        return jsonify({'ok': True, 'message': 'Camera started successfully'})
    return jsonify({'ok': False, 'error': 'Failed to open camera'}), 500


@app.route('/api/facial-recognition/camera/stop', methods=['POST'])
def stop_camera():
    """Stop the camera feed"""
    recognition_system.scanning_active = False
    recognition_system.camera_manager.stop()
    update_camera_device_status('offline')
    return jsonify({'ok': True, 'message': 'Camera stopped successfully'})


@app.route('/api/facial-recognition/camera/status', methods=['GET'])
def camera_status():
    """Get current camera status"""
    is_active = recognition_system.camera_manager.is_active()
    return jsonify({
        'ok': True,
        'active': is_active,
        'scanning': recognition_system.scanning_active
    })


@app.route('/api/facial-recognition/camera/feed')
def camera_feed():
    """Video streaming route"""
    if not recognition_system.camera_manager.is_active():
        return jsonify({'ok': False, 'error': 'Camera not active'}), 400

    return Response(recognition_system.generate_video_stream(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/facial-recognition/scanning/start', methods=['POST'])
def start_scanning():
    """Start facial recognition scanning"""
    if not recognition_system.camera_manager.is_active():
        return jsonify({'ok': False, 'error': 'Camera not active'}), 400

    payload = request.get_json() or {}
    recognition_system.session.start(**payload)
    recognition_system.scanning_active = True

    return jsonify({
        'ok': True,
        'message': 'Scanning started',
        'session': recognition_system.session.get_data()
    })


@app.route('/api/facial-recognition/scanning/stop', methods=['POST'])
def stop_scanning():
    """Stop facial recognition scanning"""
    recognition_system.scanning_active = False
    return jsonify({'ok': True, 'message': 'Scanning stopped'})


@app.route('/api/facial-recognition/faces/refresh', methods=['POST'])
def refresh_faces():
    """Reload face encodings from database"""
    def background_load():
        recognition_system.face_database.load_from_database()

    thread = threading.Thread(target=background_load, daemon=True)
    thread.start()

    return jsonify({
        'ok': True,
        'message': 'Face refresh started in background',
        'count': recognition_system.face_database.get_count()
    })


@app.route('/api/facial-recognition/faces/list', methods=['GET'])
def list_loaded_faces():
    """Get list of currently loaded face encodings"""
    faces = recognition_system.face_database.get_all_faces()
    return jsonify({
        'ok': True,
        'count': len(faces),
        'faces': faces
    })


@app.route('/api/facial-recognition/session', methods=['GET'])
def get_session():
    """Get current session data with database-synced attendance status"""
    session_data = recognition_system.session.get_data()

    # Sync attendance status from database for all recognized students today
    if session_data.get('recognized_students'):
        # Get all attendance records from today
        db_records = db_utils.query_all(
            """SELECT s.student_id, a.status
               FROM attendance a
               JOIN students s ON a.student_id = s.id
               WHERE DATE(a.check_in_time) = CURDATE()"""
        )

        # Create a map of student_id -> status from database
        status_map = {record['student_id']: record['status'] for record in db_records}

        # Update session data with database status
        for student in session_data['recognized_students']:
            if student['student_id'] in status_map:
                student['status'] = status_map[student['student_id']]
            else:
                student['status'] = 'present'  # Default if not in DB yet

    return jsonify({
        'ok': True,
        'session': session_data
    })


@app.route('/api/facial-recognition/attendance/save-one', methods=['POST'])
def save_single_attendance():
    """Save a single attendance record"""
    payload = request.get_json() or {}

    student_id = payload.get('student_id')
    timetable_id = payload.get('timetable_id')  # Get timetable_id directly from request
    module_id = payload.get('module_id')
    confidence = payload.get('confidence', 0)

    if not student_id or not module_id:
        return jsonify({'ok': False, 'error': 'student_id and module_id required'}), 400

    try:
        # Get student internal ID
        student_data = db_utils.query_one(
            "SELECT id FROM students WHERE student_id = %s",
            (student_id,)
        )

        if not student_data:
            return jsonify({'ok': False, 'error': 'Student not found'}), 404

        # Check if attendance already exists for today
        existing = db_utils.query_one(
            """SELECT id FROM attendance
               WHERE student_id = %s
                 AND module_id = %s
                 AND DATE(check_in_time) = CURDATE()
               LIMIT 1""",
            (student_data['id'], module_id)
        )

        if existing:
            return jsonify({'ok': True, 'message': 'Attendance already marked', 'already_marked': True})

        # Get class start time from timetable and attendance policy
        timetable_data = db_utils.query_one(
            """SELECT t.start_time, t.module_id
               FROM timetable t
               WHERE t.id = %s""",
            (timetable_id,)
        )

        # Get attendance policy for this module
        policy = db_utils.query_one(
            """SELECT grace_period_minutes, late_threshold_minutes
               FROM attendance_policies
               WHERE entity_id = %s AND applies_to = 'course' AND is_active = 1
               LIMIT 1""",
            (module_id,)
        )

        # Calculate attendance status based on arrival time
        from datetime import datetime, timedelta
        status = 'present'  # Default to present

        if timetable_data and policy:
            # Get class start time
            class_start = timetable_data['start_time']

            # Convert timedelta to seconds if needed
            if isinstance(class_start, timedelta):
                class_start_seconds = int(class_start.total_seconds())
            else:
                class_start_seconds = class_start.hour * 3600 + class_start.minute * 60 + class_start.second

            # Get current time in seconds
            now = datetime.now().time()
            current_seconds = now.hour * 3600 + now.minute * 60 + now.second

            # Calculate minutes late
            seconds_late = current_seconds - class_start_seconds
            minutes_late = seconds_late / 60

            grace_period = policy['grace_period_minutes']
            late_threshold = policy['late_threshold_minutes']

            # Determine status
            if minutes_late <= grace_period:
                status = 'present'
            elif minutes_late <= late_threshold:
                status = 'late'
            else:
                status = 'late'  # Still mark as late (could be 'absent' if policy requires)

        # Insert attendance record with calculated status
        db_utils.execute(
            """INSERT INTO attendance
               (student_id, module_id, timetable_id, status, face_confidence, is_manual)
               VALUES (%s, %s, %s, %s, %s, FALSE)""",
            (student_data['id'], module_id, timetable_id, status, confidence)
        )

        return jsonify({
            'ok': True,
            'message': 'Attendance marked successfully',
            'student_id': student_id,
            'status': status
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/facial-recognition/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance for a specific class"""
    module_id = request.args.get('module_id')

    if not module_id:
        return jsonify({'ok': False, 'error': 'module_id required'}), 400

    try:
        today = date.today()

        # Get all attendance records for today
        records = db_utils.query_all(
            """SELECT
                s.student_id,
                s.first_name,
                s.last_name,
                a.face_confidence,
                a.check_in_time
               FROM attendance a
               JOIN students s ON a.student_id = s.id
               WHERE a.module_id = %s
                 AND DATE(a.check_in_time) = %s
                 AND a.status = 'present'
               ORDER BY a.check_in_time""",
            (module_id, today)
        )

        # Format for frontend
        students = []
        for record in records:
            students.append({
                'student_id': record['student_id'],
                'name': f"{record['first_name']} {record['last_name']}",
                'confidence': float(record['face_confidence']) if record['face_confidence'] else 0,
                'liveness': 95.0,  # Default liveness value
                'check_in_time': record['check_in_time'].isoformat() if record['check_in_time'] else None
            })

        return jsonify({
            'ok': True,
            'students': students
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/facial-recognition/attendance/reset', methods=['POST'])
def reset_attendance():
    """Reset (delete) today's attendance for a specific class - for testing only"""
    payload = request.get_json() or {}
    module_id = payload.get('module_id')

    if not module_id:
        return jsonify({'ok': False, 'error': 'module_id required'}), 400

    try:
        today = date.today()

        # Delete all attendance records for today
        db_utils.execute(
            """DELETE FROM attendance
               WHERE module_id = %s
                 AND DATE(check_in_time) = %s""",
            (module_id, today)
        )

        return jsonify({
            'ok': True,
            'message': 'Attendance reset successfully'
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/facial-recognition/attendance/session', methods=['GET'])
def get_session_attendance():
    """Get attendance for a specific session/timetable"""
    timetable_id = request.args.get('timetable_id')

    if not timetable_id:
        return jsonify({'ok': False, 'error': 'timetable_id required'}), 400

    try:
        # Get all attendance records for this specific session
        records = db_utils.query_all(
            """SELECT
                s.student_id,
                s.first_name,
                s.last_name,
                a.face_confidence,
                a.check_in_time
               FROM attendance a
               JOIN students s ON a.student_id = s.id
               WHERE a.timetable_id = %s
                 AND a.status = 'present'
               ORDER BY a.check_in_time""",
            (timetable_id,)
        )

        # Format for frontend
        students = []
        for record in records:
            students.append({
                'student_id': record['student_id'],
                'name': f"{record['first_name']} {record['last_name']}",
                'confidence': float(record['face_confidence']) if record['face_confidence'] else 0,
                'liveness': 100.0,  # Default liveness value
                'check_in_time': record['check_in_time'].isoformat() if record['check_in_time'] else None
            })

        return jsonify({
            'ok': True,
            'students': students
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/facial-recognition/sessions/current', methods=['GET'])
def get_current_session():
    """Get the current or next session based on time from timetable"""
    try:
        today = date.today()
        now = datetime.now().time()
        day_of_week = today.isoweekday()  # 1=Monday, 7=Sunday

        # First, try to find a class that is currently ongoing
        # Priority: specific date classes first, then recurring weekly classes
        current = db_utils.query_one(
            """SELECT
                t.id as timetable_id,
                t.module_id,
                t.day_of_week,
                t.start_time,
                t.end_time,
                t.room,
                t.class_date,
                c.module_code,
                c.module_name,
                (SELECT COUNT(*) FROM student_enrollments WHERE module_id = t.module_id) as total_students
               FROM timetable t
               JOIN modules c ON t.module_id = c.id
               WHERE t.is_active = 1
                 AND (
                   (t.class_date = %s) OR
                   (t.class_date IS NULL AND t.day_of_week = %s)
                 )
                 AND t.start_time <= %s
                 AND t.end_time >= %s
               ORDER BY t.class_date DESC, t.start_time
               LIMIT 1""",
            (today, day_of_week, now, now)
        )

        # If no current class, get the next upcoming class for today
        if not current:
            current = db_utils.query_one(
                """SELECT
                    t.id as timetable_id,
                    t.module_id,
                    t.day_of_week,
                    t.start_time,
                    t.end_time,
                    t.room,
                    t.class_date,
                    c.module_code,
                    c.module_name,
                    (SELECT COUNT(*) FROM student_enrollments WHERE module_id = t.module_id) as total_students
                   FROM timetable t
                   JOIN modules c ON t.module_id = c.id
                   WHERE t.is_active = 1
                     AND (
                       (t.class_date = %s) OR
                       (t.class_date IS NULL AND t.day_of_week = %s)
                     )
                     AND t.start_time > %s
                   ORDER BY t.class_date DESC, t.start_time
                   LIMIT 1""",
                (today, day_of_week, now)
            )

        # If no upcoming class today, look for the next class in the coming 7 days
        if not current:
            current = db_utils.query_one(
                """SELECT
                    t.id as timetable_id,
                    t.module_id,
                    t.day_of_week,
                    t.start_time,
                    t.end_time,
                    t.room,
                    t.class_date,
                    c.module_code,
                    c.module_name,
                    (SELECT COUNT(*) FROM student_enrollments WHERE module_id = t.module_id) as total_students,
                    CASE
                        WHEN t.class_date IS NOT NULL THEN t.class_date
                        WHEN MOD(t.day_of_week - %s + 7, 7) = 0 THEN DATE_ADD(%s, INTERVAL 7 DAY)
                        ELSE DATE_ADD(%s, INTERVAL MOD(t.day_of_week - %s + 7, 7) DAY)
                    END as next_occurrence
                   FROM timetable t
                   JOIN modules c ON t.module_id = c.id
                   WHERE t.is_active = 1
                     AND (
                       (t.class_date > %s AND t.class_date <= DATE_ADD(%s, INTERVAL 7 DAY)) OR
                       (t.class_date IS NULL)
                     )
                   ORDER BY next_occurrence, t.start_time
                   LIMIT 1""",
                (day_of_week, today, today, day_of_week, today, today)
            )

        if not current:
            return jsonify({'ok': True, 'session': None, 'message': 'No classes scheduled in the next 7 days'})

        # Convert timedelta to time objects (MySQL TIME columns return timedelta)
        if isinstance(current['start_time'], timedelta):
            current['start_time'] = (datetime.min + current['start_time']).time()
        if isinstance(current['end_time'], timedelta):
            current['end_time'] = (datetime.min + current['end_time']).time()

        # Determine the actual class date
        if current['class_date']:
            # Specific date class - use the class_date
            actual_date = current['class_date']
        else:
            # Recurring class - calculate next occurrence based on day_of_week
            class_day = current.get('day_of_week', day_of_week)
            days_ahead = (class_day - day_of_week) % 7
            if days_ahead == 0:
                # Same day - check if class time has passed
                if current['start_time'] <= now:
                    # Class has started or ended today, next occurrence is next week
                    days_ahead = 7
            actual_date = today + timedelta(days=days_ahead)

        # Check if class is currently live (only if it's today)
        is_live = (actual_date == today and current['start_time'] <= now <= current['end_time'])

        # Get present count for the actual class date (from attendance records)
        present_count_data = db_utils.query_one(
            """SELECT COUNT(*) as count
               FROM attendance
               WHERE module_id = %s
                 AND DATE(check_in_time) = %s
                 AND status = 'present'""",
            (current['module_id'], actual_date)
        )
        present_count = present_count_data['count'] if present_count_data else 0

        session_data = {
            'session_id': None,  # No attendance_session yet
            'timetable_id': current['timetable_id'],
            'module_id': current['module_id'],
            'date': actual_date.isoformat(),
            'time': current['start_time'].strftime('%H:%M') if current['start_time'] else None,
            'end_time': current['end_time'].strftime('%H:%M') if current['end_time'] else None,
            'room': current['room'] or 'TBD',
            'module_code': current['module_code'],
            'module_name': current['module_name'],
            'enrolled_count': current['total_students'],
            'present_count': present_count,
            'is_live': is_live
        }

        return jsonify({'ok': True, 'session': session_data})

    except Exception as e:
        print(f"Error getting current session: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# Get all timetable entries for monthly calendar view
@app.route('/api/facial-recognition/timetable/all', methods=['GET'])
def get_all_timetable():
    try:
        # Get all active timetable entries with class information
        query = """
            SELECT
                t.id as timetable_id,
                t.module_id,
                t.day_of_week,
                t.class_date,
                t.start_time,
                t.end_time,
                t.room,
                c.module_code,
                c.module_name
            FROM timetable t
            JOIN modules c ON t.module_id = c.id
            WHERE t.is_active = 1
            ORDER BY t.class_date, t.day_of_week, t.start_time
        """

        results = db_utils.query_all(query)

        if not results:
            return jsonify({'ok': True, 'classes': []})

        # Map day names to numbers (1=Monday, 7=Sunday)
        day_map = {
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4,
            'Friday': 5,
            'Saturday': 6,
            'Sunday': 7
        }

        classes = []
        for row in results:
            # Handle start_time and end_time which might be timedelta or time objects
            start_time = row['start_time']
            end_time = row['end_time']

            if isinstance(start_time, timedelta):
                start_time = (datetime.min + start_time).time()
            if isinstance(end_time, timedelta):
                end_time = (datetime.min + end_time).time()

            # Convert day_of_week string to number
            day_of_week_num = day_map.get(row['day_of_week']) if row['day_of_week'] else None

            class_entry = {
                'timetable_id': row['timetable_id'],
                'module_id': row['module_id'],
                'module_code': row['module_code'],
                'module_name': row['module_name'],
                'day_of_week': day_of_week_num,  # 1=Monday, 7=Sunday
                'class_date': row['class_date'].isoformat() if row['class_date'] else None,
                'start_time': start_time.strftime('%H:%M') if start_time else None,
                'end_time': end_time.strftime('%H:%M') if end_time else None,
                'room': row['room']
            }
            classes.append(class_entry)

        return jsonify({'ok': True, 'classes': classes})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize the system
    if not recognition_system.initialize():
        print("✗ Failed to initialize facial recognition system")
        sys.exit(1)

    print("\nRunning on: http://127.0.0.1:5011")
    print("Endpoints:")
    print("  - Camera: /api/facial-recognition/camera/*")
    print("  - Scanning: /api/facial-recognition/scanning/*")
    print("  - Faces: /api/facial-recognition/faces/*")
    print("  - Session: /api/facial-recognition/session")
    print("  - Attendance: /api/facial-recognition/attendance/*")
    print("=" * 60)

    app.run(debug=True, port=5011, host='127.0.0.1', use_reloader=False)
