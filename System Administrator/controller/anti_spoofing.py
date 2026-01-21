"""
Anti-Spoofing Module using MobileNetV3-Small-FAS
Lightweight face liveness detection to prevent photo/video spoofing
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms

# Configuration
ANTI_SPOOFING_ENABLED = True  # Toggle to enable/disable
LIVENESS_THRESHOLD = 0.42  # Confidence threshold (0-1) - Balanced: blocks photos (25-35%) but allows real faces (37-50%)
DEBUG_MODE = False  # Enable for detailed logging


class MobileNetV3SmallFAS(nn.Module):
    """
    Simplified MobileNetV3-Small for Face Anti-Spoofing
    Based on MobileNetV3-Small architecture with binary classification output
    """
    def __init__(self):
        super(MobileNetV3SmallFAS, self).__init__()

        # Simple convolutional layers (lightweight)
        self.features = nn.Sequential(
            # Input: 3x128x128
            nn.Conv2d(3, 16, 3, stride=2, padding=1),  # -> 16x64x64
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),

            nn.Conv2d(16, 32, 3, stride=2, padding=1),  # -> 32x32x32
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            nn.Conv2d(32, 64, 3, stride=2, padding=1),  # -> 64x16x16
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.AdaptiveAvgPool2d(1),  # -> 64x1x1
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(64, 2),  # Binary: [spoof, live]
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class AntiSpoofingDetector:
    """
    Face Anti-Spoofing Detector with multiple checks
    Combines deep learning model with traditional CV techniques
    """

    def __init__(self, model_path=None):
        """
        Initialize anti-spoofing detector
        Args:
            model_path: Path to pre-trained model weights (optional)
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = MobileNetV3SmallFAS().to(self.device)

        # Load pre-trained weights if available
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"✓ Loaded anti-spoofing model from {model_path}")
            except Exception as e:
                print(f"⚠ Could not load model weights: {e}")
                print("  Using fallback liveness detection")

        self.model.eval()

        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        # Feature trackers for multi-frame analysis
        self.frame_buffer = []
        self.max_buffer_size = 5

    def preprocess_face(self, face_image):
        """
        Preprocess face image for anti-spoofing model
        Args:
            face_image: BGR face image (numpy array)
        Returns:
            Preprocessed tensor
        """
        # Convert BGR to RGB
        rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        # Apply transformations
        tensor = self.transform(rgb_face)
        tensor = tensor.unsqueeze(0)  # Add batch dimension

        return tensor.to(self.device)

    def check_texture_quality(self, face_image):
        """
        Check image texture quality (detect screen moiré patterns, print artifacts)
        Returns: score between 0-1 (higher = more likely real)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Calculate Laplacian variance (texture sharpness)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Real faces have higher variance than photos/screens
        # Normalize to 0-1 range
        texture_score = min(laplacian_var / 500.0, 1.0)

        if DEBUG_MODE:
            print(f"  Texture score: {texture_score:.3f} (var: {laplacian_var:.1f})")

        return texture_score

    def check_color_diversity(self, face_image):
        """
        Check color diversity (real skin has more color variation than screens/prints)
        Returns: score between 0-1 (higher = more likely real)
        """
        # Calculate color histogram
        hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)

        # Calculate standard deviation in hue and saturation channels
        h_std = np.std(hsv[:, :, 0])
        s_std = np.std(hsv[:, :, 1])

        # Real faces have more color diversity
        color_score = min((h_std + s_std) / 100.0, 1.0)

        if DEBUG_MODE:
            print(f"  Color score: {color_score:.3f} (h_std: {h_std:.1f}, s_std: {s_std:.1f})")

        return color_score

    def check_brightness_consistency(self, face_image):
        """
        Check brightness consistency (screens often have uniform backlighting)
        Returns: score between 0-1 (higher = more likely real)
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Calculate local brightness variation
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)

        # Real faces have natural lighting variation
        brightness_score = min(std_brightness / 50.0, 1.0)

        if DEBUG_MODE:
            print(f"  Brightness score: {brightness_score:.3f} (std: {std_brightness:.1f})")

        return brightness_score

    def check_screen_reflection(self, face_image):
        """
        Detect phone/screen reflections and digital display characteristics
        Screens have: uniform glow, edge artifacts, pixel grid patterns
        Returns: score between 0-1 (higher = more likely real, lower = likely screen)
        """
        try:
            # Convert to HSV for better saturation analysis
            hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)

            # Check for uniform high brightness (screen glow) - MORE AGGRESSIVE
            high_brightness_pixels = np.sum(v > 180) / v.size  # Lowered from 200
            if high_brightness_pixels > 0.2:  # More than 20% bright pixels (was 30%)
                screen_glow_penalty = 0.4  # Stronger penalty (was 0.3)
            else:
                screen_glow_penalty = 0.0

            # Check for low saturation (screens often wash out colors) - MORE AGGRESSIVE
            low_saturation_pixels = np.sum(s < 50) / s.size  # Raised from 40
            if low_saturation_pixels > 0.4:  # More than 40% desaturated (was 50%)
                low_sat_penalty = 0.3  # Stronger penalty (was 0.2)
            else:
                low_sat_penalty = 0.0

            # Check for edge artifacts (screens have sharp rectangular edges) - MORE AGGRESSIVE
            edges = cv2.Canny(cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY), 30, 120)  # More sensitive
            edge_density = np.sum(edges > 0) / edges.size

            if edge_density > 0.10:  # Lower threshold (was 0.15)
                edge_penalty = 0.3  # Stronger penalty (was 0.2)
            else:
                edge_penalty = 0.0

            # Calculate final score (start at 1.0, subtract penalties)
            screen_score = 1.0 - (screen_glow_penalty + low_sat_penalty + edge_penalty)
            screen_score = max(0.0, min(1.0, screen_score))

            if DEBUG_MODE:
                print(f"  Screen detection: {screen_score:.3f} (glow: {high_brightness_pixels:.2f}, low_sat: {low_saturation_pixels:.2f}, edges: {edge_density:.3f})")

            return screen_score

        except Exception as e:
            if DEBUG_MODE:
                print(f"  Screen detection error: {e}")
            return 1.0  # Assume real if detection fails

    def detect_liveness(self, face_image, use_model=False):
        """
        Main liveness detection function
        Args:
            face_image: BGR face image
            use_model: Whether to use deep learning model (requires trained weights)
        Returns:
            (is_live: bool, confidence: float, details: dict)
        """
        if not ANTI_SPOOFING_ENABLED:
            return True, 1.0, {"method": "disabled"}

        try:
            # Multi-check approach for better accuracy
            texture_score = self.check_texture_quality(face_image)
            color_score = self.check_color_diversity(face_image)
            brightness_score = self.check_brightness_consistency(face_image)
            screen_score = self.check_screen_reflection(face_image)

            # If model is trained and available, use it
            model_score = 0.5  # Default neutral score
            if use_model:
                tensor = self.preprocess_face(face_image)
                with torch.no_grad():
                    outputs = self.model(tensor)
                    probs = torch.softmax(outputs, dim=1)
                    model_score = probs[0][1].item()  # Probability of "live"

            # Weighted combination of scores
            weights = {
                'texture': 0.25,
                'color': 0.20,
                'brightness': 0.20,
                'screen': 0.25,  # NEW: Screen detection
                'model': 0.1 if use_model else 0.0
            }

            # Redistribute model weight if not used
            if not use_model:
                weights['texture'] += 0.05
                weights['color'] += 0.025
                weights['brightness'] += 0.025
                weights['screen'] += 0.05

            final_score = (
                texture_score * weights['texture'] +
                color_score * weights['color'] +
                brightness_score * weights['brightness'] +
                screen_score * weights['screen'] +
                model_score * weights['model']
            )

            is_live = final_score >= LIVENESS_THRESHOLD

            details = {
                'texture': round(texture_score, 3),
                'color': round(color_score, 3),
                'brightness': round(brightness_score, 3),
                'screen': round(screen_score, 3),
                'model': round(model_score, 3) if use_model else None,
                'final': round(final_score, 3),
                'threshold': LIVENESS_THRESHOLD,
                'method': 'hybrid_v2' if use_model else 'cv_with_screen_detection'
            }

            if DEBUG_MODE:
                print(f"\n🔍 Liveness Detection:")
                print(f"  Final Score: {final_score:.3f}")
                print(f"  Decision: {'✓ LIVE' if is_live else '✗ SPOOF'}")
                print(f"  Details: {details}")

            return is_live, final_score, details

        except Exception as e:
            print(f"⚠ Anti-spoofing error: {e}")
            # Fail-open: allow if error occurs
            return True, 0.5, {"error": str(e)}

    def update_frame_buffer(self, face_image):
        """
        Update frame buffer for temporal analysis
        Can be used for detecting video replay attacks
        """
        self.frame_buffer.append(face_image)
        if len(self.frame_buffer) > self.max_buffer_size:
            self.frame_buffer.pop(0)

    def check_temporal_consistency(self):
        """
        Check if frames show natural movement patterns
        (Future enhancement for detecting video replay)
        """
        if len(self.frame_buffer) < 3:
            return True, 1.0

        # TODO: Implement optical flow or frame difference analysis
        # For now, return True
        return True, 1.0


# Global detector instance
_detector = None

def get_detector():
    """Get or create anti-spoofing detector instance"""
    global _detector
    if _detector is None:
        _detector = AntiSpoofingDetector()
    return _detector


def check_face_liveness(face_image, use_model=False):
    """
    Convenient wrapper function for liveness detection
    Args:
        face_image: BGR face image (numpy array)
        use_model: Whether to use deep learning model
    Returns:
        (is_live: bool, confidence: float, details: dict)
    """
    detector = get_detector()
    return detector.detect_liveness(face_image, use_model=use_model)


# Configuration helpers
def enable_anti_spoofing():
    """Enable anti-spoofing checks"""
    global ANTI_SPOOFING_ENABLED
    ANTI_SPOOFING_ENABLED = True
    print("✓ Anti-spoofing ENABLED")


def disable_anti_spoofing():
    """Disable anti-spoofing checks"""
    global ANTI_SPOOFING_ENABLED
    ANTI_SPOOFING_ENABLED = False
    print("✓ Anti-spoofing DISABLED")


def set_liveness_threshold(threshold):
    """Set liveness detection threshold (0-1)"""
    global LIVENESS_THRESHOLD
    LIVENESS_THRESHOLD = max(0.0, min(1.0, threshold))
    print(f"✓ Liveness threshold set to {LIVENESS_THRESHOLD}")


def enable_debug():
    """Enable debug logging"""
    global DEBUG_MODE
    DEBUG_MODE = True
    print("✓ Debug mode ENABLED")


def disable_debug():
    """Disable debug logging"""
    global DEBUG_MODE
    DEBUG_MODE = False
    print("✓ Debug mode DISABLED")
